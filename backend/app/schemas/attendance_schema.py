from marshmallow import Schema, fields


class AttendanceSchema(Schema):
    id = fields.Integer(dump_only=True)
    employee_id = fields.Integer(dump_only=True)
    date = fields.Date(dump_only=True)
    check_in = fields.DateTime(dump_only=True)
    check_out = fields.DateTime(dump_only=True)
    status = fields.Method("get_status", dump_only=True)

    def get_status(self, obj):
        return obj.status.value
