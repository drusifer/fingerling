# Task Board — Sprint: Fingerling Sprint 5

**Status:** Sprint 5 Complete (Launched)
**Source:** `docs/USER_STORIES_SPRINT5.md`
**Sprint Log:** `agents/mouse.docs/sprint_log.md`

## Phase 1 — Interactive CLI Controller Script (STORY-FING-18)
- [ ] 1.1 Implement `examples/interactive_controller.py` with 8 interactive steps, colored prompts, and emojis.
- [ ] 1.2 Implement port parameterization and robust cleanup of background components on exit.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus

## Phase 2 — Multi-Pane Terminal Multiplexer Scaffolding (STORY-FING-19)
- [ ] 2.1 Implement shell launcher `examples/run_interactive_demo.sh` creating a 4-pane tmux session.
- [ ] 2.2 Implement single-terminal fallback mode running servers in background threads if tmux is missing.
- [ ] 2.3 Add `make demo-interactive` automation target in the root Makefile.

**Owner:** Neo → **UAT:** Trin → **Review:** Morpheus (last phase → hands to Oracle for `*ora groom`)

---

## Definition of Done (per phase)
- [ ] `make test` passes (all unit, integration, and E2E tests).
- [ ] Trin UAT confirms all AC + Verification Tasks for the story are met.
- [ ] Morpheus confirms architectural alignment with `docs/USER_STORIES_SPRINT5.md`.
