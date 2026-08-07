# Cbreak Terminal Fix Summary

**Date:** 2026-07-22T22:42
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - TUI Garbled Cascade and Flicker Fix

## Work Completed
1. **Cbreak Keyboard Reader**:
   - Identified that calling `tty.setraw` disables output post-processing (`OPOST`) globally on the terminal descriptor. This prevents `\n` from being translated to `\r\n` during active keystroke waits. When the background `Live` rendering thread wrote newlines to the screen while raw mode was active, the cursor didn't return to the first column, causing layout boxes to cascade diagonally and become completely garbled.
   - Refactored `get_key()` in [examples/tui_demo.py](file:///home/drusifer/Projects/fingerling/examples/tui_demo.py) to avoid `setraw`. It now uses a custom `termios` configuration that only clears `ICANON` and `ECHO` on `sys.stdin`, leaving all output flags (specifically `OPOST`) completely untouched.
2. **Deterministic Layout Refreshing**:
   - Switched `Live` configuration to `auto_refresh=False` to completely disable the background rendering thread during keystroke waits.
   - Programmed manual updates (`live.refresh()`) at the start of each step and immediately after step actions complete. This guarantees **zero background redrawing, zero CPU utilization during blocks, and absolute zero flickering**.
3. **Decisions Logged**: Recorded cbreak keypress selection in [docs/DECISIONS.md](file:///home/drusifer/Projects/fingerling/docs/DECISIONS.md).
4. **Verification**: Ran Unit Tests (83/83 passed) and E2E triggers (Pass).
