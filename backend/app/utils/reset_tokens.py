from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import current_app

RESET_PASSWORD_SALT = "password-reset"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_reset_token(user_id):
    return _serializer().dumps({"user_id": user_id}, salt=RESET_PASSWORD_SALT)


def verify_reset_token(token):
    """Returns the user_id if valid, or None if expired/tampered/malformed."""
    max_age = current_app.config["PASSWORD_RESET_TOKEN_MAX_AGE"]
    try:
        data = _serializer().loads(token, salt=RESET_PASSWORD_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("user_id")
