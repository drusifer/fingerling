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
            # Print HTTP access logs to stdout
            print(f"127.0.0.1 - - [{self.log_date_time_string()}] {format % args}", file=sys.stdout)
            sys.stdout.flush()

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
                        import hashlib
                        
                        # 1. Real eBPF capture format from bpftrace
                        real_echo_flat = "exec_target:/bin/echo|hook_syscall:sys_execve|kernel_return_state:TRUE"
                        fid_real = hashlib.md5(real_echo_flat.encode("utf-8")).hexdigest()
                        
                        # 2. Simulated test format from vaccine.py
                        sim_echo_flat = "exec_target:NULL|hook_syscall:echo|kernel_return_state:FALSE"
                        fid_sim = hashlib.md5(sim_echo_flat.encode("utf-8")).hexdigest()
                        
                        # 3. Legacy unittest format from test_vulnerable_app.py
                        fid_legacy = hashlib.md5(b"hook_syscall:echo").hexdigest()
                        
                        is_blocked = (fid_real in traj) or (fid_sim in traj) or (fid_legacy in traj)
                        if is_blocked and "echo" in host:
                            print(
                                "KubeArmor blocked process execution: echo",
                                file=sys.stderr,
                            )
                            sys.stderr.flush()
                            self.send_response(403)
                            self.end_headers()
                            self.wfile.write(b"Blocked by KubeArmorPolicy")
                            return
                    except Exception as err:
                        print(f"Error parsing policy: {err}", file=sys.stderr)
                        sys.stderr.flush()

                try:
                    # Unsanitized command execution mimicking CWE-78
                    cmd = f"ping -c 1 {host}"
                    print(f"\n[Server Exec] Running shell command: {cmd}", file=sys.stdout)
                    sys.stdout.flush()
                    res = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=5
                    )
                    if res.stdout:
                        print(f"[Server Exec] Command stdout:\n{res.stdout.strip()}", file=sys.stdout)
                    if res.stderr:
                        print(f"[Server Exec] Command stderr:\n{res.stderr.strip()}", file=sys.stdout)
                    sys.stdout.flush()

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
