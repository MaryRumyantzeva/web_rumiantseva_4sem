from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Item

vlist_bp = Blueprint('vlist', __name__, template_folder='templates')

# просмотр списка
@vlist_bp.route('/')
def index():
    items = Item.query.all()
    return render_template('vlist.html', items=items)

# добавить вещь (только для тебя — примитивно защитим паролем)
@vlist_bp.route('/add', methods=['POST'])
def add_item():
    password = request.form.get("password")
    if password != "мой_секретный_пароль":  # поменяй!
        return "Доступ запрещён", 403

    title = request.form.get("title")
    description = request.form.get("description")
    if title:
        item = Item(title=title, description=description)
        db.session.add(item)
        db.session.commit()
    return redirect(url_for('vlist.index'))

# "хочу подарить"
@vlist_bp.route('/reserve/<int:item_id>', methods=['POST'])
def reserve(item_id):
    item = Item.query.get(item_id)
    if item and not item.reserved_by:
        item.reserved_by = "Кто-то"
        db.session.commit()
    return redirect(url_for('vlist.index'))
