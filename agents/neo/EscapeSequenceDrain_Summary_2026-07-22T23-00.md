# Escape Sequence Drain Summary

**Date:** 2026-07-22T23:00
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - Stdin Escape Sequence Drain and Scroll Wheel Safety

## Work Completed
1. **Escape Sequence Filtration**:
   - Identified that mouse scroll wheels and terminal arrow keys send multi-byte escape sequences (starting with `\x1b`). 
   - Previously, when `get_key()` read `\x1b`, the loop advanced the step immediately. The next loop iterations rapidly read the remaining characters in the sequence (`[`, `A`, etc.) one-by-one as individual keypresses. This rushed the demo to the end in a fraction of a second, causing the user to miss Step 4's exploit output completely.
   - Refactored `get_key()` in [examples/demo.py](file:///home/drusifer/Projects/fingerling/examples/demo.py) to check for `ch == '\x1b'`.
   - If detected, a non-blocking `select.select()` loop drains all remaining bytes of the burst sequence from standard input and returns a safe `'escape'` key tag.
   - Refactored the `run()` loop to catch and ignore `'escape'` returns, avoiding step advancement.
2. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
