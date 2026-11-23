# Employee Management System + API Testing & Automation

A full-stack **Employee Management System** built as a **Software Testing / API Testing** college project. It combines a working Flask REST API, a vanilla HTML/CSS/JS frontend, a SQLite database, and a complete **Postman + Newman** automated test suite that can be triggered with **one click** from a browser page.

---

## 1. Project Overview

This project demonstrates a real, working system — not a mock:

- A Flask REST API backed by SQLite (via SQLAlchemy) for full employee CRUD.
- JWT-based authentication protecting the employee endpoints.
- A clean vanilla JS frontend (login page + dashboard) that talks to the API.
- A 31-request Postman collection covering positive and negative test cases.
- A Node.js server that runs the Postman collection through **Newman** and generates a real HTML test report.
- A one-click `test-runner.html` page that starts the whole Newman run and shows live PASS/FAIL results.

---

## 2. Features

- Login with JWT (`admin` / `admin123` demo account, seeded automatically)
- Full Employee CRUD (Create, Read, Read-all, Update, Delete)
- Frontend + backend input validation (name, email, phone, salary, dates, duplicate emails)
- Proper HTTP status codes (200, 201, 400, 401, 404, 409, 500)
- 31 automated Postman test cases (auth, CRUD, positive + negative)
- One-click **RUN ALL TEST CASES** button — no manual Postman clicking required
- Auto-generated HTML test report (`newman-reporter-htmlextra`)
- Clickable server URLs printed straight in the VS Code terminal on startup

---

## 3. Technology Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Frontend       | HTML5, CSS3, Vanilla JavaScript                |
| Backend        | Python, Flask, Flask-JWT-Extended, Flask-CORS  |
| Database       | SQLite + SQLAlchemy ORM                        |
| API Testing    | Postman (collection + environment)             |
| Automation     | Newman + newman-reporter-htmlextra (via Node.js/Express) |

---

## 4. Project Architecture

```
test-runner.html
      |
Node.js test runner (Express, port 3000)
      |
   Newman
      |
Postman Collection
      |
Flask API (port 5000)
      |
SQLite Database
      |
HTML Report (automation/reports/postman-report.html)
```

The Flask server ALSO serves the frontend (`login.html`, `index.html`) as static files on port 5000, so the entire app — API + UI — runs from one process.

---

## 5. Folder Structure

```
Employee-Management-System/
├── backend/
│   ├── app.py              # Flask app, routes, static frontend serving
│   ├── database.py         # SQLite/SQLAlchemy setup + auto-seed admin user
│   ├── models.py           # User & Employee models
│   ├── auth.py             # /api/login blueprint
│   ├── validators.py       # Server-side validation rules
│   ├── requirements.txt
│   └── employee.db         # created automatically on first run
│
├── frontend/
│   ├── login.html
│   ├── index.html          # dashboard
│   ├── employees.html      # alias of the dashboard
│   ├── css/style.css
│   └── js/
│       ├── login.js
│       └── employees.js
│
├── automation/
│   ├── test-runner.html    # one-click UI
│   ├── test-runner.js      # Node/Express server that drives Newman
│   └── reports/
│       └── postman-report.html   # generated after you click "RUN ALL TEST CASES"
│
├── postman/
│   ├── Employee-Management.postman_collection.json
│   ├── Employee-Management.postman_environment.json
│   └── generate_postman.py       # script used to generate the collection (reference only)
│
├── package.json
├── README.md
└── .gitignore
```

---

## 6. Installation Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+ and npm
- (Optional) Postman desktop app, if you want to run tests manually too

### Python environment setup

```bash
cd backend
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Node.js dependency installation

From the **project root** (not inside `backend/`):

```bash
npm install
```

This installs `express`, `cors`, `newman`, and `newman-reporter-htmlextra`.

---

## 7. Running the Project

Open **two terminals** in VS Code.

### Terminal 1 — start the Flask API + frontend

```bash
cd backend
python app.py
```

You'll see something like:

```
============================================================
 Employee Management System - Backend API
============================================================
 API base URL     : http://127.0.0.1:5000
 Login page       : http://127.0.0.1:5000/login.html
 Dashboard        : http://127.0.0.1:5000/index.html
 Demo credentials : admin / admin123
============================================================
```

VS Code's integrated terminal automatically turns those `http://` lines into clickable links — **Ctrl/Cmd+Click `http://127.0.0.1:5000/login.html`** to open the login page directly in your browser.

### Terminal 2 — start the test automation server

From the **project root**:

```bash
npm start
```

or

```bash
node automation/test-runner.js
```

You'll see:

```
============================================================
 Employee Management - Test Automation Server
============================================================
 Test Runner UI  : http://localhost:3000/test-runner.html
 Status endpoint : http://localhost:3000/test-status
============================================================
```

Again, Ctrl/Cmd+Click the `Test Runner UI` link to jump straight to `test-runner.html`.

---

## 8. How to Import the Postman Collection (manual testing, optional)

1. Open Postman.
2. Click **Import** → select both files from the `postman/` folder:
   - `Employee-Management.postman_collection.json`
   - `Employee-Management.postman_environment.json`
3. Select **Employee Management Environment** from the environment dropdown (top-right).
4. Make sure `base_url` is `http://127.0.0.1:5000` and the Flask API is running.

## 9. How to Run Tests Manually in Postman

1. Run **"1. Valid Login"** first — it automatically saves the JWT into `{{token}}`.
2. Run **"9. Create Employee With Valid Data"** — it automatically saves the new employee's ID into `{{employee_id}}`.
3. Run any other request individually, or click **Run collection** to execute the whole folder tree with Postman's built-in Collection Runner.

## 10. How to Run All Tests Using `test-runner.html`

1. Make sure **both** servers are running (Flask on 5000, the Node runner on 3000).
2. Open `http://localhost:3000/test-runner.html`.
3. Click **▶ RUN ALL TEST CASES**.
4. The page calls `POST /run-tests` on the Node server, which runs the entire Postman collection through Newman (login → create → read → update → delete, in order, using the shared environment).
5. The page polls `GET /test-status` every ~1.2s and updates the live status, total/passed/failed counts, and per-category breakdown until Newman finishes.
6. Once complete, click **📄 VIEW HTML REPORT** to open the generated report in a new tab.

## 11. How to View the Generated HTML Report

The report is written to `automation/reports/postman-report.html` and served at:

```
http://localhost:3000/reports/postman-report.html
```

It's also directly reachable through the **VIEW HTML REPORT** button after a run completes.

---

## 12. API Endpoint Documentation

| Method | Endpoint              | Auth required | Description                     |
|--------|------------------------|:--------------:|----------------------------------|
| POST   | `/api/login`            | No             | Authenticate, returns JWT        |
| GET    | `/api/employees`        | Yes            | List all employees               |
| POST   | `/api/employees`        | Yes            | Create a new employee            |
| GET    | `/api/employees/<id>`   | Yes            | Get a single employee            |
| PUT    | `/api/employees/<id>`   | Yes            | Update an employee                |
| DELETE | `/api/employees/<id>`   | Yes            | Delete an employee                |
| GET    | `/api/health`           | No             | Simple health check               |

All protected endpoints require: `Authorization: Bearer <token>`

---

## 13. Test Case Documentation (31 automated tests)

**Authentication Tests (8):** Valid Login, Invalid Username, Invalid Password, Missing Username, Missing Password, Empty Login Request, Protected API Without Token, Invalid Token

**CREATE Employee Tests (12):** Valid Data, Blank Name, Blank Email, Invalid Email, Invalid Phone, Negative Salary, Zero Salary, Missing Department, Missing Designation, Missing Required Fields, Duplicate Email (+ setup request)

**READ Tests (5):** Get All Employees, Get Employee By Valid ID, Get Employee By Invalid ID, Get Employee By Non-existing ID, Get Employees Without Authentication

**UPDATE Tests (4):** Valid Data, Invalid Email, Negative Salary, Non-existing Employee

**DELETE Tests (2):** Delete Existing Employee, Delete Non-existing Employee

## 14. Expected Positive/Negative Results

- **Positive tests** (valid login, valid create/update/delete/read) are expected to return `200`/`201` and are marked **PASS** when the API returns exactly that.
- **Negative tests** (blank fields, invalid formats, missing auth, non-existing IDs, duplicate emails) are expected to return `400`/`401`/`404`/`409`. A negative test is marked **PASS** precisely when the API correctly *rejects* the bad input with the expected error code — e.g. `Invalid Email → Expected 400 → Actual 400 → PASS`.

---

## 15. Demo Steps for Presenting to a Teacher

1. Start both servers (Terminal 1: Flask, Terminal 2: Node runner).
2. Open the login page, log in with `admin` / `admin123`.
3. **Demo 1 — valid data:** Click "Add Employee", fill in Rahul Sharma's details from the form, save. Show the new row in the table and the updated dashboard stats.
4. Open `test-runner.html`, click **RUN ALL TEST CASES**. Show the live status changing from *Ready* → *Running Tests...* → *Tests Completed*, with 31/31 passing.
5. Open the generated HTML report and walk through a few PASS rows.
6. **Demo 2 — invalid data:** Back on the dashboard, try adding an employee with a blank name, `abc` as email, `123` as phone, and `-5000` salary. Show the frontend validation errors.
7. Re-run **RUN ALL TEST CASES** and point out the negative test rows in the report (e.g. "Invalid Email should return 400") showing **PASS**, proving the API correctly rejects bad input.

---

## 16. Common Errors & Solutions

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Activate the virtual environment and re-run `pip install -r requirements.txt` inside `backend/`. |
| Node runner shows `ECONNREFUSED` when tests run | The Flask API isn't running — start `python app.py` in `backend/` first. |
| `test-runner.html` shows "Could not reach the test runner server" | Start the Node server: `npm start` from the project root. |
| Postman/Newman requests fail with 401 everywhere | Run the "Valid Login" request first (or click "RUN ALL TEST CASES", which always runs it first) so `{{token}}` gets populated. |
| Duplicate email test fails on a fresh database | This is expected on a brand-new database the very first time — the collection includes a setup request that creates the record before testing the duplicate rejection, so subsequent runs work correctly. |
| Port 5000 or 3000 already in use | Stop the other process using that port, or set `PORT=5050 python app.py` / `RUNNER_PORT=3001 node automation/test-runner.js`. |
| `employee.db` has stale/bad data | Stop the Flask server, delete `backend/employee.db`, and restart `python app.py` — it will be recreated automatically with a fresh admin user. |

---

## 17. Security Notes (kept intentionally simple for a demo)

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plain text).
- JWT authentication protects every employee endpoint.
- Password hashes are never returned in any API response.
- All database queries go through SQLAlchemy's ORM (parameterized — no raw SQL/SQL injection risk).
- CORS is enabled so the frontend, Postman, and Newman can all reach the API during local development.

This is a college demonstration project — the JWT secret key is hard-coded for simplicity and should be moved to an environment variable for any real deployment.
