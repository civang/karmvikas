from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.schemas.department_schema import DepartmentSchema
from app.services.department_service import DepartmentService
from app.utils.audit import record_audit
from app.utils.decorators import role_required

bp = Blueprint("departments", __name__, url_prefix="/api/v1/departments")

schema = DepartmentSchema()
service = DepartmentService()


@bp.get("")
@jwt_required()
def list_departments():
    departments = service.list()
    return jsonify(schema.dump(departments, many=True)), 200


@bp.get("/<int:department_id>")
@jwt_required()
def get_department(department_id):
    department = service.get(department_id)
    return jsonify(schema.dump(department)), 200


@bp.post("")
@role_required("admin", "hr")
def create_department():
    data = schema.load(request.get_json(silent=True) or {})
    department = service.create(data)
    return jsonify(schema.dump(department)), 201


@bp.patch("/<int:department_id>")
@role_required("admin", "hr")
def update_department(department_id):
    data = schema.load(request.get_json(silent=True) or {}, partial=True)
    department = service.update(department_id, data)
    return jsonify(schema.dump(department)), 200


@bp.delete("/<int:department_id>")
@role_required("admin", "hr")
def delete_department(department_id):
    service.delete(department_id)
    record_audit("department_delete", "department", department_id)
    return "", 204
