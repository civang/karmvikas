from flask import Blueprint, redirect, render_template

bp = Blueprint("web", __name__)


@bp.get("/")
def index():
    return redirect("/dashboard")


@bp.get("/api/docs")
def api_docs():
    return render_template("api_docs.html")


@bp.get("/login")
def login_page():
    return render_template("login.html")


@bp.get("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")


@bp.get("/reset-password")
def reset_password_page():
    return render_template("reset_password.html")


@bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@bp.get("/employees")
def employees_page():
    return render_template("employees.html")


@bp.get("/profile")
def profile_page():
    return render_template("profile.html")


@bp.get("/attendance")
def attendance_page():
    return render_template("attendance.html")


@bp.get("/leaves")
def leaves_page():
    return render_template("leaves.html")


@bp.get("/departments")
def departments_page():
    return render_template("departments.html")


@bp.get("/calendar")
def calendar_page():
    return render_template("calendar.html")


@bp.get("/audit-logs")
def audit_logs_page():
    return render_template("audit_logs.html")
