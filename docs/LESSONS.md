# Lessons Learned

Engineering lessons from each sprint, newest last. Standing rules that agents must follow
(process and tooling) are kept separately in `agents/oracle/lessons.md`.

## 2026-07-12 — POC Fingerling Sprint

**Lesson:** Architecture review should trace every acceptance criterion to a literal function
signature, not just a data-flow diagram.
**What happened:** `docs/ARCH.md`'s original §4.1 for STORY-FING-01 only specified
`tokenize(record: dict, ...)`. AC1 literally says "must accept a valid JSONL input string" —
a distinct, testable entry point that never got a signature in the architecture doc. It slipped
through Smith's Gate 2 review too (Smith checked HCI/UX concerns, not AC-to-signature
traceability — correctly outside Smith's remit). Trin caught it at Phase 1 UAT by checking the
AC text line-by-line against the actual code, not just running the existing test suite (which
passed 17/17 with the gap present).
**Applying it:** Trin's Artifact-Based Verification protocol ("never guess, check artifacts
first") is what caught this — worth reinforcing as the actual backstop for AC-to-code gaps,
since neither Smith's UX gate nor a green test suite alone will catch a missing entry point.
Morpheus should also do one AC-by-AC signature pass at code review, not just structural/smell
review, for stories with a literal "accepts X input format" clause.

**Lesson:** When an AC's wording is ambiguous about *when* an action happens (STORY-FING-02's
sample ring: "Drift State: ... insert into a ring buffer" vs. a Verification Task implying
ongoing rotation), check whether the literal reading makes the story's own Verification Task
testable at all. If it doesn't, the literal reading is probably wrong.
**Applying it:** This resolved the Warehouse sample-ring-growth ambiguity (see
`docs/DECISIONS.md`) without needing another round-trip through Cypher/Smith — Trin adjudicated
it directly against the story's own text, Morpheus endorsed at review. Good pattern for future
POCs with inherited/pre-written ACs where the original author isn't in the loop to clarify.

## 2026-07-12 — Documentation Pass (User Guide + Demo)

> **Superseded 2026-10-13:** the two-file layout this lesson describes (`Makefile.prj` + stubs
> routed through `mkf.py`) is gone. The project has one Makefile; add a target there once. The
> "lesson under the lesson" — read the tool's own documentation before diagnosing — still holds.

**Lesson:** `make demo` failed with "No rule to make target" after adding `demo` only to
`Makefile.prj`. My first diagnosis (Oracle persona) blamed `_IS_BOB_ENTRY`/`Makefile.bob`
detection — plausible-looking but wrong. The actual, documented root cause (per the `make`
skill and `make-discover` skill): **every target needs an explicit stub in both files** —
the real recipe in `Makefile.prj`, *and* a public stub (`target: ## comment` +
`@./agents/tools/mkf.py $(V) $@`) added to the `else` block's `.PHONY` line and target list in
the root `Makefile`. There is no generic catch-all for `Makefile.prj` targets; `make help`
lists them by reading `Makefile.prj` directly, which is why the target *looked* wired up
correctly even though invocation failed.
**Applying it (fixed 2026-07-12):** Added the missing `demo` stub to `Makefile`'s `else` block.
While fixing it, found `tldr` had the *same* bug — a pre-existing gap in the bob-protocol
Makefile itself (not introduced this sprint), silently broken because nothing had exercised
plain `make tldr` before. Fixed both; verified with `make help` (target appears twice: once
per file, per the skill's own verification instructions), `make demo`, `make tldr`, and a full
`make test` (50/50, no regressions). **Lesson under the lesson:** when diagnosing a tooling
failure, check the authoritative skill/doc for the *intended* design before inferring root
cause from symptoms — the real answer was one skill-read away, not a guess.

## 2026-07-21 — Sprint 2: Live Ingestion & Pipeline Polish

**Lesson:** In-process HTTP server tests must isolate their reference states.
**What happened:** During the first `make test` pass after implementing `fingerling/server.py`, the `test_post_valid_telemetry_returns_success` test failed because it was sharing the `Warehouse` and `SlidingWindowMatcher` instances with other tests. The state accumulated across tests, causing the matcher to warm up and trigger unexpected policy compilations.
**Applying it:** Reset shared states (e.g. `self.warehouse._records.clear()` and `self.matcher._window.clear()`) in `setUp()` to keep tests isolated.

**Lesson:** Use dynamic local imports to break circular dependencies in library utility helpers.
**What happened:** The new `build_whitelist` function in `warehouse.py` needed `tokenize` from `tokenizer.py`, which itself imported classes from other modules. Placing `from fingerling.tokenizer import tokenize` dynamically inside the function resolved the issue cleanly.
**Applying it:** Keep modularity high by using dynamic imports when a specific utility function needs cross-module capabilities.

## 2026-07-21 — Sprint 3: Automated GitOps Delivery Pipeline

**Lesson:** Fallback GPG signature checks simplify offline developer workflows.
**What happened:** GPG cryptographic signing requires local keys and a running gpg-agent, which is typically not present on standard test runner environments. Designing the module to raise clear exceptions on key absence and making it configurable allowed mock/offline repo tests to bypass signing while keeping logic verified.
**Applying it:** Ensure automated environment requirements fail gracefully and provide config toggles for localized test coverage.

## 2026-07-21 — Sprint 4: Controlled Exposure Sandbox (Vaccination)

**Lesson:** Implement runtime fallback mechanisms for infrastructure dependencies in test suites.
**What happened:** Writing process PIDs directly to `/sys/fs/cgroup/...` requires superuser access and system-level setup that is unavailable in sandbox container testing environments. Providing a subprocess fallback that logs warnings instead of hard-failing ensures test coverage stays green across all host environments.
**Applying it:** Fallback gracefully to simulated or process-level isolation when hardware/OS features (cgroups, network layers) are restricted.

**Lesson:** Prefer E2E verification tests that validate actual network loopbacks over pure telemetry mocks.
**What happened:** Warming up the sliding-window matcher was initially done via simulated direct JSON telemetry POSTs. By updating the tests and demos to execute actual HTTP GET requests (`/ping?host=127.0.0.1`) to the vulnerable application, we verified app server reachability, response codes, and actual HTTP behavior alongside pipeline telemetry.
**Applying it:** Ensure integration test warmups trace actual application routes whenever possible to uncover network-level failures early.

## 2026-07-22 — Sprint 5: Interactive Split-Pane Terminal UX Demo

**Lesson:** Location-agnostic path injection resolves import errors for standalone CLI scripts.
**What happened:** When `examples/interactive_controller.py` was first run, it failed with `ModuleNotFoundError: No module named 'examples'` because the project root directory was not in python's `sys.path`. Resolving this by inserting the parent directory dynamically at script startup (`sys.path.insert(0, ...)`) made the script location-agnostic.
**Applying it:** For any new scripts located in subdirectories (like `examples/`), dynamically resolve the path to the workspace root at the very top of the script so developers can execute it from anywhere.

**Lesson:** Multi-process tmux scripts must handle non-interactive TTY environments.
**What happened:** Executing `make demo-interactive` inside the sandboxed shell ran into `open terminal failed: not a terminal` because the runner environment lacks a real TTY for attaching to a `tmux` session.
**Applying it:** Add dynamic TTY checking (`! tty -s` or standard stream verification) to launcher scripts so they automatically fall back to single-terminal inline execution when running in automated testing pipelines or non-interactive shells.

## 2026-07-22 — Sprint 6: Rich TUI Dashboard UX Epic

**Lesson:** Vertical compounding of rich layout panels requires console Group containers.
**What happened:** Nesting multiple panels inside a single `rich.layout.Layout` cell via positional arguments (e.g. `Layout(Panel(a), Panel(b))`) raises a `TypeError` because Layout's constructor expects a single renderable. This was resolved by wrapping the panels inside a `rich.console.Group` object before returning it to the layout update function.
**Applying it:** When grouping multiple separate panel cards inside a layout cell, always collect them under a single `Group` container to preserve rendering flow.

**Lesson:** Temporarily stopping/starting `Live` rendering contexts simplifies stdin read gates in TUIs.
**What happened:** Running keyboard input prompts inside an active `rich.live.Live` context is prone to rendering jitter and cursor mismatch because standard stream buffering conflicts with curses-like terminal takeovers. Stopping the live context (`live.stop()`) before calling `input()` and restarting it immediately after (`live.start()`) provides an extremely simple and robust input gateway that works on any terminal without requiring complex low-level keyboard hook libraries.

## 2026-08-08 — Sprint 7

See `agents/oracle/lessons.md`: `rich.text.Text` does not parse bracket markup; extend an existing
TUI step rather than renumbering.

## 2026-10-12 — Sprint 8: Fingerprint Sampling CLI

**Lesson:** When swapping an implementation behind a stable contract, prove equivalence by running old and new side by side, not by trusting the test suite.
**What happened:** Replacing the hand-rolled JSONPath resolver risked silently changing fingerprint IDs. Trin loaded the pre-sprint `tokenizer.py` from git alongside the new one and compared tokens for every `(path, modifier)` literal in the repo across edge-case records (90 comparisons, 0 differences).
**Applying it:** For any "same behaviour, new engine" change, keep the old module importable from `git show HEAD:<file>` and diff outputs over real inputs before deleting it.

**Lesson:** Check how the interpreter is managed before choosing a dependency.
**What happened:** The Pi's system Python is PEP 668 "externally managed" — `pip install` (even `--user`) is refused, and existing deps came from apt. A project `.venv` with `--system-site-packages` added the library without touching the system or losing the apt packages.
**Applying it:** New dependencies go in `pyproject.toml` and are installed with `make install`. Run everything through `make` so the venv interpreter is used.

**Lesson:** A type change surfaces dead attribute access.
**What happened:** `examples/demo.py` read `entry.raw_record`, an attribute `FingerprintRecord` never had; it only escaped notice because that branch needs a live eBPF run. It was found while migrating callers to the new record shape.
**Applying it:** When changing a dataclass, grep every attribute access on it, including in code paths the tests cannot reach.

**Lesson:** Make "merge" and "first run" the same code path.
**What happened:** Because aggregator state is plain data that is loaded and folded further, batch-vs-split equivalence needed no special merge logic and holds at every split point.
**Applying it:** Prefer resumable state over a separate merge routine when a tool accumulates across runs.

## 2026-10-13 — Sprint 9: Fingerprint Package + SDLC Tooling

**Lesson:** A formatter's defaults reach further than you expect — check the first diff before committing it.
**What happened:** `ruff format .` also reformatted Python code blocks inside Markdown, breaking hand-aligned signature sketches in `docs/ARCH.md`. Separately, running ruff with no explicit rule selection flagged dozens of style rules beyond the intended baseline.
**Applying it:** Pin the rule list and the exclusions in `pyproject.toml`, and put a mechanical reformat in its own commit so it can be reviewed and reverted alone.

**Lesson:** A shell pipe hides the exit status you care about.
**What happened:** The first `make test-all` piped test output through `tail`, so a failing Python version would have reported success.
**Applying it:** In Makefile recipes capture output to a variable and test the command's own status; never judge success through a pipe.

**Lesson:** uv picks its own interpreter unless told otherwise.
**What happened:** After `make test-all` downloaded Pythons 3.10-3.12, the next `uv sync` rebuilt `.venv` on 3.12 instead of the system 3.13.
**Applying it:** Keep `.python-version` in the repo for the development interpreter, and set `UV_PYTHON` explicitly where a different one is wanted (the CI matrix).

**Lesson:** To split a package without touching its callers, move the code and leave re-export shims at the old paths.
**What happened:** Parked modules and their tests import `fingerling.tokenizer` / `fingerling.warehouse`; those now re-export the same objects from `fingerprint_sampler`, so the split needed no edits to parked code. A set file written before the split merged with identical IDs afterwards.
**Applying it:** Verify a move with an artifact produced by the old layout, and with the new package installed alone in a clean environment.

