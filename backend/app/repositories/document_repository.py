from app.extensions import db
from app.models.employee_document import EmployeeDocument


class DocumentRepository:
    def get_by_id(self, document_id):
        return db.session.get(EmployeeDocument, document_id)

    def query(self, employee_id=None):
        q = EmployeeDocument.query
        if employee_id is not None:
            q = q.filter_by(employee_id=employee_id)
        return q.order_by(EmployeeDocument.created_at.desc())

    def create(self, **kwargs):
        document = EmployeeDocument(**kwargs)
        db.session.add(document)
        db.session.commit()
        return document

    def delete(self, document):
        db.session.delete(document)
        db.session.commit()
