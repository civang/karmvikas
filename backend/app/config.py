import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    REDIS_URL = os.environ["REDIS_URL"]
    RATELIMIT_STORAGE_URI = REDIS_URL

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB upload limit
    DOCUMENT_UPLOAD_FOLDER = "app/static/uploads/documents"
    DOCUMENT_ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
    }
    DOCUMENT_ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", BaseConfig.SQLALCHEMY_DATABASE_URI)


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
