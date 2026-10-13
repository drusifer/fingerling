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
- 2026-10-12 Sprint 8 P1 done: tokenizer uses python-jsonpath (compile_path cached, find_values, tokenize_values); resolve_path/resolve_segments/has_wildcard removed. Makefile has PYTHON var + install target; always run tests via bobp make test (uses .venv).
- 2026-10-12 Sprint 8 P2 done: aggregators.update(state, entry, record)->skipped; state keyed by fn NAME (LAST not LAST(3)); Warehouse(aggregates, profile_id).upsert(tokens, record, timestamp); save atomic; load(path, force) raises FingerprintSetError/ProfileMismatchError; TELEMETRY_AGGREGATES replaces hardcoded duration/samples. demo.py entry.raw_record bug fixed via entry.tokens['exec_target'].
- 2026-10-12 Sprint 8 P3 done: profile.py + validate_modifier; examples/profiles/{ebpf_telemetry,access_log}.yaml, examples/data/access_log.jsonl (8 events -> used by CLI tests).
- 2026-10-12 Sprint 8 P4 done: cli.py/_fold_stream, __main__.py dependency hint, make fingerprint, tests/test_cli.py (in-process main() + subprocess entry-point tests). Set YAML uses sort_keys=False (header, then tokens, counters, aggregates). Not run: sudo make demo-live (no TTY in session) — demo.py changes are 3 lines (TELEMETRY_AGGREGATES, len(warehouse), entry.tokens).
- 2026-10-12 Sprint 8 closed. One post-UAT fix: argparse prog='python -m fingerling'.

## Current Task
**Sprint:** 8 — Fingerprint Sampling CLI (`docs/USER_STORIES_SPRINT8.md`, board: `task.md`)
**Status:** Sprint 8 complete

## Next Steps
No pending tasks.

---
*Last updated: 2026-10-12T21:29:12-04:00*
