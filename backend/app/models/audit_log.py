from app.extensions import db
from app.models.base import utcnow


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity}:{self.entity_id}>"
