from marshmallow import Schema, fields, validate

PASSWORD_POLICY = validate.Regexp(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$",
    error="Password must be at least 8 characters and include an uppercase letter, "
    "a lowercase letter, a digit, and a special character.",
)


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=PASSWORD_POLICY)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    date_joined = fields.Date(required=True)
    department_id = fields.Integer(required=False, allow_none=True)
    designation_id = fields.Integer(required=False, allow_none=True)
    role = fields.String(required=False, validate=validate.OneOf(["admin", "hr", "employee"]))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.String(required=True)
    new_password = fields.String(required=True, load_only=True, validate=PASSWORD_POLICY)
