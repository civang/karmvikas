from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt

from app.errors.exceptions import AuthorizationError


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                raise AuthorizationError("You do not have permission to perform this action")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
