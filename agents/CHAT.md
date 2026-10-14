# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md:


> ## [{msg_num}]: From: @{AgentName}, Subject: {Subject}
> 
> {TLDR(LastStep)};
> 
> ### Request: { An '@' or '*' targeted command  for a specic purpose like 'perform this task Y' or 'help me with X}

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_8.md` (2026-10-12 21:29:12) — Sprint 8 - Fingerprint Sampling CLI (2026-10-12). Tier 1, 16/16 pts, STORY-FING-23..26. Delivered python -m fingerling fingerprint: merges any JSONL event stream into a growing, profile-bound fingerprint set; python-jsonpath replaces the hand-rolled resolver; SUM/AVG/MIN/MAX/LAST(n) aggregators; YAML profiles; project .venv via make install. Both Smith gates approved with additions; 4 phases passed UAT and review first time; one cosmetic fix after user testing. 178 tests. This archive also holds the Sprint 1-7 log, which had never been archived.

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_9.md` (2026-10-13 00:09:31) — Sprint 9 - Fingerprint Package + SDLC Tooling (2026-10-12/13). First sprint run under docs/SDLC.md, on branch sprint-9. Delivered STORY-FING-27..30 (18/18 pts): uv with a committed lockfile, ruff and gitleaks gates, Python 3.10-3.13, CI and PyPI trusted-publishing workflows, the fingerprint tool split out as the fingerprint-sampler package (command: fingerprint merge), and this per-phase chat report. Planning also contains the pre-sprint build bootstrap and SDLC decisions. Released as fingerprint-sampler 0.1.0 (tag v0.1.0), merged to main, not pushed.

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_POST_SPRINT_9.md` (2026-10-13 20:02:25) — Maintenance after Sprint 9 (2026-10-13), each change on its own fix/ branch and merged to main: one Makefile with no team-tooling targets; documentation tree groomed (sprint stories to docs/sprints/, README map, agents index); nine stale agents/tools copies of bobp tools removed; session close-out. In bob_protocol (uncommitted there): bobp tldr now uses the system via command and indexes first, and bobp setup-agent-links removes the legacy tool copies. No release - the published package did not change.

---

---
[<small>2026-10-13 20:02:26</small>] [**Mouse**]->[**all**] *sm handoff*:
 Session closed. No sprint in flight. main = Sprint 9 + four merged fix/ branches, tagged v0.1.0, ahead of origin, nothing pushed. Waiting on the owner: PyPI one-time setup, push main, push the tag, bob_protocol sync. Queued next: artifact rubrics (owner to pick the pilot). To resume: read task.md, docs/SDLC.md and agents/mouse/state.md; next sprint is sprint-10, next story STORY-FING-31. Active scope is the fingerprint tool only.

---
[<small>2026-10-13 20:07:26</small>] [**User**]->[**Cypher**] *request*:
 /sprint complete artifacts rubrics sprint

---
[<small>2026-10-13 20:07:26</small>] [**Mouse**]->[**Cypher**] *sm start*:
 Sprint 10 start. Stage 0 SDLC gate: docs/SDLC.md present - pass. Branch sprint-10 created from clean main. Scope: the queued artifact-rubrics request. @Cypher *pm plan sprint10

---
[<small>2026-10-13 20:07:26</small>] [**Cypher**]->[**Smith**] *pm handoff*:
 Sprint 10 stories drafted: docs/sprints/USER_STORIES_SPRINT10.md, 10 pts. FING-31 artifact inventory + rubric format, FING-32 stories template with rubric, FING-33 SDLC and lesson rubrics, FING-34 calibration on real artifacts. Owner did not choose a pilot or a blocking rule, so three assumptions are stated at the top: 3 pilots, any Weak rejects, judgement not scoring. @Smith *user review sprint10

---
[<small>2026-10-13 20:08:10</small>] [**Smith**]->[**Morpheus**] *user approve*:
 *user approve Gate 1. Stories state outcomes and each AC is checkable. Added FING-31 AC6: a verdict must fit one 512-char chat message, or reviewers will skip citing criteria - the Sprint 8 handoff already hit that limit once. FING-34 AC2 (a rubric that passes everything is not discriminating) is the right test of the test. @Morpheus *lead arch sprint10

---
[<small>2026-10-13 20:08:10</small>] [**Morpheus**]->[**Smith**] *lead handoff*:
 Sprint 10 arch D1-D7 written. agents/templates/ARTIFACTS.md holds the inventory and rubric format; rubrics are an appendix between RUBRIC-START/END markers with short criterion codes so a verdict fits one chat line; any Weak rejects. Reviewer is never the author: stories->Smith Gate 1, SDLC->Oracle at groom, lessons->Smith at close test. No build change, so no Phase 0. Bob implements (his files). @Smith *user feedback sprint10 arch

---
[<small>2026-10-13 20:08:10</small>] [**Smith**]->[**Mouse**] *user approve*:
 *user approve Gate 2. Criterion codes make the verdict line scannable; observable level descriptions keep it from becoming taste. Separating 'is the document good' (rubric) from 'does the project match it' (Tank's check) avoids two reviews of the same thing. @Mouse *sm plan sprint10

---
[<small>2026-10-13 20:08:10</small>] [**Mouse**]->[**Morpheus**] *sm handoff*:
 Sprint 10 planned in task.md: 4 phases, one story each - 1 inventory+format, 2 stories template+rubric, 3 SDLC and lesson rubrics, 4 calibration on real artifacts. Format comes first because phases 2-3 are written in it; calibration last because it needs all three rubrics. No Tank Phase 0. @Morpheus *lead review sprint plan

---
[<small>2026-10-13 20:08:10</small>] [**Morpheus**]->[**Bob**] *lead handoff*:
 Sprint plan approved: order matches dependencies and each phase is one reviewable document set. Phase 1 ready. @Bob *prompt impl phase-1

---
[<small>2026-10-13 20:08:10</small>] [**Mouse**]->[**all**] *phase 1*:
 Inventory and rubric format (STORY-FING-31): one document listing every artifact agents are expected to produce, and defining how a rubric is written, applied and reported.
