import os

SECRET_KEY = b'afd41e94b269e053cc3f6d065a717cffde51ee5208928463ce897faed531006b'
# SECRET_KEY = os.environ.get('SECRET_KEY')

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2445_films:04122001@std-mysql.ist.mospolytech.ru/std_2445_films'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')


ADMIN_ROLE_ID = 1