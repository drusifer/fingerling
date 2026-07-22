# Task Board — Sprint: Fingerling Sprint 4

**Status:** Sprint 4 Complete (Launched)
**Source:** `docs/USER_STORIES_SPRINT4.md`
**Sprint Log:** `agents/mouse.docs/sprint_log.md`

## Phase 1 — Sandbox Environment Scaffolding (STORY-FING-13)
- [x] 1.1 Implement `run_in_sandbox(command, cgroup_name)` in `fingerling/sandbox.py`.
- [x] 1.2 Add unit tests for sandbox in `tests/test_sandbox.py`.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 2 — Vulnerable Target Application (STORY-FING-14)
- [x] 2.1 Implement `examples/vulnerable_app.py` exposing unsanitized command injection.
- [x] 2.2 Add unit tests for vulnerable app server.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 3 — Controlled Exposure Replay Engine (STORY-FING-15)
- [x] 3.1 Implement `run_vaccination(app_port, webhook_url)` in `fingerling/vaccine.py`.
- [x] 3.2 Add unit tests for vaccine engine.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 4 — E2E Vaccination Verification (STORY-FING-16)
- [x] 4.1 Create `tests/test_vaccination.py` orchestrating end-to-end vaccination flow.
- [x] 4.2 Assert KubeArmor policy is automatically committed and merged via GitOps.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus (last phase → hands to Oracle for `*ora groom`)

---

## Definition of Done (per phase)
- [x] `make test` passes (all unit, integration, and E2E tests).
- [x] Trin UAT confirms all AC + Verification Tasks for the story are met.
- [x] Morpheus confirms architectural alignment with `docs/USER_STORIES_SPRINT4.md`.

## Refinement Phase — HTTP GET Baseline Verification (STORY-FING-17)
- [x] R.1 Refine `examples/vaccination_demo.py` to send two actual HTTP GET requests for warmup.
- [x] R.2 Refine `tests/test_vaccination.py` to warm up using two actual HTTP GET requests.
- [x] R.3 Refine `fingerling/vaccine.py` to send two baseline GET requests under the vaccine engine.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

