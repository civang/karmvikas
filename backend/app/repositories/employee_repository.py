from app.extensions import db
from app.models.employee import Employee


class EmployeeRepository:
    def create(self, **kwargs):
        employee = Employee(**kwargs)
        db.session.add(employee)
        db.session.commit()
        return employee

    def get_by_user_id(self, user_id):
        return Employee.query.filter_by(user_id=user_id, is_deleted=False).first()

    def get_by_id(self, employee_id):
        return Employee.query.filter_by(id=employee_id, is_deleted=False).first()

    def query(self, search=None):
        q = Employee.query.filter_by(is_deleted=False)
        if search:
            like = f"%{search}%"
            q = q.filter(
                db.or_(
                    Employee.first_name.ilike(like),
                    Employee.last_name.ilike(like),
                )
            )
        return q

    def update(self, employee, **kwargs):
        for key, value in kwargs.items():
            setattr(employee, key, value)
        db.session.commit()
        return employee

    def soft_delete(self, employee):
        employee.soft_delete()
        db.session.commit()
