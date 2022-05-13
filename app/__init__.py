from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config') #конфигурация настроек приложения из файла config.py
db = SQLAlchemy(app)
migrate = Migrate(app,  db) #потом в терминале flask db init для создания папки migrations
mail = Mail(app) #для отправки сообщений на почту, экземпляр класса Mail
login_manager = LoginManager(app) #создаем экземпляр класса LоginManager для авторизации админа
login_manager.login_view = ".login" #какую страницу показывать неавторизованному админу
login_manager.login_message_category = 'success' #категория для всплывающих сллбщений

from app.admin.views import admin #импортируем блюпринт здесь, иначе циклический импорт
app.register_blueprint(admin, url_prefix='/admin', template_folder='templates', static_folder='static')
#регистрируем переменную admin класса blueprint
#Все url внутри этого blueprinta будут иметь вид домен/url_prefix/url_blueprint

from app import views