import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 优先使用 PostgreSQL（Railway 提供），否则使用 SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway PostgreSQL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    # 添加连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 连接前检查
        'pool_recycle': 300,    # 5分钟回收连接
        'pool_size': 5,
        'max_overflow': 10
    }
else:
    # 本地 SQLite
    DB_PATH = os.path.join(BASE_DIR, 'score.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
    SQLALCHEMY_ENGINE_OPTIONS = {}

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-2024')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'avatars')
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
