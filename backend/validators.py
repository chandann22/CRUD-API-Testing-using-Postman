"""
validators.py
--------------
Server-side input validation helpers for the Employee Management API.
The frontend also validates input, but the backend NEVER trusts the
client -- every rule here is re-checked on the server.
"""

import re
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\d{10}$")

REQUIRED_FIELDS = ["name", "email", "phone", "department", "designation", "salary", "joining_date"]


def validate_employee_payload(data, partial=False):
    """
    Validate an employee create/update payload.
    Returns (is_valid: bool, errors: list[str]).
    If `partial` is True, missing fields are allowed (used for PUT where
    the client may only send changed fields) -- but any field present
    is still fully validated.
    """
    errors = []

    if not isinstance(data, dict) or not data:
        return False, ["Request body must be a valid JSON object"]

    # Required field presence check (skipped in partial/update mode)
    if not partial:
        for field in REQUIRED_FIELDS:
            if field not in data or data.get(field) in (None, ""):
                errors.append(f"{field.replace('_', ' ').capitalize()} is required")

    # Name
    if "name" in data:
        name = str(data.get("name", "")).strip()
        if "name" in data and not name:
            errors.append("Employee name is required")

    # Email
    if "email" in data:
        email = str(data.get("email", "")).strip()
        if not email:
            errors.append("Email is required")
        elif not EMAIL_REGEX.match(email):
            errors.append("Invalid email format")

    # Phone
    if "phone" in data:
        phone = str(data.get("phone", "")).strip()
        if not phone:
            errors.append("Phone number is required")
        elif not PHONE_REGEX.match(phone):
            errors.append("Phone number must be exactly 10 digits")

    # Department
    if "department" in data:
        if not str(data.get("department", "")).strip():
            errors.append("Department is required")

    # Designation
    if "designation" in data:
        if not str(data.get("designation", "")).strip():
            errors.append("Designation is required")

    # Salary
    if "salary" in data:
        salary = data.get("salary")
        try:
            salary_val = float(salary)
            if salary_val <= 0:
                errors.append("Salary must be greater than zero")
        except (TypeError, ValueError):
            errors.append("Salary must be a valid number")

    # Joining date
    if "joining_date" in data:
        joining_date = str(data.get("joining_date", "")).strip()
        if not joining_date:
            errors.append("Joining date is required")
        else:
            try:
                datetime.strptime(joining_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Joining date must be in YYYY-MM-DD format")

    return (len(errors) == 0), errors


def validate_login_payload(data):
    errors = []
    if not isinstance(data, dict) or not data:
        return False, ["Request body must be a valid JSON object"]

    if not data.get("username"):
        errors.append("Username is required")
    if not data.get("password"):
        errors.append("Password is required")

    return (len(errors) == 0), errors
