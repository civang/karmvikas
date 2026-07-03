class AppError(Exception):
    status_code = 400
    code = "APP_ERROR"

    def __init__(self, message, status_code=None, code=None, details=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = details


class ValidationAppError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class AuthenticationError(AppError):
    status_code = 401
    code = "AUTHENTICATION_ERROR"


class AuthorizationError(AppError):
    status_code = 403
    code = "AUTHORIZATION_ERROR"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
