# Neo Context

## Recent Decisions
- Refined baseline requests to execute actual HTTP GET requests to `examples/vulnerable_app.py` in `examples/vaccination_demo.py`, `tests/test_vaccination.py`, and `fingerling/vaccine.py` instead of relying entirely on mocked baseline telemetry.
- Sprint 5 Phase 1: Implemented examples/interactive_controller.py containing the interactive CLI controller logic.
- Sprint 5 Phase 2: Implemented run_interactive_demo.sh launcher with 4-pane tmux scripting and robust fallback mode.
- Interactive Demo Cleanup Hardening: Added trap-based cleanup handler to run_interactive_demo.sh to guarantee cleanup of tmux session and temporary directory on EXIT/INT/TERM/SIGHUP.
- Sprint 6 TUI UX Enhancement: User requested new Textual-based TUI dashboard. Initiated planning.
- Sprint 6 Implementation: Implemented examples/tui_demo.py incorporating split layout dashboard widgets, thread-safe LogPipe redirections, E2E click-through runners, signal traps, and make demo-rich stubs.
- Mode Synchronization: Updated examples/interactive_controller.py to synchronize telemetry whitelists, code viewer snippets, and PID hot-patch verification prints.
- TUI Panel Splitting & Webhook Ingestion: Recovered TUI dashboard demo.py, split the middle row into separate left (bpftrace traces) and right (daemon status/logs) panels, separate bottom logs, and print low-cardinality Webhook payload.

---
*Last updated: 2026-07-23T20:49:00*
