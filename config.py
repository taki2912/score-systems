import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 优先使用 PostgreSQL（Railway 提供），否则使用 SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway PostgreSQL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # 本地 SQLite
    DB_PATH = os.path.join(BASE_DIR, 'score.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-2024')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'avatars')
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
