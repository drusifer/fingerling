# Sprint 18 User Stories: Depend on sketch-tastic

*   **Total Points**: 3 (Tier 2)
*   **Branch**: `sprint-18`
*   **Source**: owner, 2026-10-14: the fingerprint tool moved to `drusifer/sketch-tastic` (pushed at `6c4606f`); fingerling depends on it through git.
*   **Status**: Approved (Smith Gates 1 and 2, 2026-10-14)

## Goal

fingerling stops carrying its own copy of the tool. Its parked code uses sketch-tastic from
GitHub, and its docs point there, so there is exactly one place where the tool is developed.

## Assumptions made for the owner

1. The dependency is pinned to the pushed commit (`rev = 6c4606f…`). Moving to a newer
   sketch-tastic means bumping the pin and running `uv lock`.
2. fingerling no longer builds or publishes anything: `publish.yml`, `build`, `smoke`,
   `release-check`, `run`, `fingerprint`, `gharchive` and `quality` (which only covered the
   package) are removed. They now live in sketch-tastic.
3. The parked code keeps its own words (fingerprint ids, warehouse). Only the library names it
   imports change.

---

## STORY-FING-51: fingerling uses sketch-tastic from GitHub
**Points:** 3 · **Owner:** Tank (Phase 0), Neo (Phase 1)

**As the** owner,
**I want** fingerling to depend on sketch-tastic instead of a copy of it,
**so that** the tool is developed in one place.

### Acceptance Criteria
1. `packages/fingerprint-sampler` is gone. `pyproject.toml` depends on `sketch-tastic`, sourced
   from `https://github.com/drusifer/sketch-tastic` at the pinned commit, and `uv.lock` records it.
2. `make install` and then `make test` pass from clean, and the parked tests (50) pass against
   the installed sketch-tastic.
3. No file in fingerling imports `fingerprint_sampler`. The parked code imports `sketchtastic`
   (`Sketch`, `skit_id`, `Field`, `Aggregate`, `tokens`).
4. The Makefile has only targets that still apply. The SDLC describes the new layout and the
   pin, and the CI workflow calls only targets that exist.
5. The README, USER_GUIDE and ARCH point to sketch-tastic for the tool instead of documenting it.

## Out of Scope
- Any change to sketch-tastic.
- Reviving the parked pipeline.

## Open Questions
None.

---

## Architecture (Morpheus)

**D1 — Dependency (Tank, Phase 0, mechanism).** Remove `[tool.uv.workspace]` and the workspace
source. Add `sketch-tastic` to `dependencies` with
`[tool.uv.sources] sketch-tastic = { git = "https://github.com/drusifer/sketch-tastic", rev = "<sha>" }`.
Remove `src` from `[tool.ruff]`. Then `git rm -r packages/fingerprint-sampler` and `uv lock`.

**D2 — Makefile and CI (Tank).** `test` runs `unittest discover -s tests`, and `test-all` runs
the same on 3.14 and 3.15. `check` compiles `fingerling examples tests`. Remove the
package-only targets and `publish.yml`. `ci.yml` keeps `install`, `lint`, `test` and `secrets`.
Rewrite the affected SDLC sections (1, 3, 4, 5, 7, 8, 10).

**D3 — Parked code (Neo, Phase 1).** Rename the imports: `fingerprint_sampler` →
`sketchtastic`, `.fingerprint_set` → `.sketch`, `FingerprintSet` → `Sketch`,
`fingerprint_id` → `skit_id`. Docs become pointers.
