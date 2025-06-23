from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField, FileField, BooleanField
from wtforms import StringField, PasswordField, DateTimeField  
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import DateTimeField
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class EventForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    date = DateTimeField(
        'Дата и время мероприятия',
        format='%Y-%m-%d',
        validators=[DataRequired()],
        default=datetime.now 
    )
    location = StringField('Место', validators=[DataRequired()])
    volunteers_needed = IntegerField('Нужно волонтеров', validators=[DataRequired()])
    image = FileField('Изображение мероприятия', validators=[
        FileRequired(),  # Обязательное поле
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    submit = SubmitField('Сохранить')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    contact_info = StringField('Контактные данные', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
    first_name = StringField('Имя',  validators=[DataRequired()])
    last_name = StringField('Фамилия',  validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Optional()])
