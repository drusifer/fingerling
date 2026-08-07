# Live eBPF TUI Capture Summary

**Date:** 2026-07-22T22:47
**Author:** Neo (Senior Software Engineer)
**Sprint:** Sprint 6 - E2E eBPF Capture Support in TUI

## Work Completed
1. **Subprocess Server Launch**:
   - Refactored [examples/tui_demo.py](file:///home/drusifer/Projects/fingerling/examples/tui_demo.py) to launch the vulnerable target app as an isolated subprocess using `subprocess.Popen` instead of a background thread.
   - Wired a background logs forwarding thread to pipe the target app's output/request logs dynamically into the log pipe to preserve the scrolling console logs panel.
2. **Dynamic bpftrace Probing**:
   - Added automatic probe-check in the constructor to verify if `sudo bpftrace` is available on the hosting system.
   - If available, the TUI runs in **Live eBPF Tracing Mode**:
     - Attaches `bpftrace` (`tools/capture_syscalls.bt`) to the target app subprocess PID.
     - Spawns the capture streams dynamically during Step 3 (Baseline) and Step 4 (Exploit Detonation).
     - Streams actual kernel `execve()` syscall events captured from child processes directly into the tokenization and webhook matching pipeline.
     - Resolves whitelisted fingerprint hashes back to binary names for transitions display.
     - If `bpftrace` or root is not available, it displays a status message and falls back to simulated tracing.
3. **Decisions Logged**: Recorded the live eBPF TUI capture integration in [docs/DECISIONS.md](file:///home/drusifer/Projects/fingerling/docs/DECISIONS.md).
4. **Verification**: Checked that `make test` runs 100% clean and E2E simulation triggers exit with code 0.
