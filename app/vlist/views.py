from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from .models import db, Item, User
import os
from werkzeug.utils import secure_filename
import uuid

vlist_bp = Blueprint('vlist', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    """Проверяем допустимое расширение файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 🔹 генерируем уникальный guest_id для каждого посетителя
@vlist_bp.before_app_request
def ensure_guest_id():
    if "guest_id" not in session:
        session["guest_id"] = str(uuid.uuid4())


# 🔹 главная страница со списком подарков
@vlist_bp.route('/')
def index():
    items = Item.query.all()
    is_admin = session.get("is_admin", False)
    guest_id = session.get("guest_id")
    return render_template('vlist.html', items=items, is_admin=is_admin, guest_id=guest_id)


# 🔹 вход админа
@vlist_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["is_admin"] = True
            return redirect(url_for('vlist.index'))
        return "Неверный логин или пароль", 403
    return render_template("login.html")


# 🔹 выход админа
@vlist_bp.route('/logout')
def logout():
    session.pop("is_admin", None)
    return redirect(url_for('vlist.index'))


# 🔹 добавить карточку (только админ)
@vlist_bp.route('/add', methods=['POST'])
def add_item():
    if not session.get("is_admin"):
        return "Доступ запрещён", 403

    title = request.form.get("title")
    description = request.form.get("description")
    image_file = request.files.get("image")

    filename = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)

        # папка загрузки берётся из config
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, filename)
        image_file.save(save_path)

    if title:
        item = Item(title=title, description=description, image=filename)
        db.session.add(item)
        db.session.commit()

    return redirect(url_for('vlist.index'))


# 🔹 забронировать подарок
@vlist_bp.route('/reserve/<int:item_id>', methods=['POST'])
def reserve(item_id):
    item = Item.query.get_or_404(item_id)
    if item.reserved_by:
        return "Этот подарок уже зарезервирован", 400

    item.reserved_by = session["guest_id"]
    db.session.commit()
    return redirect(url_for('vlist.index'))


# 🔹 отменить бронь (только тот, кто бронировал)
@vlist_bp.route('/unreserve/<int:item_id>', methods=['POST'])
def unreserve(item_id):
    item = Item.query.get_or_404(item_id)

    if item.reserved_by != session.get("guest_id"):
        return "Вы не можете отменить эту бронь", 403

    item.reserved_by = None
    db.session.commit()
    return redirect(url_for('vlist.index'))


# 🔹 удалить карточку (только админ)
@vlist_bp.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if not session.get("is_admin"):
        return "Доступ запрещён", 403

    item = Item.query.get_or_404(item_id)

    # удаляем файл картинки с диска, если он есть
    if item.image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('vlist.index'))
