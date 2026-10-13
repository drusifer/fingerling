"""Tests for STORY-FING-15: Controlled Exposure Replay Engine."""

from __future__ import annotations

import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from examples.vulnerable_app import run_app
from fingerling.vaccine import run_vaccination


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class MockWebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_POST(self) -> None:
        if self.path == "/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "success", "policies": ["mock-policy"]}')


class VaccineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_port = get_free_port()
        self.app_server = run_app(self.app_port)
        self.app_thread = threading.Thread(target=self.app_server.serve_forever)
        self.app_thread.daemon = True
        self.app_thread.start()

        self.webhook_port = get_free_port()
        self.webhook_server = HTTPServer(("127.0.0.1", self.webhook_port), MockWebhookHandler)
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

    def test_run_vaccination_replays_successfully(self) -> None:
        webhook_url = f"http://127.0.0.1:{self.webhook_port}/telemetry"
        res = run_vaccination(self.app_port, webhook_url)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exploit_response"]["policies"], ["mock-policy"])


if __name__ == "__main__":
    unittest.main()
