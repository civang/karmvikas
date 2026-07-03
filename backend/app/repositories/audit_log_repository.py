from app.extensions import db
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def create(self, **kwargs):
        log = AuditLog(**kwargs)
        db.session.add(log)
        db.session.commit()
        return log

    def query(self):
        return AuditLog.query.order_by(AuditLog.timestamp.desc())
