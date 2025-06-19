from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .models import Bike, User, Like, Comment
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os


bp = Blueprint('kp', __name__, template_folder='templates')

@bp.route('/')
def home():
    try:       
        # Пробуем простейший шаблон
        return render_template('kp/index.html')
    except Exception as e:
        return f"Ошибка: {str(e)}", 500
    

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


@bp.route('/add_bike', methods=['GET', 'POST'])
@login_required
def add_bike():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        image_url = request.form['image_url']

        new_bike = Bike(
            title=title,
            description=description,
            price=price,
            category=category,
            image_url=image_url,
            owner_id=current_user.id
        )
        db.session.add(new_bike)
        db.session.commit()
        flash('Велосипед успешно добавлен!', 'success')
        return redirect(url_for('kp.bikes'))

    return render_template('add_bike.html')



@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@bp.route('/profile')
@login_required
def profile():
    return render_template('kp/profile.html')

    
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
    return redirect(url_for('kp.bike_detail', bike_id=bike.id))

@bp.route('/bike/<int:bike_id>', methods=['GET', 'POST'])
def bike_detail(bike_id):
    bike = Bike.query.get_or_404(bike_id)

    if request.method == 'POST' and current_user.is_authenticated:
        text = request.form['comment']
        if text:
            comment = Comment(text=text, user_id=current_user.id, bike_id=bike.id)
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий добавлен!', 'success')
            return redirect(url_for('kp.bike_detail', bike_id=bike.id))

    return render_template('bike_detail.html', bike=bike)