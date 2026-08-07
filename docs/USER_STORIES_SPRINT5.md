# Sprint 5: "Interactive Split-Pane Terminal UX Demo"

This document combines **User Stories** and **Architecture Design** for Sprint 5.

*   **Total Points**: 8 Story Points
*   **Target Scenario**: An interactive terminal multiplexer demo utilizing `tmux` (with a single-terminal fallback) that guides the user step-by-step through Project Fingerling's closed-loop vaccination pipeline.

---

## 📋 User Stories & Acceptance Criteria

### STORY-FING-18: Interactive CLI Controller Script
**Points:** 4 · **Epic:** Interactive Usability & Visual Experience
**Role:** Developer Experience (DX) Specialist

**As a** Developer using Project Fingerling,
**I want** an interactive, step-by-step CLI demo controller that uses colors and emojis for emphasis,
**so that** I can easily follow and comprehend each stage of the closed-loop vaccination pipeline.

#### Acceptance Criteria
1. **Runnable Controller Script**: Create a runnable python script `examples/interactive_controller.py` that drives the demo steps.
2. **Interactive Prompts**: Prompts the user with `[Press Enter to continue...]` (or `[Continue...]`) before executing and explaining each step:
   - **Step 1**: Scaffolding the GitOps repository.
   - **Step 2**: Booting the Target App and Webhook Server.
   - **Step 3**: Sending baseline HTTP GET warmup traffic (using two actual HTTP pings).
   - **Step 4**: Executing the benign command injection exploit.
   - **Step 5**: Webhook anomaly detection and GitOps KubeArmorPolicy commit & auto-merge.
   - **Step 6**: Antibody deployment (shutting down undefended server and restarting with KubeArmor policy).
   - **Step 7**: Retriggering the exploit command injection and verifying it is BLOCKED.
   - **Step 8**: Verifying that normal baseline pings are still ALLOWED.
3. **Rich Aesthetics**: Emphasizes system status, actions, and results using ANSI terminal colors (green for success, red for blocked/failure, blue/yellow for info) and descriptive emojis (🛡️, 🚀, 🧪, 💉, 🔒, 🟢).
4. **Parameterizable Interface**: Accepts arguments for app port, webhook port, and GitOps repo path, allowing it to be run standalone or dynamically driven inside multiplexer panes.
5. **Robust Cleanup**: Gracefully shuts down any spawned background components (if run in standalone mode) or logs diagnostic completion steps on exit.

---

### STORY-FING-19: Multi-Pane Terminal Multiplexer Scaffolding
**Points:** 4 · **Epic:** Interactive Usability & Visual Experience
**Role:** DevSecOps Tooling Engineer

**As a** Security Engineer evaluating Project Fingerling,
**I want** to see the Target App logs, Webhook server logs, GitOps commit status, and interactive controller in separate, simultaneous terminal frames,
**so that** I have full visibility of the system status during the demo.

#### Acceptance Criteria
1. **Shell Launcher**: Create a launcher script `examples/run_interactive_demo.sh` (or `examples/tmux_demo.sh`) that manages environment setup.
2. **Tmux Check & Session Scaffolding**:
   - Checks if `tmux` is installed.
   - If `tmux` is available:
     - Sets up random/free ports for the App and Webhook.
     - Creates a temporary GitOps repository directory.
     - Spawns a detached `tmux` session named `fingerling-demo`.
     - Splits the session window into 4 panes:
       - **Pane 0 (Top-Left)**: Displays the `interactive_controller.py` script to guide the user.
       - **Pane 1 (Bottom-Left)**: Launches and shows stdout/stderr logs from `examples/vulnerable_app.py`.
       - **Pane 2 (Bottom-Right)**: Launches and shows stdout/stderr logs from the Telemetry Webhook Server.
       - **Pane 3 (Right Column)**: Displays real-time GitOps activity (e.g., watching directory files or displaying `git log --oneline --graph --all` in a loop).
     - Standardizes session cleanup: when the controller script in Pane 0 exits, the launcher terminates the `tmux` session and kills the spawned processes.
3. **Graceful Fallback Mode**:
   - If `tmux` is NOT available:
     - Warns the user about the missing multiplexer.
     - Falls back to running `interactive_controller.py` directly in the current terminal window.
     - Spawns target servers in background daemon threads (redirecting logs to a temporary file), still offering the interactive colored step-through prompts but in a single-terminal view.
4. **Integration with Build Automation**:
   - Add a `make demo-interactive` target in the project root `Makefile` to trigger the launcher script.

---

## 🛠️ Architecture & Technical Design

### Interactive Multiplexer Layout

When `tmux` is available, the terminal workspace is divided into active, isolated zones:

```
+-------------------------------------------------------------+
|                                                             |
|                   1. Main Controller Pane                   |
|  Runs `interactive_controller.py`                           |
|  - Renders user prompts, explanations, colors, emojis.       |
|  - Drives HTTP request injections and baseline traffic.     |
|  - [Press Enter to continue...]                             |
|                                                             |
+------------------------------+------------------------------+
|                              |                              |
|     2. Target Application    |   3. Telemetry Webhook       |
|  Runs `vulnerable_app.py`    |  Runs `fingerling.server`    |
|  - Prints HTTP server logs.  |  - Prints anomaly telemetry. |
|  - Shows exploit injection.  |  - Logs GitOps commits.      |
|                              |                              |
+------------------------------+------------------------------+
|                                                             |
|                     4. GitOps Repository                    |
|  Monitors `policies/` files and prints git status.           |
|                                                             |
+-------------------------------------------------------------+
```

### Component Inter-process Coordination

- The **Launcher** initializes a temporary GitOps repo path, allocates two free ports, and exports them to environment variables.
- `tmux` panes are created via scripting:
  - `tmux split-window -h`
  - `tmux split-window -v`
- Keystrokes/commands are sent to each pane using `tmux send-keys` or passed as terminal commands to run upon pane initialization.
- Log tracking is maintained within individual panes, preventing log-interlacing.
- Clean shutdown is triggered by the controller's exit status. The launcher listens to the main controller exit and executes `tmux kill-session -t fingerling-demo` to clean up all background targets.
