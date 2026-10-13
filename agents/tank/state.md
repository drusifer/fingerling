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

## Current Task
**Task:** SDLC decisions (pre-Sprint 9)
**Status:** SDLC decisions recorded; Sprint 9 will build section 11

## Next Steps
Sprint 9 Phase 0 is Tank's: install uv (pipx install uv), migrate to uv sync + uv.lock, ruff, gitleaks target + hook, CI workflows, requires-python >=3.10, delete leftovers; move each item from SDLC section 11 into sections 1-8 as it lands.

---
*Last updated: 2026-10-12T23:54:20-04:00*
