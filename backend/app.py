"""
app.py
------
Main Flask application entry point for the Employee Management System.

Run with:
    python app.py

This starts the REST API on http://127.0.0.1:5000 AND serves the
frontend (login.html / index.html / employees.html) as static files
from the same server, so the whole app can be opened from one URL.
"""

import os
from datetime import timedelta

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)

from database import db, init_db
from models import Employee
from validators import validate_employee_payload
from auth import auth_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)  # allow the frontend / Postman / Newman to call the API freely

# --- Config ---
app.config["JWT_SECRET_KEY"] = "dev-secret-key-change-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)

jwt = JWTManager(app)
init_db(app)
app.register_blueprint(auth_bp)


# ---------------------------------------------------------------------
# JWT error handlers -> always return clean JSON with 401
# ---------------------------------------------------------------------
@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({"success": False, "message": "Missing or invalid authorization token"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"success": False, "message": "Invalid token"}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "message": "Token has expired"}), 401


# ---------------------------------------------------------------------
# Generic error handlers -> never leak raw Flask/Python errors
# ---------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": "Resource not found"}), 404
    # fall back to serving index.html for unknown frontend routes
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "message": "Internal server error"}), 500


# ---------------------------------------------------------------------
# Frontend static routes (so you can click links straight from VS Code)
# ---------------------------------------------------------------------
@app.route("/")
def serve_root():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/<path:filename>")
def serve_frontend_file(filename):
    # Only serve real files that exist in the frontend folder; otherwise
    # let Flask's normal routing / 404 handler take over for /api/*.
    full_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, filename)
    return not_found(None)


# ---------------------------------------------------------------------
# Employee CRUD API
# ---------------------------------------------------------------------
@app.route("/api/employees", methods=["POST"])
@jwt_required()
def create_employee():
    data = request.get_json(silent=True) or {}

    is_valid, errors = validate_employee_payload(data, partial=False)
    if not is_valid:
        return jsonify({"success": False, "message": errors[0], "errors": errors}), 400

    if Employee.query.filter_by(email=data["email"].strip()).first():
        return jsonify({"success": False, "message": "An employee with this email already exists"}), 409

    employee = Employee(
        name=str(data["name"]).strip(),
        email=str(data["email"]).strip(),
        phone=str(data["phone"]).strip(),
        department=str(data["department"]).strip(),
        designation=str(data["designation"]).strip(),
        salary=float(data["salary"]),
        joining_date=str(data["joining_date"]).strip(),
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Employee created successfully",
        "employee": employee.to_dict()
    }), 201


@app.route("/api/employees", methods=["GET"])
@jwt_required()
def get_employees():
    employees = Employee.query.order_by(Employee.id.asc()).all()
    return jsonify({
        "success": True,
        "count": len(employees),
        "employees": [e.to_dict() for e in employees]
    }), 200


@app.route("/api/employees/<int:employee_id>", methods=["GET"])
@jwt_required()
def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if employee is None:
        return jsonify({"success": False, "message": "Employee not found"}), 404
    return jsonify({"success": True, "employee": employee.to_dict()}), 200


@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
@jwt_required()
def update_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if employee is None:
        return jsonify({"success": False, "message": "Employee not found"}), 404

    data = request.get_json(silent=True) or {}

    is_valid, errors = validate_employee_payload(data, partial=True)
    if not is_valid:
        return jsonify({"success": False, "message": errors[0], "errors": errors}), 400

    # Duplicate email check (excluding this employee's own record)
    if "email" in data:
        existing = Employee.query.filter(
            Employee.email == data["email"].strip(),
            Employee.id != employee_id
        ).first()
        if existing:
            return jsonify({"success": False, "message": "An employee with this email already exists"}), 409

    for field in ["name", "email", "phone", "department", "designation", "joining_date"]:
        if field in data:
            setattr(employee, field, str(data[field]).strip())

    if "salary" in data:
        employee.salary = float(data["salary"])

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Employee updated successfully",
        "employee": employee.to_dict()
    }), 200


@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
@jwt_required()
def delete_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if employee is None:
        return jsonify({"success": False, "message": "Employee not found"}), 404

    db.session.delete(employee)
    db.session.commit()

    return jsonify({"success": True, "message": "Employee deleted successfully"}), 200


# Handle non-integer employee IDs gracefully (e.g. /api/employees/abc) -> 404
@app.route("/api/employees/<employee_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def invalid_employee_id(employee_id):
    return jsonify({"success": False, "message": "Invalid employee ID"}), 404


# ---------------------------------------------------------------------
# Health check (handy for Postman / Newman pre-flight checks)
# ---------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"success": True, "message": "API is running"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "127.0.0.1"

    print("\n" + "=" * 60)
    print(" Employee Management System - Backend API")
    print("=" * 60)
    print(f" API base URL     : http://{host}:{port}")
    print(f" Login page       : http://{host}:{port}/login.html")
    print(f" Dashboard        : http://{host}:{port}/index.html")
    print(" Demo credentials : admin / admin123")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=True)
