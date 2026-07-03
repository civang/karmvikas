from app.extensions import db
from app.models.attendance import Attendance


class AttendanceRepository:
    def get_by_employee_and_date(self, employee_id, date_):
        return Attendance.query.filter_by(employee_id=employee_id, date=date_).first()

    def create(self, **kwargs):
        record = Attendance(**kwargs)
        db.session.add(record)
        db.session.commit()
        return record

    def update(self, record, **kwargs):
        for key, value in kwargs.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    def query(self, employee_id=None, date_from=None, date_to=None):
        q = Attendance.query
        if employee_id is not None:
            q = q.filter(Attendance.employee_id == employee_id)
        if date_from is not None:
            q = q.filter(Attendance.date >= date_from)
        if date_to is not None:
            q = q.filter(Attendance.date <= date_to)
        return q
