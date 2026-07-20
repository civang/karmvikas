from app.extensions import db
from app.models.leave import LeaveBalance, LeaveRequest


class LeaveRequestRepository:
    def get_by_id(self, leave_id):
        return db.session.get(LeaveRequest, leave_id)

    def create(self, **kwargs):
        leave = LeaveRequest(**kwargs)
        db.session.add(leave)
        db.session.commit()
        return leave

    def query(self, employee_id=None, status=None):
        q = LeaveRequest.query
        if employee_id is not None:
            q = q.filter(LeaveRequest.employee_id == employee_id)
        if status is not None:
            q = q.filter(LeaveRequest.status == status)
        return q


class LeaveBalanceRepository:
    def get(self, employee_id, leave_type):
        return LeaveBalance.query.filter_by(employee_id=employee_id, leave_type=leave_type).first()

    def create(self, **kwargs):
        balance = LeaveBalance(**kwargs)
        db.session.add(balance)
        db.session.commit()
        return balance

    def list_for_employee(self, employee_id):
        return LeaveBalance.query.filter_by(employee_id=employee_id).all()
