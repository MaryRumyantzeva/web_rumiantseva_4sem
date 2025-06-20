from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .models import Bike, User, Like, Comment, BikeImage, Reservation
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
from uuid import uuid4
from .utils import allowed_file  
from flask import abort


bp = Blueprint('kp', __name__, template_folder='templates')

@bp.route('/')
def home():
    try:       
        # Пробуем простейший шаблон
        return render_template('kp/index.html')
    except Exception as e:
        return f"Ошибка: {str(e)}", 500
    

@bp.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)  # Запрет доступа
    users = User.query.all()
    bikes = Bike.query.all()
    return render_template('admin_panel.html', users=users, bikes=bikes)
    

@bp.route('/bikes')
def bikes():
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    query = Bike.query
    
    if category:
        query = query.filter_by(category=category)
    if min_price:
        query = query.filter(Bike.price >= float(min_price))
    if max_price:
        query = query.filter(Bike.price <= float(max_price))
    
    bikes = query.all()
    categories = db.session.query(Bike.category.distinct()).all()  # Уникальные категории
    return render_template('bikes.html', bikes=bikes, categories=categories)

@bp.route("/add_bike", methods=["GET", "POST"])
@login_required
def add_bike():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")

        if not title or not description or not price or not category:
            flash("Пожалуйста, заполните все поля", "danger")
            return redirect(url_for("kp.add_bike"))

        try:
            price = int(price)
        except ValueError:
            flash("Цена должна быть числом", "danger")
            return redirect(url_for("kp.add_bike"))

        # Создаем велосипед
        new_bike = Bike(
            title=title,
            description=description,
            price=price,
            category=category,
            owner_id=current_user.id
        )
        db.session.add(new_bike)
        db.session.flush()  # чтобы получить new_bike.id до commit

        # Папка для загрузок
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Обработка изображений
        if 'images' in request.files:
            files = request.files.getlist('images')
            print("Получено файлов:", len(files))
            for file in files:
                if file.filename:
                    print("Файл:", file.filename)
                    filename = f"{current_user.id}_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    print("Сохраняем:", filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)

                    # Сохраняем в БД
                    image = BikeImage(bike_id=new_bike.id, filename=filename)
                    db.session.add(image)

        db.session.commit()
        flash("Велосипед добавлен!", "success")
        return redirect(url_for("kp.bikes"))

    return render_template("add_bike.html")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Пароли не совпадают.', 'danger')
            return redirect(url_for('kp.register'))

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято.', 'danger')
            return redirect(url_for('kp.register'))

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('kp.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('kp.home'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно вошли.', 'success')
            return redirect(url_for('kp.home'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('kp.home'))


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        file = request.files.get('avatar')
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            current_user.avatar_url = filename
            db.session.commit()
            flash('Аватар обновлён!', 'success')
            return redirect(url_for('kp.profile'))

    # 💡 Добавляем велосипеды пользователя
    my_bikes = Bike.query.filter_by(owner_id=current_user.id).all()

    # 💡 Добавляем велосипеды, на которые пользователь поставил лайк
    liked_bike_ids = [like.bike_id for like in current_user.likes]
    liked_bikes = Bike.query.filter(Bike.id.in_(liked_bike_ids)).all()

    return render_template('profile.html',
                           my_bikes=my_bikes,
                           liked_bikes=liked_bikes)


    
@bp.route('/like/<int:bike_id>', methods=['POST'])
@login_required
def like(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    like = Like.query.filter_by(user_id=current_user.id, bike_id=bike.id).first()

    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, bike_id=bike.id))

    db.session.commit()
    return redirect(url_for('kp.bikes', bike_id=bike.id))


@bp.route('/bike/<int:bike_id>', methods=['GET', 'POST'])
def bike_detail(bike_id):
    bike = Bike.query.get_or_404(bike_id)

    # Получаем изображения как список BikeImage объектов
    images = bike.images  # list of BikeImage instances

    if request.method == 'POST' and current_user.is_authenticated:
        text = request.form.get('comment')
        if text:
            comment = Comment(text=text, user_id=current_user.id, bike_id=bike.id)
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий добавлен!', 'success')
        return redirect(url_for('kp.bikes', bike_id=bike.id))

    return render_template('bike_detail.html', bike=bike, images=images)


@bp.route('/reserve/<int:bike_id>', methods=['POST'])
@login_required
def reserve(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    if current_user.id == bike.owner_id:
        flash("Нельзя бронировать свой велосипед.", "warning")
        return redirect(url_for('kp.bike_detail', bike_id=bike.id))

    existing = Reservation.query.filter_by(user_id=current_user.id, bike_id=bike.id).first()
    if existing:
        flash("Вы уже забронировали этот велосипед.", "info")
    else:
        new_res = Reservation(user_id=current_user.id, bike_id=bike.id)
        db.session.add(new_res)
        db.session.commit()
        flash("Велосипед забронирован!", "success")

    return redirect(url_for('kp.bike_detail', bike_id=bike.id))


@bp.route('/bike/<int:bike_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)

    if current_user.id != bike.owner_id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        bike.title = request.form['title']
        bike.price = request.form['price']
        bike.description = request.form['description']

        # === Очищаем старые изображения ===
        if bike.images:
            for img in bike.images:
                # Удаляем с диска
                old_path = os.path.join(current_app.root_path, 'static/uploads', img.filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
                # Удаляем из базы
                db.session.delete(img)

        # === Загружаем новые изображения ===
        files = request.files.getlist('images')
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = f"{current_user.id}_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                db.session.add(BikeImage(bike_id=bike.id, filename=filename))
        print("Файл найден:", file.filename)
        print("Разрешённый?", allowed_file(file.filename))


        db.session.commit()
        flash('Велосипед успешно обновлён!')
        return redirect(url_for('kp.bike_detail', bike_id=bike.id))

    return render_template('edit_bike.html', bike=bike)






@bp.route('/delete/<int:bike_id>')
@login_required
def delete_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    Like.query.filter_by(bike_id=bike.id).delete()
    db.session.delete(bike)
    db.session.commit()
    flash('Велосипед успешно удалён', 'success')
    return redirect(url_for('kp.home'))


@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        bikes = Bike.query.filter(
            (Bike.title.ilike(f'%{query}%')) | (Bike.description.ilike(f'%{query}%'))
        ).all()
    else:
        bikes = []

    categories = db.session.query(Bike.category.distinct()).all()
    return render_template('bikes.html', bikes=bikes, categories=categories)


@bp.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)

    if user.is_admin:
        flash('Нельзя удалить администратора.', 'warning')
        return redirect(url_for('kp.admin_panel'))

    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удалён.', 'success')
    return redirect(url_for('kp.admin_panel'))


@bp.route('/admin/delete_bike/<int:bike_id>')
@login_required
def delete_bike_admin(bike_id):
    if not current_user.is_admin:
        abort(403)

    bike = Bike.query.get_or_404(bike_id)

    db.session.delete(bike)
    db.session.commit()
    flash('Велосипед удалён.', 'success')
    return redirect(url_for('kp.admin_panel'))

@bp.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if not current_user.is_admin:
        abort(403)

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Комментарий удалён.", "info")
    return redirect(url_for('kp.bike_detail', bike_id=comment.bike_id))