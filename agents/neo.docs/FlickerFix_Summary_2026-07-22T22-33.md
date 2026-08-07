# Flicker Fix Summary

**Date:** 2026-07-22T22:33
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - TUI Flickering Fix

## Work Completed
1. **Raw Terminal Keyboard Reader**:
   - Implemented `get_key()` raw-mode terminal reader using `termios` and `tty` in [examples/tui_demo.py](file:///home/drusifer/Projects/fingerling/examples/tui_demo.py).
   - This function reads single raw keystrokes without echoing them or requiring Enter, and falls back to a clean stdin stream read in non-interactive/piped/automated test environments.
2. **Persistent Live Rendering Context**:
   - Removed the `live.stop()` clears which caused screen toggling (restoring the shell screen buffer and causing flicker).
   - Wrapped the entire demo loop inside a single `with Live(..., screen=True, auto_refresh=True) as live:` block. The dashboard now stays completely stable on the screen while waiting for keyboard inputs.
3. **Decisions Logged**: Recorded the raw keypress reading decision in [docs/DECISIONS.md](file:///home/drusifer/Projects/fingerling/docs/DECISIONS.md).
4. **Verification**: Ran Unit Tests (83/83 OK) and E2E simulation triggers (Pass).
