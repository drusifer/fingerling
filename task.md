# Task Board — Sprint: Fingerling Sprint 6 (TUI Dashboard UX Epic)

**Status:** Sprint 6 Complete (Launched)
**Source:** `docs/USER_STORIES_SPRINT6.md`
**Sprint Log:** `agents/mouse.docs/sprint_log.md`

---

## Sprint Backlog

### Phase 1: TUI Dashboard Engine & Layout (STORY-FING-20)
- [ ] **Task 1.1 (Layout Scaffolding)**: Implement `Layout` layout grid partitions in `examples/tui_demo.py` using Python `rich.layout.Layout`. [Assignee: Neo]
- [ ] **Task 1.2 (Vulnerable Code Viewer)**: Build the code rendering panel with syntax highlighting pointing out the CWE-78 vulnerability. [Assignee: Neo]
- [ ] **Task 1.3 (eBPF Telemetry Tracker)**: Build the telemetry visualizer displaying syscall 2-gram tables, whitelists, red anomaly highlights, and antibody rules. [Assignee: Neo]
- [ ] **Task 1.4 (Instruction & Status Panels)**: Code the step-by-step narrative and status footer panel. [Assignee: Neo]
- [ ] **Task 1.5 (Phase 1 UAT)**: Verify standalone layout rendering, visual states, and highlights. [Assignee: Trin]
- [ ] **Task 1.6 (Phase 1 Code Review)**: Approve Phase 1 code structure and abstractions. [Assignee: Morpheus]

### Phase 2: Live In-Process Run Engine & Automation (STORY-FING-21)
- [ ] **Task 2.1 (Background Servers)**: Integrate target application and webhook server launch in background daemon threads. [Assignee: Neo]
- [ ] **Task 2.2 (Log Pipe Redirector)**: Implement `stdout`/`stderr` capturing to route background print statements directly into the scrolling TUI log pane. [Assignee: Neo]
- [ ] **Task 2.3 (Step Replayer Logic)**: Implement the E2E click-through logic driving GET requests, GitOps commits, and antibody validations. [Assignee: Neo]
- [ ] **Task 2.4 (Signal Trap Cleanups)**: Ensure signal traps and thread shutdowns guarantee no orphaned sockets or temp directories. [Assignee: Neo]
- [ ] **Task 2.5 (Makefile Targets)**: Add `demo-rich` targets in the root `Makefile` and `Makefile.prj`. [Assignee: Neo]
- [ ] **Task 2.6 (Phase 2 UAT)**: Run the complete TUI demo end-to-end verifying hot-patching protection without restarts. [Assignee: Trin]
- [ ] **Task 2.7 (Phase 2 Code Review)**: Approve final TUI runner architecture. [Assignee: Morpheus]
