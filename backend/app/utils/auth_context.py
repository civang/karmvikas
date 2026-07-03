from flask_jwt_extended import get_jwt_identity

from app.errors.exceptions import NotFoundError
from app.repositories.employee_repository import EmployeeRepository


def current_employee():
    user_id = get_jwt_identity()
    employee = EmployeeRepository().get_by_user_id(int(user_id))
    if not employee:
        raise NotFoundError("Employee profile not found for current user")
    return employee
