"""
auth.py
-------
Authentication routes. Implements JWT-based login using
Flask-JWT-Extended.

Demo credentials (seeded automatically in database.py):
    username: admin
    password: admin123
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from models import User
from validators import validate_login_payload

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    is_valid, errors = validate_login_payload(data)
    if not is_valid:
        return jsonify({"success": False, "message": errors[0], "errors": errors}), 400

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.username)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "username": user.username
    }), 200
