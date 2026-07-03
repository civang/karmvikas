from sqlalchemy.exc import IntegrityError

from app.errors.exceptions import ConflictError, NotFoundError
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository


class DepartmentService:
    def __init__(self, repo=None):
        self.repo = repo or DepartmentRepository()

    def list(self):
        return self.repo.query().order_by(Department.name).all()

    def get(self, department_id):
        department = self.repo.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department not found")
        return department

    def create(self, data):
        if self.repo.get_by_name(data["name"]):
            raise ConflictError("A department with this name already exists")
        return self.repo.create(**data)

    def update(self, department_id, data):
        department = self.get(department_id)
        return self.repo.update(department, **data)

    def delete(self, department_id):
        department = self.get(department_id)
        try:
            self.repo.delete(department)
        except IntegrityError:
            raise ConflictError("Cannot delete a department with existing designations or employees")
