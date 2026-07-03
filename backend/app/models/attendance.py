from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import AttendanceStatus


class Attendance(db.Model, TimestampMixin):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime(timezone=True), nullable=True)
    check_out = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)

    employee = db.relationship("Employee", back_populates="attendance_records")

    __table_args__ = (db.UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date"),)

    def __repr__(self):
        return f"<Attendance emp={self.employee_id} date={self.date}>"
