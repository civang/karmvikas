from app.extensions import db
from app.models.calendar_event import CalendarEvent


class CalendarEventRepository:
    def query(self, date_from=None, date_to=None):
        q = CalendarEvent.query
        if date_from is not None:
            q = q.filter(CalendarEvent.date >= date_from)
        if date_to is not None:
            q = q.filter(CalendarEvent.date <= date_to)
        return q.order_by(CalendarEvent.date.asc())

    def get_by_id(self, event_id):
        return CalendarEvent.query.get(event_id)

    def create(self, **kwargs):
        event = CalendarEvent(**kwargs)
        db.session.add(event)
        db.session.commit()
        return event

    def delete(self, event):
        db.session.delete(event)
        db.session.commit()
