# Global Echo and Canonical Control Summary

**Date:** 2026-07-23T10:21
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - Global Terminal Echo Suppression

## Work Completed
1. **Global Termios Configuration**:
   - Updated `TUIDemo.run()` inside [examples/demo.py](file:///home/drusifer/Projects/fingerling/examples/demo.py) to disable TTY input echo (`ECHO`) and canonical line-buffering (`ICANON`) globally for the entire duration of the dashboard execution.
   - Updated `TUIDemo.cleanup()` to restore the original TTY termios settings upon exit, ensuring standard terminal state behavior is fully restored.
2. **Pre-Block Stdin Flush**:
   - Inserted a non-blocking `select.select()` loop at the beginning of the `get_key()` raw key reader.
   - This loop immediately flushes/discards any queued control sequences (such as scroll wheel clicks) buffered by the TTY driver while the steps were executing synchronous actions, preventing character leaking when `read(1)` blocks.
3. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
