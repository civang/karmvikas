from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.schemas.calendar_event_schema import CalendarEventCreateSchema, CalendarEventSchema
from app.services.calendar_event_service import CalendarEventService
from app.utils.audit import record_audit
from app.utils.decorators import role_required

bp = Blueprint("calendar", __name__, url_prefix="/api/v1/calendar-events")

create_schema = CalendarEventCreateSchema()
schema = CalendarEventSchema()
service = CalendarEventService()


@bp.get("")
@jwt_required()
def list_events():
    date_from = request.args.get("from", type=date.fromisoformat)
    date_to = request.args.get("to", type=date.fromisoformat)
    events = service.list(date_from=date_from, date_to=date_to)
    return jsonify(schema.dump(events, many=True)), 200


@bp.post("")
@role_required("admin", "hr")
def create_event():
    data = create_schema.load(request.get_json(silent=True) or {})
    event = service.create(data, int(get_jwt_identity()))
    record_audit("calendar_event_create", "calendar_event", event.id)
    return jsonify(schema.dump(event)), 201


@bp.delete("/<int:event_id>")
@role_required("admin", "hr")
def delete_event(event_id):
    service.delete(event_id)
    record_audit("calendar_event_delete", "calendar_event", event_id)
    return "", 204
