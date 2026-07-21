"""Vulnerable target web application exposing command injection (STORY-FING-14)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


class VulnerableHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Suppress logging to keep tests quiet
        pass

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/ping":
            query = parse_qs(parsed.query)
            host = query.get("host", [""])[0]
            if not host:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing host parameter")
                return

            try:
                # Unsanitized command execution mimicking CWE-78
                cmd = f"ping -c 1 {host}"
                res = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=5
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(
                    f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}".encode("utf-8")
                )
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


def run_app(port: int) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), VulnerableHandler)
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    srv = run_app(args.port)
    print(f"Vulnerable app running on port {args.port}...")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping vulnerable app...")
        sys.exit(0)
