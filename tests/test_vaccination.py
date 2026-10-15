"""Tests for STORY-FING-16: End-to-End Vaccination & GitOps Verification."""

from __future__ import annotations

import json
import os
import socket
import tempfile
import threading
import unittest
import urllib.request

from sketchtastic import Field, Sketch

from examples.vulnerable_app import run_app
from fingerling.gitops import initialize_repo
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.vaccine import run_vaccination


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class E2EVaccinationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo_path = os.path.join(self.tmpdir.name, "gitops-repo")
        initialize_repo(self.repo_path, default_branch="main")

        self.app_port = get_free_port()
        self.app_server = run_app(self.app_port)
        self.app_thread = threading.Thread(target=self.app_server.serve_forever)
        self.app_thread.daemon = True
        self.app_thread.start()

        self.webhook_port = get_free_port()
        self.warehouse = Sketch()
        # Seed whitelist with the baseline transition: (fid_ping, fid_ping)
        from sketchtastic import skit_id

        fid_ping = skit_id({"hook_syscall": "ping"})
        self.matcher = SlidingWindowMatcher(n=2, whitelist={(fid_ping, fid_ping)})
        self.mask_profile = [Field("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")]
        self.webhook_server = run_server(
            port=self.webhook_port,
            warehouse=self.warehouse,
            matcher=self.matcher,
            mask_profile=self.mask_profile,
            workload_name="vulnerable-target-app",
            match_labels={"app": "vuln-app"},
            gitops_repo_path=self.repo_path,
            gpg_sign=False,
        )
        self.webhook_thread = threading.Thread(target=self.webhook_server.serve_forever)
        self.webhook_thread.daemon = True
        self.webhook_thread.start()

    def tearDown(self) -> None:
        self.app_server.shutdown()
        self.app_server.server_close()
        self.app_thread.join()

        self.webhook_server.shutdown()
        self.webhook_server.server_close()
        self.webhook_thread.join()

        self.tmpdir.cleanup()

    def test_end_to_end_vaccination_flow_merges_policy(self) -> None:
        webhook_url = f"http://127.0.0.1:{self.webhook_port}/telemetry"

        # Step 1: Run baseline telemetry to warm up the matcher
        # We need 2 baseline calls to fill the window (n=2)
        base_telemetry = '{"process_kprobe": {"function_name": "ping"}, "duration_ms": 10.0}'
        for _ in range(2):
            # 1. Send the actual GET request to the target app with normal characters
            base_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1"
            with urllib.request.urlopen(base_url) as resp:
                resp.read()

            # 2. Warm up the server's telemetry pipeline
            req = urllib.request.Request(
                webhook_url,
                data=base_telemetry.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(res["status"], "success")

        # Step 2: Trigger vaccine (baseline request + exploit request)
        res = run_vaccination(self.app_port, webhook_url)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exploit_response"]["gitops_status"], "success")

        # Verify that policy was committed and merged to main branch
        policy_file = os.path.join(
            self.repo_path, "policies", "fingerling-vulnerable-target-app.yaml"
        )
        self.assertTrue(os.path.exists(policy_file))

        with open(policy_file) as f:
            yaml_content = f.read()

        self.assertIn("KubeArmorPolicy", yaml_content)
        self.assertIn("vulnerable-target-app", yaml_content)
        self.assertIn("app: vuln-app", yaml_content)

        # Step 3: Deploy the policy (antibody) to the target app environment and retrigger exploit
        # Shut down the unprotected vulnerable app instance
        self.app_server.shutdown()
        self.app_server.server_close()
        self.app_thread.join()

        # Start a new vulnerable app instance bound to the compiled GitOps policy file
        self.app_server = run_app(self.app_port, policy_file=policy_file)
        self.app_thread = threading.Thread(target=self.app_server.serve_forever)
        self.app_thread.daemon = True
        self.app_thread.start()

        # Retrigger the exploit request and assert it is blocked by KubeArmor (returning 403)
        exploit_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1;echo%20boo"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(exploit_url)
        self.assertEqual(ctx.exception.code, 403)
        self.assertIn("Blocked by KubeArmorPolicy", ctx.exception.read().decode("utf-8"))

        # Assert normal traffic (baseline) still succeeds perfectly!
        base_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1"
        with urllib.request.urlopen(base_url) as resp:
            self.assertEqual(resp.status, 200)


if __name__ == "__main__":
    unittest.main()
