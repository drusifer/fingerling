# Next Steps

## Immediate Next Action
None — real eBPF capture + live exploit demo delivered, verified end-to-end, committed
(`4e38116`), and pushed. No further action planned.

## Waiting On
Nothing.

## Planned Work
- [ ] If future project targets are added, remember the two-file pattern (Makefile.prj recipe
      + Makefile else-block stub) — `make help | grep <target>` should show it twice.
- [ ] Backlog, not scheduled: real `connect()` dport extraction (needs BTF or `buf()`-based raw
      byte parsing — see context.md's 2026-07-13 entry), Sprint 2's other 3 stories
      (`docs/USER_STORIES_SPRINT2.md`, still pending Smith Gate 1 review).
- [ ] `tools/capture_syscalls.bt` only traces `execve`; connect/read/write/close were explicitly
      scoped out of v1 (no payoff for the execve-only anomaly signal this demo needs) — revisit
      if a future scenario needs them.

---
*Last updated: 2026-07-13T17:15*
