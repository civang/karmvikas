from flask import request

from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, repo=None):
        self.repo = repo or AuditLogRepository()

    def log(self, user_id, action, entity, entity_id=None):
        self.repo.create(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            ip_address=request.remote_addr if request else None,
        )

    def list(self, limit=200):
        return self.repo.query().limit(limit).all()
