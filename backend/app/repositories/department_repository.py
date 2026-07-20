from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.department import Department


class DepartmentRepository:
    def get_by_id(self, department_id):
        return db.session.get(Department, department_id)

    def get_by_name(self, name):
        return Department.query.filter_by(name=name).first()

    def query(self):
        return Department.query

    def create(self, **kwargs):
        department = Department(**kwargs)
        db.session.add(department)
        db.session.commit()
        return department

    def update(self, department, **kwargs):
        for key, value in kwargs.items():
            setattr(department, key, value)
        db.session.commit()
        return department

    def delete(self, department):
        try:
            db.session.delete(department)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise
