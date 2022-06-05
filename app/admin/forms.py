from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, FileField, EmailField, \
    IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class LoginFormAdmin(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    psw = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()


class AddPostAdmin(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    text = TextAreaField("Текст", validators=[DataRequired()])
    image = FileField('Картинка', validators=[DataRequired()])
    url = StringField("Url", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddCourseAdmin(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    duration = StringField("Длительность занятия", validators=[DataRequired()])
    age = StringField("Возраст детей", validators=[DataRequired()])
    text = TextAreaField("Текст", validators=[DataRequired()])
    image = FileField('Картинка', validators=[DataRequired()])
    url = StringField("Url", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddLessonAdmin(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    duration = StringField("Длительность занятия", validators=[DataRequired()])
    age = StringField("Возраст детей", validators=[DataRequired()])
    text = TextAreaField("Текст", validators=[DataRequired()])
    image = FileField('Картинка', validators=[DataRequired()])
    url = StringField("Url", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddTeacherAdmin(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    email = EmailField("E-mail", validators=[DataRequired(), Email("Неккоректный e-mail адрес")])
    tel = StringField("Телефон в формате:  8-***-***-****", validators=[DataRequired(), Length(min=14, max=14)])
    age = IntegerField("Возраст", validators=[DataRequired(), NumberRange(min=18, max=60)])
    text = TextAreaField("Текст", validators=[DataRequired()])
    image = FileField('Фото', validators=[DataRequired()])
    submit = SubmitField("Добавить")


class SelectTeacher(FlaskForm):
    name = SelectField('Имя', choices=[])
    submit = SubmitField("Посмотреть")


class UpdatePostAdmin(AddPostAdmin):
    image = FileField('Картинка')
    submit = SubmitField("Обновить")


class UpdateCourseAdmin(AddCourseAdmin):  # наследуем форму от AddCorseAdmin, меняем только поле image и submit
    image = FileField('Картинка')
    submit = SubmitField("Обновить")


class UpdateLessonAdmin(AddLessonAdmin):
    image = FileField('Картинка')
    submit = SubmitField("Обновить")


class UpdateTeacherAdmin(AddTeacherAdmin):
    image = FileField('Фото')
    submit = SubmitField("Обновить")
