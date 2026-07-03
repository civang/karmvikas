import datetime

import click

from app.extensions import db, bcrypt
from app.models.employee import Employee
from app.models.enums import UserRole
from app.models.user import User


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--first-name", prompt=True, default="Admin")
    @click.option("--last-name", prompt=True, default="User")
    def create_admin(email, password, first_name, last_name):
        """Bootstrap the first admin account (run once, in a trusted context)."""
        if User.query.filter_by(email=email).first():
            click.echo("A user with this email already exists.")
            return

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(email=email, password_hash=password_hash, role=UserRole.ADMIN)
        db.session.add(user)
        db.session.commit()

        employee = Employee(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            date_joined=datetime.date.today(),
        )
        db.session.add(employee)
        db.session.commit()

        click.echo(f"Admin user created: {email}")
