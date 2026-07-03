from marshmallow import Schema, fields, validate


class CalendarEventCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    date = fields.Date(required=True)
    event_type = fields.String(
        required=False,
        load_default="event",
        validate=validate.OneOf(["holiday", "meeting", "deadline", "event", "other"]),
    )
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))


class CalendarEventSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    date = fields.Date(dump_only=True)
    event_type = fields.Method("get_event_type", dump_only=True)
    description = fields.String(dump_only=True)
    created_by = fields.Integer(dump_only=True)

    def get_event_type(self, obj):
        return obj.event_type.value
