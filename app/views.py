from app import app, db, mail
from flask_mail import Message
from flask import render_template, request, abort, jsonify, flash, redirect, url_for
from app.models import MainMenu, Post, Lesson, Course, MenuAdmin, Teacher, Signup, FeedBack
from app.forms import SignUpCourse, ShowSignUp, ContactForm
import sqlite3


def convert(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if line.endswith('\r'):
            new = line.replace('\r', '<br>')
            new_lines.append(new)
        else:
            new = line + '<br>'
            new_lines.append(new)
    return ''.join(new_lines)

@app.route('/')
def index():
    try:
        menu = MainMenu.query.all()
        content = Post.query.filter(Post.id == 1).first()
    except:
        print("Ошибка чтения из БД")

    return render_template('index.html',menu=menu, title='Главная страница',content=content)

@app.route('/listpost')
def posts():
    try:
        menu = MainMenu.query.all()
        content = Post.query.filter(Post.id != 1).all()
    except:
        print("Ошибка чтения из БД")

    return render_template('listposts.html', menu=menu, title='Посты', content=content)

@app.route('/listpost/<posturl>')
def showpost (posturl):
    try:
        menu = MainMenu.query.all()
        content = Post.query.filter(Post.url == posturl).first()
    except:
        print("Ошибка чтения из БД")

    if posturl not in [post.url for post in Post.query.all()]:
        abort (404)

    return render_template('post.html', menu=menu, title=content.title, content=content)

@app.route('/listcourse')
def courses():
    try:
        menu = MainMenu.query.all()
        content = Course.query.all()
    except:
        print("Ошибка чтения из БД")

    return render_template('listcourses.html', menu=menu, title='Курсы', content=content)

@app.route('/listcourse/<courseurl>')
def showcourse(courseurl):
    try:
        menu = MainMenu.query.all()
        content = Course.query.filter(Course.url == courseurl).first()
    except:
        print ("Ошибка чтения из БД")

    if courseurl not in [course.url for course in Course.query.all()]:
        abort(404)

    return render_template('course.html', menu=menu, title=content.title, content=content)

@app.route('/listcourse/<courseurl>/<lessonurl>', methods = ["GET","POST"])
def showlesson (courseurl, lessonurl):
    try:
        menu = MainMenu.query.all()
        content = Lesson.query.filter(Lesson.url == lessonurl).first()
    except:
        print ("ошибка чтения из БД")

    if lessonurl not in [lesson.url for lesson in Lesson.query.all()] or content.course.url != courseurl:
        '''если url подкурса нет в БД или в курсе с url courseurl нет подкурса (например, если url подкурса из одного курса
        скопировать и вставить в окно браузера, где courseurl другой'''
        abort(404)

    return render_template('lesson.html', menu=menu, title=content.title, content=content)

@app.route('/teachers')
def teachers():
    try:
        menu = MainMenu.query.all()
        result = Teacher.query.all()
    except:
        print("Ошибка чтения из БД")

    return render_template('teachers.html',menu=menu, result=result, title='Наши учителя')

@app.route('/signup', methods = ['GET','POST'])
def signups():
    try:
        menu = MainMenu.query.all()
    except:
        print("Ошибка чтения из БД")
    show_form = ShowSignUp()
    signup_form = SignUpCourse()
    signup_form.course.choices = [(course.id, course.title) for course in Course.query.all()]
    signup_form.lesson.choices = [(lesson.id, lesson.title) for lesson in Lesson.query.filter_by(course_id=1).all()]
    signup_form.teacher.choices = [(teacher.id, teacher.name) for teacher in Teacher.query.all()]
    flag = False

    if show_form.show.data and show_form.validate(): #проверка,есть ли у кнопки (show.data) данные для отправки методом "POST"
        result = Signup.query.filter_by(email=show_form.email.data).first()
        if not result:
            flash('Вы не записывались', category='error')
        else:
            return redirect(url_for('showsignup', signupemail=result.email))

    if signup_form.insert.data and signup_form.validate():#проверка,есть ли у кнопки (insert.data) данные для отправки методом "POST"
        sign_up = Signup.query.filter_by(email=signup_form.email.data).all()
        if sign_up:
            for s in sign_up:
                if s.lesson.course_id == int(signup_form.course.data) and s.lesson_id == int(signup_form.lesson.data) \
                        and s.name_child.lower() == signup_form.name_c.data.lower():
                    flag = True
            if flag:
                flash("Вы уже записывались на эти занятия", category='error')
            else:
                try:
                    result = Signup(name=signup_form.name.data, surname=signup_form.surname.data, email=signup_form.email.data,
                                    tel=signup_form.tel.data, age_child=signup_form.age.data,
                                    name_child=signup_form.name_c.data,
                                    teacher_id=signup_form.teacher.data, lesson_id=signup_form.lesson.data)
                    db.session.add(result)
                    db.session.commit()
                    msg = Message("Запись на курс", recipients=[signup_form.email.data])
                    msg.body = f'Ваш ребенок {signup_form.name_c.data} записан на занятия ' \
                               f'{Lesson.query.filter_by(id=signup_form.lesson.data).first().title} ' \
                               f'по курсу {Lesson.query.filter_by(id=signup_form.lesson.data).first().course.title}'
                    msg2 = Message("Новая запись", recipients=['alex-alex9494@yandex.ru'])
                    msg2.body = 'Новая запись, проверьте список записей!'
                    mail.send(msg)
                    mail.send(msg2)
                    flash("Поздравляем, вы записались на курс! На вашу почту отправлено письмо с информацией",
                          category='success')
                    return redirect (url_for('index'))
                except sqlite3.Error as e:
                    db.session.rollback()
                    print("Ошибка добавления в БД " + str(e))
                    flash("Ошибка добавления в БД", category='error')
        else:
            try:
                result = Signup(name=signup_form.name.data, surname=signup_form.surname.data,
                                email=signup_form.email.data,
                                tel=signup_form.tel.data, name_child=signup_form.name_c.data,
                                age_child=signup_form.age.data, teacher_id=signup_form.teacher.data,
                                lesson_id=signup_form.lesson.data)
                db.session.add(result)
                db.session.commit()
                msg = Message("Запись на курс", recipients=[signup_form.email.data])
                msg.body = f'Ваш ребенок {signup_form.name_c.data} записан на занятия ' \
                           f'{Lesson.query.filter_by(id=signup_form.lesson.data).first().title} ' \
                           f'по курсу {Lesson.query.filter_by(id=signup_form.lesson.data).first().course.title}'
                msg2 = Message("Новая запись", recipients=['alex-alex9494@yandex.ru'])
                msg2.body = 'Новая запись, проверьте список записей!'
                mail.send (msg)
                mail.send (msg2)
                flash("Поздравляем, вы записались на курс! На вашу почту отправлено письмо с информацией", category='success')
                return redirect(url_for('index'))
            except sqlite3.Error as e:
                db.session.rollback()
                print("Ошибка добавления в БД " + str(e))
                flash("Ошибка добавления в БД", category='error')

    return render_template('signup.html', menu=menu, title='Запись на курс', form1=show_form, form2=signup_form)

'''функция создает json со всеми подкурсами по id курса '''
@app.route('/lesson/<int:course>')
def lesson(course):
    lessons = Lesson.query.filter_by(course_id=course).all()
    lessonsArray = []
    for lesson in lessons:
        lessonObj = {}
        lessonObj['id'] = lesson.id
        lessonObj['title'] = lesson.title
        lessonsArray.append(lessonObj)
    return jsonify({'lessons': lessonsArray})


@app.route('/watchsignup/<signupemail>', methods=['GET','POST'])
def showsignup(signupemail):
    data={}
    try:
        menu = MainMenu.query.all()
        content = Signup.query.filter_by(email=signupemail).all()
    except:
        print("Ошибка чтения из БД")

    if signupemail not in [signup.email for signup in Signup.query.all()]:
        abort(404)

    data['name']=content[0].name
    data['tel']=content[0].tel
    data['email']=content[0].email

    return render_template('showsignup.html', menu=menu, title='Просмотр записей', content=content, data=data)

@app.route('/contact', methods = ['GET','POST'])
def contact():
    try:
        menu = MainMenu.query.all()
    except:
        print ("Ошибка чтения из БД")
    form = ContactForm()
    if form.validate_on_submit():
        try:
            result = FeedBack (name=form.name.data, tel=form.tel.data, text=convert(form.text.data))
            db.session.add(result)
            db.session.commit()
            flash("Спасибо за обращение! Мы свяжимся с Вами в ближайшее время!", category='success')
            msg = Message("Новое обращение", recipients=['alex-alex9494@yandex.ru'])
            msg.body = f'Новое обращение от {form.name.data}.\nТелефон для связи: {form.tel.data}.\nТекст обращения: {form.text.data}!'
            mail.send(msg)
        except sqlite3.Error as e:
            db.session.rollback()
            print("Ошибка добавления в БД " + str(e))
            flash("Ошибка добавления в БД", category='error')
        return redirect(url_for('index'))

    return render_template('contact.html', menu=menu, form=form)

@app.errorhandler(404)
def pageNotFound(error):
    if request.path.startswith('/admin/'):
        '''если путь начинается на админ, мы возвращаем 404 admin
        #метод request.path возвращает часть url адреса после request.root_path, starwith - возвращает True, если строка начинается 
        с указанного префикса (строки)'''
        try:
            menu = MenuAdmin.query.all()
        except:
            print("Ошибка чтения из БД")
        for m in menu:
            m.url = 'admin'+m.url #прибавляем к адресу admin для маршрутизации внутри blueprint

        return render_template("admin/page404.html", title="Страница не найдена", menu=menu), 404
    else:
        try:
            menu = MainMenu.query.all()
        except:
            print("Ошибка чтения из БД")

        return render_template("page404.html", title="Страница не найдена", menu=menu), 404


