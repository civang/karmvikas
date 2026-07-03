from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import UserRole


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    employee = db.relationship(
        "Employee", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
