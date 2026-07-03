import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app.errors.exceptions import NotFoundError, ValidationAppError
from app.models.enums import DocumentType
from app.repositories.document_repository import DocumentRepository
from app.repositories.employee_repository import EmployeeRepository


class DocumentService:
    def __init__(self, repo=None, employee_repo=None):
        self.repo = repo or DocumentRepository()
        self.employee_repo = employee_repo or EmployeeRepository()

    def upload(self, employee_id, file_storage, document_type_raw, uploaded_by):
        if not self.employee_repo.get_by_id(employee_id):
            raise NotFoundError("Employee not found")

        try:
            document_type = DocumentType(document_type_raw)
        except ValueError:
            raise ValidationAppError(f"Invalid document type: {document_type_raw}")

        # secure_filename strips path separators and unsafe characters - used
        # here only to safely read the extension for validation/display.
        # The file is never saved under the client-supplied name.
        safe_original = secure_filename(file_storage.filename or "")
        if not safe_original or "." not in safe_original:
            raise ValidationAppError("A valid file name with an extension is required")

        extension = safe_original.rsplit(".", 1)[-1].lower()
        allowed_ext = current_app.config["DOCUMENT_ALLOWED_EXTENSIONS"]
        allowed_mime = current_app.config["DOCUMENT_ALLOWED_MIME_TYPES"]

        if extension not in allowed_ext:
            raise ValidationAppError(f"File type .{extension} is not allowed")
        if file_storage.mimetype not in allowed_mime:
            raise ValidationAppError("File content type is not allowed")

        upload_folder = os.path.abspath(current_app.config["DOCUMENT_UPLOAD_FOLDER"])
        os.makedirs(upload_folder, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}.{extension}"
        file_storage.save(os.path.join(upload_folder, stored_filename))
        file_size = os.path.getsize(os.path.join(upload_folder, stored_filename))

        return self.repo.create(
            employee_id=employee_id,
            document_type=document_type,
            stored_filename=stored_filename,
            original_filename=safe_original,
            content_type=file_storage.mimetype,
            file_size=file_size,
            uploaded_by=uploaded_by,
        )

    def list_for_employee(self, employee_id):
        return self.repo.query(employee_id=employee_id).all()

    def get_by_id(self, document_id):
        document = self.repo.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found")
        return document

    def delete(self, document_id):
        document = self.get_by_id(document_id)
        upload_folder = os.path.abspath(current_app.config["DOCUMENT_UPLOAD_FOLDER"])
        path = os.path.join(upload_folder, document.stored_filename)
        if os.path.exists(path):
            os.remove(path)
        self.repo.delete(document)
