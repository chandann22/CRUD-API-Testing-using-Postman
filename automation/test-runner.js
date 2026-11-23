/**
 * test-runner.js
 * ----------------
 * Small Node.js/Express server that bridges the browser (test-runner.html)
 * with Newman (the Postman CLI runner), because a browser cannot execute
 * a Newman process directly.
 *
 * Architecture:
 *   test-runner.html --fetch()--> this server --> Newman --> Postman
 *   collection --> Flask API --> SQLite --> HTML report
 *
 * Run with:
 *   node automation/test-runner.js
 * or:
 *   npm start
 */

const path = require("path");
const express = require("express");
const cors = require("cors");
const newman = require("newman");

const app = express();
const PORT = process.env.RUNNER_PORT || 3000;

const ROOT_DIR = path.join(__dirname, "..");
const COLLECTION_PATH = path.join(ROOT_DIR, "postman", "Employee-Management.postman_collection.json");
const ENVIRONMENT_PATH = path.join(ROOT_DIR, "postman", "Employee-Management.postman_environment.json");
const REPORTS_DIR = path.join(__dirname, "reports");
const REPORT_FILENAME = "postman-report.html";
const REPORT_PATH = path.join(REPORTS_DIR, REPORT_FILENAME);

app.use(cors());
app.use(express.json());

// Serve the test-runner UI and the generated reports as static files
app.use(express.static(__dirname));
app.use("/reports", express.static(REPORTS_DIR));

// ---------------------------------------------------------------------
// In-memory test execution state (shared between /run-tests and
// /test-status so the HTML page can poll for progress)
// ---------------------------------------------------------------------
let testState = {
  status: "idle", // idle | running | completed | failed | error
  total: 0,
  passed: 0,
  failed: 0,
  successRate: 0,
  startedAt: null,
  finishedAt: null,
  reportUrl: null,
  message: "Ready to run tests.",
  categories: {
    "Authentication Tests": { total: 0, passed: 0, failed: 0 },
    "CREATE Employee Tests": { total: 0, passed: 0, failed: 0 },
    "READ Tests": { total: 0, passed: 0, failed: 0 },
    "UPDATE Tests": { total: 0, passed: 0, failed: 0 },
    "DELETE Tests": { total: 0, passed: 0, failed: 0 }
  }
};

function resetCategoryCounts() {
  Object.keys(testState.categories).forEach((k) => {
    testState.categories[k] = { total: 0, passed: 0, failed: 0 };
  });
}

// ---------------------------------------------------------------------
// POST /run-tests -> triggers Newman to run the FULL Postman collection
// ---------------------------------------------------------------------
app.post("/run-tests", (req, res) => {
  if (testState.status === "running") {
    return res.status(409).json({ success: false, message: "Tests are already running." });
  }

  testState.status = "running";
  testState.message = "Running Tests...";
  testState.startedAt = new Date().toISOString();
  testState.finishedAt = null;
  testState.total = 0;
  testState.passed = 0;
  testState.failed = 0;
  testState.successRate = 0;
  resetCategoryCounts();

  // Respond immediately; the client polls /test-status for progress
  res.json({ success: true, message: "Test execution started." });

  newman.run(
    {
      collection: require(COLLECTION_PATH),
      environment: require(ENVIRONMENT_PATH),
      reporters: ["cli", "htmlextra"],
      reporter: {
        htmlextra: {
          export: REPORT_PATH,
          title: "Employee Management API - Automation Report",
          browserTitle: "Employee Management API Test Report"
        }
      }
    },
    (err, summary) => {
      testState.finishedAt = new Date().toISOString();

      if (err) {
        testState.status = "error";
        testState.message = `Newman failed to run: ${err.message}`;
        console.error("Newman run error:", err);
        return;
      }

      // Tally results per top-level folder (category)
      summary.run.executions.forEach((execution) => {
        const folderName = (execution.item && execution.item.parent && execution.item.parent().name)
          || guessCategory(execution.item.name);

        if (!testState.categories[folderName]) {
          testState.categories[folderName] = { total: 0, passed: 0, failed: 0 };
        }

        const assertions = execution.assertions || [];
        assertions.forEach((assertion) => {
          testState.categories[folderName].total += 1;
          if (assertion.error) {
            testState.categories[folderName].failed += 1;
          } else {
            testState.categories[folderName].passed += 1;
          }
        });
      });

      const stats = summary.run.stats.assertions;
      testState.total = stats.total;
      testState.passed = stats.total - stats.failed;
      testState.failed = stats.failed;
      testState.successRate = stats.total > 0
        ? Math.round(((stats.total - stats.failed) / stats.total) * 100)
        : 0;

      testState.status = "completed";
      testState.message = "Tests Completed";
      testState.reportUrl = `/reports/${REPORT_FILENAME}`;

      console.log(
        `\nNewman run finished -> Total: ${testState.total}, Passed: ${testState.passed}, Failed: ${testState.failed} (${testState.successRate}%)\n`
      );
    }
  );
});

function guessCategory(name) {
  if (/^\d+\./.test(name)) {
    const n = parseInt(name, 10);
    if (n <= 8) return "Authentication Tests";
    if (n <= 19) return "CREATE Employee Tests";
    if (n <= 24) return "READ Tests";
    if (n <= 28) return "UPDATE Tests";
    return "DELETE Tests";
  }
  return "Other";
}

// ---------------------------------------------------------------------
// GET /test-status -> current execution status / results
// ---------------------------------------------------------------------
app.get("/test-status", (req, res) => {
  res.json(testState);
});

// ---------------------------------------------------------------------
// Root convenience redirect
// ---------------------------------------------------------------------
app.get("/", (req, res) => {
  res.redirect("/test-runner.html");
});

app.listen(PORT, () => {
  const base = `http://localhost:${PORT}`;
  console.log("\n" + "=".repeat(60));
  console.log(" Employee Management - Test Automation Server");
  console.log("=".repeat(60));
  console.log(` Test Runner UI  : ${base}/test-runner.html`);
  console.log(` Status endpoint : ${base}/test-status`);
  console.log(" Make sure the Flask API is running on http://127.0.0.1:5000");
  console.log("=".repeat(60) + "\n");
});
