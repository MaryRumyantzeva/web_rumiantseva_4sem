from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from datetime import datetime
from ..models import Event, User, event_volunteer, db
from .utils import role_required
from ..forms import EventForm
from werkzeug.utils import secure_filename
from sqlalchemy import select, update
import os
from flask import abort
from ..utils import role_required

bp = Blueprint('events', __name__, url_prefix='/events')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class EmptyPagination:
    """Класс для эмуляции пагинации при ошибках"""
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.total = 0
        self.items = []
        self.pages = 0
        self.has_prev = False
        self.has_next = False
        self.prev_num = None
        self.next_num = None

@bp.route('/')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        events = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(
            Event.date.asc()
        ).paginate(
            page=page,
            per_page=10,
            error_out=False
        )
        return render_template('events/index.html', events=events)
    except Exception as e:
        flash(f'Ошибка загрузки: {str(e)}', 'danger')
        return render_template('events/index.html', events=[])

@bp.route('/<int:event_id>')
@login_required
def details(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        form = FlaskForm()  # нужен только для CSRF
        return render_template('events/details.html', event=event, form=form)
    except Exception as e:
        flash(f'Мероприятие не найдено: {str(e)}', 'danger')
        return redirect(url_for('events.index'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create():
    form = EventForm()

    if form.validate_on_submit():
        try:
            file = form.image.data
            filename = None

            # Обработка файла
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'exam', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
            else:
                flash("Недопустимый формат изображения", "danger")
                return render_template('events/add_edit_event.html', form=form)

            # Создание события
            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=form.date.data,
                location=form.location.data,
                volunteers_needed=form.volunteers_needed.data,
                image_filename=filename,
                organizer_id=current_user.id
            )
            db.session.add(event)
            db.session.commit()

            flash("Мероприятие успешно создано!", "success")
            return redirect(url_for('events.index'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ошибка при создании события: {str(e)}")
            flash(f"Ошибка при создании: {str(e)}", "danger")

    return render_template("events/add_edit_event.html", form=form)


@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'moderator')
def edit(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        form = EventForm(obj=event)

        if form.validate_on_submit():
            form.populate_obj(event)

            # Обработка новой картинки (если загружена)
            if form.image.data and allowed_file(form.image.data.filename):
                file = form.image.data
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'exam', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                event.image_filename = filename

            db.session.commit()
            flash("Мероприятие обновлено!", "success")
            return redirect(url_for('events.details', event_id=event.id))

        return render_template("events/add_edit_event.html", form=form, event=event)

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при редактировании: {str(e)}", "danger")
        return redirect(url_for('events.index'))


@bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return '', 204  # <-- Важно: возвращаем пустой успешный ответ
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.context_processor
def utility_processor():
    def format_datetime(value, fmt='%d.%m.%Y %H:%M'):
        return value.strftime(fmt) if value else ''
    return dict(format_datetime=format_datetime)

@bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)
    if event.volunteers_count >= event.volunteers_needed:
        flash('Набор волонтеров завершен', 'warning')
    elif current_user in event.volunteers:
        flash('Вы уже зарегистрированы', 'info')
    else:
        event.volunteers.append(current_user)
        db.session.commit()
        flash('Вы успешно зарегистрированы!', 'success')
    return redirect(url_for('events.details', event_id=event_id))

@bp.route('/accept_volunteer/<int:event_id>/<int:user_id>')
@login_required
@role_required('admin', 'moderator')
def accept_volunteer(event_id, user_id):
    try:
        # Обновляем статус через SQLAlchemy Core
        stmt = (
            update(event_volunteer)
            .where(event_volunteer.c.event_id == event_id)
            .where(event_volunteer.c.volunteer_id == user_id)
            .values(status='accepted')
        )
        db.session.execute(stmt)
        db.session.commit()
        flash('Волонтер принят', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('events.details', event_id=event_id))

@bp.route('/reject_volunteer/<int:event_id>/<int:user_id>')
@login_required
@role_required('admin', 'moderator')
def reject_volunteer(event_id, user_id):
    try:
        stmt = (
            update(event_volunteer)
            .where(event_volunteer.c.event_id == event_id)
            .where(event_volunteer.c.volunteer_id == user_id)
            .values(status='rejected')
        )
        db.session.execute(stmt)
        db.session.commit()
        flash('Заявка отклонена', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('events.details', event_id=event_id))

@bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Проверка прав (только организатор или админ)
    if current_user != event.organizer and current_user.role.name != 'admin':
        abort(403)
    
    form = EventForm(obj=event)  # Заполняем форму данными события
    
    if form.validate_on_submit():
        form.populate_obj(event)  # Обновляем объект данными из формы
        db.session.commit()
        flash('Событие обновлено!', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    return render_template('events/edit_event.html', form=form, event=event)  # Не забудьте передать form!

@bp.route('/event/<int:id>')
def event_details(id):
    event = Event.query.get_or_404(id)
    form = EventForm()  # Создаём экземпляр формы
    return render_template('event.html', event=event, form=form)


@bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
        return 'File uploaded successfully'