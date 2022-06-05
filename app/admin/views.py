from flask import render_template, redirect, url_for, flash, request, current_app, abort
from app import db
from flask_login import login_required, login_user, current_user, logout_user
from app.models import MenuAdmin, UserAdmin, Post, Course, Lesson, Teacher, Signup, FeedBack
from app.admin import admin   # импортируем blueprint из admin/__init__
from app.admin.forms import LoginFormAdmin, AddPostAdmin, UpdatePostAdmin, AddCourseAdmin, AddLessonAdmin, \
    UpdateCourseAdmin,UpdateLessonAdmin, AddTeacherAdmin, SelectTeacher,UpdateTeacherAdmin
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError


def validate_name(filename):   # проверка картинки на png или jpg
    ext = filename.rsplit('.', 1)[1].lower()  # разделяем строку с конца по точке, берем из списка послдений элемент
    if ext == "png" or ext == "jpg":
        return True
    return False


def save_picture(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'] + '\\admin\static\images', filename))
    # сохраняем картинку в папку
    route = os.path.join('\\admin\static\images', filename)
    # сохраняем путь картинки для сохранения в БД
    return route


@admin.route('/', methods=['GET', 'POST'])
def index():
    try:
        menu = MenuAdmin.query.all()
    except Exception:
        print("Ошибка чтения из БД")
    form = SelectTeacher()
    form.name.choices = [(teacher.id, teacher.name) for teacher in Teacher.query.all()]
    # создаем кортеж из id и имени для selectfield
    # кортеж отправляется в selectfield, оттуда прилетает id
    if form.validate_on_submit():
        # form.name.data  # id полученный из формы
        return redirect(url_for('.showTeacher', teacherid=form.name.data))

    return render_template('admin/index.html', title='Админ-панель', menu=menu, user=current_user, form=form)
    # с помощью user_loader
    # в сurrent_user хранится авторизованный админ


@admin.route('/login', methods=['POST', 'GET'])
def login():
    try:
        menu = MenuAdmin.query.all()
    except Exception:
        print("Ошибка чтения из БД")
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginFormAdmin()
    if form.validate_on_submit():
        user = db.session.query(UserAdmin).filter(UserAdmin.username == form.username.data).first()
        if user and user.check_password(form.psw.data):
            login_user(user, remember=form.remember.data) # запись текущего пользователя в сессию функцией login_user
            return redirect(url_for('.index'))
        else:
            flash("Invalid username/password", category='error')

    return render_template('admin/login.html', title='Админ-панель', menu=menu, form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out", category='success')
    return redirect(url_for('.login'))


@admin.route('/listpost')
@login_required
def posts():
    try:
        menu = MenuAdmin.query.all()
        content = Post.query.all()
    except Exception:
        print("Ошибка чтения из БД")

    return render_template('admin/listpost.html', title='Админ-панель', menu=menu, content=content)


@admin.route('/listpost/<posturl>', methods=['POST', 'GET'])
@login_required
def showPost(posturl):
    try:
        menu = MenuAdmin.query.all()
        content = Post.query.filter(Post.url == posturl).first()
    except:
        print("Ошибка чтения из БД")
    if request.method == 'POST':  # если нажали удалить статью
        try:
            db.session.delete(content)
            db.session.commit()
            flash("Статья удалена", category='success')
        except DBAPIError as error:
            #print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления статьи в БД " + str(error))
            flash("Ошибка удаления в БД", category='error')
        return redirect(url_for('.posts'))

    if posturl not in [post.url for post in Post.query.all()]:
        abort(404)

    return render_template('admin/post.html', menu=menu, title='Админ-панель', content=content)


@admin.route('listpost/addPost', methods=['POST', 'GET'])
@login_required
def addPost():
    try:
        menu = MenuAdmin.query.all()
    except Exception:
        print("Ошибка чтения из БД")
    form = AddPostAdmin()
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and validate_name(file.filename):  # если считали, и расширение png или jpg
            route = save_picture(file)  # функция сохранения картинки в папку
            try:
                result = Post(title=form.title.data, text=form.text.data, image=route, url=form.url.data)
                # считываем данные из формы, создаем объект класса Post
                db.session.add(result)  # добавляем в БД
                db.session.commit()
                flash("Пост добавлен", category='success')
                return redirect(url_for('.posts'))
            except DataError as error: # ошибка sqlalchemy если данные из формы не помещаются в БД
                # print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка добавления в БД", category='error')
                print("Ошибка добавления статьи в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка добавления статьи в БД " + str(error))
        else:
            flash("Неправильный тип файла", category='error')

    return render_template('admin/addPost.html', title='Админ-панель', menu=menu, form=form)


@admin.route('/listpost/<posturl>/update', methods = ['POST','GET'])
@login_required
def updatePost(posturl):
    try:
        menu = MenuAdmin.query.all()
        content = Post.query.filter(Post.url == posturl).first()
    except Exception:
        print("Ошибка чтения из БД")
    form = UpdatePostAdmin(obj=content)  # подгружаем данные из БД в форму
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and not validate_name(file.filename):  # если считали, и расширение не png или jpg
            flash("Неправильный тип файла", category='error')
        elif file and validate_name(file.filename):
            try:
                route = save_picture(file)  # функция сохранения картинки в папку
                content.image = route
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                db.session.commit()
                flash("Статья обновлена", category='success')
                return redirect(url_for('.posts'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                # print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления статьи в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления статьи в БД " + str(error))
        else:
            try:
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                db.session.commit()
                flash("Статья обновлена", category='success')
                return redirect(url_for('.posts'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                # print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления статьи в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления статьи в БД " + str(error))

    return render_template('admin/updatepost.html', title='Админ-панель', menu=menu, form=form, post_url=posturl)


@admin.route('/listcourses')
@login_required
def courses():
    try:
        menu = MenuAdmin.query.all()
        content = Course.query.all()
    except Exception:
        print("Ошибка чтения из БД")

    return render_template('admin/listcourse.html', title='Админ-панель', menu=menu, content=content)


@admin.route('/listcourses/<courseurl>', methods = ["GET","POST"])
@login_required
def showCourse(courseurl):
    try:
        menu = MenuAdmin.query.all()
        content = Course.query.filter(Course.url == courseurl).first()
    except Exception:
        print("ошибка чтения из БД")
    if request.method == 'POST':  # если нажали удалить
        try:
            db.session.delete(content)
            db.session.commit()
            flash("Курс удален", category='success')
        except DBAPIError as error:
            # print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления курса из БД " + str(error))
            flash("Ошибка удаления в БД", category='error')
        return redirect(url_for('.courses'))

    if courseurl not in [course.url for course in Course.query.all()]:
        abort(404)

    return render_template('admin/course.html', title="Админ-панель", menu=menu, content=content)


@admin.route('listcourses/addCourse', methods = ["GET", "POST"])
@login_required
def addCourse():
    try:
        menu = MenuAdmin.query.all()
    except Exception:
        print ("Ошибка чтения из БД")
    form = AddCourseAdmin()
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and validate_name(file.filename):  # если считали, и расширение png или jpg
            route = save_picture(file)  # функция сохранения картинки в папку
            try:
                result = Course(title=form.title.data, duration=form.duration.data, age=form.age.data,
                                 text=form.text.data, image=route, url=form.url.data)
                # считываем данные из формы, создаем объект класса
                db.session.add(result)  # добавляем в БД
                db.session.commit()
                flash("Курс добавлен", category='success')
                return redirect(url_for('.courses'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                # print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка добавления в БД", category='error')
                print("Ошибка добавления курса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка добавления курса в БД " + str(error))
        else:
            flash("Неправильный тип файла", category='error')

    return render_template('admin/addCourse.html', title="Админ-панель", menu=menu, form=form)


@admin.route('/listcourses/<courseurl>/update', methods = ["GET","POST"])
@login_required
def updateCourse(courseurl):
    try:
        menu = MenuAdmin.query.all()
        content = Course.query.filter(Course.url == courseurl).first()
    except Exception:
        print("Ошибка чтения из БД")
    form = UpdateCourseAdmin(obj=content)
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and not validate_name(file.filename):  # если считали, и расширение не png или jpg
            flash("Неправильный тип файла", category='error')
        elif file and validate_name(file.filename):
            try:
                route = save_picture(file)  # функция сохранения картинки в папку
                content.image = route
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                content.duration = form.duration.data
                content.age = form.age.data
                db.session.commit()
                flash("Курс обновлен", category='success')
                return redirect(url_for('.courses'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления курса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления курса в БД " + str(error))
        else:
            try:
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                content.duration = form.duration.data
                content.age = form.age.data
                db.session.commit()
                flash("Курс обновлен", category='success')
                return redirect(url_for('.courses'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления курса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления курса в БД " + str(error))

    return render_template('admin/updatecourse.html', title='Админ-панель', menu=menu, form=form, course_url=courseurl)


@admin.route('/listcourses/<courseurl>/<lessonurl>', methods = ["GET","POST"])
@login_required
def showLesson(courseurl, lessonurl):
    try:
        menu = MenuAdmin.query.all()
        content = Lesson.query.filter(Lesson.url == lessonurl).first()
    except Exception:
        print("ошибка чтения из БД")
    if request.method == 'POST': # если нажали удалить
        try:
            db.session.delete(content)
            db.session.commit()
            flash("Подкурс удален", category='success')
        except DBAPIError as error:
            # print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления подкурса из БД " + str(error))
            flash("Ошибка удаления в БД", category='error')
        return redirect(url_for('.showCourse', courseurl=courseurl))

    if lessonurl not in [lesson.url for lesson in Lesson.query.all()] or content.course.url != courseurl:
        '''если url подкурса нет в БД или в курсе с url courseurl нет подкурса (например, если url подкурса из одного курса
        скопировать и вставить в окно браузера, где courseurl другой'''
        abort(404)

    return render_template('admin/lesson.html', menu=menu, content=content, course_url=courseurl)


@admin.route('/listcourses/<courseurl>/addLesson', methods = ['GET','POST'])
@login_required
def addLesson(courseurl):
    try:
        menu = MenuAdmin.query.all()
        course = Course.query.filter(Course.url == courseurl).first()
    except Exception:
        print("Ошибка чтения из БД")
    form = AddLessonAdmin()
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and validate_name(file.filename):  # если считали, и расширение png или jpg
            route = save_picture(file) #функция сохранения картинки в папку
            try:
                result = Lesson(title=form.title.data, duration=form.duration.data, age=form.age.data,
                                text=form.text.data, image=route,  # добавляем id курса для связи между таблицами
                                url=form.url.data, course_id=course.id)
                # считываем данные из формы, создаем объект класса
                db.session.add(result)  # добавляем в БД
                db.session.commit()
                flash("Подкурс добавлен", category='success')
                return redirect(url_for('.showCourse', courseurl=courseurl))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка добавления в БД", category='error')
                print("Ошибка добавления подкурса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка добавления подкурса в БД " + str(error))
        else:
            flash("Неправильный тип файла", category='error')

    return render_template('admin/addLesson.html', title="Админ-панель", menu=menu, form=form, course_url=courseurl)


@admin.route('/listcourses/<courseurl>/<lessonurl>/update', methods = ["GET","POST"])
@login_required
def updateLesson(courseurl, lessonurl):
    try:
        menu = MenuAdmin.query.all()
        content = Lesson.query.filter(Lesson.url == lessonurl).first()
    except Exception:
        print("Ошибка чтения из БД")
    form = UpdateLessonAdmin(obj=content)
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and not validate_name(file.filename):  # если считали, и расширение не png или jpg
            flash("Неправильный тип файла", category='error')
        elif file and validate_name(file.filename):
            try:
                route = save_picture(file)  # функция сохранения картинки в папку
                content.image = route
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                content.duration = form.duration.data
                content.age = form.age.data
                db.session.commit()
                flash("Подкурс обновлен", category='success')
                return redirect(url_for('.showCourse', courseurl=courseurl))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления подкурса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления подкурса в БД " + str(error))
        else:
            try:
                content.title = form.title.data  # считываем данные из формы, создаем объект класса Post
                content.text = form.text.data
                content.url = form.url.data
                content.duration = form.duration.data
                content.age = form.age.data
                db.session.commit()
                flash("Подкурс обновлен", category='success')
                return redirect(url_for('.showCourse', courseurl=courseurl))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления подкурса в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                flash("Такой URL уже существует", category='error')
                print("Ошибка обновления подкурса в БД " + str(error))

    return render_template('admin/updatelesson.html', title='Админ-панель', menu=menu, form=form, course_url=courseurl,
                           lesson_url=lessonurl)


@admin.route('/addTeacher', methods = ["GET","POST"])
@login_required
def addTeacher():
    try:
        menu = MenuAdmin.query.all()
    except Exception:
        print("Ошибка чтения из БД")
    form = AddTeacherAdmin()
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and validate_name(file.filename):  # если разрешение правильное
            route = save_picture(file)  # функция сохранения картинки в папку
            try:
                result = Teacher(name=form.name.data, surname=form.surname.data, age=form.age.data,
                                 tel=form.tel.data, image=route, email=form.email.data, text=form.text.data)
                # считываем данные из формы, создаем объект класса
                db.session.add(result)  # добавляем в БД
                db.session.commit()
                flash("Данные учителя добавлены", category='success')
                return redirect(url_for('.index'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка добавления в БД", category='error')
                print("Ошибка добавления данных в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                print("Ошибка добавления статьи в БД " + str(error))
                flash("Телефон или Email уже используется", category='error')
        else:
            flash("Неправильный тип файла", category='error')

    return render_template('admin/addTeach.html', title="Админ-панель", menu=menu, form=form)


@admin.route('/teacher/<int:teacherid>', methods = ['GET','POST'])
@login_required
def showTeacher(teacherid):
    try:
        menu = MenuAdmin.query.all()
        result = Teacher.query.filter(Teacher.id == teacherid).first()
    except Exception:
        print("Ошибка чтения из БД")

    if request.method == 'POST':
        try:
            db.session.delete(result)
            db.session.commit()
            flash("Данные об учителе удалены", category='success')
        except DBAPIError as error:
            # print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления данных из БД " + str(error))
            flash("Ошибка удаления в БД", category='error')
        return redirect(url_for('.index'))

    if teacherid not in [teacher.id for teacher in Teacher.query.all()]:
        abort(404)

    return render_template('admin/teacher.html', title="Админ-панель", menu=menu, result=result)


@admin.route('/teacher/<int:teacherid>/update', methods = ['GET','POST'])
@login_required
def updateTeacher(teacherid):
    try:
        menu = MenuAdmin.query.all()
        teacher = Teacher.query.get (teacherid)
    except Exception:
        print("Ошибка чтения из БД")
    form = UpdateTeacherAdmin(obj=teacher)
    if form.validate_on_submit():
        file = request.files['image']  # считываем данные из формы. поле image
        if file and not validate_name(file.filename):  # если считали, и расширение не png или jpg
            flash("Неправильный тип файла", category='error')
        elif file and validate_name(file.filename):  # если считали картинку
            try:
                route = save_picture(file)  # функция сохранения картинки в папку
                teacher.image = route
                teacher.name = form.name.data  # считываем данные из формы, создаем объект класса Post
                teacher.surname = form.surname.data
                teacher.email = form.email.data
                teacher.tel = form.tel.data
                teacher.age = form.age.data
                teacher.text = form.text.data
                db.session.commit()
                flash("Данные об учителе обновлены", category='success')
                return redirect(url_for('.index'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                print("Ошибка обновления в БД " + str(error))
                flash("Телефон или Email уже используется", category='error')
        else:  # если не считали картинку
            try:
                teacher.name = form.name.data  # считываем данные из формы, создаем объект класса Post
                teacher.surname = form.surname.data
                teacher.email = form.email.data
                teacher.tel = form.tel.data
                teacher.age = form.age.data
                teacher.text = form.text.data
                db.session.commit()
                flash("Данные об учителе обновлены", category='success')
                return redirect(url_for('.index'))
            except DataError as error:  # ошибка sqlalchemy если данные из формы не помещаются в БД
                #    print(error.orig.pgcode)  #Код ошибки
                db.session.rollback()
                flash("Ошибка обновления в БД", category='error')
                print("Ошибка обновления в БД " + str(error))
            except IntegrityError as error:  # ошибка sqlalchemy если url занят
                db.session.rollback()
                print("Ошибка обновления в БД " + str(error))
                flash("Телефон или Email уже используется", category='error')

    return render_template('admin/updateteacher.html', title="Админ-панель", menu=menu, form=form, teacher_id=teacherid)


@admin.route('/listsignup')
@login_required
def signups():
    try:
        menu = MenuAdmin.query.all()
        signups = Signup.query.all()
    except Exception:
        print("Ошибка чтения из БД")

    return render_template('admin/listsignup.html', title='Админ-панель', menu=menu, signup=signups)


@admin.route('/listsignup/<signupid>', methods=['GET','POST'])
@login_required
def del_signup(signupid):
    try:
        signup = Signup.query.filter_by(id=signupid).first()
    except Exception:
        print("Ошибка чтения из БД")
    if request.method == 'POST':
        try:
            db.session.delete(signup)
            db.session.commit()
            flash("Запись на занятия удалена ", category='success')
        except DBAPIError as error:
            # print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления данных из БД " + str(error))
            flash("Ошибка удаления в БД", category='error')

    return redirect(url_for('.signups'))


@admin.route('/showfeedback')
@login_required
def showfeedback():
    try:
        menu = MenuAdmin.query.all()
        result = FeedBack.query.all()
    except Exception:
        print('Ошибка чтения из БД')

    return render_template('admin/feedback.html', menu=menu, result=result, title='Админ-панель')


@admin.route('/showfeedback/<feedbackid>', methods=['GET','POST'])
@login_required
def del_feedback(feedbackid):
    try:
        feedback = FeedBack.query.filter_by(id=feedbackid).first()
    except Exception:
        print("Ошибка чтения из БД")
    if request.method == 'POST':
        try:
            db.session.delete(feedback)
            db.session.commit()
            flash("Обращение удалено ", category='success')
        except DBAPIError as error:
            # print(error.orig.pgcode)  #Код ошибки
            db.session.rollback()
            print("Ошибка удаления данных из БД " + str(error))
            flash("Ошибка удаления в БД", category='error')

    return redirect(url_for('.showfeedback'))
