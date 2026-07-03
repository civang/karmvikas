from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt

from app.extensions import bcrypt
from app.errors.exceptions import AuthenticationError, ConflictError
from app.models.enums import UserRole
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.services.leave_service import LeaveService
from app.utils.redis_client import redis_client

REFRESH_TOKEN_TTL = timedelta(days=7)


class AuthService:
    def __init__(self, user_repo=None, employee_repo=None, leave_service=None):
        self.user_repo = user_repo or UserRepository()
        self.employee_repo = employee_repo or EmployeeRepository()
        self.leave_service = leave_service or LeaveService()

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

    def _revoke_current_token(self):
        jti = get_jwt()["jti"]
        redis_client.client.setex(f"revoked:{jti}", REFRESH_TOKEN_TTL, "true")
