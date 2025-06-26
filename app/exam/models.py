from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
import markdown
import bleach


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    description = db.Column(db.Text)

    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=True)
    middle_name = db.Column(db.String(25), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    contact_info = db.Column(db.String(255), nullable=True)

    role = db.relationship('Role', back_populates='users')
    organized_events = db.relationship('Event', back_populates='organizer')
    volunteer_registrations = db.relationship('VolunteerRegistration', back_populates='volunteer')

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    @property
    def is_admin(self):
        return self.role and self.role.name == 'admin'

    @property
    def is_moderator(self):
        return self.role and self.role.name == 'moderator'

    @property
    def is_user(self):
        return self.role and self.role.name == 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_volunteer_status(self, event_id):
        reg = VolunteerRegistration.query.filter_by(event_id=event_id, volunteer_id=self.id).first()
        return reg.status if reg else None

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128), nullable=False)
    volunteers_needed = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(128), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    organizer = db.relationship('User', back_populates='organized_events')
    volunteer_registrations = db.relationship(
        'VolunteerRegistration',
        back_populates='event',
        cascade="all, delete-orphan"
    )

    @property
    def volunteers_count(self):
        return VolunteerRegistration.query.filter_by(event_id=self.id, status='accepted').count()

    @property
    def is_registration_open(self):
        return self.volunteers_count < self.volunteers_needed and self.date > datetime.utcnow()

    def is_registered(self, user):
        return VolunteerRegistration.query.filter_by(event_id=self.id, volunteer_id=user.id).first() is not None

    @property
    def accepted_registrations(self):
        return [reg for reg in self.volunteer_registrations if reg.status == 'accepted']

    @property
    def pending_registrations(self):
        return [reg for reg in self.volunteer_registrations if reg.status == 'pending']

    @property
    def volunteers(self):
        return [reg.volunteer for reg in self.accepted_registrations]

    @property
    def description_html(self):
        raw_html = markdown.markdown(self.description or "")
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'ul', 'ol', 'li', 'br', 'strong', 'em', 'a']
        return bleach.clean(raw_html, tags=allowed_tags, strip=True)

    def __repr__(self):
        return f'<Event {self.title}>'


class VolunteerRegistration(db.Model):
    __tablename__ = 'volunteer_registrations'

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending', nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)

    event = db.relationship('Event', back_populates='volunteer_registrations')
    volunteer = db.relationship('User', back_populates='volunteer_registrations')
