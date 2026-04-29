import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro-cambiar")

    _db_user = os.environ.get("DB_USER", "olp300_user")
    _db_pass = os.environ.get("DB_PASSWORD", "cambia-esto")
    _db_host = os.environ.get("DB_HOST", "localhost")
    _db_port = os.environ.get("DB_PORT", "3306")
    _db_name = os.environ.get("DB_NAME", "olp300")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote_plus(_db_user)}:{quote_plus(_db_pass)}"
        f"@{_db_host}:{_db_port}/{_db_name}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


config_by_name = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig,
}
