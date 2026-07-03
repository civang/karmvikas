from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.errors.exceptions import ConflictError, NotFoundError
from app.repositories.department_repository import DepartmentRepository
from app.repositories.designation_repository import DesignationRepository


class DesignationService:
    def __init__(self, repo=None, department_repo=None):
        self.repo = repo or DesignationRepository()
        self.department_repo = department_repo or DepartmentRepository()

    def list(self, department_id=None):
        q = self.repo.query()
        if department_id is not None:
            q = q.filter_by(department_id=department_id)
        return q.all()

    def get(self, designation_id):
        designation = self.repo.get_by_id(designation_id)
        if not designation:
            raise NotFoundError("Designation not found")
        return designation

    def create(self, data):
        if not self.department_repo.get_by_id(data["department_id"]):
            raise NotFoundError("Department not found")
        try:
            return self.repo.create(**data)
        except IntegrityError:
            db.session.rollback()
            raise ConflictError("This designation already exists in the department")

    def update(self, designation_id, data):
        designation = self.get(designation_id)
        return self.repo.update(designation, **data)

    def delete(self, designation_id):
        designation = self.get(designation_id)
        try:
            self.repo.delete(designation)
        except IntegrityError:
            raise ConflictError("Cannot delete a designation with existing employees")
