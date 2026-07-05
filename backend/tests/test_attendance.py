from tests.conftest import auth_header


class TestCheckInOut:
    def test_check_in_creates_record(self, client, employee_token):
        res = client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        assert res.status_code == 201
        body = res.get_json()
        assert body["check_in"] is not None
        assert body["check_out"] is None

    def test_duplicate_check_in_same_day_conflicts(self, client, employee_token):
        client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        res = client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        assert res.status_code == 409

    def test_check_out_requires_check_in_first(self, client, employee_token):
        res = client.post("/api/v1/attendance/check-out", headers=auth_header(employee_token))
        assert res.status_code == 422

    def test_check_out_after_check_in_succeeds(self, client, employee_token):
        client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        res = client.post("/api/v1/attendance/check-out", headers=auth_header(employee_token))
        assert res.status_code == 200
        assert res.get_json()["check_out"] is not None

    def test_duplicate_check_out_conflicts(self, client, employee_token):
        client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        client.post("/api/v1/attendance/check-out", headers=auth_header(employee_token))
        res = client.post("/api/v1/attendance/check-out", headers=auth_header(employee_token))
        assert res.status_code == 409


class TestAttendanceIDOR:
    def test_employee_sees_only_own_records(self, client, employee_token, other_employee_token):
        client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        client.post("/api/v1/attendance/check-in", headers=auth_header(other_employee_token))

        res = client.get("/api/v1/attendance", headers=auth_header(employee_token))
        assert res.status_code == 200
        assert len(res.get_json()) == 1

    def test_employee_cannot_view_others_attendance_via_query_param(
        self, client, employee_token, other_employee
    ):
        res = client.get(
            f"/api/v1/attendance?employee_id={other_employee['employee_id']}",
            headers=auth_header(employee_token),
        )
        assert res.status_code == 403

    def test_admin_can_view_any_employees_attendance(self, client, admin_token, employee, employee_token):
        client.post("/api/v1/attendance/check-in", headers=auth_header(employee_token))
        res = client.get(
            f"/api/v1/attendance?employee_id={employee['employee_id']}", headers=auth_header(admin_token)
        )
        assert res.status_code == 200
        assert len(res.get_json()) == 1
