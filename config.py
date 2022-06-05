# конфигурация приложения
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'SITE.db') # БД ORM
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:12345@localhost:5432/Test_site"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = '4598ujrjwoiip[]dmk//?Kojkdiou732940imkf;d'
UPLOAD_FOLDER = os.path.join(basedir + '\\app')
MAX_CONTENT_LENGTH = 1024*1024
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'Testmail@gmail.com'  # введите свой адрес электронной почты здесь
MAIL_DEFAULT_SENDER = 'Testmail@gmail.com'  # и здесь
MAIL_PASSWORD = 'Password'   # введите пароль
