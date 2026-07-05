from tests.conftest import auth_header


class TestEmployeeDirectory:
    def test_list_returns_paginated_envelope(self, client, admin_token, employee):
        res = client.get("/api/v1/employees", headers=auth_header(admin_token))
        assert res.status_code == 200
        body = res.get_json()
        assert "items" in body and "meta" in body
        assert body["meta"]["total"] >= 1

    def test_search_filters_by_name(self, client, admin_token, employee, other_employee):
        res = client.get("/api/v1/employees?search=Alice", headers=auth_header(admin_token))
        body = res.get_json()
        names = [item["first_name"] for item in body["items"]]
        assert "Alice" in names
        assert "Bob" not in names

    def test_me_returns_own_profile(self, client, employee_token, employee):
        res = client.get("/api/v1/employees/me", headers=auth_header(employee_token))
        assert res.status_code == 200
        assert res.get_json()["email"] == employee["email"]


class TestEmployeeSelfServiceIDOR:
    def test_employee_can_update_own_phone(self, client, employee_token, employee):
        res = client.patch(
            f"/api/v1/employees/{employee['employee_id']}",
            json={"phone": "9999999999"},
            headers=auth_header(employee_token),
        )
        assert res.status_code == 200
        assert res.get_json()["phone"] == "9999999999"

    def test_employee_cannot_update_department_id(self, client, employee_token, employee):
        res = client.patch(
            f"/api/v1/employees/{employee['employee_id']}",
            json={"department_id": 1},
            headers=auth_header(employee_token),
        )
        assert res.status_code == 403
        assert "department_id" in res.get_json()["error"]["message"]

    def test_employee_cannot_update_another_employees_profile(
        self, client, employee_token, other_employee
    ):
        res = client.patch(
            f"/api/v1/employees/{other_employee['employee_id']}",
            json={"phone": "1111111111"},
            headers=auth_header(employee_token),
        )
        assert res.status_code == 403
        assert "own profile" in res.get_json()["error"]["message"]

    def test_admin_can_update_any_employee_including_restricted_fields(
        self, client, admin_token, employee
    ):
        res = client.patch(
            f"/api/v1/employees/{employee['employee_id']}",
            json={"phone": "5555555555"},
            headers=auth_header(admin_token),
        )
        assert res.status_code == 200
        assert res.get_json()["phone"] == "5555555555"


class TestEmployeeDeletion:
    def test_employee_role_cannot_delete(self, client, employee_token, other_employee):
        res = client.delete(
            f"/api/v1/employees/{other_employee['employee_id']}", headers=auth_header(employee_token)
        )
        assert res.status_code == 403

    def test_admin_soft_delete_removes_from_directory(self, client, admin_token, employee):
        res = client.delete(f"/api/v1/employees/{employee['employee_id']}", headers=auth_header(admin_token))
        assert res.status_code == 204

        listing = client.get("/api/v1/employees", headers=auth_header(admin_token))
        ids = [item["id"] for item in listing.get_json()["items"]]
        assert employee["employee_id"] not in ids

    def test_soft_deleted_employee_loses_self_service_access(
        self, client, admin_token, employee, employee_token
    ):
        client.delete(f"/api/v1/employees/{employee['employee_id']}", headers=auth_header(admin_token))

        res = client.get("/api/v1/employees/me", headers=auth_header(employee_token))
        assert res.status_code == 404
