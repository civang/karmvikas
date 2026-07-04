from app.extensions import db
from app.models.user import User


class UserRepository:
    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def create(self, **kwargs):
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    def update_password(self, user, password_hash):
        user.password_hash = password_hash
        db.session.commit()
        return user
