import hashlib
from datetime import timedelta

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt

from app.extensions import bcrypt
from app.errors.exceptions import AuthenticationError, ConflictError, ValidationAppError
from app.models.enums import UserRole
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.services.leave_service import LeaveService
from app.utils.redis_client import redis_client
from app.utils.reset_tokens import generate_reset_token, verify_reset_token

REFRESH_TOKEN_TTL = timedelta(days=7)


class AuthService:
    def __init__(self, user_repo=None, employee_repo=None, leave_service=None, email_service=None):
        self.user_repo = user_repo or UserRepository()
        self.employee_repo = employee_repo or EmployeeRepository()
        self.leave_service = leave_service or LeaveService()
        self.email_service = email_service or EmailService()

    def register(self, data):
        if self.user_repo.get_by_email(data["email"]):
            raise ConflictError("A user with this email already exists")

        password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        user = self.user_repo.create(
            email=data["email"],
            password_hash=password_hash,
            role=UserRole(data.get("role", "employee")),
        )
        employee = self.employee_repo.create(
            user_id=user.id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_joined=data["date_joined"],
            department_id=data.get("department_id"),
            designation_id=data.get("designation_id"),
        )
        self.leave_service.seed_default_balances(employee.id)
        self.email_service.send_welcome(user.email, employee.first_name)
        return user, employee

    def login(self, email, password):
        user = self.user_repo.get_by_email(email)
        if not user or not user.is_active or not bcrypt.check_password_hash(user.password_hash, password):
            raise AuthenticationError("Invalid email or password")

        claims = {"role": user.role.value}
        access_token = create_access_token(identity=str(user.id), additional_claims=claims)
        refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)
        return access_token, refresh_token, user

    def refresh(self, identity, role):
        self._revoke_current_token()
        claims = {"role": role}
        access_token = create_access_token(identity=identity, additional_claims=claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=claims)
        return access_token, refresh_token

    def logout(self):
        self._revoke_current_token()

    def request_password_reset(self, email):
        # Deliberately silent on a missing/inactive user - the route always
        # returns the same generic message regardless, to prevent attackers
        # from using this endpoint to enumerate valid account emails.
        user = self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return

        token = generate_reset_token(user.id)
        reset_link = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
        self.email_service.send_password_reset(user.email, reset_link)

    def reset_password(self, token, new_password):
        user_id = verify_reset_token(token)
        if user_id is None:
            raise ValidationAppError("This password reset link is invalid or has expired")

        # Reset tokens must be single-use: without this check, a leaked link
        # (forwarded email, browser history, proxy logs) stays valid to
        # replay for its full lifetime instead of just once.
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        redis_key = f"reset_used:{token_hash}"
        if redis_client.client.exists(redis_key):
            raise ValidationAppError("This password reset link is invalid or has expired")

        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValidationAppError("This password reset link is invalid or has expired")

        password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
        self.user_repo.update_password(user, password_hash)

        max_age = current_app.config["PASSWORD_RESET_TOKEN_MAX_AGE"]
        redis_client.client.setex(redis_key, max_age, "true")

    def _revoke_current_token(self):
        jti = get_jwt()["jti"]
        redis_client.client.setex(f"revoked:{jti}", REFRESH_TOKEN_TTL, "true")
