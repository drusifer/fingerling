"""Vulnerable target web application exposing command injection (STORY-FING-14)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import yaml


def create_handler(policy_file: str | None = None) -> type[BaseHTTPRequestHandler]:
    """Factory to create a VulnerableHandler, optionally bound to a policy file."""

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

                # Simulated KubeArmor Policy Enforcement
                if policy_file and os.path.exists(policy_file):
                    try:
                        with open(policy_file) as f:
                            policy_data = yaml.safe_load(f)
                        annotations = (
                            policy_data.get("metadata", {}).get("annotations", {})
                        )
                        traj = annotations.get("fingerling.io/anomalous-trajectory", "")
                        # If anomalous trajectory contains the fingerprint ID of echo and host contains 'echo', block execution
                        import hashlib
                        fid_echo = hashlib.md5(b"hook_syscall:echo").hexdigest()
                        if fid_echo in traj and "echo" in host:
                            print(
                                "KubeArmor blocked process execution: echo",
                                file=sys.stderr,
                            )
                            self.send_response(403)
                            self.end_headers()
                            self.wfile.write(b"Blocked by KubeArmorPolicy")
                            return
                    except Exception as err:
                        print(f"Error parsing policy: {err}", file=sys.stderr)

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

    return VulnerableHandler


def run_app(port: int, policy_file: str | None = None) -> HTTPServer:
    handler_class = create_handler(policy_file)
    server = HTTPServer(("127.0.0.1", port), handler_class)
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--policy-file", type=str, default=None)
    args = parser.parse_args()

    srv = run_app(args.port, args.policy_file)
    print(f"Vulnerable app running on port {args.port}...")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping vulnerable app...")
        sys.exit(0)
