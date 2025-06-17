from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from ..models import Event, User
from ..extensions import db
from .utils import role_required
from ..forms import EventForm
from werkzeug.utils import secure_filename
import os
from flask import current_app
from flask_wtf.csrf import generate_csrf

bp = Blueprint('events', __name__)

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
        return render_template('events/details.html', event=event)
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
            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=form.date.data,
                location=form.location.data,
                volunteers_needed=form.volunteers_needed.data,
                organizer_id=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash('Мероприятие успешно создано!', 'success')
            return redirect(url_for('events.index'))  # Редирект на список мероприятий
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании: {str(e)}', 'danger')
    return render_template('events/create.html', form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'moderator')
def edit(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        
        if request.method == 'POST':
            event.title = request.form.get('title', event.title)
            event.description = request.form.get('description', event.description)
            event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
            event.location = request.form.get('location', event.location)
            event.volunteers_needed = int(request.form.get('volunteers_needed', event.volunteers_needed))
            
            db.session.commit()
            flash('Мероприятие обновлено!', 'success')
            return redirect(url_for('events.details', event_id=event.id))
            
        return render_template('events/edit.html', event=event)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при редактировании: {str(e)}', 'danger')
        return redirect(url_for('events.index'))

@bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        flash('Мероприятие удалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
    
    return redirect(url_for('events.index'))

@bp.context_processor
def utility_processor():
    def format_datetime(value, fmt='%d.%m.%Y %H:%M'):
        return value.strftime(fmt) if value else ''
    return dict(format_datetime=format_datetime)