# Complete Sprint 4 Summary

**Date:** 2026-07-21T16-57
**Author:** Cypher (Product Manager)
**Sprint:** Fingerling Sprint 4 — "Controlled Exposure Sandbox (Vaccination)"

## Work Completed
1. **Sprint Planning & Review Gates**: Defined Sprint 4, combining stories and architecture design in `docs/USER_STORIES_SPRINT4.md` (Fast-Track tier). Combined review passed by Smith/Mouse. Created task breakdown in `task.md`.
2. **Phase 1 Implementation (STORY-FING-13)**: Implemented `run_in_sandbox()` in `fingerling/sandbox.py`. Restricts process resources under cgroups or falls back gracefully to standard subprocess process containment.
3. **Phase 2 Implementation (STORY-FING-14)**: Implemented vulnerable HTTP server target in `examples/vulnerable_app.py` containing unsanitized host ping parameter (CWE-78 command injection).
4. **Phase 3 Implementation (STORY-FING-15)**: Implemented vaccine runner `run_vaccination()` in `fingerling/vaccine.py`. It sends baseline and benign exploit triggers, forwarding telemetries.
5. **Phase 4 Implementation (STORY-FING-16)**: Built E2E integration test `tests/test_vaccination.py` orchestrating baseline warmup, exploit triggering, anomaly detection, policy compilation, and GitOps commits/merges.
6. **Documentation & Retros**: Groomed docs (USER_GUIDE.md, DECISIONS.md, LESSONS.md) and recorded retrospectives for all personas.

All 82 tests pass.
