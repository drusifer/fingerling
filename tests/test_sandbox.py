"""Tests for STORY-FING-13: Sandbox Scaffolding."""

from __future__ import annotations

import sys
import unittest
from fingerling.sandbox import run_in_sandbox


class SandboxTests(unittest.TestCase):
    def test_run_in_sandbox_executes_process(self) -> None:
        # Run a simple python subcommand that prints test
        proc = run_in_sandbox([sys.executable, "-c", "print('hello-sandbox')"])
        stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("hello-sandbox", stdout)

    def test_run_in_sandbox_cgroup_fallback_gracefully(self) -> None:
        # Provide an invalid cgroup name that we don't have permissions to create or write
        # (e.g. nested in root path or fictitious directories), verifying it falls back without crashing
        proc = run_in_sandbox(
            [sys.executable, "-c", "print('fallback-ok')"],
            cgroup_name="invalid/fictitious/cgroup/path/12345",
        )
        stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("fallback-ok", stdout)


if __name__ == "__main__":
    unittest.main()
