from flask import Blueprint, jsonify

from app.schemas.audit_log_schema import AuditLogSchema
from app.services.audit_service import AuditService
from app.utils.decorators import role_required

bp = Blueprint("audit_logs", __name__, url_prefix="/api/v1/audit-logs")

schema = AuditLogSchema()
service = AuditService()


@bp.get("")
@role_required("admin")
def list_audit_logs():
    logs = service.list()
    return jsonify(schema.dump(logs, many=True)), 200
