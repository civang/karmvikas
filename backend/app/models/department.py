from app.extensions import db
from app.models.base import TimestampMixin


class Department(db.Model, TimestampMixin):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)

    designations = db.relationship("Designation", back_populates="department")
    employees = db.relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"


class Designation(db.Model, TimestampMixin):
    __tablename__ = "designations"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False, index=True)

    department = db.relationship("Department", back_populates="designations")
    employees = db.relationship("Employee", back_populates="designation")

    __table_args__ = (db.UniqueConstraint("title", "department_id", name="uq_designation_title_department"),)

    def __repr__(self):
        return f"<Designation {self.title}>"
