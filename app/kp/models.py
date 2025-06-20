from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Модель пользователя
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    bikes = db.relationship('Bike', backref='owner', cascade='all, delete-orphan', passive_deletes=True)
    comments = db.relationship('Comment', backref='author', cascade='all, delete-orphan', passive_deletes=True)
    likes = db.relationship('Like', backref='user', cascade='all, delete-orphan', passive_deletes=True)
    reservations = db.relationship('Reservation', backref='user', cascade='all, delete-orphan', passive_deletes=True)

    is_admin = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(255), default='static/default_avatar.png')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Bike(db.Model):
    __tablename__ = 'bike'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False, default='other')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    comments = db.relationship('Comment', backref='bike_item', cascade='all, delete-orphan', passive_deletes=True)
    likes = db.relationship('Like', backref='bike', cascade='all, delete-orphan', passive_deletes=True)
    images = db.relationship('BikeImage', back_populates='bike', cascade='all, delete-orphan', passive_deletes=True)
    reservations = db.relationship('Reservation', backref='bike', cascade='all, delete-orphan', passive_deletes=True)

    image_filenames = db.Column(db.Text)


class BikeImage(db.Model):
    __tablename__ = 'bike_image'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id', ondelete='CASCADE'), nullable=False)

    bike = db.relationship('Bike', back_populates='images')



class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id', ondelete='CASCADE'), nullable=False)


class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id', ondelete='CASCADE'), nullable=False)


class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id', ondelete='CASCADE'), nullable=False)
