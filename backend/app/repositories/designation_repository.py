from app.extensions import db
from app.models.department import Designation


class DesignationRepository:
    def get_by_id(self, designation_id):
        return Designation.query.get(designation_id)

    def query(self):
        return Designation.query

    def create(self, **kwargs):
        designation = Designation(**kwargs)
        db.session.add(designation)
        db.session.commit()
        return designation

    def update(self, designation, **kwargs):
        for key, value in kwargs.items():
            setattr(designation, key, value)
        db.session.commit()
        return designation

    def delete(self, designation):
        db.session.delete(designation)
        db.session.commit()
