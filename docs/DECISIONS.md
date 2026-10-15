# Project Decisions

Architectural and product decisions, in chronological order. See `docs/ARCH.md` for the full
technical rationale behind each — this file is the index Oracle keeps current.

## 2026-07-12 — POC Fingerling Sprint

**Context:** First sprint in this repo. A full BRD/PRD/ARCH + 4 pre-written user stories already
existed in `docs/SOURCE_SPEC.md` (moved here from repo root during grooming — was `Finglering
Initial Docs.md`). Cypher formalized them into `docs/sprints/USER_STORIES_SPRINT1.md` as the sprint backlog.

**Decision:** Scope the POC to the pure-logic fingerprinting core only — STORY-FING-01..04
(tokenizer, warehouse, ring-buffer matcher, policy compiler). Webhook ingestion, sandbox
provisioning, live exploit execution, and GitOps commit/PR automation are explicitly deferred;
none require external infra, so `make test` runs fully offline.
**Consequences:** Every module is a pure Python library function/class with no network,
filesystem-required-at-import, or cluster dependency. Makes the POC fast to build and verify,
but the infra pieces (webhook server, sandbox cgroups, GPG-signed auto-merge) remain unimplemented
and un-battle-tested — flagged as the natural next-sprint scope.

**Decision:** No third-party JSONPath library — hand-rolled dot/bracket-index resolver in
`fingerling/tokenizer.py`, limited to the subset the spec actually uses.
**Consequences:** Zero new dependency weight for the POC. Will need to grow (wildcards,
recursive descent) if a future sprint needs full JSONPath — flagged in `docs/ARCH.md` §8 as
anticipated technical debt, not silently reinvented under time pressure later.

**Decision:** `SlidingWindowMatcher.warm` property added alongside the spec-mandated `push()`
0.0/1.0 contract (`fingerling/ringbuffer.py`).
**Consequences:** Resolves a real HCI gap Smith caught at Gate 1 — a `0.0` score during warm-up
was indistinguishable from a genuine "confirmed clean" match (Nielsen Heuristic #1, Visibility
of System Status). The external `push()` contract Trin tests against is unchanged; `warm` is an
additive side-channel for callers (e.g. a future enforcement gate) that need to know the
difference before trusting a `0.0`.

**Decision:** `compile_policy(..., action: Literal["Block","Post"] = "Block")` is an explicit
caller parameter — no inference from workload metadata (`fingerling/policy.py`).
**Consequences:** Resolves Smith's Gate-1 ambiguity note on STORY-FING-04 AC3 ("defaults to
Block or Post based on the target specification" never said which field). Removes a guessing
game Neo would otherwise have had at implementation time.

**Decision:** Warehouse sample ring (`fingerling/warehouse.py`, cap 3) grows on every `upsert()`
call, not just on Drift.
**Consequences:** The story's own AC text ("Do not append a new record block" on Match) only
forbids a new top-level dict entry, not sample-ring growth. This is the only reading under which
the story's own Verification Task ("dropping or rotating older rows") is testable at all — Trin
caught this during Phase 2 UAT, Morpheus endorsed it, `docs/ARCH.md` §4.2/§7 updated to match.

**Decision:** `parse_jsonl(jsonl_text: str) -> list[dict]` added to `fingerling/tokenizer.py`
during Phase 1 UAT (not in the original architecture).
**Consequences:** STORY-FING-01 AC1 literally requires accepting "a valid JSONL input string,"
but the original architecture only specified `tokenize(record: dict, ...)`. Trin caught the gap
at UAT (tests only exercised pre-parsed dicts); Neo added a 4-line wrapper. Lesson: architecture
review should trace every AC to a literal function signature, not just a data-flow diagram — see
`docs/LESSONS.md`.

## 2026-07-21 — Sprint 2: Live Ingestion & Pipeline Polish

**Decision:** Hand-rolled recursive descent and wildcard path resolver in `fingerling/tokenizer.py`.
**Consequences:** Avoids introducing heavy external libraries like `jsonpath-ng` or `jsonpath-rw`. Code remains stdlib-only.

**Decision:** Sorted, deduplicated, comma-joined token aggregation for wildcard matches.
**Consequences:** Multiple matches from a wildcard query are tokenized individually and combined deterministically. This prevents array ordering from causing fingerprint drift.

**Decision:** Aligned Policy API accepting tuples.
**Consequences:** Avoids manual comma-joining glue at call sites, allowing direct handoff of the output from `SlidingWindowMatcher` to `compile_policy`.

**Decision:** stdlib-only `http.server` for Webhook Ingestion.
**Consequences:** The webhook server requires no external framework dependencies (like FastAPI/Flask) and remains completely offline-testable.

## 2026-07-21 — Sprint 3: Automated GitOps Delivery Pipeline

**Decision:** Self-contained GitOps workspace scaffolding using python subprocess.
**Consequences:** Avoids third-party Git integration libraries like GitPython. Utilizes standard git CLI directly, which runs offline and requires zero setup.

**Decision:** Optional/Fallback GPG signing execution.
**Consequences:** Commits are signed if a key is provided, but failure is handled gracefully with clear `RuntimeError` reporting. This makes it easy to write local offline integration tests on systems that may not have GPG key rings initialized.

**Decision:** Automated non-fast-forward branch merging (`git merge --no-ff`).
**Consequences:** Guarantees that a merge commit is generated for every policy deployment, preserving history trace integrity in the GitOps pipeline. Branch is cleaned up automatically post-merge.

## 2026-07-21 — Sprint 4: Controlled Exposure Sandbox (Vaccination)

**Decision:** Graceful fallback to process-level isolation in `fingerling/sandbox.py`.
**Consequences:** If writing to `/sys/fs/cgroup` fails due to permissions or read-only filesystem, the sandbox logs a stderr warning and runs the target application via standard subprocess. This guarantees full offline testability on systems lacking cgroups configuration.

**Decision:** stdlib-only Vulnerable Target HTTP App.
**Consequences:** Avoids introducing Flask or other external frameworks. Keeps dependencies to zero and enables simple in-process server thread lifecycles in the test suite.

**Decision:** Simulated benign exploit payload (`echo`) for CW-78 verification.
**Consequences:** Safely verifies that the vaccination engine triggers command injection anomalies, compiles KubeArmor policies, and delivers them via GitOps without any risk of system damage or malware detonation.

**Decision:** Actual HTTP GET requests for baseline warmup.
**Consequences:** Rather than mocking baseline telemetry directly via POSTs, the E2E verification test and demo scripts execute two actual GET requests to the vulnerable app with normal query characters (`/ping?host=127.0.0.1`). This exercises target app reachability and validates the clean trajectory pipeline under realistic connectivity.

## 2026-07-22 — Sprint 5: Interactive Split-Pane Terminal UX Demo

**Decision:** Dynamic TTY detection and fallback in tmux launcher.
**Consequences:** If `tmux` is missing or the script is run in a non-interactive shell (like a pipe or inside a CI sandbox lacking a TTY), `examples/run_interactive_demo.sh` automatically falls back to running the inline `interactive_controller.py` in standalone mode rather than crashing.

**Decision:** Standard library-only CLI helper runners.
**Consequences:** Added `examples/run_webhook_server.py` to allow the Webhook server to run as a separate command-line process in a dedicated tmux pane. This keeps the workspace free of third-party frameworks while meeting the multi-process layout requirement.

## 2026-07-22 — Sprint 6: Rich TUI Dashboard UX Epic

**Decision:** Unified single-process python `rich` layout dashboard.
**Consequences:** Replaces the multi-pane tmux shell launcher script and legacy scripts with a consolidated flagship `examples/demo.py` dashboard utilizing Python's `rich` layout and live rendering engine. This provides a much richer and more integrated visual user experience (including syntax-highlighted code viewers, eBPF telemetry transition tables, scrolling logs, and step narratives) while running natively in a single terminal process with no external dependencies (like tmux or textual).

**Decision:** Thread-safe `LogPipe` print redirection.
**Consequences:** Rather than writing logs to temporary files and running loop pollers, we replace `sys.stdout` and `sys.stderr` inside the execution context with a custom string stream that appends prints to a shared thread-safe queue. This allows TUI widgets to render background server output logs in real-time.

**Decision:** Direct execution of interactive demo targets bypassing `mkf.py`.
**Consequences:** The target `demo` is designed for live user stdout rendering and active stdin (`get_key()`) interactions. Routing it through the `mkf.py` build filter redirects outputs to log files and blocks terminal stream interactions. Bypassing `mkf.py` allows the target to run directly in the foreground console with live I/O.

**Decision:** Persistent Live Rendering context with raw termios raw keypress reads.
**Consequences:** To eliminate terminal flicker, the step-advancement loop stays entirely inside a single `with Live(..., screen=True)` block. Instead of halting live rendering (which toggles the screen buffer and causes flicker) to read lines via `input()`, a raw `get_key()` reader queries standard input character-by-character on Unix (using `termios` and `tty`), falling back to stream reads in non-TTY piped environments.

**Decision:** Condensed layout panel sizes and compact table padding.
**Consequences:** To ensure the interactive TUI fits completely inside standard 24-line or 30-line terminal windows, the target app code snippet was shortened to a high-level 10-line view, nested panel borders in telemetry widgets were grouped into a single layout cell, table padding was minimized, and log pipe deques were capped at 6 lines. This completely eliminates CPU lag, layout clipping, and text overlapping.

**Decision:** Bounding TUI Console rendering specifically to `sys.__stdout__`.
**Consequences:** Globally reassigning `sys.stdout` to capture background server prints hijacks `rich.live.Live` updates, writing binary terminal drawing escape codes directly into the log buffers instead of rendering them to the screen. To prevent TUI screen freezes/garbling, the `Console` instance is explicitly bound to the Python interpreter's original standard output stream `sys.__stdout__`, rendering TUI graphics perfectly while cleanly trapping print statements.

**Decision:** Cbreak-equivalent termios configuration and manual rendering refreshes.
**Consequences:** Using `tty.setraw` disables output post-processing (`OPOST`) on the terminal descriptor. When the background rendering thread prints `\n` to draw layout boxes while raw mode is active, the cursor does not return to the first column, causing panels to cascade diagonally and become completely garbled. This was resolved by implementing a custom `termios` setup that only disables canonical input (`ICANON`) and echo (`ECHO`) on stdin. Additionally, setting `auto_refresh=False` and manually calling `live.refresh()` at step transitions completely eliminates background redrawing loops, guaranteeing zero CPU overhead and zero screen flickering.

**Decision:** Full-width stacked layout structure for logs and narratives.
**Consequences:** Splitting all panels into two narrow columns (Left and Right) forces text lines (such as 80+ char server logs and paragraphs of instructions) to wrap heavily, making them illegible. To resolve this, a hybrid vertical grid layout was adopted: the narrow code snippet and telemetry tables are split horizontally in the top row, while the narrative guide and server output logs get full-width rows. This maximizes scanning readability and provides clean formatting.

**Decision:** Adaptive step-based layout panel splitting.
**Consequences:** Showing the code viewer, telemetry transition tables, narratives, and scrolling logs simultaneously on a standard terminal screen height results in heavy layout clipping, rendering errors, and overlapping. To resolve this, we implemented an adaptive layout structure that dynamically splits and populates only the active panels for the current E2E vaccination step. This saves significant height space and ensures all visible widgets fit perfectly on any standard screen size.

**Decision:** Dual eBPF / Simulated fallback capture mechanism in TUI dashboard.
**Consequences:** To verify technology credibility under real-world conditions while preserving portable, zero-dependency executions, the TUI dashboard probes for `sudo bpftrace` at startup. If root privileges and kernel probing tools are present, the TUI spawns the target app as an isolated subprocess, attaches `bpftrace` to capture live `sys_enter_execve` events generated by the shell commands, and pipes real kernel events into the scoring engine. If not available, it prints a fallback notification and executes using offline simulation fixtures.

**Decision:** Consolidated single flagship entry point script.
**Consequences:** Having separate synthetic, live-eBPF, tmux, and TUI scripts led to huge code duplication and confusing operational instructions. To address this, we consolidated all demo logic under a single script `examples/demo.py` and a single Makefile target `make demo`. It runs as our flagship interactive TUI, dynamically attaching eBPF kernel kprobes if root privileges are present and falling back to simulated telemetry if not.

**Decision:** Telemetry endpoint path targeting.
**Consequences:** Telemetry ingestion POSTs are now explicitly directed to `/telemetry`. Previously, target webhook URLs in the TUI were pointing directly to the root path `/` which resulted in `404 Not Found` response codes since the webhook server asserts `/telemetry` as the single ingestion route.

**Decision:** Private attribute matching on SlidingWindowMatcher.
**Consequences:** Fixed an attribute resolution lookup error where the TUI matched `_whitelist` instead of `whitelist`, resolving runtime errors when parsing real dynamically learned whitelist transitions in eBPF capture mode.

**Decision:** Captured exploit command injection output printing.
**Consequences:** The TUI now captures the HTTP response body of the exploit request and prints it to the stdout log feed. This logs `[Exploit Response] Stdout: boo` during Step 4, proving to the user that the command was successfully injected and executed by the shell before the vaccine is deployed.

**Decision:** SGR ANSI color rendering in TUI logs.
**Consequences:** Changed the logs panel text construction to use `Text.from_ansi`. This allows the scrolling logs feed to render inline terminal colors (such as the glaring bright red success alerts framing exploit stdout captures) instead of locking the entire widget under a single dim style.

**Decision:** Top-aligned Narrative Guide layout hierarchy.
**Consequences:** Changed the dynamic layout split order to guarantee that the `narrative` guide panel is always on top. This leads the user's focus immediately to instructions and explanations before they scan code snippets, whitelists, or output logs.

**Decision:** Dual-column Middle Row splitting with Raw JSON trace feed panel.
**Consequences:** The middle dashboard row is now split horizontally. The left panel shows the Transitions Whitelist Map, and the right panel shows a real-time scrolling JSON feed of the raw trace events being ingested (with color coding matching clean, anomalous, or denied execve states). This gives the user immediate visual confirmation of the kernel telemetries processed by the engine.

**Decision:** Sequential baseline requests with live-view repainting.
**Consequences:** Changed baseline query execution in Step 3 to execute and parse telemetry records sequentially with a 1.0 second delay in between. By attaching the `Live` context manager instance to `self.live_view`, the actions loop pushes new logs and whitelist transitions to the screen immediately, giving the user real-time visual feedback of each baseline request's ingestion process.

**Decision:** Strict eBPF and root enforcement at startup (simulation dropped).
**Consequences:** Removed all fallback simulated paths from the dashboard codebase. The TUI now asserts root execution and `bpftrace` visibility at start, exiting with clear diagnostics if they are missing. This guarantees that the E2E vaccination demo executes exclusively using real eBPF kernel instrumentation, reinforcing technology credibility.

**Decision:** Split Client and Server Log Feeds in bottom TUI row.
**Consequences:** The bottom logs row is split horizontally. The left panel renders client/attack actions (`client_log_pipe`), and the right panel renders target application server logs (`server_log_pipe`). This gives the user clear separation between client request triggers and server-side responses.

**Decision:** Render HTTP response body/status code in Client Logs.
**Consequences:** All baseline and exploit verify triggers now capture and print the resulting HTTP response status and body in the Client Logs pane. Blocked requests are colored red (`\033[91;1m`), matching exploit detonation styling.

**Decision:** Enable unbuffered Python execution (`-u`) for Target App subprocess.
**Consequences:** Added the `-u` argument to the target application's Popen execution list. This disables stdout/stderr stream buffering in the child process, allowing server log prints to flow in real time without lag.

**Decision:** Route all eBPF/Tracer log messages directly into the eBPF Tracer panel.
**Consequences:** Renamed the middle-right panel to `eBPF Tracer Logs & Raw Feeds`. Setup messages (eBPF activation status, capture start, event counts) are now appended directly to `self.raw_traces` and formatted using bold cyan highlights instead of printing to the Client Logs feed.

**Decision:** Autoscrolling terminal logs via dynamic terminal viewport slicing.
**Consequences:** Added `limit_text_lines(text, max_lines)` to split styled Rich text and slice to show only the last N lines. Terminal height is calculated dynamically via `self.console.size.height` to compute fitting line counts. This makes Client logs, Server logs, and the eBPF Tracer panel scroll automatically to keep recent entries at the bottom.

**Decision:** Restore HTTP access logs and print command traces on the Target App server.
**Consequences:** Enabled HTTP request tracking in `vulnerable_app.py`'s log handler, and added stdout/stderr console prints before and after executing shell commands. This makes the `echo boo` command injection payload output stand out clearly in the Target App Server logs pane.

**Decision:** Automated line numbering in LogPipe buffers.
**Consequences:** Programmed the `LogPipe` constructor to maintain a running line counter, splitting multiline inputs and prefixing each line with a unique formatted number (e.g. ` 1 | `).

**Decision:** Granular client/server stream classification.
**Consequences:** Replaced generic labels with specific stream identifiers. The Client pane uses `[Client request]`, `[Client response]`, `[Client stdout]`, and `[Client stderr]`. The Server pane uses two dedicated subprocess pipes to distinguish and print `[Server stdout]`, `[Server stderr]`, `[Server access.log]`, and `[Server webhook.log]`.

**Decision:** Staggered chronological step execution with live TUI refreshing.
**Consequences:** Refactored walkthrough step actions to execute in a staggered sequence of events (Outbound HTTP Client $\rightarrow$ Subprocess execution $\rightarrow$ eBPF event capture $\rightarrow$ Telemetry POST $\rightarrow$ Matcher analysis) utilizing explicit `time.sleep` intervals and calling `live.refresh()` at each stage. This allows the user to visually watch the logs hit the panels chronologically in real-time.

**Decision:** Multi-schema validation support in simulated policy checks.
**Consequences:** Configured the target web application to resolve KubeArmor block criteria against three independent hashing schemas of the target anomalous binary (actual eBPF, simulated test, and raw legacy). This resolves a bug where the target server failed to match incoming policy annotations and execute the block in live and integration test environments.



**Decision:** Unified eBPF Daemon & Analysis Orchestrator panel.
**Consequences:** Replaced the separate side-by-side middle telemetry and raw traces panels with a single consolidated `orchestrator` panel. It layouts eBPF Daemon Status (Monitored PID, active probes, warehouse size, anomaly score) and the transitions whitelist map table side-by-side with the scrolling live telemetry logs using a grid layout, keeping control plane telemetries centered in one pane.

**Decision:** Embed Unicode architecture flowcharts in narrative guides.
**Consequences:** Integrated visual ASCII/Unicode flow diagrams into the narrative guide text blocks across walkthrough steps (Steps 1, 3, 4, 5, 7) to visually map out telemetry ingestion, anomaly scoring, GitOps reconciliation, and process block enforcement. Relocated ports, paths, and PID details strictly to the narrative and daemon status sections.

**Decision:** Unified webhook server log prefix matching.
**Consequences:** Changed the webhook handler's log prefix output inside `fingerling/server.py` from `[Webhook Server]` to `[Server webhook.log]`. This aligns with the `LogPipe` parser mapping pattern in `demo.py`, allowing it to correctly capture and format the telemetry access logs as `[SRV:WHK]`.

**Decision:** Dynamic webhook logging and complete client/server console isolation.
**Consequences:** Added `log_writer` to `run_server` and routed webhook server access logs (`[Webhook Server] ...`) to `self.server_log_pipe`. Routed anomaly alarms, server status logs, and GitOps commit prints to `self.server_log_pipe` as well, keeping the Client Logs pane reserved exclusively for outbound requests and responses.


**Decision:** 1-request step pacing (reduced baseline count).
**Consequences:** Decreased Step 3's baseline requests from 2 to 1. This matches the target frequency across other validation steps, simplifying the walkthrough pacing.


**Decision:** Global TTY Echo suppression and pre-block stdin flushes.
**Consequences:** Disabled `ICANON` and `ECHO` globally in `run()` and restored them in `cleanup()`. A non-blocking stdin flush loop is executed in `get_key()` before blocking on a read. This prevents scroll wheel clicks from leaking or displaying control characters (like `^[[A`) on the screen during busy periods.








**Decision:** High-fidelity visual telemetry structure (PID, Parent, Target, Return).
**Consequences:** The TUI raw trace capture panel now displays full execution lineage metadata (e.g. process PIDs, parent binaries like `sh`, target binary paths like `/bin/echo`, and return states) in a tree-indented console format. Simulated payloads were enriched to mirror this schema, keeping the dashboard's look and feel identical in both modes.





**Decision:** Filter and drain ANSI escape sequences in cbreak keyboard reader.
**Consequences:** Using mouse scroll wheels or arrow keys sends multi-byte ANSI escape sequences starting with `\x1b`. To prevent these sequences from being parsed as multiple rapid keypresses (which skips step actions and shuts down the TUI), `get_key()` uses `select.select()` to drain any active burst sequences from the stdin buffer and returns `'escape'`, which the loop ignores.

**Decision:** Updated Narrative text spatial references from above to below.
**Consequences:** Since the narrative guide was promoted to the top of the body layout to establish visual priority, spatial descriptions inside the text segments (Steps 2 and 5) were updated from "(displayed above)" to "(displayed below)" to match their new relative placement.

## 2026-08-08 — Sprint 7: Comprehensive Input-Validation Policy Demo

**Decision:** `compile_policy(..., block_pattern=None)` as an additive optional parameter emitting `spec.process.matchPattern`.
**Consequences:** Content-based blocking sits alongside the exact-fingerprint block with no schema rewrite; existing callers are unaffected. Block was chosen over silent sanitisation so the demo visibly rejects `;` payloads.

## 2026-10-12 — Sprint 8: Fingerprint Sampling CLI

**Decision:** Replace the hand-rolled JSONPath resolver with the `python-jsonpath` library. **Supersedes** the 2026-07-12 and 2026-07-21 "no third-party JSONPath library" decisions.
**Consequences:** Full syntax (filters, slices, unions, negative indexes) for complex events; a second third-party dependency. A differential run of the old and new tokenizers over every path in the repo showed no token changes, so existing fingerprint IDs are stable.

**Decision:** Install dependencies into a project `.venv` created with `--system-site-packages` (`make install`); the Makefile uses it when present.
**Consequences:** No change to the externally-managed system Python. Running `python3 -m fingerling` outside the venv prints a "run make install" hint rather than a traceback. `sudo python3 -m examples.demo` no longer works directly — use `sudo make demo-live`, which goes through the venv interpreter.

**Decision:** The fingerprint tool is a general-purpose sampler for any JSONL event stream, independent of eBPF capture and of sequence analysis (user direction).
**Consequences:** `fingerling/cli.py` reads only JSONL + a profile. N-gram baselines and anomaly scoring remain a later stage that consumes fingerprint IDs; `ringbuffer.py` was not touched.

**Decision:** Per-fingerprint statistics are declared as aggregators (`SUM`, `AVG`, `MIN`, `MAX`, `LAST(n)`) over JSONPath-selected values, across events. The warehouse's hardcoded `duration_ms` min/max and 3-sample ring were removed outright, not shimmed.
**Consequences:** **Breaking:** `Warehouse.upsert(tokens, duration_ms, raw_record)` is now `upsert(tokens, record)`, and `FingerprintRecord` carries `tokens` and `aggregates`. Telemetry callers pass `TELEMETRY_AGGREGATES` to keep the old data. Only one production caller existed, so a shim would have cost more than the migration.

**Decision:** Aggregator state is keyed by function name (`LAST`, not `LAST(3)`) and `AVG` stores `{avg, sum, count}`.
**Consequences:** State continues to fold after a reload, so batch and split runs produce equal sets; changing `n` keeps collected samples; the file shows the average directly. One `LAST` per aggregate.

**Decision:** Fingerprint set files are versioned and record the `profile_id` (MD5 of the profile's `fields`); merging under a different profile is refused unless `--force-profile`.
**Consequences:** Prevents silently mixing incomparable fingerprints. Editing only `aggregates` does not invalidate a set. Pre-Sprint-8 warehouse files are not migrated.

**Decision:** Sets also store each fingerprint's tokens, and are written header-first in insertion order rather than alphabetically.
**Consequences:** A person can read what a 32-character ID means. Slightly larger files.

**Decision:** CLI entry point is `python -m fingerling` plus `make fingerprint`; exit codes 0 (clean) / 1 (written, lines skipped) / 2 (nothing written).
**Consequences:** No packaging metadata needed. A `fingerling` console script is deferred to the backlog.

## 2026-10-12 — Build environment bootstrap (Tank, `build-env` skill)

**Decision:** `pyproject.toml` (PEP 621, setuptools backend) is the dependency manifest; `requirements.txt` is reduced to a pointer (`-e .[dev]`). **Supersedes** the Sprint 8 "`.venv` created with `--system-site-packages`" detail: the venv is now isolated.
**Consequences:** Every dependency, including `rich` (the `demo` extra), comes from the manifest, so a clean checkout is reproducible with `make install`. The apt copies of PyYAML and rich are no longer used by the project. `requires-python` is `>=3.13`, the only version it has been run on.

**Decision:** `[project.scripts]` provides a `fingerling` command (`.venv/bin/fingerling`).
**Consequences:** Closes the Sprint 8 "no console script" gap. `python -m fingerling` still works.

**Decision:** Standard Makefile targets `install`, `test`, `check`, `run`, `clean`, `distclean`, `help`; targets fail with "run 'make install' first" when `.venv` is missing instead of falling back to the system Python.
**Consequences:** One failure mode instead of import errors. No `lint`/`format`/`build` targets yet: the project has no linter configured and ships no artifact.

## 2026-10-12 / 13 — Sprint 9: Fingerprint Package + SDLC Tooling

**Decision (owner):** Only the fingerprint tool is active scope; all other fingerling features are back-burnered until the fingerprint CLI is complete.
**Consequences:** No new gates, tests or manual checks for parked modules; `sudo make demo-live` stays unverified by choice. Parked code must keep importing and its existing tests must pass.

**Decision (owner):** Change management — a branch per sprint (`sprint-<N>`), agents branch/commit/merge but never push, Conventional Commits, SemVer bumped by what changed, the per-phase chat report as the record instead of a changelog. `docs/SDLC.md` is the source of truth.
**Consequences:** `main` only ever holds finished sprints. Releases reach PyPI only when the owner pushes a tag.

**Decision (owner):** `uv` with a committed `uv.lock`; `ruff` and `gitleaks` as baseline gates; Python 3.10+; CI gates plus PyPI trusted publishing. **Supersedes** "venv + pip, no lockfile" from the bootstrap.
**Consequences:** Installs are exact. `uv` and `gitleaks` are machine prerequisites. Ruff's rule list is pinned (`E4`, `E7`, `E9`, `F`, `I`) so a tool upgrade cannot move the gate. A `.python-version` pins the development interpreter because uv otherwise prefers its own downloaded Pythons.

**Decision:** The fingerprint tool is the `fingerprint-sampler` distribution (import `fingerprint_sampler`, command `fingerprint merge`), a uv workspace member in `packages/fingerprint-sampler/`. `fingerling` and `fingerprint` were already taken on PyPI.
**Consequences:** It installs alone with PyYAML and python-jsonpath. `fingerling` keeps re-export shims and the `fingerling fingerprint` alias, so nothing parked changed. **Breaking:** CLI message prefix is now `fingerprint:`; the access-log example moved into the package. Fingerprint IDs and file formats are unchanged.

**Decision:** One version stream — `fingerprint-sampler`, starting at 0.1.0, tagged `v<version>`. Root `fingerling` is marked private.
**Consequences:** Sprint numbers and versions are no longer related; a sprint that does not touch the published package makes no release.

**Decision:** `bobp chat-report` splits the archive by `*phase <label>*` marker messages (change made in the bob_protocol repository).
**Consequences:** One document per sprint: summary, then each phase's description and diagram. Logs without markers archive as before.

## 2026-10-13 — Sprint 10: Artifact Rubrics

**Decision:** Templated artifacts carry a review rubric as an appendix to the template; `agents/templates/ARTIFACTS.md` holds the artifact inventory and the rubric format. Piloted on sprint stories, the SDLC and lessons.
**Consequences:** Reviews cite written criteria. Each rubric is applied by an independent reviewer at a step that already existed (Smith at Gate 1 and the close test, Oracle at groom), so no new ceremony was added.

**Decision (assumed for the owner, not confirmed):** any criterion judged Weak rejects at the gate; rubrics guide judgement and are never scored numerically.
**Consequences:** A rubric can stop a sprint at Gate 1. If the owner prefers rubrics to inform rather than block, the verdict rule in `ARTIFACTS.md` is the one place to change.

**Decision:** Persona state, chat messages and TLDR blocks get no rubric.
**Consequences:** Their failures are mechanical and are better caught by checks that can be run; none exist yet.

## 2026-10-13 — Sprint 11: Structured Modifiers and Profile Checking

**Decision (owner):** Python 3.14 and later only; 3.14 and 3.15 are tested. **Supersedes** "Python 3.10+" from Sprint 9.
**Consequences:** Code may use current syntax and `re` features (ruff now formats `except A, B:` without parentheses). Users on older Pythons cannot install 0.2.0 or later. 3.15 was two weeks old, so the floor stays one release back until the dependency chain is known to work there; it installed cleanly.

**Decision (owner):** Profiles are checked by a JSON Schema through `jsonschema`, a new runtime dependency of fingerprint-sampler, rather than by hand-written checks.
**Consequences:** PyPI users also install `attrs`, `referencing` and `rpds-py`. Editors can check profiles while typing.

**Decision (owner):** No effort on backwards compatibility while a SemVer project is below 1.0 — rip and replace.
**Consequences:** Sprint 11 dropped the migration hint for the old string form and the guarantee that profile ids stay the same; old set files simply report a profile mismatch. The `fingerling` re-export shims and the `fingerling fingerprint` alias are compatibility code of the same kind, left for a later cleanup since the parked package is out of scope.

## 2026-10-14 — Mainline development

**Decision (owner):** No more tags or releases for now; the project is in mainline development.
**Consequences:** Sprint close no longer bumps the version or tags; `main` is the only line. Nothing is published to PyPI. SDLC section 7 records the suspension; releasing resumes only when the owner says so.

## 2026-10-14 — Sprint 12: Domain Model and Consolidated Validation

**Decision:** Every modifier and aggregate function is a `Rule` subclass, registered by `name`, built from a bare name or mapping, checked by the schema and then by its own `check()`. `Field` and `Aggregate` take the YAML keys as arguments.
**Consequences:** One construction and validation path; `parse_fn`, the modifier dispatch table and the name switches are gone. Aggregate functions use the modifier convention (`{name: LAST, n: 3}`). Adding a rule is one class plus a schema definition.

**Decision (owner):** The tokenizer module belongs with the eBPF features: it moved to `fingerling`, built on fingerprint-sampler's `Field`.
**Consequences:** fingerprint-sampler reads JSONL and tokenizes through `Profile.tokens`. The `fingerling` shims, the `fingerling` command and the `fingerprint-sampler` script were deleted (no compatibility before 1.0). `Warehouse` became `FingerprintSet`.

**Decision (owner):** Checks that agents ran by hand become a smoke suite (`make smoke`) against the installed wheel, including the README's own examples; `make quality` reports smells (report only).
**Consequences:** No ad hoc verification commands; UAT cites make targets. README drift now fails a gate.

## 2026-10-14 — Built-in fingerprint metadata

**Decision (owner):** Every fingerprint gets built-in metadata that needs no profile setting: `count`, wall-clock `first_seen` / `last_seen`, and the first and last 3 events (`first`, `last`), each with the time it was seen. `samples: N` in the profile changes the number (0 = none) and does not affect the profile id. Event-time tracking stays a user-defined aggregate: defaults assume nothing about an event's shape.
**Consequences:** Built-in metadata sits beside `aggregates`, which hold only what the profile asked for. `total_occurrences` is now `count`; the set file is version 2 and version-1 files are refused (no compatibility before 1.0). Hand-rolled whole-event `LAST` aggregates in the telemetry pipeline and the eBPF example were removed.

**Decision (owner, same day, supersedes the above):** The built-in metadata is a small profile shipped with the package (`builtin.yaml`) using the ordinary aggregate functions, plus the new `COUNT` and `FIRST(n)`. It reads each parsed record wrapped in an envelope, `{meta: {seen: <wall clock>}, record: <parsed record>}`, and its results go to a `meta` section beside the profile's `aggregates`.
**Consequences:** No special-case fields or code in `FingerprintSet`; injected fields and built-in keys can never clash with the record or the user's aggregate keys. The `samples` setting is gone. The set file reads `meta: {count: {COUNT: n}, ...}` — uniform with aggregates, slightly noisier.

**Decision (owner, 2026-10-14):** A missing key and a key set to `null` mean different things. `IS_PRESENT` is TRUE when the key exists (even if null); `IS_NULL` is TRUE only for an explicit null. Missing → FALSE/FALSE, null → TRUE/TRUE, value → TRUE/FALSE.
**Consequences:** Supersedes the source spec's definitions, under which the two were exact complements. Profiles using either modifier may produce different tokens for records with explicit nulls.

**Decision (owner, 2026-10-14):** An aggregate with one function stores its value directly (`count: 12`); several functions keep a map by name. `MIN`/`MAX` order text as well as numbers, so ISO-8601 times work; the built-in `first_seen`/`last_seen` are `MIN`/`MAX` of `$.meta.seen`. `FIRST`/`LAST` always take `n` and keep a list.
**Consequences:** `meta` reads `{count: n, first_seen: t, last_seen: t, first: [..], last: [..]}` with no special case. Event-time min/max are correct even for out-of-order streams. Set files are version 3; older ones are refused.

**Decision (owner, 2026-10-14):** Dates and times are declared with `type: DATETIME` or `type: DATE` on a field or aggregate, not a modifier: the type says what the input is, which fields and aggregates both need. Values are ISO-8601 only — no formats, epochs or parsing options ("we're not writing a parser"). Times are normalised to UTC (no zone = UTC). `TRUNC` buckets typed values for fields.
**Consequences:** `MIN`/`MAX` compare real datetimes across zones; the set stores YAML timestamps. Built-in `first_seen`/`last_seen` are typed. A field's type is part of the profile id.


**Decision (Sprint 13, 2026-10-14):** An aggregate path that selects nothing in an event is not a skip; only a present value that a function cannot use (or that does not convert to the declared `type`) is counted, reported as "unusable aggregate values". A bare rule name that needs arguments (`GLOB`, `LAST`, ...) is reported as such, with the required arguments read from the profile schema.
**Consequences:** The skipped count is 0 on data where fields are optional (GH Archive), so a non-zero count points to a real problem. New rules get the "needs arguments" message without code changes. `fingerprint show SET` prints a set as a table (no options yet).

**Decision (owner, Sprint 14, 2026-10-14):** Weighted aggregates use an `op` on the aggregate (`{path: $.payload, op: SIZE, fn: [SUM, AVG, MAX]}`), not a parameter of one function (`SUM(..., op=SIZE)`): measuring is a step on the value, summing a step after it, and every function should get the measured value. `SIZE` is UTF-8 bytes for text and compact-JSON bytes otherwise. `op` and `type` are exclusive.
**Consequences:** `Op` is a new Rule family; new ops (`LEN`, `ABS`) need no syntax change. A cross-key schema rule (`not`) supplies its own message through its `description`. The profile id is unchanged by `op`.

**Decision (owner, Sprint 15, 2026-10-14):** Each fingerprint carries its share of the set (percent of the total over all fingerprints) for every value that adds up: the built-in `count` and each `SUM` and `COUNT` aggregate, not `AVG`/`MIN`/`MAX`/`FIRST`/`LAST`. Shares are stored in the set file (`share`, laid out like `meta`/`aggregates`, recomputed on every save, 2 decimals) and shown by `fingerprint show` (`COUNT %` plus a value and `%` column per shared aggregate, 1 decimal).
**Consequences:** Shares describe the set as last written; an in-memory set's shares are stale until saved. `show` recomputes nothing, so a set written before shares existed shows `-` until its next merge. Set format still `version: 0`.

**Decision (owner, Sprint 16, 2026-10-14):** Lightweight history: every merge that updates the set also writes just that run's fingerprints (a set file with a `run:` header) to `<set without extension>.history/<UTC start>.yaml`. Always on, no flag; `-o` (kept for now, may be revisited) writes none. Same-second runs get `_2`, `_3` (`-2` was rejected in UAT: it sorts before `.yaml`, breaking run order). The set is saved first; a failed history write exits 3.
**Consequences:** History needs no new reader: `fingerprint show` reads run files. Nothing is pruned, so history grows by one file per run. Set-to-set merge (backlog) would let runs be recombined.

**Decision (owner, 2026-10-14):** The built-in metadata keeps one sample record each for `first` and `last` (was 3 each), to keep sets and run files small (Sprint 16 found ~6.2 MB run files on a GH Archive hour, dominated by samples).
**Consequences:** Profiles that want more samples add their own `FIRST`/`LAST` aggregates. An existing set keeps its 3 stored `first` records (`FIRST` never drops samples it already has); `last` trims to 1 on the next merge. No migration (0.x).
