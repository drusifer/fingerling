# Sprint 4: "Controlled Exposure Sandbox (Vaccination)"

This document combines **User Stories** and **Architecture Design** for Sprint 4.

*   **Total Points**: 13 Story Points
*   **Target Scenario**: An unsanitized input field in a local target app exploited via benign command injection.

---

## 📋 User Stories & Acceptance Criteria

### STORY-FING-13: Sandbox Environment Scaffolding
**Points:** 4 · **Epic:** Sequence Trajectory Enforcement
**Role:** DevSecOps Engineer

**As a** DevSecOps Engineer,
**I want** a module to provision and launch a target application process in an isolated environment,
**so that** I can contain the execution context during offensive testing.

#### Acceptance Criteria
1. Function `fingerling.sandbox.run_in_sandbox(command: list[str], cgroup_name: str | None = None) -> subprocess.Popen`:
   - Launches a target process using `subprocess.Popen`.
   - If `cgroup_name` is provided, attempts to write the process PID to `/sys/fs/cgroup/<cgroup_name>/cgroup.procs`.
   - Falls back gracefully to process isolation (plain subprocess execution) if running without root or if cgroup directory does not exist, logging a warning rather than crashing.

---

### STORY-FING-14: Vulnerable Target Application with Unsanitized Input
**Points:** 3 · **Epic:** Behavioral Tokenization Infrastructure
**Role:** Core Security Engineer

**As a** Core Security Engineer,
**I want** a minimal vulnerable application containing an unsanitized input field,
**so that** I can trigger a command injection exploit under controlled conditions.

#### Acceptance Criteria
1. A runnable application `examples/vulnerable_app.py` implementing a standard library HTTP server.
2. Exposes an endpoint `/ping?host=<ip>` which executes `ping -c 1 {host}` using shell execution (`shell=True` in subprocess).
3. If `host` contains shell metacharacters (e.g. `127.0.0.1; whoami`), it executes the command injection.
4. Accepts a `--port` argument to bind to a specific port.

---

### STORY-FING-15: Controlled Exposure (Vaccine) Replay Engine
**Points:** 3 · **Epic:** Sequence Trajectory Enforcement
**Role:** DevSecOps Automation Specialist

**As a** DevSecOps Automation Specialist,
**I want** a vaccination engine to simulate baseline traffic and benign exploits against the vulnerable application,
**so that** the pipeline can build a whitelist and capture anomaly signatures automatically.

#### Acceptance Criteria
1. Function `fingerling.vaccine.run_vaccination(app_port: int, webhook_url: str) -> dict`:
   - Sends baseline requests (e.g. `host=127.0.0.1`) to the vulnerable application.
   - Streams the resulting telemetry to `webhook_url`.
   - Sends a benign exploit request (e.g. `host=127.0.0.1;whoami`) to trigger command injection telemetry, streaming it to `webhook_url`.
   - Returns a status dictionary detailing the baseline and exploit request outcomes.

---

### STORY-FING-16: End-to-End Vaccination & GitOps Verification
**Points:** 3 · **Epic:** Automated GitOps Delivery
**Role:** DevSecOps Automation Specialist

**As a** DevSecOps Automation Specialist,
**I want** an integration test verifying the entire closed-loop vaccination pipeline,
**so that** I can guarantee anomalies are detected and delivered to GitOps automatically.

#### Acceptance Criteria
1. An integration test in `tests/test_vaccination.py` that:
   - Starts the Webhook server (linked to a temp GitOps repo).
   - Starts the vulnerable application.
   - Runs `run_vaccination` baseline and exploit sequences.
   - Asserts that the anomalous `whoami` trajectory is detected.
   - Asserts that a KubeArmorPolicy manifest is successfully committed and merged into the GitOps repository.

---

## 🛠️ Architecture & Technical Design

### Closed-Loop Vaccination Architecture

```
                                 [ 1. Baseline Request ]
                                           │
                                           ▼
 [ Webhook Server ] ◄───Telemetry─── [ Sandbox ] ───Executes──► [ Vulnerable App ]
        │                                  ▲
        ▼ (Anomaly Detected)               │
 [ GitOps merge ] ─────────────────────────┘
 (KubeArmorPolicy blocks whoami execution)
```
