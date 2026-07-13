# Current Task

**Status:** Complete
**Assigned to:** Neo (implicit — implementation work done directly, not via formal Bloop handoff)
**Started:** 2026-07-13

## Task Description
User asked directly for "a way to capture the eBPF sequences from a real process," then "a real
exploit we can use as a demo/test case." Built real bpftrace-based syscall capture plus a real,
safe, local CWE-78 command-injection demo to exercise it end-to-end — see the plan at
`/home/drusifer/.claude/plans/deep-prancing-donut.md` for the full design and its Context section.

## Progress
- [x] Installed `bpftrace` v0.23.2 via apt (confirmed no BTF on this kernel — see context.md)
- [x] `tools/capture_syscalls.bt` — process-subtree execve tracer (fork-propagation via
      `sched_process_fork`, cleanup via `sched_process_exit` guarded `pid == tid`)
- [x] `fingerling/capture.py` — pure ENTER/EXIT-pairing parser (`tests/test_capture.py`, 10
      unit tests, offline) + `run_capture`/`stop_capture`/CLI (`python -m fingerling.capture`)
- [x] `examples/vuln_ping_app.py` — minimal loopback-only CWE-78 Flask target
- [x] `examples/demo_live_exploit.py` — real baseline capture -> real attack capture -> same
      tokenizer/warehouse/ringbuffer/policy pipeline as `examples/demo.py`, on real data
- [x] `Makefile.prj` + `Makefile` else-block stub for `demo-live` (two-file pattern from the
      2026-07-12 Makefile fix, applied correctly first try)
- [x] `docs/USER_GUIDE.md` — new "Live Capture (Real eBPF)" section + updated Known Gaps
- [x] Found and fixed 2 real bugs via live testing (stderr pipe deadlock risk; `sched_process_exit`
      firing per-thread not per-process) — see context.md for full writeups
- [x] Verified: `make test` (60/60, offline), `sudo make demo-live` end-to-end (anomaly detected,
      policy compiled, `/tmp/pwned_poc` confirmed then cleaned up, no orphaned processes)
- [x] Committed as `4e38116` and pushed to `origin/main`

## Blockers
None

## Oracle Consultations
None — this was direct user-driven implementation outside the formal sprint Bloop (a Sprint 2
planning pass was in progress via Cypher but got redirected mid-flow; see
`agents/cypher.docs/current_task.md` and the separate commit `6ed562b` for that unfinished
thread, which is unrelated to this task).

---
*Last updated: 2026-07-13T17:15*
