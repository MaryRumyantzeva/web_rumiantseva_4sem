from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField, FileField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class EventForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    location = StringField('Место', validators=[DataRequired()])
    volunteers_needed = IntegerField('Нужно волонтёров', validators=[DataRequired()])
    image = FileField('Изображение')
    submit = SubmitField('Сохранить')

class RegistrationForm(FlaskForm):
    contact_info = StringField('Контактные данные', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')