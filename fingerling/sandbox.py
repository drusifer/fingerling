"""Sandbox containment and cgroup scaffolding module (STORY-FING-13)."""

from __future__ import annotations

import os
import subprocess
import sys


def run_in_sandbox(command: list[str], cgroup_name: str | None = None) -> subprocess.Popen:
    """Launch a command inside a subprocess with optional cgroup v2 resource limits.

    Falls back gracefully to plain subprocess execution if cgroups v2 is not supported
    or running without root permissions.
    """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if cgroup_name:
        cgroup_path = f"/sys/fs/cgroup/{cgroup_name}"
        try:
            # Attempt to write the PID to cgroups procs file
            os.makedirs(cgroup_path, exist_ok=True)
            with open(os.path.join(cgroup_path, "cgroup.procs"), "w") as f:
                f.write(str(proc.pid))
        except (PermissionError, FileNotFoundError, OSError) as err:
            # Gracefully log warning on fallback
            print(
                f"Warning: Cgroup assignment failed: {err}. "
                "Falling back to standard process isolation.",
                file=sys.stderr,
            )

    return proc
