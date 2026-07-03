from marshmallow import Schema, fields, validate


class LeaveRequestCreateSchema(Schema):
    leave_type = fields.String(required=True, validate=validate.OneOf(["casual", "sick", "earned", "unpaid"]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)


class LeaveReviewSchema(Schema):
    comment = fields.String(required=False, allow_none=True, validate=validate.Length(max=500))


class LeaveRequestSchema(Schema):
    id = fields.Integer(dump_only=True)
    employee_id = fields.Integer(dump_only=True)
    leave_type = fields.Method("get_leave_type", dump_only=True)
    start_date = fields.Date(dump_only=True)
    end_date = fields.Date(dump_only=True)
    status = fields.Method("get_status", dump_only=True)
    reviewed_by = fields.Integer(dump_only=True)
    comment = fields.String(dump_only=True)

    def get_leave_type(self, obj):
        return obj.leave_type.value

    def get_status(self, obj):
        return obj.status.value


class LeaveBalanceSchema(Schema):
    leave_type = fields.Method("get_leave_type", dump_only=True)
    total = fields.Integer(dump_only=True)
    used = fields.Integer(dump_only=True)
    remaining = fields.Integer(dump_only=True)

    def get_leave_type(self, obj):
        return obj.leave_type.value
