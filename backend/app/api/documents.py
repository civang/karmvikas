import os

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.errors.exceptions import AuthorizationError, ValidationAppError
from app.schemas.document_schema import EmployeeDocumentSchema
from app.services.document_service import DocumentService
from app.utils.audit import record_audit
from app.utils.auth_context import current_employee

bp = Blueprint("documents", __name__, url_prefix="/api/v1")

schema = EmployeeDocumentSchema()
service = DocumentService()


def _assert_own_or_privileged(role, employee_id):
    if role == "employee" and current_employee().id != employee_id:
        raise AuthorizationError("You can only access your own documents")


@bp.post("/employees/<int:employee_id>/documents")
@jwt_required()
def upload_document(employee_id):
    role = get_jwt().get("role")
    _assert_own_or_privileged(role, employee_id)

    if "file" not in request.files or request.files["file"].filename == "":
        raise ValidationAppError("No file provided")

    document_type = request.form.get("document_type", "other")
    document = service.upload(employee_id, request.files["file"], document_type, int(get_jwt_identity()))
    record_audit("document_upload", "employee_document", document.id)
    return jsonify(schema.dump(document)), 201


@bp.get("/employees/<int:employee_id>/documents")
@jwt_required()
def list_documents(employee_id):
    role = get_jwt().get("role")
    _assert_own_or_privileged(role, employee_id)

    documents = service.list_for_employee(employee_id)
    return jsonify(schema.dump(documents, many=True)), 200


@bp.get("/documents/<int:document_id>/download")
@jwt_required()
def download_document(document_id):
    role = get_jwt().get("role")
    document = service.get_by_id(document_id)
    _assert_own_or_privileged(role, document.employee_id)

    upload_folder = os.path.abspath(current_app.config["DOCUMENT_UPLOAD_FOLDER"])
    return send_from_directory(
        upload_folder,
        document.stored_filename,
        as_attachment=True,
        download_name=document.original_filename,
    )


@bp.delete("/documents/<int:document_id>")
@jwt_required()
def delete_document(document_id):
    role = get_jwt().get("role")
    document = service.get_by_id(document_id)
    _assert_own_or_privileged(role, document.employee_id)

    service.delete(document_id)
    record_audit("document_delete", "employee_document", document_id)
    return "", 204
