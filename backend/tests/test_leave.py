from tests.conftest import auth_header


class TestLeaveBalances:
    def test_default_balances_seeded_on_registration(self, client, employee_token):
        res = client.get("/api/v1/leaves/balances", headers=auth_header(employee_token))
        assert res.status_code == 200
        balances = {b["leave_type"]: b for b in res.get_json()}
        assert balances["casual"]["total"] == 12
        assert balances["sick"]["total"] == 10
        assert balances["earned"]["total"] == 15
        assert balances["unpaid"]["total"] == 0
        for b in balances.values():
            assert b["used"] == 0
            assert b["remaining"] == b["total"]


class TestLeaveLifecycle:
    def _apply(self, client, token, leave_type="casual", start="2026-08-01", end="2026-08-03"):
        return client.post(
            "/api/v1/leaves",
            json={"leave_type": leave_type, "start_date": start, "end_date": end},
            headers=auth_header(token),
        )

    def test_apply_creates_pending_request(self, client, employee_token):
        res = self._apply(client, employee_token)
        assert res.status_code == 201
        assert res.get_json()["status"] == "pending"

    def test_employee_cannot_approve_own_leave(self, client, employee_token):
        leave_id = self._apply(client, employee_token).get_json()["id"]
        res = client.patch(f"/api/v1/leaves/{leave_id}/approve", json={}, headers=auth_header(employee_token))
        assert res.status_code == 403

    def test_admin_approve_deducts_balance(self, client, employee_token, admin_token):
        # 3-day casual leave (Aug 1-3 inclusive)
        leave_id = self._apply(client, employee_token).get_json()["id"]

        res = client.patch(f"/api/v1/leaves/{leave_id}/approve", json={}, headers=auth_header(admin_token))
        assert res.status_code == 200
        assert res.get_json()["status"] == "approved"

        balances = {
            b["leave_type"]: b
            for b in client.get("/api/v1/leaves/balances", headers=auth_header(employee_token)).get_json()
        }
        assert balances["casual"]["used"] == 3
        assert balances["casual"]["remaining"] == 9

    def test_reject_leaves_balance_untouched(self, client, employee_token, admin_token):
        leave_id = self._apply(client, employee_token).get_json()["id"]

        res = client.patch(f"/api/v1/leaves/{leave_id}/reject", json={}, headers=auth_header(admin_token))
        assert res.status_code == 200
        assert res.get_json()["status"] == "rejected"

        balances = {
            b["leave_type"]: b
            for b in client.get("/api/v1/leaves/balances", headers=auth_header(employee_token)).get_json()
        }
        assert balances["casual"]["used"] == 0

    def test_approval_blocked_when_exceeding_balance(self, client, employee_token, admin_token):
        # Sick balance is 10 days; request 20 to force an over-allocation.
        leave_id = self._apply(
            client, employee_token, leave_type="sick", start="2026-09-01", end="2026-09-20"
        ).get_json()["id"]

        res = client.patch(f"/api/v1/leaves/{leave_id}/approve", json={}, headers=auth_header(admin_token))
        assert res.status_code == 409

    def test_cannot_review_already_reviewed_request(self, client, employee_token, admin_token):
        leave_id = self._apply(client, employee_token).get_json()["id"]
        client.patch(f"/api/v1/leaves/{leave_id}/approve", json={}, headers=auth_header(admin_token))

        res = client.patch(f"/api/v1/leaves/{leave_id}/reject", json={}, headers=auth_header(admin_token))
        assert res.status_code == 409

    def test_employee_only_sees_own_leave_requests(self, client, employee_token, other_employee_token):
        self._apply(client, employee_token)
        self._apply(client, other_employee_token)

        res = client.get("/api/v1/leaves", headers=auth_header(employee_token))
        assert len(res.get_json()) == 1
