"""Tests for STORY-FING-14: Vulnerable Target Application."""

from __future__ import annotations

import socket
import threading
import unittest
import urllib.error
import urllib.request
from examples.vulnerable_app import run_app


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class VulnerableAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = get_free_port()
        cls.server = run_app(cls.port)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def test_ping_endpoint_normal_execution(self) -> None:
        url = f"http://127.0.0.1:{self.port}/ping?host=127.0.0.1"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertIn("Stdout", body)

    def test_ping_endpoint_command_injection(self) -> None:
        # Injecting 'echo pwned-exploit-trigger'
        # Space should be url encoded as %20
        url = f"http://127.0.0.1:{self.port}/ping?host=127.0.0.1;echo%20pwned-exploit-trigger"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertIn("pwned-exploit-trigger", body)

    def test_missing_host_returns_400(self) -> None:
        url = f"http://127.0.0.1:{self.port}/ping"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 400)

    def test_ping_endpoint_blocked_by_policy(self) -> None:
        import tempfile
        import os
        import hashlib
        fid_echo = hashlib.md5(b"hook_syscall:echo").hexdigest()
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tf:
            tf.write(
                f"metadata:\n  annotations:\n    fingerling.io/anomalous-trajectory: 'ping,{fid_echo}'\n".encode("utf-8")
            )
            policy_path = tf.name

        try:
            port = get_free_port()
            server = run_app(port, policy_path)
            t = threading.Thread(target=server.serve_forever)
            t.daemon = True
            t.start()

            url = f"http://127.0.0.1:{port}/ping?host=127.0.0.1;echo%20boo"
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(url)
            self.assertEqual(ctx.exception.code, 403)
            body = ctx.exception.read().decode("utf-8")
            self.assertIn("Blocked by KubeArmorPolicy", body)

            # Normal ping without echo should still work
            url_ok = f"http://127.0.0.1:{port}/ping?host=127.0.0.1"
            with urllib.request.urlopen(url_ok) as resp:
                self.assertEqual(resp.status, 200)

            server.shutdown()
            server.server_close()
            t.join()
        finally:
            if os.path.exists(policy_path):
                os.remove(policy_path)


if __name__ == "__main__":
    unittest.main()
