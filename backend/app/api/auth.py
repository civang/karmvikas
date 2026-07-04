from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import limiter
from app.schemas.auth_schema import ForgotPasswordSchema, LoginSchema, RegisterSchema, ResetPasswordSchema
from app.services.auth_service import AuthService
from app.utils.audit import record_audit
from app.utils.decorators import role_required

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
auth_service = AuthService()


@bp.post("/register")
@role_required("admin", "hr")
def register():
    data = register_schema.load(request.get_json(silent=True) or {})
    user, employee = auth_service.register(data)
    return (
        jsonify(id=user.id, email=user.email, role=user.role.value, employee_id=employee.id),
        201,
    )


@bp.post("/login")
@limiter.limit("5 per minute")
def login():
    data = login_schema.load(request.get_json(silent=True) or {})
    access_token, refresh_token, user = auth_service.login(data["email"], data["password"])
    record_audit("login", "user", user.id, user_id=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    role = get_jwt().get("role")
    access_token, refresh_token = auth_service.refresh(identity, role)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@bp.post("/logout")
@jwt_required(refresh=True)
def logout():
    auth_service.logout()
    record_audit("logout", "user")
    return jsonify(message="Logged out successfully"), 200


@bp.post("/forgot-password")
@limiter.limit("3 per hour")
def forgot_password():
    data = forgot_password_schema.load(request.get_json(silent=True) or {})
    auth_service.request_password_reset(data["email"])
    # Identical response whether or not the email exists - prevents
    # attackers from using this endpoint to enumerate valid accounts.
    return jsonify(message="If an account with that email exists, a reset link has been sent."), 200


@bp.post("/reset-password")
@limiter.limit("5 per hour")
def reset_password():
    data = reset_password_schema.load(request.get_json(silent=True) or {})
    auth_service.reset_password(data["token"], data["new_password"])
    return jsonify(message="Password reset successfully. You can now sign in."), 200
