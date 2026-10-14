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
- 2026-10-13 Removed superseded agents/tools/*.py (chat, chat_merge, mkf, prep_tldr, session_trace,
  setup_agent_links, teardown_agent_links, tldr, trace_annotate); kept trace_rules.json. Done by
  the new remove_legacy_tools() in bob_protocol's setup_agent_links.py, which runs on every
  `bobp setup-agent-links` / `bobp update`. References in oracle, judge, personas skills and
  PROJECT.md repointed to bobp subcommands.
- 2026-10-13 Sprint 10 (artifact rubrics): new agents/templates/ARTIFACTS.md (inventory + rubric
  format), _template_USER_STORIES.md (STORIES rubric), SDLC rubric on the 3 SDLC templates, LESSON
  rubric on _template_LESSON.md. Wired into cypher, smith, tank, oracle SKILL.md and the sprint
  and build-env skills. Verdict rule: any Weak rejects (assumed for the owner).
- 2026-10-13 BobProtocol sync complete: tool changes, build-env skill, SDLC/rubric templates, skill and persona edits and the AGENTS.md SDLC guideline are committed and pushed in ~/Projects/bob_protocol (agents/ and bobp/templates/agents/). Fingerling's agents/skills, agents/templates and agents/AGENTS.md match upstream. bobp reinstalled with `bobp make system-install`.

## Current Task
**Status:** Complete — nothing pending.

## Next Steps
- Still fingerling-specific and not upstreamed, by design: `agents/DOCUMENTATION_INDEX.md`, `agents/bob/HELP.md` edits.
- Known upstream gaps: `bobp prep-tldr` imports via as a library (broken); `bobp setup-agent-links` exits 0 when a step fails; `bobp pull` never creates new files.
- Next rubric candidate: architecture template.

---
*Last updated: 2026-10-13T22:07:32-04:00*
