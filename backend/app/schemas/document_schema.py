from marshmallow import Schema, fields


class EmployeeDocumentSchema(Schema):
    id = fields.Integer(dump_only=True)
    employee_id = fields.Integer(dump_only=True)
    document_type = fields.Method("get_document_type", dump_only=True)
    original_filename = fields.String(dump_only=True)
    content_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    uploaded_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    def get_document_type(self, obj):
        return obj.document_type.value
