from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class SignUpCourse(FlaskForm):
    name = StringField("Ваше имя", validators=[DataRequired()])
    surname = StringField("Ваша фамилия", validators=[DataRequired()])
    email = EmailField("Ваш e-mail", validators=[DataRequired(), Email("Неккоректный e-mail адрес")])
    tel = StringField("Ваш телефон в формате:  8-***-***-****", validators=[DataRequired(), Length(min=14, max=14)])
    age = IntegerField("Возраст ребенка", validators=[DataRequired(), NumberRange(min=3, max=18)])
    name_c = StringField("Имя ребенка", validators=[DataRequired()])
    course = SelectField('Выберете курс', choices=[], coerce=int, validate_choice=False)
    lesson = SelectField('Выберете подкурс', choices=[], coerce=int, validate_choice=False)
    teacher = SelectField('Выберете учителя', choices=[], coerce=int, validate_choice=False)
    insert = SubmitField("Добавить")


class ShowSignUp(FlaskForm):
    email = EmailField("Ваш e-mail", validators=[DataRequired(), Email("Неккоректный e-mail адрес")])
    show = SubmitField("Посмотреть")


class ContactForm(FlaskForm):
    name = StringField("Ваше имя", validators=[DataRequired()])
    tel = StringField("Ваш телефон в формате:  8-***-***-****", validators=[DataRequired(), Length(min=14, max=14)])
    text = TextAreaField("Ваш вопрос", validators=[DataRequired()])
    submit = SubmitField("Добавить")
