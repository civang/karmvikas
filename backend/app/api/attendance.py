from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.errors.exceptions import AuthorizationError
from app.schemas.attendance_schema import AttendanceSchema
from app.services.attendance_service import AttendanceService
from app.utils.auth_context import current_employee

bp = Blueprint("attendance", __name__, url_prefix="/api/v1/attendance")

schema = AttendanceSchema()
service = AttendanceService()


@bp.post("/check-in")
@jwt_required()
def check_in():
    employee = current_employee()
    record = service.check_in(employee.id)
    return jsonify(schema.dump(record)), 201


@bp.post("/check-out")
@jwt_required()
def check_out():
    employee = current_employee()
    record = service.check_out(employee.id)
    return jsonify(schema.dump(record)), 200


@bp.get("")
@jwt_required()
def list_attendance():
    role = get_jwt().get("role")
    requested_employee_id = request.args.get("employee_id", type=int)

    if role == "employee":
        employee_id = current_employee().id
        if requested_employee_id is not None and requested_employee_id != employee_id:
            raise AuthorizationError("You can only view your own attendance records")
    else:
        employee_id = requested_employee_id

    date_from = request.args.get("from", type=date.fromisoformat)
    date_to = request.args.get("to", type=date.fromisoformat)

    records = service.list(employee_id=employee_id, date_from=date_from, date_to=date_to)
    return jsonify(schema.dump(records, many=True)), 200
