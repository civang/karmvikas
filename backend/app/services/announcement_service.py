from app.errors.exceptions import NotFoundError
from app.repositories.announcement_repository import AnnouncementRepository


class AnnouncementService:
    def __init__(self, repo=None):
        self.repo = repo or AnnouncementRepository()

    def list(self, limit=10):
        return self.repo.query().limit(limit).all()

    def create(self, title, body, posted_by):
        return self.repo.create(title=title, body=body, posted_by=posted_by)

    def delete(self, announcement_id):
        announcement = self.repo.get_by_id(announcement_id)
        if not announcement:
            raise NotFoundError("Announcement not found")
        self.repo.delete(announcement)
