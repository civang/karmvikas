from app.extensions import db
from app.models.announcement import Announcement


class AnnouncementRepository:
    def query(self):
        return Announcement.query.order_by(Announcement.created_at.desc())

    def get_by_id(self, announcement_id):
        return Announcement.query.get(announcement_id)

    def create(self, **kwargs):
        announcement = Announcement(**kwargs)
        db.session.add(announcement)
        db.session.commit()
        return announcement

    def delete(self, announcement):
        db.session.delete(announcement)
        db.session.commit()
