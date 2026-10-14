# Agent State

## Context
Agents *must* use this for keeping their context.md files organized

> ## Recent Decisions
>
>
> ## Key Findings
> - {WHAT}: 
>   - {WHY}
>
> ## Important Notes
> {EXTESIVE Notes}
>
>---
>*Last updated: 2026-10-13T23:55:00-04:00*
- 2026-10-12 Bootstrapped fingerling's Python build env (build-env skill): pyproject.toml (PEP 621/setuptools) is the manifest, isolated .venv via venv+pip, extras demo=[rich] and dev=[fingerling[demo]], console script 'fingerling', requires-python >=3.13, requirements.txt reduced to '-e .[dev]'. Makefile: install/test/check/run/clean/distclean/help, venv guard on env targets. Verified from clean: 178/178. No lockfile (plain pip). No CI in repo. Summary in agents/tank/BootstrapPython_Summary_*.md.
- 2026-10-12 Wrote docs/SDLC.md (from agents/templates/_template_SDLC.python.md): source of truth for change management. OPEN items needing User decision: lint/format tool, branching (currently direct on main), commit-message convention, changelog, release/versioning policy. Known deviations: no lockfile, no lint gate, no gitleaks hook, Makefile.prj unused.
- 2026-10-12 SDLC revised from owner decisions (2026-10-12): branch per sprint (sprint-<N>), agents commit/merge but never push, Conventional Commits, SemVer bump at sprint merge with tag, record = per-phase chat report (no CHANGELOG), active scope = fingerprint tool only. Section 11 lists agreed-but-unbuilt tooling: uv+lock, Python 3.10-3.13, ruff, gitleaks, CI gates+PyPI publish, package split (working name fingerprint-sampler), delete Makefile.prj/requirements.txt, per-phase chat-report. uv is NOT installed on this box; gitleaks and gh are.
- 2026-10-12 Sprint 9 Phase 0 done: uv 0.13 (pipx), uv.lock, requires-python >=3.10, ruff pinned rules, gitleaks target+hook (.githooks, core.hooksPath), make test-all. SDLC sections 1-5 current.
- 2026-10-13 Sprint 9 Phase 2 done: make build / release-check; .github/workflows/ci.yml + publish.yml (unexercised until owner pushes); SDLC sections 3,4,7,8 updated; only the chat-report row remains in section 11.
- 2026-10-13 Sprint 9 sdlc-check passed. After launch: merged sprint-9 into main (--no-ff), tagged v0.1.0, deleted branch; nothing pushed.
- 2026-10-13 2026-10-13 fix/single-makefile: project Makefile no longer has chat/tldr targets; SDLC section 3 says exactly one Makefile, no team-tooling targets. bob_protocol (uncommitted there): bobp/tools/tldr.py now shells out to the system via CLI (via -mg '*' -tF -oJ -n 0) and uses find_project_root; tests/test_tldr.py added. bobp prep-tldr still imports via as a library and is still broken.
- 2026-10-13 Sprint 10 sdlc-check passed; SDLC section 8 corrected (main was pushed; CI result unknown). SDLC section 6 now requires confirming the sprint record is complete before merging. Self-check SDLC edits against the SDLC rubric.

- 2026-10-13 Sprint 11 Phase 0: Python floor 3.14 (owner), PYTHONS 3.14 3.15, CI matrix, ruff py314; jsonschema added. sdlc-check passed at close. Open: `make test-fingerprint ARGS=test_cli` ModuleNotFoundError; queued: dependency analysis tool in bob_protocol.

- 2026-10-14 Owner: mainline development, no tags or releases until further notice (SDLC section 7).

## Current Task
**Sprint:** 10 — Artifact rubrics (`docs/sprints/USER_STORIES_SPRINT10.md`, board: `task.md`)
**Status:** Sprint 10 complete

## Next Steps
Update the SDLC in the same change as any out-of-sprint action that makes a sentence stale.

---
*Last updated: 2026-10-13T23:55:00-04:00*
