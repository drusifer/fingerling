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


if __name__ == "__main__":
    unittest.main()
