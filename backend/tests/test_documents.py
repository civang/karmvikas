import io

from tests.conftest import auth_header


def _upload(client, token, employee_id, filename="resume.pdf", content=b"%PDF-1.4 test", document_type="resume"):
    return client.post(
        f"/api/v1/employees/{employee_id}/documents",
        data={"file": (io.BytesIO(content), filename), "document_type": document_type},
        content_type="multipart/form-data",
        headers=auth_header(token),
    )


class TestDocumentUpload:
    def test_employee_can_upload_own_document(self, client, employee_token, employee):
        res = _upload(client, employee_token, employee["employee_id"])
        assert res.status_code == 201
        body = res.get_json()
        assert body["original_filename"] == "resume.pdf"
        assert body["document_type"] == "resume"

    def test_disallowed_extension_rejected(self, client, employee_token, employee):
        res = _upload(client, employee_token, employee["employee_id"], filename="malware.exe")
        assert res.status_code == 422

    def test_employee_cannot_upload_to_another_employee(self, client, employee_token, other_employee):
        res = _upload(client, employee_token, other_employee["employee_id"])
        assert res.status_code == 403

    def test_admin_can_upload_for_any_employee(self, client, admin_token, employee):
        res = _upload(client, admin_token, employee["employee_id"])
        assert res.status_code == 201


class TestDocumentAccessIDOR:
    def test_employee_can_list_own_documents(self, client, employee_token, employee):
        _upload(client, employee_token, employee["employee_id"])
        res = client.get(f"/api/v1/employees/{employee['employee_id']}/documents", headers=auth_header(employee_token))
        assert res.status_code == 200
        assert len(res.get_json()) == 1

    def test_employee_cannot_list_others_documents(self, client, employee_token, other_employee_token, other_employee):
        _upload(client, other_employee_token, other_employee["employee_id"])
        res = client.get(
            f"/api/v1/employees/{other_employee['employee_id']}/documents", headers=auth_header(employee_token)
        )
        assert res.status_code == 403

    def test_download_requires_authentication(self, client, employee_token, employee):
        upload_res = _upload(client, employee_token, employee["employee_id"])
        doc_id = upload_res.get_json()["id"]

        res = client.get(f"/api/v1/documents/{doc_id}/download")
        assert res.status_code == 401

    def test_employee_can_download_own_document(self, client, employee_token, employee):
        upload_res = _upload(client, employee_token, employee["employee_id"])
        doc_id = upload_res.get_json()["id"]

        res = client.get(f"/api/v1/documents/{doc_id}/download", headers=auth_header(employee_token))
        assert res.status_code == 200

    def test_employee_cannot_download_others_document_by_guessing_id(
        self, client, employee_token, other_employee_token, other_employee
    ):
        upload_res = _upload(client, other_employee_token, other_employee["employee_id"])
        doc_id = upload_res.get_json()["id"]

        res = client.get(f"/api/v1/documents/{doc_id}/download", headers=auth_header(employee_token))
        assert res.status_code == 403

    def test_employee_cannot_delete_others_document(
        self, client, employee_token, other_employee_token, other_employee
    ):
        upload_res = _upload(client, other_employee_token, other_employee["employee_id"])
        doc_id = upload_res.get_json()["id"]

        res = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_header(employee_token))
        assert res.status_code == 403

    def test_owner_can_delete_own_document(self, client, employee_token, employee):
        upload_res = _upload(client, employee_token, employee["employee_id"])
        doc_id = upload_res.get_json()["id"]

        res = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_header(employee_token))
        assert res.status_code == 204

        listing = client.get(
            f"/api/v1/employees/{employee['employee_id']}/documents", headers=auth_header(employee_token)
        )
        assert listing.get_json() == []
