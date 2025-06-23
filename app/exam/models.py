from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from sqlalchemy import event
from sqlalchemy.orm import validates

# Таблица для связи многие-ко-многим между событиями и волонтёрами
event_volunteer = db.Table(
    'volunteer_registrations',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), nullable=False),
    db.Column('volunteer_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('registration_date', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('contact_info', db.String(128), nullable=False),
    db.Column('status', db.String(20), default='pending', nullable=False,
             server_default='pending'),
    db.UniqueConstraint('event_id', 'volunteer_id', name='uq_event_volunteer'),
    db.CheckConstraint("status IN ('pending', 'accepted', 'rejected')", name='chk_status')
)

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


    role = db.relationship('Role', backref='users')

    @property
    def is_admin(self):
        return self.role and self.role.name == 'admin'

    @property
    def is_moderator(self):
        return self.role and self.role.name == 'moderator'

    @property
    def is_user(self):
        return self.role and self.role.name == 'user'

    
    # Relationships
    role = db.relationship('Role', back_populates='users')
    organized_events = db.relationship('Event', back_populates='organizer')
    volunteer_events = db.relationship(
        'Event',
        secondary=event_volunteer,
        back_populates='volunteers',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    def get_volunteer_status(self, event_id):
        result = db.session.execute(
            event_volunteer.select()
            .where(event_volunteer.c.event_id == event_id)
            .where(event_volunteer.c.volunteer_id == self.id)
        ).fetchone()
        return result.status if result else None
    
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
    
    # Relationships
    organizer = db.relationship('User', back_populates='organized_events')
    volunteers = db.relationship(
        'User',
        secondary=event_volunteer,
        back_populates='volunteer_events',
        lazy='dynamic'
    )
    
    @property
    def volunteers_count(self):
        return self.volunteers.filter(
            event_volunteer.c.status == 'accepted'
        ).count()
    
    @property
    def is_registration_open(self):
        return (self.volunteers_count < self.volunteers_needed and 
                self.date > datetime.utcnow())
    
    def is_registered(self, user):
        return self.volunteers.filter(
            event_volunteer.c.volunteer_id == user.id
        ).count() > 0
    
    def __repr__(self):
        return f'<Event {self.title}>'

# Валидация статуса при добавлении волонтера
@event.listens_for(Event.volunteers, 'append')
def validate_status(target, value, initiator):
    if hasattr(value, 'status') and value.status not in ['pending', 'accepted', 'rejected']:
        raise ValueError("Invalid status value")