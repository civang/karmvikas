from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.schemas.department_schema import DesignationSchema
from app.services.designation_service import DesignationService
from app.utils.audit import record_audit
from app.utils.decorators import role_required

bp = Blueprint("designations", __name__, url_prefix="/api/v1/designations")

schema = DesignationSchema()
service = DesignationService()


@bp.get("")
@jwt_required()
def list_designations():
    department_id = request.args.get("department_id", type=int)
    designations = service.list(department_id=department_id)
    return jsonify(schema.dump(designations, many=True)), 200


@bp.get("/<int:designation_id>")
@jwt_required()
def get_designation(designation_id):
    designation = service.get(designation_id)
    return jsonify(schema.dump(designation)), 200


@bp.post("")
@role_required("admin", "hr")
def create_designation():
    data = schema.load(request.get_json(silent=True) or {})
    designation = service.create(data)
    return jsonify(schema.dump(designation)), 201


@bp.patch("/<int:designation_id>")
@role_required("admin", "hr")
def update_designation(designation_id):
    data = schema.load(request.get_json(silent=True) or {}, partial=True)
    designation = service.update(designation_id, data)
    return jsonify(schema.dump(designation)), 200


@bp.delete("/<int:designation_id>")
@role_required("admin", "hr")
def delete_designation(designation_id):
    service.delete(designation_id)
    record_audit("designation_delete", "designation", designation_id)
    return "", 204
