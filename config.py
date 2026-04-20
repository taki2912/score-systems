import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'score.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-2024')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'avatars')
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
