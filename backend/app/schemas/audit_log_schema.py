from marshmallow import Schema, fields


class AuditLogSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    action = fields.String(dump_only=True)
    entity = fields.String(dump_only=True)
    entity_id = fields.Integer(dump_only=True)
    ip_address = fields.String(dump_only=True)
    timestamp = fields.DateTime(dump_only=True)
