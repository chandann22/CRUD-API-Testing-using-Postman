/* =======================================================
   login.js - handles the login form and JWT storage
   ======================================================= */

const API_BASE_URL = window.location.origin; // Flask serves API + frontend on the same origin

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

// If already logged in, skip straight to the dashboard
if (sessionStorage.getItem("ems_token")) {
  window.location.href = "index.html";
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.textContent = "";

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    loginError.textContent = "Please enter both username and password";
    return;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      loginError.textContent = data.message || "Login failed. Please try again.";
      return;
    }

    // Store JWT for this demo session (sessionStorage is fine for a college project)
    sessionStorage.setItem("ems_token", data.access_token);
    sessionStorage.setItem("ems_username", data.username);

    window.location.href = "index.html";
  } catch (err) {
    loginError.textContent = "Could not reach the server. Is the Flask API running on port 5000?";
  }
});
