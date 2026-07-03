from sqlalchemy.exc import IntegrityError

from app.errors.exceptions import ConflictError, NotFoundError
from app.extensions import db
from app.models.enums import CalendarEventType
from app.repositories.calendar_event_repository import CalendarEventRepository


class CalendarEventService:
    def __init__(self, repo=None):
        self.repo = repo or CalendarEventRepository()

    def list(self, date_from=None, date_to=None):
        return self.repo.query(date_from=date_from, date_to=date_to).all()

    def create(self, data, created_by):
        try:
            return self.repo.create(
                title=data["title"],
                date=data["date"],
                event_type=CalendarEventType(data.get("event_type", "event")),
                description=data.get("description"),
                created_by=created_by,
            )
        except IntegrityError:
            db.session.rollback()
            raise ConflictError("An event with this title already exists on that date")

    def delete(self, event_id):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("Calendar event not found")
        self.repo.delete(event)
