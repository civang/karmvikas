from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import DocumentType


class EmployeeDocument(db.Model, TimestampMixin):
    __tablename__ = "employee_documents"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    document_type = db.Column(db.Enum(DocumentType), nullable=False, default=DocumentType.OTHER)

    # Server-generated (UUID-based) filename on disk - never derived from
    # client input, so a malicious filename can't traverse the filesystem
    # or overwrite another employee's file.
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    original_filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)

    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    employee = db.relationship("Employee", back_populates="documents")
    uploader = db.relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<EmployeeDocument {self.original_filename} emp={self.employee_id}>"
