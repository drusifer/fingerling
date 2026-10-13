"""Real eBPF syscall capture: bpftrace output -> Tetragon-shaped JSONL.

Pairs the ENTER/EXIT lines emitted by `tools/capture_syscalls.bt` into the
same telemetry record shape `fingerling.tokenizer.parse_jsonl`/`tokenize`
already consume, so a live capture drops into the existing pipeline
unmodified. Only the parsing/formatting logic here is pure and unit tested
(see tests/test_capture.py); `run_capture` is the sole function that shells
out to bpftrace and is exercised manually via `make demo-live`.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import IO, Iterable, Iterator

READY_LINE = "READY"


@dataclass(frozen=True)
class ProbeEvent:
    """One ENTER or EXIT line emitted by the bpftrace capture script."""

    kind: str  # "ENTER" or "EXIT"
    syscall: str
    pid: int
    comm: str
    nsecs: int
    extra: str  # ENTER: exec filename. EXIT: return value (still a string here).


def parse_line(line: str) -> ProbeEvent:
    """Parse one tab-delimited bpftrace output line into a `ProbeEvent`."""
    kind, syscall, pid, comm, nsecs, extra = line.rstrip("\n").split("\t", 5)
    return ProbeEvent(
        kind=kind, syscall=syscall, pid=int(pid), comm=comm, nsecs=int(nsecs), extra=extra
    )


def _to_record(enter: ProbeEvent, exit_: ProbeEvent) -> dict:
    duration_ms = (exit_.nsecs - enter.nsecs) / 1e6
    return {
        "process_exec": {"process": {"pid": enter.pid, "binary": enter.comm}},
        "process_kprobe": {
            "function_name": f"sys_{enter.syscall}",
            "return_value": int(exit_.extra),
            "args": [{"exec_arg": {"filename": enter.extra}}],
        },
        "duration_ms": duration_ms,
    }


def pair_events(events: Iterable[ProbeEvent]) -> Iterator[dict]:
    """Pair ENTER/EXIT events per (pid, syscall) into Tetragon-shaped records.

    Uses a LIFO stack per (pid, syscall) key so nested same-syscall calls on
    the same pid pair correctly. An EXIT with no matching ENTER on its stack
    (capture started mid-call) is skipped with a stderr note. An ENTER still
    unmatched when the stream ends (capture stopped mid-call, or the process
    never exits) is dropped rather than emitted with a fabricated duration or
    return value.
    """
    stacks: dict[tuple[int, str], list[ProbeEvent]] = {}

    for event in events:
        key = (event.pid, event.syscall)
        if event.kind == "ENTER":
            stacks.setdefault(key, []).append(event)
        elif event.kind == "EXIT":
            stack = stacks.get(key)
            if not stack:
                print(f"capture: unmatched EXIT for {key}, skipping", file=sys.stderr)
                continue
            enter = stack.pop()
            yield _to_record(enter, event)

    dropped = sum(len(stack) for stack in stacks.values())
    if dropped:
        print(
            f"capture: {dropped} unmatched ENTER event(s) dropped (mid-call at stream end)",
            file=sys.stderr,
        )


def to_jsonl(records: Iterable[dict]) -> Iterator[str]:
    """Render each record dict as one compact JSON line."""
    for record in records:
        yield json.dumps(record)


def _safe_parse_lines(lines: Iterable[str]) -> Iterator[ProbeEvent]:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == READY_LINE:
            continue
        try:
            yield parse_line(line)
        except ValueError:
            print(f"capture: skipping unparseable line: {line!r}", file=sys.stderr)


def parse_stream(lines: Iterable[str]) -> Iterator[dict]:
    """Parse raw bpftrace stdout lines into records.

    Tolerates the READY sync line, blank lines, and any other non-tab-
    delimited diagnostic output bpftrace may emit (e.g. its startup
    "Attaching N probes..." banner, or an unsuppressed exit-time map dump)
    by skipping and logging rather than raising.
    """
    yield from pair_events(_safe_parse_lines(lines))


def run_capture(
    root_pid: int,
    bt_path: str = "tools/capture_syscalls.bt",
    bpftrace_bin: str = "bpftrace",
) -> subprocess.Popen:
    """Launch `sudo bpftrace <bt_path> <root_pid>`, returning the live process.

    The only function in this module that shells out. Callers must read the
    `READY_LINE` from `proc.stdout` before generating any traffic against the
    traced process -- bpftrace takes ~1-2s to JIT-compile and attach probes,
    and events before that point are silently missed, not queued.

    stderr is merged into stdout rather than opened as its own pipe: an
    unread stderr pipe fills its OS buffer once bpftrace writes enough to
    it, which blocks bpftrace's write() and silently stalls its whole event
    loop -- losing later events, not just diagnostics. Merging is safe now
    that `parse_stream` tolerates non-tab-delimited lines.
    """
    return subprocess.Popen(
        ["sudo", bpftrace_bin, bt_path, str(root_pid)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def wait_ready(stdout: IO[str]) -> None:
    """Block until the `READY_LINE` sync marker is read from `stdout`."""
    for line in stdout:
        if line.strip() == READY_LINE:
            return
    raise RuntimeError("capture process ended before READY was seen")


def stop_capture(proc: subprocess.Popen, timeout: float = 3.0) -> None:
    """Terminate a `run_capture` process, falling back to kill() so a root
    bpftrace process is never left orphaned even if `sudo` doesn't forward
    SIGTERM promptly."""
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=timeout)


def _read_lines_for(proc: subprocess.Popen, seconds: float) -> Iterator[str]:
    """Yield stdout lines from `proc` until it exits or `seconds` elapse, then terminate it."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        yield line
    proc.terminate()
    yield from proc.stdout


def main(argv: list[str] | None = None) -> None:
    """`python -m fingerling.capture --pid <pid> | --cmd "<command>" [--out FILE] [--seconds N]`.

    NOTE: with `--cmd`, the launched command must not fork before bpftrace
    finishes attaching (~1-2s) -- fine for a long-running server that only
    forks on-demand (e.g. examples/vuln_ping_app.py), not for a one-shot
    command that forks immediately on startup.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--pid", type=int, help="Attach to an already-running root pid.")
    target.add_argument("--cmd", help="Launch this command and trace it and its descendants.")
    parser.add_argument("--out", help="Output JSONL path (default: stdout).")
    parser.add_argument(
        "--seconds", type=float, default=10.0, help="Capture duration (default: 10s)."
    )
    args = parser.parse_args(argv)

    launched = subprocess.Popen(shlex.split(args.cmd)) if args.cmd else None
    root_pid = launched.pid if launched else args.pid

    proc = run_capture(root_pid)
    try:
        wait_ready(proc.stdout)
        lines = (line for line in _read_lines_for(proc, args.seconds) if line.strip())
        records = pair_events(parse_line(line) for line in lines)

        out = open(args.out, "w") if args.out else sys.stdout
        try:
            for jsonl_line in to_jsonl(records):
                print(jsonl_line, file=out)
        finally:
            if args.out:
                out.close()
    finally:
        stop_capture(proc)
        if launched:
            launched.terminate()


if __name__ == "__main__":
    main()
