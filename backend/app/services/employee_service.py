from app.errors.exceptions import AuthorizationError, NotFoundError
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee_schema import EMPLOYEE_SELF_EDITABLE_FIELDS


class EmployeeService:
    def __init__(self, repo=None):
        self.repo = repo or EmployeeRepository()

    def list(self, search=None):
        return self.repo.query(search=search)

    def get(self, employee_id):
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee not found")
        return employee

    def update(self, employee_id, data, acting_role, acting_employee_id):
        employee = self.get(employee_id)

        if acting_role == "employee":
            if employee.id != acting_employee_id:
                raise AuthorizationError("You can only update your own profile")
            disallowed = set(data.keys()) - EMPLOYEE_SELF_EDITABLE_FIELDS
            if disallowed:
                raise AuthorizationError(
                    f"You are not permitted to update: {', '.join(sorted(disallowed))}"
                )

        return self.repo.update(employee, **data)

    def delete(self, employee_id):
        employee = self.get(employee_id)
        self.repo.soft_delete(employee)
