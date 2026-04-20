import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 使用 Railway 持久化存储目录（如果存在）
if os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'):
    DB_PATH = os.path.join(os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'), 'score.db')
else:
    DB_PATH = os.path.join(BASE_DIR, 'score.db')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-2024')

# 头像存储也使用持久化目录
if os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'):
    UPLOAD_FOLDER = os.path.join(os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'), 'avatars')
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'avatars')

MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
