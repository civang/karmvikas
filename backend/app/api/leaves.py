from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.errors.exceptions import AuthorizationError
from app.schemas.leave_schema import (
    LeaveBalanceSchema,
    LeaveRequestCreateSchema,
    LeaveRequestSchema,
    LeaveReviewSchema,
)
from app.services.leave_service import LeaveService
from app.utils.audit import record_audit
from app.utils.auth_context import current_employee

bp = Blueprint("leaves", __name__, url_prefix="/api/v1/leaves")

create_schema = LeaveRequestCreateSchema()
review_schema = LeaveReviewSchema()
leave_schema = LeaveRequestSchema()
balance_schema = LeaveBalanceSchema()
service = LeaveService()


@bp.post("")
@jwt_required()
def apply_leave():
    employee = current_employee()
    data = create_schema.load(request.get_json(silent=True) or {})
    leave = service.apply(employee.id, data)
    return jsonify(leave_schema.dump(leave)), 201


@bp.get("")
@jwt_required()
def list_leaves():
    role = get_jwt().get("role")
    status = request.args.get("status")
    requested_employee_id = request.args.get("employee_id", type=int)

    if role == "employee":
        employee_id = current_employee().id
        if requested_employee_id is not None and requested_employee_id != employee_id:
            raise AuthorizationError("You can only view your own leave requests")
    else:
        employee_id = requested_employee_id

    leaves = service.list(employee_id=employee_id, status=status)
    return jsonify(leave_schema.dump(leaves, many=True)), 200


@bp.get("/balances")
@jwt_required()
def my_balances():
    employee = current_employee()
    balances = service.balances(employee.id)
    return jsonify(balance_schema.dump(balances, many=True)), 200


@bp.patch("/<int:leave_id>/approve")
@jwt_required()
def approve_leave(leave_id):
    role = get_jwt().get("role")
    if role not in ("admin", "hr"):
        raise AuthorizationError("Only Admin or HR can approve leave requests")

    data = review_schema.load(request.get_json(silent=True) or {})
    reviewer_id = int(get_jwt_identity())
    leave = service.approve(leave_id, reviewer_id, comment=data.get("comment"))
    record_audit("leave_approve", "leave_request", leave_id)
    return jsonify(leave_schema.dump(leave)), 200


@bp.patch("/<int:leave_id>/reject")
@jwt_required()
def reject_leave(leave_id):
    role = get_jwt().get("role")
    if role not in ("admin", "hr"):
        raise AuthorizationError("Only Admin or HR can reject leave requests")

    data = review_schema.load(request.get_json(silent=True) or {})
    reviewer_id = int(get_jwt_identity())
    leave = service.reject(leave_id, reviewer_id, comment=data.get("comment"))
    record_audit("leave_reject", "leave_request", leave_id)
    return jsonify(leave_schema.dump(leave)), 200
