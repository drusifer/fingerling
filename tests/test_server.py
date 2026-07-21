"""Tests for STORY-FING-08: stdlib-only Webhook Telemetry Ingestion HTTP Server."""

from __future__ import annotations

import json
import os
import socket
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from fingerling.gitops import initialize_repo
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.tokenizer import MaskEntry
from fingerling.warehouse import Warehouse


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TelemetryServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = get_free_port()
        cls.warehouse = Warehouse()
        # Seed whitelist with one trajectory so we can test match vs anomaly
        cls.matcher = SlidingWindowMatcher(n=2, whitelist={("a1", "b1")})
        cls.mask_profile = [
            MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")
        ]
        cls.server = run_server(
            port=cls.port,
            warehouse=cls.warehouse,
            matcher=cls.matcher,
            mask_profile=cls.mask_profile,
            workload_name="test-workload",
            match_labels={"app": "test"},
        )
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def setUp(self) -> None:
        # Reset the shared pipeline state between test runs
        self.warehouse._records.clear()
        self.matcher._window.clear()

    def test_post_valid_telemetry_returns_success(self) -> None:
        url = f"http://127.0.0.1:{self.port}/telemetry"
        data = '{"process_kprobe": {"function_name": "sys_connect"}, "duration_ms": 1.5}'
        req = urllib.request.Request(
            url,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["processed_records"], 1)
            self.assertEqual(res["scores"], [0.0])  # first push is warm-up -> score 0.0
            self.assertEqual(res["policies"], [])

    def test_post_malformed_json_returns_400(self) -> None:
        url = f"http://127.0.0.1:{self.port}/telemetry"
        data = '{"process_kprobe": {'  # Invalid JSON
        req = urllib.request.Request(
            url,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
        res = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("error", res)

    def test_post_subsequent_valid_request_succeeds_after_error(self) -> None:
        url = f"http://127.0.0.1:{self.port}/telemetry"
        # Malformed first
        req_bad = urllib.request.Request(
            url,
            data=b"bad-data",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(req_bad)

        # Valid second
        req_good = urllib.request.Request(
            url,
            data=b'{"process_kprobe": {"function_name": "sys_write"}}',
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req_good) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["status"], "success")

    def test_post_anomalous_sequence_compiles_policy(self) -> None:
        url = f"http://127.0.0.1:{self.port}/telemetry"
        # We push a sequence of 2 calls. Whitelist is {("a1", "b1")}, so this sequence will be anomalous.
        data1 = '{"process_kprobe": {"function_name": "sys_connect"}}'
        data2 = '{"process_kprobe": {"function_name": "sys_write"}}'
        
        # Send first
        req1 = urllib.request.Request(
            url,
            data=data1.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req1) as resp:
            self.assertEqual(resp.status, 200)

        # Send second -> window is full (n=2), score should be 1.0 (anomalous), policy compiles
        req2 = urllib.request.Request(
            url,
            data=data2.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["scores"], [1.0])
            self.assertEqual(len(res["policies"]), 1)
            self.assertIn("KubeArmorPolicy", res["policies"][0])


class GitOpsTelemetryServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo_path = os.path.join(self.tmpdir.name, "gitops-repo")
        initialize_repo(self.repo_path, default_branch="main")

        self.port = get_free_port()
        self.warehouse = Warehouse()
        self.matcher = SlidingWindowMatcher(n=2, whitelist={("a1", "b1")})
        self.mask_profile = [
            MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")
        ]
        self.server = run_server(
            port=self.port,
            warehouse=self.warehouse,
            matcher=self.matcher,
            mask_profile=self.mask_profile,
            workload_name="test-gitops-workload",
            match_labels={"app": "test-gitops"},
            gitops_repo_path=self.repo_path,
            gpg_sign=False,
        )
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join()
        self.tmpdir.cleanup()

    def test_post_anomalous_sequence_triggers_gitops_commit_and_merge(self) -> None:
        url = f"http://127.0.0.1:{self.port}/telemetry"
        data1 = '{"process_kprobe": {"function_name": "sys_connect"}}'
        data2 = '{"process_kprobe": {"function_name": "sys_write"}}'

        req1 = urllib.request.Request(
            url,
            data=data1.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req1) as resp:
            self.assertEqual(resp.status, 200)

        req2 = urllib.request.Request(
            url,
            data=data2.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req2) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["gitops_status"], "success")

        # Verify the policy file exists in policies/ on main branch
        policy_file = os.path.join(
            self.repo_path, "policies", "fingerling-test-gitops-workload.yaml"
        )
        self.assertTrue(os.path.exists(policy_file))

