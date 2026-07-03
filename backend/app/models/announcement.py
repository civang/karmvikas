from app.extensions import db
from app.models.base import TimestampMixin


class Announcement(db.Model, TimestampMixin):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    author = db.relationship("User", foreign_keys=[posted_by])

    def __repr__(self):
        return f"<Announcement {self.title}>"
