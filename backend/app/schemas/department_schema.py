from marshmallow import Schema, fields, validate


class DepartmentSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))


class DesignationSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    department_id = fields.Integer(required=True)
