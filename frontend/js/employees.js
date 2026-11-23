/* =======================================================
   employees.js - Employee dashboard logic (CRUD + validation)
   ======================================================= */

const API_BASE_URL = window.location.origin;

const token = sessionStorage.getItem("ems_token");
const username = sessionStorage.getItem("ems_username");

if (!token) {
  window.location.href = "login.html";
}

document.getElementById("user-tag").textContent = username ? `Signed in as ${username}` : "";

// ---------- DOM references ----------
const tableBody = document.getElementById("employee-table-body");
const emptyState = document.getElementById("empty-state");
const modal = document.getElementById("employee-modal");
const modalTitle = document.getElementById("modal-title");
const employeeForm = document.getElementById("employee-form");

let employeesCache = [];

// ---------- Auth helper ----------
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

async function handleAuthFailure(res) {
  if (res.status === 401) {
    showToast("Please login again", "error");
    sessionStorage.clear();
    setTimeout(() => (window.location.href = "login.html"), 1200);
    return true;
  }
  return false;
}

// ---------- Toasts ----------
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

// ---------- Load employees ----------
async function loadEmployees() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/employees`, { headers: authHeaders() });
    if (await handleAuthFailure(res)) return;

    const data = await res.json();
    if (!res.ok || !data.success) {
      showToast(data.message || "Failed to load employees", "error");
      return;
    }

    employeesCache = data.employees;
    renderTable(employeesCache);
    renderStats(employeesCache);
  } catch (err) {
    showToast("Could not reach the server. Is the Flask API running?", "error");
  }
}

function renderStats(employees) {
  document.getElementById("stat-total").textContent = employees.length;
  document.getElementById("stat-active").textContent = employees.length; // all records are "active" in this demo
  const departments = new Set(employees.map((e) => e.department));
  document.getElementById("stat-departments").textContent = departments.size;
  const latest = employees[employees.length - 1];
  document.getElementById("stat-latest").textContent = latest ? latest.name : "-";
}

function renderTable(employees) {
  tableBody.innerHTML = "";
  emptyState.style.display = employees.length === 0 ? "block" : "none";

  employees.forEach((emp) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${emp.id}</td>
      <td>${escapeHtml(emp.name)}</td>
      <td>${escapeHtml(emp.email)}</td>
      <td>${escapeHtml(emp.phone)}</td>
      <td>${escapeHtml(emp.department)}</td>
      <td>${escapeHtml(emp.designation)}</td>
      <td>₹${Number(emp.salary).toLocaleString("en-IN")}</td>
      <td class="actions-cell">
        <button class="btn-secondary" onclick="openEditModal(${emp.id})">Edit</button>
        <button class="btn-danger" onclick="deleteEmployee(${emp.id})">Delete</button>
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- Modal handling ----------
document.getElementById("add-employee-btn").addEventListener("click", () => openAddModal());
document.getElementById("cancel-modal-btn").addEventListener("click", closeModal);
document.getElementById("clear-form-btn").addEventListener("click", () => employeeForm.reset());

function openAddModal() {
  modalTitle.textContent = "Add Employee";
  employeeForm.reset();
  document.getElementById("employee-id").value = "";
  clearFieldErrors();
  modal.classList.add("active");
}

window.openEditModal = function (id) {
  const emp = employeesCache.find((e) => e.id === id);
  if (!emp) return;

  modalTitle.textContent = "Edit Employee";
  clearFieldErrors();
  document.getElementById("employee-id").value = emp.id;
  document.getElementById("name").value = emp.name;
  document.getElementById("email").value = emp.email;
  document.getElementById("phone").value = emp.phone;
  document.getElementById("department").value = emp.department;
  document.getElementById("designation").value = emp.designation;
  document.getElementById("salary").value = emp.salary;
  document.getElementById("joining_date").value = emp.joining_date;

  modal.classList.add("active");
};

function closeModal() {
  modal.classList.remove("active");
}

// ---------- Frontend validation ----------
function clearFieldErrors() {
  document.querySelectorAll(".field-error").forEach((el) => (el.textContent = ""));
}

function validateForm(payload) {
  clearFieldErrors();
  let valid = true;

  const setErr = (field, msg) => {
    document.getElementById(`err-${field}`).textContent = msg;
    valid = false;
  };

  if (!payload.name.trim()) setErr("name", "Employee name is required");
  if (!payload.email.trim()) setErr("email", "Email is required");
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) setErr("email", "Invalid email address");

  if (!payload.phone.trim()) setErr("phone", "Phone number is required");
  else if (!/^\d{10}$/.test(payload.phone)) setErr("phone", "Phone number must be exactly 10 digits");

  if (!payload.department.trim()) setErr("department", "Department is required");
  if (!payload.designation.trim()) setErr("designation", "Designation is required");

  if (payload.salary === "" || isNaN(payload.salary)) setErr("salary", "Salary must be a valid number");
  else if (Number(payload.salary) <= 0) setErr("salary", "Salary must be greater than zero");

  if (!payload.joining_date) setErr("joining_date", "Joining date is required");

  return valid;
}

// ---------- Create / Update submit ----------
employeeForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const id = document.getElementById("employee-id").value;
  const payload = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    phone: document.getElementById("phone").value,
    department: document.getElementById("department").value,
    designation: document.getElementById("designation").value,
    salary: document.getElementById("salary").value,
    joining_date: document.getElementById("joining_date").value
  };

  if (!validateForm(payload)) return;

  const isEdit = Boolean(id);
  const url = isEdit ? `${API_BASE_URL}/api/employees/${id}` : `${API_BASE_URL}/api/employees`;
  const method = isEdit ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method,
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (await handleAuthFailure(res)) return;

    const data = await res.json();

    if (!res.ok || !data.success) {
      showToast(data.message || "Something went wrong", "error");
      return;
    }

    showToast(isEdit ? "Employee updated successfully" : "Employee added successfully", "success");
    closeModal();
    loadEmployees();
  } catch (err) {
    showToast("Could not reach the server", "error");
  }
});

// ---------- Delete ----------
window.deleteEmployee = async function (id) {
  if (!confirm("Are you sure you want to delete this employee?")) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/employees/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });
    if (await handleAuthFailure(res)) return;

    const data = await res.json();
    if (!res.ok || !data.success) {
      showToast(data.message || "Failed to delete employee", "error");
      return;
    }

    showToast("Employee deleted successfully", "success");
    loadEmployees();
  } catch (err) {
    showToast("Could not reach the server", "error");
  }
};

// ---------- Logout ----------
document.getElementById("logout-btn").addEventListener("click", () => {
  sessionStorage.clear();
  window.location.href = "login.html";
});

// ---------- Init ----------
loadEmployees();
