"""
database.py
------------
Handles SQLite database configuration and initialization.
The database file (employee.db) is created automatically the first
time the application runs -- no manual setup required.
"""

import os
from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance used across the app
db = SQLAlchemy()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "employee.db")


def init_db(app):
    """Configure SQLAlchemy on the given Flask app and create tables."""
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        # Import models here so SQLAlchemy knows about them before create_all
        from models import User, Employee  # noqa: F401

        db.create_all()
        _seed_default_admin()


def _seed_default_admin():
    """Create a demo admin user (admin / admin123) if none exists yet."""
    from models import User

    if User.query.filter_by(username="admin").first() is None:
        admin = User(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Seeded default admin user -> username: admin | password: admin123")
