from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, VersionedMixin


class Employee(db.Model, TimestampMixin, SoftDeleteMixin, VersionedMixin):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    date_joined = db.Column(db.Date, nullable=False)
    profile_image_url = db.Column(db.String(500), nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True, index=True)
    designation_id = db.Column(db.Integer, db.ForeignKey("designations.id"), nullable=True, index=True)

    user = db.relationship("User", back_populates="employee")
    department = db.relationship("Department", back_populates="employees")
    designation = db.relationship("Designation", back_populates="employees")

    attendance_records = db.relationship("Attendance", back_populates="employee")
    leave_requests = db.relationship(
        "LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id"
    )
    leave_balances = db.relationship("LeaveBalance", back_populates="employee")
    documents = db.relationship("EmployeeDocument", back_populates="employee")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.full_name}>"
