from flask import jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException

from app.errors.exceptions import AppError, AuthorizationError


def register_error_handlers(app):
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(err):
        try:
            from app.utils.audit import record_audit

            record_audit("authorization_denied", "request", None)
        except Exception:
            app.logger.exception("Failed to record audit log for authorization denial")

        payload = {"error": {"code": err.code, "message": err.message}}
        return jsonify(payload), err.status_code

    @app.errorhandler(AppError)
    def handle_app_error(err):
        payload = {"error": {"code": err.code, "message": err.message}}
        if err.details:
            payload["error"]["details"] = err.details
        return jsonify(payload), err.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_validation_error(err):
        payload = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": err.messages,
            }
        }
        return jsonify(payload), 422

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        code = (err.name or "HTTP_ERROR").upper().replace(" ", "_")
        return jsonify({"error": {"code": code, "message": err.description}}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        current_app.logger.exception("Unhandled exception")
        payload = {"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
        return jsonify(payload), 500
