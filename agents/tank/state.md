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
>*Last updated: [timestamp]*
- 2026-10-12 Bootstrapped fingerling's Python build env (build-env skill): pyproject.toml (PEP 621/setuptools) is the manifest, isolated .venv via venv+pip, extras demo=[rich] and dev=[fingerling[demo]], console script 'fingerling', requires-python >=3.13, requirements.txt reduced to '-e .[dev]'. Makefile: install/test/check/run/clean/distclean/help, venv guard on env targets. Verified from clean: 178/178. No lockfile (plain pip). No CI in repo. Summary in agents/tank/BootstrapPython_Summary_*.md.
- 2026-10-12 Wrote docs/SDLC.md (from agents/templates/_template_SDLC.python.md): source of truth for change management. OPEN items needing User decision: lint/format tool, branching (currently direct on main), commit-message convention, changelog, release/versioning policy. Known deviations: no lockfile, no lint gate, no gitleaks hook, Makefile.prj unused.
- 2026-10-12 SDLC revised from owner decisions (2026-10-12): branch per sprint (sprint-<N>), agents commit/merge but never push, Conventional Commits, SemVer bump at sprint merge with tag, record = per-phase chat report (no CHANGELOG), active scope = fingerprint tool only. Section 11 lists agreed-but-unbuilt tooling: uv+lock, Python 3.10-3.13, ruff, gitleaks, CI gates+PyPI publish, package split (working name fingerprint-sampler), delete Makefile.prj/requirements.txt, per-phase chat-report. uv is NOT installed on this box; gitleaks and gh are.
- 2026-10-12 Sprint 9 Phase 0 done: uv 0.13 (pipx), uv.lock, requires-python >=3.10, ruff pinned rules, gitleaks target+hook (.githooks, core.hooksPath), make test-all. SDLC sections 1-5 current.
- 2026-10-13 Sprint 9 Phase 2 done: make build / release-check; .github/workflows/ci.yml + publish.yml (unexercised until owner pushes); SDLC sections 3,4,7,8 updated; only the chat-report row remains in section 11.
- 2026-10-13 Sprint 9 sdlc-check passed. After launch: merged sprint-9 into main (--no-ff), tagged v0.1.0, deleted branch; nothing pushed.

## Current Task
**Sprint:** 9 — SDLC tooling + fingerprint package split (`docs/USER_STORIES_SPRINT9.md`, board: `task.md`)
**Status:** Sprint 9 complete

## Next Steps
Owner must do one-time PyPI setup then push main and the tag. First CI run is the workflows' real test - if it fails, check parked tests (ping/servers) on the runner first.

---
*Last updated: 2026-10-13T00:09:31-04:00*
