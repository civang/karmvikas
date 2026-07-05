import datetime

import pytest

from app import create_app
from app.extensions import db
from app.services.auth_service import AuthService


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_tables(app):
    """Isolates each test: truncate every table after it runs."""
    yield
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_user(app, email, password, role="employee", first_name="Test", last_name="User", **extra):
    with app.app_context():
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "date_joined": datetime.date.today().isoformat(),
            "role": role,
            **extra,
        }
        user, employee = AuthService().register(data)
        return user.id, employee.id


def login(client, email, password):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin(app):
    user_id, employee_id = register_user(app, "admin@test.local", "AdminPass123!", role="admin")
    return {"user_id": user_id, "employee_id": employee_id, "email": "admin@test.local", "password": "AdminPass123!"}


@pytest.fixture()
def admin_token(client, admin):
    return login(client, admin["email"], admin["password"])["access_token"]


@pytest.fixture()
def hr(app):
    user_id, employee_id = register_user(app, "hr@test.local", "HrPass123!", role="hr")
    return {"user_id": user_id, "employee_id": employee_id, "email": "hr@test.local", "password": "HrPass123!"}


@pytest.fixture()
def hr_token(client, hr):
    return login(client, hr["email"], hr["password"])["access_token"]


@pytest.fixture()
def employee(app):
    user_id, employee_id = register_user(
        app, "alice@test.local", "AlicePass123!", role="employee", first_name="Alice", last_name="Doe"
    )
    return {"user_id": user_id, "employee_id": employee_id, "email": "alice@test.local", "password": "AlicePass123!"}


@pytest.fixture()
def employee_token(client, employee):
    return login(client, employee["email"], employee["password"])["access_token"]


@pytest.fixture()
def other_employee(app):
    user_id, employee_id = register_user(
        app, "bob@test.local", "BobPass123!", role="employee", first_name="Bob", last_name="Lee"
    )
    return {"user_id": user_id, "employee_id": employee_id, "email": "bob@test.local", "password": "BobPass123!"}


@pytest.fixture()
def other_employee_token(client, other_employee):
    return login(client, other_employee["email"], other_employee["password"])["access_token"]
