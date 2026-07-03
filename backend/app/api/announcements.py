from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.schemas.announcement_schema import AnnouncementCreateSchema, AnnouncementSchema
from app.services.announcement_service import AnnouncementService
from app.utils.decorators import role_required

bp = Blueprint("announcements", __name__, url_prefix="/api/v1/announcements")

create_schema = AnnouncementCreateSchema()
schema = AnnouncementSchema()
service = AnnouncementService()


@bp.get("")
@jwt_required()
def list_announcements():
    limit = request.args.get("limit", 10, type=int)
    announcements = service.list(limit=limit)
    return jsonify(schema.dump(announcements, many=True)), 200


@bp.post("")
@role_required("admin", "hr")
def create_announcement():
    data = create_schema.load(request.get_json(silent=True) or {})
    announcement = service.create(data["title"], data["body"], int(get_jwt_identity()))
    return jsonify(schema.dump(announcement)), 201


@bp.delete("/<int:announcement_id>")
@role_required("admin", "hr")
def delete_announcement(announcement_id):
    service.delete(announcement_id)
    return "", 204
