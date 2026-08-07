# Stdout Redirect Fix Summary

**Date:** 2026-07-22T22:41
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - TUI Screen Freeze Fix

## Work Completed
1. **Stdout Bound Console**:
   - Identified that globally redirecting `sys.stdout` and `sys.stderr` to the log pipe caused `Live`'s screen drawing routines to write control characters directly into the log pipe instead of rendering them to the terminal.
   - Refactored [examples/tui_demo.py](file:///home/drusifer/Projects/fingerling/examples/tui_demo.py) to instantiate the `rich.console.Console` using the Python interpreter's original standard output stream `sys.__stdout__`.
   - Passed this console object to the `Live` context manager (`console=self.console`). This ensures that TUI renders continuously to the actual terminal screen even when standard print statements are globally hijacked.
2. **Decisions Logged**: Recorded the `sys.__stdout__` bounding selection choice in [docs/DECISIONS.md](file:///home/drusifer/Projects/fingerling/docs/DECISIONS.md).
3. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
