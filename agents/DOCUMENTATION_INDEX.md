# Agents Documentation Index

**Last Updated:** 2026-10-13 (Oracle groom)

Index of everything under `agents/`. Project documentation (user guide, architecture, SDLC,
sprint stories) is indexed in the repository [README](../README.md).

## Shared instructions

- **[AGENTS.md](AGENTS.md)** — instructions every agent follows. The repository root serves the
  same file as `AGENTS.md`, `AGENT.md`, `CHATGPT.md`, `GEMINI.md` and `.cursorrules`.
- **[PROJECT.md](PROJECT.md)** — project capability declarations (e.g. `via: enabled`).
- **[bob/HELP.md](bob/HELP.md)** — quick reference for personas and commands.
- **[../docs/SDLC.md](../docs/SDLC.md)** — owned by Tank; the source of truth for how changes are
  made. Read before touching tooling, gates, branches or releases.

## Personas

Each folder holds `SKILL.md` (instructions), `state.md` (working memory: context, current task,
next steps) and dated `<Task>_Summary_<timestamp>.md` work summaries.

| Persona | Role | Instructions | Prefix |
|---------|------|--------------|--------|
| Bob | Prompt Engineer | [bob/SKILL.md](bob/SKILL.md) | `*prompt` |
| Cypher | Product Manager | [cypher/SKILL.md](cypher/SKILL.md) | `*pm` |
| Morpheus | Tech Lead / Architect | [morpheus/SKILL.md](morpheus/SKILL.md) | `*lead` |
| Mouse | Scrum Master | [mouse/SKILL.md](mouse/SKILL.md) | `*sm` |
| Neo | Senior Software Engineer | [neo/SKILL.md](neo/SKILL.md) | `*swe` |
| Oracle | Knowledge Officer | [oracle/SKILL.md](oracle/SKILL.md) | `*ora` |
| Smith | HCI Expert / UX Advocate | [smith/SKILL.md](smith/SKILL.md) | `*user` |
| Tank | DevOps Engineer | [tank/SKILL.md](tank/SKILL.md) | `*devops` |
| Trin | QA Guardian | [trin/SKILL.md](trin/SKILL.md) | `*qa` |

## Skills

Shared procedures in `skills/<name>/SKILL.md`:

| Skill | Use for |
|---|---|
| [bob-protocol](skills/bob-protocol/SKILL.md) | Persona switching, state management, chat workflow |
| [bloop](skills/bloop/SKILL.md) | Multi-persona loops: `*fix`, `*impl`, `*qa`, `*review`, `*plan sprint` |
| [sprint](skills/sprint/SKILL.md) | The full sprint cycle, including the SDLC gate and Tank's close check |
| [build-env](skills/build-env/SKILL.md) | Tank: build-environment bootstrap, `docs/SDLC.md`, conformance check |
| [chat](skills/chat/SKILL.md) | Posting to `CHAT.md` |
| [make](skills/make/SKILL.md), [make-discover](skills/make-discover/SKILL.md) | Running and discovering make targets through `bobp make` |
| [test-runner](skills/test-runner/SKILL.md), [linter](skills/linter/SKILL.md) | Running tests and quality checks |
| [via](skills/via/SKILL.md) | Symbol and relationship queries |
| [judge](skills/judge/SKILL.md) | Evaluating agent tool/skill usage |
| [personas](skills/personas/SKILL.md), [bob-tools](skills/bob-tools/SKILL.md) | Persona directory; `bobp` subcommands |
| [render](skills/render/SKILL.md) | Render deployments (not used by this project) |

## Team communication and records

- **[CHAT.md](CHAT.md)** — live log for the current work; **[CHAT.diagram.md](CHAT.diagram.md)**
  is a generated view of it (do not edit).
- **[chat_archive/](chat_archive/)** — per-sprint reports produced by `bobp chat-report`:
  `CHAT_<SPRINT>.md` (full text) and `CHAT_<SPRINT>.diagram.md` (summary, then each phase's
  description and diagram). These are the project's change record.
- **[mouse/sprint_log.md](mouse/sprint_log.md)** — one entry per sprint: tier, points, phases.
- **[oracle/lessons.md](oracle/lessons.md)** — standing rules agents must follow;
  **[oracle/memory.md](oracle/memory.md)** — project context and major decisions at a glance.

## Templates

**[templates/ARTIFACTS.md](templates/ARTIFACTS.md)** lists every artifact agents are expected to
produce, which have a template and a review rubric, and how rubrics are written and applied.

In `templates/`:

| Template | For |
|---|---|
| `_template_state.md` | Persona `state.md` |
| `_template_CHAT.md` | Chat message format |
| `_template_ARCH.md` | Architecture decision record |
| `_template_LESSON.md` | Lesson entry (with LESSON rubric) |
| `_template_finding.md` | Research finding |
| `_template_tldr.md` | TLDR block formats |
| `_template_USER_STORIES.md` | Sprint stories document (with STORIES rubric) |
| `_template_SDLC.md`, `_template_SDLC.python.md`, `_template_SDLC.javascript.md` | `docs/SDLC.md` (base and per language; with SDLC rubric) |
| `_template_context.md`, `_template_current_task.md`, `_template_next_steps.md` | Superseded by the single `state.md`; kept for older projects |

## Tools

Team tooling is the `bobp` command (`bobp chat`, `bobp make`, `bobp tldr`, `bobp chat-report`,
`bobp setup-agent-links`, ...); run `bobp --help`.

`tools/` is for this project's own helper scripts. It currently holds only `trace_rules.json`,
the anti-pattern rules `bobp trace-annotate` reads. The copies of the bobp tools that used to
live here were removed on 2026-10-13; `bobp setup-agent-links` removes them from older projects.
