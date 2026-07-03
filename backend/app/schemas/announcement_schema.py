from marshmallow import Schema, fields, validate


class AnnouncementCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    body = fields.String(required=True, validate=validate.Length(min=1))


class AnnouncementSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    body = fields.String(dump_only=True)
    posted_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
