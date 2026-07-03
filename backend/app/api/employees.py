from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.schemas.employee_schema import EmployeeSchema
from app.services.employee_service import EmployeeService
from app.utils.auth_context import current_employee
from app.utils.decorators import role_required
from app.utils.audit import record_audit
from app.utils.pagination import apply_sort, paginated_response, parse_list_params
from app.models.employee import Employee

bp = Blueprint("employees", __name__, url_prefix="/api/v1/employees")

schema = EmployeeSchema()
service = EmployeeService()

SORTABLE_FIELDS = {"first_name", "last_name", "date_joined"}


@bp.get("")
@jwt_required()
def list_employees():
    params = parse_list_params(allowed_filters=["department_id", "designation_id"])
    query = service.list(search=params["search"] or None)

    for field, value in params["filters"].items():
        query = query.filter(getattr(Employee, field) == value)

    query = apply_sort(query, Employee, params["sort"], SORTABLE_FIELDS)
    return jsonify(paginated_response(query, params["page"], params["per_page"], schema)), 200


@bp.get("/me")
@jwt_required()
def get_my_profile():
    employee = current_employee()
    return jsonify(schema.dump(employee)), 200


@bp.get("/<int:employee_id>")
@jwt_required()
def get_employee(employee_id):
    employee = service.get(employee_id)
    return jsonify(schema.dump(employee)), 200


@bp.patch("/<int:employee_id>")
@jwt_required()
def update_employee(employee_id):
    claims = get_jwt()
    role = claims.get("role")
    acting_employee_id = None
    if role == "employee":
        acting_employee_id = current_employee().id

    data = schema.load(request.get_json(silent=True) or {}, partial=True)
    employee = service.update(employee_id, data, acting_role=role, acting_employee_id=acting_employee_id)
    return jsonify(schema.dump(employee)), 200


@bp.delete("/<int:employee_id>")
@role_required("admin", "hr")
def delete_employee(employee_id):
    service.delete(employee_id)
    record_audit("employee_soft_delete", "employee", employee_id)
    return "", 204
