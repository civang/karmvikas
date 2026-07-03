from datetime import datetime, timezone

from sqlalchemy.ext.declarative import declared_attr

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class SoftDeleteMixin:
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = utcnow()


class VersionedMixin:
    """Enables SQLAlchemy optimistic concurrency control on the mapped class."""
    version_id = db.Column(db.Integer, nullable=False, default=1)

    @declared_attr
    def __mapper_args__(cls):
        return {"version_id_col": cls.version_id}
