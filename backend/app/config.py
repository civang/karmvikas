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

    # Email is an auxiliary feature (password reset, welcome emails), not a
    # core dependency like the database or JWT secret - the app should still
    # boot and run without it configured (email sending is then skipped with
    # a logged warning), so this uses .get() rather than fail-fast [] access.
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
    MAIL_FROM_EMAIL = os.environ.get("MAIL_FROM_EMAIL", "no-reply@karmvikas.test")
    MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "Karmvikas HR")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5000")
    PASSWORD_RESET_TOKEN_MAX_AGE = 1800  # 30 minutes


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", BaseConfig.SQLALCHEMY_DATABASE_URI)
    # Rate limits exist to slow down real attackers, not our own test suite
    # running hundreds of requests against the same endpoints in seconds.
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
