"""
generate_postman.py
--------------------
One-off generator script used to build the Postman collection and
environment JSON files for the Employee Management API.

You do NOT need to run this again -- the generated files are already
committed in this folder. It's kept here for transparency / in case
you want to add more test cases later.

Run with: python3 generate_postman.py
"""

import json
import uuid

COLLECTION_NAME = "Employee Management API - Automation"
BASE_URL = "http://127.0.0.1:5000"


def uid():
    return str(uuid.uuid4())


def header(auth=True, content_type=True):
    h = []
    if content_type:
        h.append({"key": "Content-Type", "value": "application/json", "type": "text"})
    if auth:
        h.append({"key": "Authorization", "value": "Bearer {{token}}", "type": "text"})
    return h


def url(path):
    full = "{{base_url}}" + path
    parts = [p for p in path.split("/") if p]
    return {"raw": full, "host": ["{{base_url}}"], "path": parts}


def body(obj):
    return {
        "mode": "raw",
        "raw": json.dumps(obj, indent=2),
        "options": {"raw": {"language": "json"}}
    }


def test_script(lines):
    return [{
        "listen": "test",
        "script": {"id": uid(), "type": "text/javascript", "exec": lines}
    }]


def request(name, method, path, expect_status, test_name, extra_test_lines=None,
            payload=None, auth=True, capture_token=False, capture_id=False,
            no_content_type=False):
    lines = [
        f"pm.test(\"{test_name}\", function () {{",
        f"    pm.response.to.have.status({expect_status});",
        "});",
        "",
        "pm.test(\"Response is valid JSON\", function () {",
        "    pm.response.to.be.json;",
        "});"
    ]

    if capture_token:
        lines += [
            "",
            "if (pm.response.code === 200) {",
            "    var jsonData = pm.response.json();",
            "    pm.test(\"Access token is present\", function () {",
            "        pm.expect(jsonData.access_token).to.exist;",
            "    });",
            "    pm.environment.set(\"token\", jsonData.access_token);",
            "}"
        ]

    if capture_id:
        lines += [
            "",
            "if (pm.response.code === 201) {",
            "    var jsonData = pm.response.json();",
            "    pm.test(\"Employee object returned with an ID\", function () {",
            "        pm.expect(jsonData.employee.id).to.exist;",
            "    });",
            "    pm.environment.set(\"employee_id\", jsonData.employee.id);",
            "}"
        ]

    if extra_test_lines:
        lines += [""] + extra_test_lines

    item = {
        "name": name,
        "event": test_script(lines),
        "request": {
            "method": method,
            "header": header(auth=auth, content_type=(not no_content_type)),
            "url": url(path)
        },
        "response": []
    }
    if payload is not None:
        item["request"]["body"] = body(payload)

    return item


# =====================================================================
# 1. AUTHENTICATION TESTS
# =====================================================================
auth_tests = [
    request(
        "1. Valid Login", "POST", "/api/login", 200,
        "Status code should be 200",
        payload={"username": "admin", "password": "admin123"},
        auth=False, capture_token=True
    ),
    request(
        "2. Invalid Username", "POST", "/api/login", 401,
        "Invalid username should return 401",
        payload={"username": "wronguser", "password": "admin123"},
        auth=False
    ),
    request(
        "3. Invalid Password", "POST", "/api/login", 401,
        "Invalid password should return 401",
        payload={"username": "admin", "password": "wrongpass"},
        auth=False
    ),
    request(
        "4. Missing Username", "POST", "/api/login", 400,
        "Missing username should return 400",
        payload={"password": "admin123"},
        auth=False
    ),
    request(
        "5. Missing Password", "POST", "/api/login", 400,
        "Missing password should return 400",
        payload={"username": "admin"},
        auth=False
    ),
    request(
        "6. Empty Login Request", "POST", "/api/login", 400,
        "Empty login body should return 400",
        payload={},
        auth=False
    ),
    request(
        "7. Protected API Without Token", "GET", "/api/employees", 401,
        "Request without token should return 401",
        auth=False
    ),
    {
        "name": "8. Invalid Token",
        "event": test_script([
            "pm.test(\"Invalid token should return 401\", function () {",
            "    pm.response.to.have.status(401);",
            "});"
        ]),
        "request": {
            "method": "GET",
            "header": [
                {"key": "Content-Type", "value": "application/json"},
                {"key": "Authorization", "value": "Bearer this.is.not.a.valid.jwt.token"}
            ],
            "url": url("/api/employees")
        },
        "response": []
    }
]

# =====================================================================
# 2. CREATE EMPLOYEE TESTS
# =====================================================================
valid_employee = {
    "name": "Rahul Sharma",
    "email": "rahul.sharma.{{$randomInt}}@gmail.com",
    "phone": "9876543210",
    "department": "IT",
    "designation": "Software Engineer",
    "salary": 50000,
    "joining_date": "2026-09-21"
}

create_tests = [
    request(
        "9. Create Employee With Valid Data", "POST", "/api/employees", 201,
        "Status code should be 201",
        payload=valid_employee, capture_id=True
    ),
    request(
        "10. Create Employee With Blank Name", "POST", "/api/employees", 400,
        "Blank name should return 400",
        payload={**valid_employee, "name": "", "email": "blankname@gmail.com"}
    ),
    request(
        "11. Create Employee With Blank Email", "POST", "/api/employees", 400,
        "Blank email should return 400",
        payload={**valid_employee, "email": ""}
    ),
    request(
        "12. Create Employee With Invalid Email", "POST", "/api/employees", 400,
        "Invalid email should return 400",
        payload={**valid_employee, "email": "abc"}
    ),
    request(
        "13. Create Employee With Invalid Phone", "POST", "/api/employees", 400,
        "Invalid phone should return 400",
        payload={**valid_employee, "email": "invalidphone@gmail.com", "phone": "123"}
    ),
    request(
        "14. Create Employee With Negative Salary", "POST", "/api/employees", 400,
        "Negative salary should return 400",
        payload={**valid_employee, "email": "negsalary@gmail.com", "salary": -5000}
    ),
    request(
        "15. Create Employee With Zero Salary", "POST", "/api/employees", 400,
        "Zero salary should return 400",
        payload={**valid_employee, "email": "zerosalary@gmail.com", "salary": 0}
    ),
    request(
        "16. Create Employee With Missing Department", "POST", "/api/employees", 400,
        "Missing department should return 400",
        payload={k: v for k, v in valid_employee.items() if k != "department"} | {"email": "missingdept@gmail.com"}
    ),
    request(
        "17. Create Employee With Missing Designation", "POST", "/api/employees", 400,
        "Missing designation should return 400",
        payload={k: v for k, v in valid_employee.items() if k != "designation"} | {"email": "missingdesig@gmail.com"}
    ),
    request(
        "18. Create Employee With Missing Required Fields", "POST", "/api/employees", 400,
        "Missing required fields should return 400",
        payload={"name": "Incomplete Employee"}
    ),
    request(
        "19. Create Employee With Duplicate Email", "POST", "/api/employees", 409,
        "Duplicate email should return 409",
        payload={**valid_employee, "email": "admin.duplicate@gmail.com"},
        extra_test_lines=None
    ),
]

# The duplicate-email test needs to run the SAME create twice; we insert
# a companion "setup" request right before it that creates the record once.
duplicate_setup = request(
    "19a. Create Employee For Duplicate Test (Setup)", "POST", "/api/employees", 201,
    "Setup employee created (201) or already exists",
    payload={**valid_employee, "email": "admin.duplicate@gmail.com"}
)
# Relax setup assertion so re-runs of the collection don't fail this step
duplicate_setup["event"][0]["script"]["exec"] = [
    "pm.test(\"Setup request completes\", function () {",
    "    pm.expect([201, 409]).to.include(pm.response.code);",
    "});"
]

create_tests.insert(len(create_tests) - 1, duplicate_setup)

# =====================================================================
# 3. READ TESTS
# =====================================================================
read_tests = [
    request(
        "20. Get All Employees", "GET", "/api/employees", 200,
        "Status code should be 200",
        extra_test_lines=[
            "pm.test(\"Response contains employees array\", function () {",
            "    var jsonData = pm.response.json();",
            "    pm.expect(jsonData.employees).to.be.an('array');",
            "});"
        ]
    ),
    request(
        "21. Get Employee By Valid ID", "GET", "/api/employees/{{employee_id}}", 200,
        "Status code should be 200",
        extra_test_lines=[
            "pm.test(\"Returned employee has correct ID\", function () {",
            "    var jsonData = pm.response.json();",
            "    pm.expect(String(jsonData.employee.id)).to.eql(pm.environment.get(\"employee_id\").toString());",
            "});"
        ]
    ),
    request(
        "22. Get Employee By Invalid ID", "GET", "/api/employees/abc123", 404,
        "Invalid ID format should return 404"
    ),
    request(
        "23. Get Employee By Non-existing ID", "GET", "/api/employees/999999", 404,
        "Non-existing ID should return 404"
    ),
    request(
        "24. Get Employees Without Authentication", "GET", "/api/employees", 401,
        "Unauthenticated request should return 401",
        auth=False
    ),
]

# =====================================================================
# 4. UPDATE TESTS
# =====================================================================
update_tests = [
    request(
        "25. Update Employee With Valid Data", "PUT", "/api/employees/{{employee_id}}", 200,
        "Status code should be 200",
        payload={"designation": "Senior Software Engineer", "salary": 65000}
    ),
    request(
        "26. Update Employee With Invalid Email", "PUT", "/api/employees/{{employee_id}}", 400,
        "Invalid email should return 400",
        payload={"email": "not-an-email"}
    ),
    request(
        "27. Update Employee With Negative Salary", "PUT", "/api/employees/{{employee_id}}", 400,
        "Negative salary should return 400",
        payload={"salary": -1000}
    ),
    request(
        "28. Update Non-existing Employee", "PUT", "/api/employees/999999", 404,
        "Updating non-existing employee should return 404",
        payload={"salary": 70000}
    ),
]

# =====================================================================
# 5. DELETE TESTS
# =====================================================================
delete_tests = [
    request(
        "29. Delete Existing Employee", "DELETE", "/api/employees/{{employee_id}}", 200,
        "Status code should be 200"
    ),
    request(
        "30. Delete Non-existing Employee", "DELETE", "/api/employees/999999", 404,
        "Deleting non-existing employee should return 404"
    ),
]

collection = {
    "info": {
        "_postman_id": uid(),
        "name": COLLECTION_NAME,
        "description": "Automated API test suite for the Employee Management System. "
                        "Covers authentication, CRUD operations, and positive/negative "
                        "validation scenarios (30+ test cases).",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {"name": "Authentication Tests", "item": auth_tests},
        {"name": "CREATE Employee Tests", "item": create_tests},
        {"name": "READ Tests", "item": read_tests},
        {"name": "UPDATE Tests", "item": update_tests},
        {"name": "DELETE Tests", "item": delete_tests},
    ]
}

environment = {
    "id": uid(),
    "name": "Employee Management Environment",
    "values": [
        {"key": "base_url", "value": BASE_URL, "type": "default", "enabled": True},
        {"key": "token", "value": "", "type": "secret", "enabled": True},
        {"key": "employee_id", "value": "", "type": "default", "enabled": True},
    ],
    "_postman_variable_scope": "environment"
}

with open("Employee-Management.postman_collection.json", "w") as f:
    json.dump(collection, f, indent=2)

with open("Employee-Management.postman_environment.json", "w") as f:
    json.dump(environment, f, indent=2)

total = len(auth_tests) + len(create_tests) + len(read_tests) + len(update_tests) + len(delete_tests)
print(f"Generated collection with {total} requests (excluding folder nodes).")
