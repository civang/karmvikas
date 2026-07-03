from flask_jwt_extended import get_jwt_identity

from app.services.audit_service import AuditService


def record_audit(action, entity, entity_id=None, user_id=None):
    if user_id is None:
        try:
            user_id = int(get_jwt_identity())
        except Exception:
            user_id = None
    AuditService().log(user_id, action, entity, entity_id)
