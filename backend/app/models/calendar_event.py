from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import CalendarEventType


class CalendarEvent(db.Model, TimestampMixin):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    event_type = db.Column(db.Enum(CalendarEventType), nullable=False, default=CalendarEventType.EVENT)
    description = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    creator = db.relationship("User", foreign_keys=[created_by])

    __table_args__ = (db.UniqueConstraint("date", "title", name="uq_calendar_event_date_title"),)

    def __repr__(self):
        return f"<CalendarEvent {self.title} {self.date}>"
