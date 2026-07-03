from app.errors.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.extensions import db
from app.models.enums import LeaveStatus, LeaveType
from app.repositories.leave_repository import LeaveBalanceRepository, LeaveRequestRepository

DEFAULT_LEAVE_ALLOWANCE = {
    LeaveType.CASUAL: 12,
    LeaveType.SICK: 10,
    LeaveType.EARNED: 15,
    LeaveType.UNPAID: 0,
}


class LeaveService:
    def __init__(self, repo=None, balance_repo=None):
        self.repo = repo or LeaveRequestRepository()
        self.balance_repo = balance_repo or LeaveBalanceRepository()

    def seed_default_balances(self, employee_id):
        for leave_type, total in DEFAULT_LEAVE_ALLOWANCE.items():
            self.balance_repo.create(employee_id=employee_id, leave_type=leave_type, total=total, used=0)

    def apply(self, employee_id, data):
        leave_type = LeaveType(data["leave_type"])
        start_date, end_date = data["start_date"], data["end_date"]
        if end_date < start_date:
            raise ValidationAppError("End date cannot be before start date")

        return self.repo.create(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            status=LeaveStatus.PENDING,
        )

    def list(self, employee_id=None, status=None):
        return self.repo.query(employee_id=employee_id, status=status)

    def get(self, leave_id):
        leave = self.repo.get_by_id(leave_id)
        if not leave:
            raise NotFoundError("Leave request not found")
        return leave

    def approve(self, leave_id, reviewer_id, comment=None):
        leave = self.get(leave_id)
        if leave.status != LeaveStatus.PENDING:
            raise ConflictError("This leave request has already been reviewed")

        days_requested = (leave.end_date - leave.start_date).days + 1

        if leave.leave_type != LeaveType.UNPAID:
            balance = self.balance_repo.get(leave.employee_id, leave.leave_type)
            if not balance or balance.remaining < days_requested:
                raise ConflictError("Insufficient leave balance for this request")
            balance.used += days_requested

        leave.status = LeaveStatus.APPROVED
        leave.reviewed_by = reviewer_id
        leave.comment = comment
        db.session.commit()
        return leave

    def reject(self, leave_id, reviewer_id, comment=None):
        leave = self.get(leave_id)
        if leave.status != LeaveStatus.PENDING:
            raise ConflictError("This leave request has already been reviewed")

        leave.status = LeaveStatus.REJECTED
        leave.reviewed_by = reviewer_id
        leave.comment = comment
        db.session.commit()
        return leave

    def balances(self, employee_id):
        return self.balance_repo.list_for_employee(employee_id)
