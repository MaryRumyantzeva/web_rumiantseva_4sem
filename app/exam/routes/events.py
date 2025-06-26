from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import update
from ..models import Event, User, VolunteerRegistration, db
from ..forms import EventForm
from ..utils import role_required
import os

bp = Blueprint('events', __name__, url_prefix='/events')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        events = Event.query.filter(Event.date >= datetime.utcnow()) \
            .order_by(Event.date.asc()) \
            .paginate(page=page, per_page=10, error_out=False)
        return render_template('events/index.html', events=events)
    except Exception as e:
        flash(f'Ошибка загрузки: {str(e)}', 'danger')
        return render_template('events/index.html', events=[])

@bp.route('/<int:event_id>')
@login_required
def details(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        form = FlaskForm()  # Для CSRF
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

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
            else:
                flash("Недопустимый формат изображения", "danger")
                return render_template('events/add_edit_event.html', form=form)

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
            flash(f"Ошибка при создании: {str(e)}", "danger")

    return render_template("events/add_edit_event.html", form=form)

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'moderator')
def edit(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        form.populate_obj(event)

        file = form.image.data
        if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                event.image_filename = filename
            else:
                flash("Недопустимый формат изображения", "danger")
                return render_template("events/add_edit_event.html", form=form, event=event)
        db.session.commit()
        flash("Мероприятие обновлено!", "success")
        return redirect(url_for('events.details', event_id=event.id))

    return render_template("events/add_edit_event.html", form=form, event=event)


@bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)

    if event.is_registered(current_user):
        flash('Вы уже зарегистрированы', 'info')
        return redirect(url_for('events.details', event_id=event_id))

    if not event.is_registration_open:
        flash('Набор волонтеров завершён', 'warning')
        return redirect(url_for('events.details', event_id=event_id))

    try:
        registration = VolunteerRegistration(
            event_id=event.id,
            volunteer_id=current_user.id,
            contact_info=current_user.contact_info
        )
        db.session.add(registration)
        db.session.commit()
        flash('Вы успешно зарегистрированы!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка регистрации: {str(e)}', 'danger')

    return redirect(url_for('events.details', event_id=event.id))

@bp.route('/accept_volunteer/<int:event_id>/<int:user_id>')
@login_required
@role_required('admin', 'moderator')
def accept_volunteer(event_id, user_id):
    try:
        event = Event.query.get_or_404(event_id)
        accepted_count = VolunteerRegistration.query.filter_by(event_id=event_id, status='accepted').count()

        if accepted_count >= event.volunteers_needed:
            flash('Невозможно принять: лимит достигнут.', 'warning')
            return redirect(url_for('events.details', event_id=event_id))

        VolunteerRegistration.query.filter_by(event_id=event_id, volunteer_id=user_id).update({
            'status': 'accepted'
        })

        accepted_count += 1
        if accepted_count >= event.volunteers_needed:
            VolunteerRegistration.query.filter(
                VolunteerRegistration.event_id == event_id,
                VolunteerRegistration.status == 'pending'
            ).update({'status': 'rejected'})

        db.session.commit()
        flash('Волонтёр принят', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при принятии: {str(e)}', 'danger')

    return redirect(url_for('events.details', event_id=event_id))

@bp.route('/reject_volunteer/<int:event_id>/<int:user_id>')
@login_required
@role_required('admin', 'moderator')
def reject_volunteer(event_id, user_id):
    try:
        VolunteerRegistration.query.filter_by(event_id=event_id, volunteer_id=user_id).update({
            'status': 'rejected'
        })
        db.session.commit()
        flash('Волонтёр отклонён', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при отклонении: {str(e)}', 'danger')

    return redirect(url_for('events.details', event_id=event_id))
