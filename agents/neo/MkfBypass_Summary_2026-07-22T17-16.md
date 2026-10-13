# Mkf Bypass Summary

**Date:** 2026-07-22T17:16
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - Build Interceptor Bypass

## Work Completed
1. **Makefile Bypassing**:
   - Modified the root [Makefile](file:///home/drusifer/Projects/fingerling/Makefile) to directly invoke `run_interactive_demo.sh` and `tui_demo.py` instead of wrapping them via `mkf.py`.
   - This ensures that interactive stdin/stdout streams are connected directly to the user's terminal TTY session, allowing live interaction.
2. **Decisions Logged**: Recorded the direct execution choice in [docs/DECISIONS.md](file:///home/drusifer/Projects/fingerling/docs/DECISIONS.md).
3. **Verification**: Checked that `make help` correctly displays the targets and they route correctly.
