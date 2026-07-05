from app.utils.reset_tokens import generate_reset_token
from tests.conftest import auth_header, login


class TestRegistration:
    def test_register_requires_admin_or_hr(self, client, employee_token):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@test.local",
                "password": "NewPass123!",
                "first_name": "New",
                "last_name": "Hire",
                "date_joined": "2026-01-01",
            },
            headers=auth_header(employee_token),
        )
        assert res.status_code == 403

    def test_register_rejects_without_token(self, client):
        res = client.post("/api/v1/auth/register", json={})
        assert res.status_code == 401
        assert res.get_json()["error"]["code"] == "TOKEN_MISSING"

    def test_admin_can_register_employee(self, client, admin_token):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@test.local",
                "password": "NewPass123!",
                "first_name": "New",
                "last_name": "Hire",
                "date_joined": "2026-01-01",
            },
            headers=auth_header(admin_token),
        )
        assert res.status_code == 201
        assert res.get_json()["email"] == "new@test.local"

    def test_duplicate_email_conflict(self, client, admin_token, employee):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": employee["email"],
                "password": "NewPass123!",
                "first_name": "Dup",
                "last_name": "User",
                "date_joined": "2026-01-01",
            },
            headers=auth_header(admin_token),
        )
        assert res.status_code == 409

    def test_weak_password_rejected(self, client, admin_token):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@test.local",
                "password": "weak",
                "first_name": "Weak",
                "last_name": "Pass",
                "date_joined": "2026-01-01",
            },
            headers=auth_header(admin_token),
        )
        assert res.status_code == 422
        assert "password" in res.get_json()["error"]["details"]


class TestLogin:
    def test_wrong_password_rejected(self, client, employee):
        res = client.post("/api/v1/auth/login", json={"email": employee["email"], "password": "wrong"})
        assert res.status_code == 401
        assert res.get_json()["error"]["code"] == "AUTHENTICATION_ERROR"

    def test_nonexistent_email_rejected(self, client):
        res = client.post("/api/v1/auth/login", json={"email": "nobody@test.local", "password": "whatever"})
        assert res.status_code == 401

    def test_correct_credentials_issue_tokens(self, client, employee):
        body = login(client, employee["email"], employee["password"])
        assert "access_token" in body
        assert "refresh_token" in body


class TestRefreshAndLogout:
    def test_refresh_rotates_and_revokes_old_token(self, client, employee):
        tokens = login(client, employee["email"], employee["password"])
        old_refresh = tokens["refresh_token"]

        res = client.post("/api/v1/auth/refresh", headers=auth_header(old_refresh))
        assert res.status_code == 200
        new_tokens = res.get_json()
        assert new_tokens["refresh_token"] != old_refresh

        replay = client.post("/api/v1/auth/refresh", headers=auth_header(old_refresh))
        assert replay.status_code == 401
        assert replay.get_json()["error"]["code"] == "TOKEN_REVOKED"

    def test_logout_revokes_refresh_token(self, client, employee):
        tokens = login(client, employee["email"], employee["password"])
        refresh = tokens["refresh_token"]

        res = client.post("/api/v1/auth/logout", headers=auth_header(refresh))
        assert res.status_code == 200

        replay = client.post("/api/v1/auth/refresh", headers=auth_header(refresh))
        assert replay.status_code == 401
        assert replay.get_json()["error"]["code"] == "TOKEN_REVOKED"

    def test_access_token_independent_of_refresh_lifecycle(self, client, employee):
        tokens = login(client, employee["email"], employee["password"])
        client.post("/api/v1/auth/logout", headers=auth_header(tokens["refresh_token"]))

        res = client.get("/api/v1/employees/me", headers=auth_header(tokens["access_token"]))
        assert res.status_code == 200


class TestPasswordReset:
    def test_forgot_password_identical_response_for_unknown_email(self, client, employee):
        known = client.post("/api/v1/auth/forgot-password", json={"email": employee["email"]})
        unknown = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@test.local"})
        assert known.status_code == unknown.status_code == 200
        assert known.get_json() == unknown.get_json()

    def test_reset_with_garbage_token_rejected(self, client):
        res = client.post("/api/v1/auth/reset-password", json={"token": "garbage", "new_password": "NewPass123!"})
        assert res.status_code == 422

    def test_reset_with_weak_password_rejected(self, app, client, employee):
        with app.app_context():
            token = generate_reset_token(employee["user_id"])
        res = client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "weak"})
        assert res.status_code == 422

    def test_valid_reset_changes_password_and_is_single_use(self, app, client, employee):
        with app.app_context():
            token = generate_reset_token(employee["user_id"])

        first = client.post(
            "/api/v1/auth/reset-password", json={"token": token, "new_password": "BrandNewPass123!"}
        )
        assert first.status_code == 200

        old_login = client.post(
            "/api/v1/auth/login", json={"email": employee["email"], "password": employee["password"]}
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/v1/auth/login", json={"email": employee["email"], "password": "BrandNewPass123!"}
        )
        assert new_login.status_code == 200

        replay = client.post(
            "/api/v1/auth/reset-password", json={"token": token, "new_password": "AnotherPass456!"}
        )
        assert replay.status_code == 422
