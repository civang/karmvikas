from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import LeaveType, LeaveStatus


class LeaveRequest(db.Model, TimestampMixin):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(LeaveStatus), nullable=False, default=LeaveStatus.PENDING, index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    comment = db.Column(db.String(500), nullable=True)

    employee = db.relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])

    __table_args__ = (db.CheckConstraint("end_date >= start_date", name="ck_leave_dates_valid"),)

    def __repr__(self):
        return f"<LeaveRequest emp={self.employee_id} {self.status}>"


class LeaveBalance(db.Model, TimestampMixin):
    __tablename__ = "leave_balances"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    total = db.Column(db.Integer, nullable=False, default=0)
    used = db.Column(db.Integer, nullable=False, default=0)

    employee = db.relationship("Employee", back_populates="leave_balances")

    __table_args__ = (
        db.UniqueConstraint("employee_id", "leave_type", name="uq_leave_balance_employee_type"),
    )

    @property
    def remaining(self):
        return self.total - self.used
