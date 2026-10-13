# Narrative On Top Summary

**Date:** 2026-07-23T08:46
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - Narrative Layout Priority Highlight

## Work Completed
1. **Layout Reordering**:
   - Refactored `update_view()` in [examples/demo.py](file:///home/drusifer/Projects/fingerling/examples/demo.py) to always split the body column such that the `narrative` guide panel is placed first (on top).
   - In Step 2: Narrative is on top, and target app source code is on bottom.
   - In Step 5: Narrative is on top, and compiled policy YAML is on bottom.
   - In Steps 3, 4, 6, 7: Narrative is on top, telemetry whitelist tables are in the middle, and live output logs are at the bottom.
   - This ensures a clean and consistent top-down user experience.
2. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
