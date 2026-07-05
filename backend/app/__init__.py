import os
import logging

from flask import Flask, jsonify

from app.config import config_by_name
from app.extensions import db, migrate, jwt, bcrypt, cors, ma, limiter


def create_app(env_name=None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env_name])

    _init_extensions(app)
    _init_logging(app)
    _register_error_handlers(app)
    _register_blueprints(app)
    _register_health_routes(app)
    _register_cli(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    from app import models  # noqa: F401 — registers models on db.metadata before migrate/create_all
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}})

    from app.utils.redis_client import redis_client
    redis_client.init_app(app)

    from app.utils import jwt_callbacks  # noqa: F401 — registers JWT blocklist/error callbacks


def _register_error_handlers(app):
    from app.errors.handlers import register_error_handlers
    register_error_handlers(app)


def _register_cli(app):
    from app.cli import register_cli
    register_cli(app)


def _init_logging(app):
    log_format = (
        '{"time": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )
    logging.basicConfig(level=logging.INFO, format=log_format)


def _register_blueprints(app):
    from app.api.auth import bp as auth_bp
    from app.api.departments import bp as departments_bp
    from app.api.designations import bp as designations_bp
    from app.api.employees import bp as employees_bp
    from app.api.attendance import bp as attendance_bp
    from app.api.leaves import bp as leaves_bp
    from app.api.announcements import bp as announcements_bp
    from app.api.audit_logs import bp as audit_logs_bp
    from app.api.calendar import bp as calendar_bp
    from app.api.documents import bp as documents_bp
    from app.web import bp as web_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(designations_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leaves_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(audit_logs_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(web_bp)


def _register_health_routes(app):
    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/ready")
    def ready():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify(status="ready"), 200
        except Exception:
            app.logger.exception("Readiness check failed")
            return jsonify(status="not_ready"), 503
