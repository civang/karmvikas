from datetime import datetime, timezone

from app.errors.exceptions import ConflictError, ValidationAppError
from app.models.enums import AttendanceStatus
from app.repositories.attendance_repository import AttendanceRepository


class AttendanceService:
    def __init__(self, repo=None):
        self.repo = repo or AttendanceRepository()

    def check_in(self, employee_id):
        today = datetime.now(timezone.utc).date()
        existing = self.repo.get_by_employee_and_date(employee_id, today)
        if existing and existing.check_in:
            raise ConflictError("Already checked in for today")
        if existing:
            return self.repo.update(existing, check_in=datetime.now(timezone.utc))
        return self.repo.create(
            employee_id=employee_id,
            date=today,
            check_in=datetime.now(timezone.utc),
            status=AttendanceStatus.PRESENT,
        )

    def check_out(self, employee_id):
        today = datetime.now(timezone.utc).date()
        existing = self.repo.get_by_employee_and_date(employee_id, today)
        if not existing or not existing.check_in:
            raise ValidationAppError("You must check in before checking out")
        if existing.check_out:
            raise ConflictError("Already checked out for today")
        return self.repo.update(existing, check_out=datetime.now(timezone.utc))

    def list(self, employee_id=None, date_from=None, date_to=None):
        return self.repo.query(employee_id=employee_id, date_from=date_from, date_to=date_to)
