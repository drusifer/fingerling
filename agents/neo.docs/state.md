# Agent State

## Context
## Recent Decisions
- Package layout: `fingerling/{tokenizer,warehouse,ringbuffer,policy}.py` + `tests/test_*.py`,
  per `docs/ARCH.md` §6. Only `make test` target exists in this repo (no `test-q`/`lint`/`install`
  yet despite SKILL.md mentioning them) — using `make test` for all phases; not adding the
  extra targets since nothing in this POC needs lint/coverage tooling yet (YAGNI).

## Key Findings
- Phase 1 (tokenizer): hand-rolled dot/bracket-index path resolver via regex, sentinel
  `_MISSING` object distinguishes "absent" from `None`. Modifier registry is a plain dict of
  callables keyed by name parsed from `NAME(args)` strings.

## Important Notes
- `apply_modifier` raises `ValueError` on unknown modifier names immediately (no separate
  profile-load validation step added — no persistent "engine" object exists to validate at
  load time for a stateless functional module, so validating at first use is equivalent).

## 2026-07-13: Real eBPF capture (tools/capture_syscalls.bt + fingerling/capture.py)
- This Pi's kernel (`6.12.62+rpt-rpi-2712`) has NO BTF (`/sys/kernel/btf/vmlinux` absent,
  `CONFIG_DEBUG_INFO_BTF` not set in `/boot/config-*`). bpftrace can't resolve named struct
  casts (`struct sockaddr_in *`) without it, and raw pointer arithmetic on a user pointer
  (`*(uint8*)uptr(args->uservaddr+2)`) reliably read 0 in a live test against a known-nonzero
  port. `str()`/plain integer tracepoint fields work fine without BTF though — so `execve()`
  tracing (via `str(args->filename)`) is unaffected; only raw socket-argument extraction
  (`connect()`'s dport) is blocked. Rebuilding the kernel with BTF is a multi-hour undertaking,
  not attempted — not needed since the capture tool's only consumer (`examples/demo_live_exploit.py`)
  has an execve-only anomaly signal.
- bpftrace requires root; `sudo bpftrace <script> <pid>` takes ~1-2s to JIT-compile and attach
  probes. Any traffic generated before that completes is silently dropped, not queued — solved
  with an explicit `printf("READY\n")` in `BEGIN` that callers block on before generating traffic
  (`fingerling.capture.wait_ready`), not a blind `sleep()`.
- **Two real bugs found only by testing against the live Flask target, not by reasoning about
  the design:**
  1. `run_capture` originally opened `stderr=subprocess.PIPE` but nothing ever read it. An
     unread pipe fills its OS buffer once bpftrace writes enough to it, blocking bpftrace's own
     `write()` and silently stalling its whole event loop — not just losing diagnostics, losing
     later *events*. Fixed by merging `stderr=subprocess.STDOUT` (safe once the parser tolerates
     non-tab-delimited lines).
  2. Tracing a real Flask (Werkzeug dev server) process captured only the *first* of 3 identical
     baseline requests' forked children, deterministically, regardless of delay between
     requests — ruled out pid-reuse/races by reproducing directly against bpftrace with no
     Python wrapper involved. Root cause: `sched_process_exit` fires per-*task* (thread), not
     per-process, and Werkzeug spawns a helper thread that exits early; a thread's exit shares
     its process's tgid, so it satisfied the same `@target[pid]` predicate as a full process exit
     and deleted the *root* pid's tracking entry after request 1 — orphaning every subsequent
     fork's parent-lookup. Fixed with a `pid == tid` guard in the `sched_process_exit` probe
     (only the thread-group leader has `pid == tid`; ordinary thread exits don't). **General
     lesson: any bpftrace subtree tracer that cleans up on process-exit needs this guard if the
     traced process might be multi-threaded — a plain `/@target[pid]/` predicate silently breaks
     tracking the first time a thread (not the whole process) exits.**
- bpftrace auto-prints any non-empty global map on exit (an unsuppressed `@target[<pid>]: 1`
  line, since the root pid's entry is never deleted while it's still alive) — added an
  `END { clear(@target); }` block, and separately made the Python parser skip (not raise on)
  any non-tab-delimited line, since real-world bpftrace output isn't guaranteed to be 100%
  clean data lines (startup banners, diagnostics, map dumps).
- Confirmed the `Makefile.prj` recipe + `Makefile` else-block stub two-file pattern (see the
  2026-07-12 entry below) still holds — applied it correctly for the new `demo-live` target on
  the first attempt this time, verified via `make -n demo-live` and `make help | grep demo-live`
  before running the real thing.

## 2026-07-12: Makefile fix
- Every `make` target needs TWO stubs: the real recipe in `Makefile.prj`, and a public stub in
  `Makefile`'s `else` block (`.PHONY` entry + `@./agents/tools/mkf.py $(V) $@`). Missing the
  second one produces "No rule to make target" on plain invocation even though `make help`
  shows the target correctly (help reads `Makefile.prj` directly). Fixed `demo` (my own
  incomplete addition) and `tldr` (pre-existing gap, not introduced this sprint) — see
  `docs/LESSONS.md` for the full writeup.

## Current Task
**Status:** Phase 1 complete — Trin's AC7 finding (stale telemetry-widget caption after Step 7
overwrites `policy_manifest`) fixed: caption now branches on whether `matchPattern` is present
in the current manifest. Also fixed markup: `rich.text.Text.append()`/`Text(...)` do NOT parse
`[bold]...[/bold]` bracket markup (confirmed empirically) — my new narrative/widget text uses
real `style="bold"` spans instead. Pre-existing bracket-markup instances elsewhere in the file
are out of scope for this story, left as-is. Re-verified: 88/88 tests, smoke test sequence
unchanged, widget caption confirmed correct via direct Console render. Handed back to Trin.
**Assigned to:** Neo
**Started:** 2026-08-08

## Task Description
STORY-FING-22 (Sprint 7, fast-track): add a comprehensive, pattern-based (`;`) block
alongside the existing exact-fingerprint block in the live demo, entirely via fingerling's
policy layer — zero changes to `vulnerable_app.py`'s vulnerable `cmd = f"ping -c 1 {host}"` /
`shell=True` line. Note the Makefile note above (two-file `Makefile.prj`/mkf.py stub pattern)
is now obsolete — Sprint 6 consolidated the Makefile to a single self-contained file with no
`-include Makefile.prj` at all; ignore that pattern for any new targets going forward.

## Progress
- [x] TDD: added `test_block_pattern_omitted_by_default` / `test_block_pattern_adds_match_pattern_field`
      to `tests/test_policy.py` first, then implemented.
- [x] `fingerling/policy.py`: `compile_policy()` gained optional `block_pattern: str | None`
      param → emits `spec.process.matchPattern` only when passed; `matchPaths`/existing fields
      untouched when omitted. 10/10 `test_policy.py` passing.
- [x] TDD: added 3 tests to `tests/test_vulnerable_app.py` (novel payload NOT blocked by
      fingerprint-only policy; blocked by matchPattern policy; clean traffic unaffected by
      matchPattern policy), then implemented.
- [x] `examples/vulnerable_app.py`: added an independent `matchPattern` check in the existing
      "Simulated KubeArmor Policy Enforcement" block, alongside (not replacing) the fingerprint
      check. 7/7 `test_vulnerable_app.py` passing.
- [x] `examples/demo.py`: extended Step 7 (narrative + `run_step_actions`) rather than inserting
      a new numbered step — avoids touching the `while self.step <= 8` loop bound and the
      `step == 1 or step == 8` layout branch in a large, fragile, manually-choreographed TUI
      file. Sequence: retrigger original exploit (existing, unchanged) → novel `;id` payload
      (200, narrow policy blind spot, per Smith's explicit note) → compile+write comprehensive
      policy via `compile_policy(..., block_pattern=";")`, preserving the existing
      `anomalous-trajectory` annotation read back from `self.policy_file` → retry both payloads
      (403/403) → clean baseline (200).
- [x] `make test`: 88/88 passing (83 pre-existing + 5 new: 2 in `test_policy.py`, 3 in
      `test_vulnerable_app.py`). No regressions.
- [x] Scripted smoke test of `examples/demo.py` steps 2→7 (`TUIDemo` driven directly, bypassing
      the interactive `Live`/keypress loop): confirmed via `client_log_pipe.get_logs()` the
      exact expected sequence — novel payload 200 → both payloads 403/403 under comprehensive
      policy → baseline 200. No exceptions.
- [ ] Did NOT run the actual interactive `sudo make demo-live` TUI end-to-end (needs a real
      terminal + sudo password prompt, not available in this session) — flagging for Trin/Smith
      to do a real interactive pass if possible, though the scripted smoke test exercises the
      exact same `run_step_actions` code path.

## Blockers
None.

## Oracle Consultations
None needed — straightforward additive change, no ambiguity requiring history lookup.

## Next Steps
## Immediate Next Action
Trin: run `make test` (88/88 expected), review the 5 new/changed test cases against
STORY-FING-22's AC1-AC7 in `docs/USER_STORIES_SPRINT7.md`, and — if a real terminal is
available — do one interactive `sudo make demo-live` pass through step 7 to confirm the TUI
rendering (colors/narrative) looks right, not just the underlying logic.

## Waiting On
Trin (`*qa uat phase-1`).

## Planned Work
- [ ] None beyond this story — Sprint 7 is single-phase.

---
*Last updated: 2026-08-08T15:00:00-04:00*
