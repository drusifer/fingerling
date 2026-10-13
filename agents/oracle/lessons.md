# Project Lessons Learned

> Standing rules for agents. Sprint-by-sprint engineering lessons are in `docs/LESSONS.md`.

This file contains critical lessons and rules derived from past errors, technical discoveries, and architectural decisions. All agents MUST review this file before starting new implementation or architectural tasks.

---

## [2026-05-06] Transition to Artifact-Based Verification

> **Tags:** #Process #Oracle #Neo

### Context
Agents were previously instructed to consult the Oracle persona via chat for historical context and decisions. This often resulted in chat messages that were never picked up or processed by the intended persona.

### The Issue
Chat-based consultation is asynchronous and unreliable for immediate blocking needs. Agents would wait for a response that might not come, stalling progress.

### The Solution
Replaced "Oracle First" chat-based consultation with "Artifacts First" document-based verification. Agents now read consolidated logs and sprint plans directly.

### The Rule (The "Lesson")
DO NOT consult the Oracle via chat (`@Oracle *ora ask ...`) for routine historical or context checks. Instead, read the following artifacts in order: 1) Mouse's sprint plan (`agents/mouse/`), 2) Oracle's `lessons.md` and `memory.md`, and 3) the recent `CHAT.md` history.

### References
- **Files:** `agents/*/SKILL.md`, `agents/oracle/lessons.md`

---

## [2026-08-08] `rich.text.Text` Does Not Parse Bracket Markup

> **Tags:** #Neo #Trin #examples/demo.py

### Context
STORY-FING-22 (Sprint 7) added new narrative/widget text to `examples/demo.py`'s TUI. Trin's
UAT caught a stale-caption bug, and while fixing it Neo confirmed empirically (`Console(record=True)`
round-trip) that `Text.append(str)` and `Text(str)` render `[bold]...[/bold]`-style bracket tags
as **literal characters**, not styling — markup parsing only happens via `Text.from_markup()` or
`console.print(..., markup=True)` on a plain string, neither of which this file uses.

### The Issue
Large parts of `get_narrative_text()`'s pre-existing text (written across Sprints 5-6) use
exactly this bracket-tag pattern (e.g. `"...an [bold red]HTTP 403 Forbidden[/bold red]
response!"`), meaning those specific words most likely render as literal bracketed text in the
live TUI rather than being bold/red. Not confirmed against a real terminal render this session
(no interactive TTY available) — flagged, not fixed, since fixing every pre-existing instance is
out of scope for a single 3pt story.

### The Rule (The "Lesson")
In `examples/demo.py` (and anywhere else building `rich.text.Text` via `.append()`), NEVER use
inline `[style]...[/style]` bracket tags inside a string argument — they will not be parsed.
Split the string into separate `.append(text, style="...")` calls instead. If a future story
touches `get_narrative_text()`, sweep it for the pre-existing bracket-tag instances.

### References
- **Files:** `examples/demo.py` (`get_narrative_text`, `get_telemetry_widget`)
- **Story:** STORY-FING-22, `docs/sprints/USER_STORIES_SPRINT7.md`

---

## [2026-08-08] Extend an Existing TUI Step Instead of Renumbering

> **Tags:** #Morpheus #Neo #examples/demo.py

### Context
STORY-FING-22 needed a new demonstration sequence in the 8-step `examples/demo.py` TUI. The
step count is load-bearing in three separate places: the `while self.step <= 8` loop bound in
`run()`, the `if self.step == 1 or self.step == 8` layout-reset branch in `update_view()`, and
every `elif self.step == N` branch across `get_narrative_text()` and `run_step_actions()`.

### The Rule (The "Lesson")
For a small, additive demo scenario, prefer extending an existing step's narrative + actions
over inserting a new numbered step and renumbering everything after it. Renumbering touches
three independent branching mechanisms in a large, manually-choreographed file with no test
coverage of the interactive loop itself (only `run_step_actions()` is scriptable/testable) —
the blast radius of a renumbering mistake is much larger than the blast radius of one step doing
more. Only renumber if the new content genuinely doesn't fit the pedagogical flow of any
existing step.

### References
- **Files:** `examples/demo.py`
- **Story:** STORY-FING-22, `docs/sprints/USER_STORIES_SPRINT7.md`

---

## [2026-10-12] Dependencies Live in the Project `.venv` — Run Everything via `make`

> **Tags:** #Neo #Trin #Tank #Makefile

### Context
Sprint 8 added the first pip-only dependency (`python-jsonpath`). This Pi's system Python is
PEP 668 "externally managed": `pip install`, even `--user`, is refused; PyYAML and rich come
from apt.

### The Rule (The "Lesson")
`make install` creates an isolated `.venv` and installs the project from `pyproject.toml`
(`pip install -e ".[dev]"`). Make targets always use `.venv/bin/python` and say "run 'make
install' first" if it is missing. Add dependencies to `pyproject.toml`, not `requirements.txt`. Always run tests,
the CLI and the demo through `make` (`bobp make test`, `make fingerprint`, `sudo make demo-live`);
bare `python3 -m ...` will fail to import `jsonpath`. Never use `--break-system-packages`.

### References
- **Files:** `Makefile`, `pyproject.toml`, `fingerling/__main__.py` (prints the install hint)
- **More Sprint 8 lessons:** `docs/LESSONS.md` (differential old-vs-new verification; one fold
  path for merge; type changes surface dead attribute access)
