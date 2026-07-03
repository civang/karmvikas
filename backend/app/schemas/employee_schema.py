from marshmallow import Schema, fields, validate


class EmployeeSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Method("get_email", dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    date_joined = fields.Date(dump_only=True)
    profile_image_url = fields.String(dump_only=True)
    department_id = fields.Integer(required=False, allow_none=True)
    designation_id = fields.Integer(required=False, allow_none=True)
    department_name = fields.Method("get_department_name", dump_only=True)
    designation_title = fields.Method("get_designation_title", dump_only=True)

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_designation_title(self, obj):
        return obj.designation.title if obj.designation else None


# Fields an employee is allowed to self-edit; anything else on this schema
# requires admin/hr and is enforced in the service layer, not just the client.
EMPLOYEE_SELF_EDITABLE_FIELDS = {"first_name", "last_name", "phone"}
