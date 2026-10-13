# Agent State

## Context
## Recent Decisions
- Executed `setup_agent_links.py` to refresh agent discovery links and MCP configuration.
- Migrated Makefile to the simplified `bobp` flow structure (deleting Makefile.prj, removing `ifdef MKF_ACTIVE` splits).

## Key Findings
- 9 personas and 13 skills are linked and ready.
- Hardened `.mcp.json` for sandboxed via MCP startup.
- Registered via MCP server with Codex.
- Verified `bobp make` successfully intercepts and captures target outputs in the new structure.

## Important Notes
None.
- 2026-10-12 Created shared skill `agents/skills/build-env/SKILL.md` (triggers `*devops bootstrap`,
  `*devops build-env`) at User request: Tank does initial build-env setup per language convention
  (Python pyproject.toml + .venv, JS package.json + lockfile, Go, Rust, generic fallback), fronted
  by a standard Makefile target contract. Wired into `agents/tank/SKILL.md` (trigger, requires,
  section 4b, command, Neo row) and `agents/neo/SKILL.md` (hand-off rule). Registered with
  `bobp setup-agent-links` (14 shared skills).
- User confirmed 2026-10-12 that a project `.venv` is the expected approach for Python deps.
- Caveat: `agents/skills/` is populated by BobProtocol; this skill exists only in this project.
  `bobp update` may not preserve it — it needs adding to the BobProtocol source to reach other
  projects.
- 2026-10-12 SDLC wiring (User direction): Tank owns `docs/SDLC.md`, which is the project's
  source of truth for change management. build-env skill gained the SDLC section, triggers
  `*devops sdlc` / `*devops sdlc-check`, and templates in `agents/templates/_template_SDLC{,.python,.javascript}.md`.
  sprint skill: Stage 0 SDLC gate (blocker), Morpheus build-env check, Mouse Phase 0 rule,
  Step 6a Tank sdlc-check before Oracle groom. bloop `*plan sprint`: step 0 + widened 3b.
  Persona edits: tank (4c + commands), mouse, morpheus, cypher. agents/AGENTS.md: guideline 4.

## Current Task
**Status:** Complete — SDLC ownership, gates and templates wired in
**Assigned to:** Bob

## Next Steps
- All of this is local to fingerling; upstream to the BobProtocol source to reach other projects
  (`bobp update` may overwrite agents/skills and agents/AGENTS.md).
- Untested in a real sprint: Stage 0 gate, Phase 0 scheduling, Step 6a check.
- Possible additions: SDLC templates for Go and Rust.

---
*Last updated: 2026-10-12T23:35:17-04:00*
