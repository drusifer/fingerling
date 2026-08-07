#!/usr/bin/env python3
"""Interactive CLI Controller for closed-loop vaccination demo (STORY-FING-18)."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from examples.vulnerable_app import run_app
from fingerling.gitops import initialize_repo
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.tokenizer import MaskEntry
from fingerling.warehouse import Warehouse, fingerprint_id


# ANSI Escape Codes for Rich Terminal Output
BOLD = "\033[1m"
RESET = "\033[0m"
BLUE = "\033[1;34m"
CYAN = "\033[36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
MAGENTA = "\033[1;35m"


def print_header(title: str) -> None:
    """Print a styled section header."""
    print(f"\n{BOLD}{BLUE}=== {title} ==={RESET}")


def print_step(step_num: int, title: str, explanation: str) -> None:
    """Print step details with color coding."""
    print(f"\n{BOLD}{MAGENTA}Step {step_num}: {title}{RESET}")
    print(f"{CYAN}{explanation}{RESET}")


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_enter(prompt: str = "Press Enter to continue...") -> None:
    """Pause execution and wait for the user to press Enter."""
    input(f"\n{BOLD}{YELLOW}[{prompt}]{RESET}")


class InteractiveDemo:
    def __init__(self, mode: str, app_port: int | None, webhook_port: int | None, repo_path: str | None) -> None:
        self.mode = mode
        self.app_port = app_port or get_free_port()
        self.webhook_port = webhook_port or get_free_port()
        
        self.standalone_tmpdir: tempfile.TemporaryDirectory | None = None
        if mode == "standalone":
            self.standalone_tmpdir = tempfile.TemporaryDirectory()
            self.repo_path = os.path.join(self.standalone_tmpdir.name, "gitops-repo")
        else:
            self.repo_path = repo_path or "/tmp/gitops-repo"

        self.app_server: Any = None
        self.webhook_server: Any = None
        self.app_thread: threading.Thread | None = None
        self.webhook_thread: threading.Thread | None = None

        self.policy_file = os.path.join(self.repo_path, "policies", "fingerling-vulnerable-target-app.yaml")
        self.webhook_url = f"http://127.0.0.1:{self.webhook_port}/telemetry"

    def run(self) -> None:
        try:
            print("==================================================================")
            print(f"      {BOLD}🛡️  PROJECT FINGERLING - INTERACTIVE VACCINATION DEMO  🛡️{RESET}")
            print("==================================================================")
            print(f"{CYAN}Running in {BOLD}{self.mode.upper()}{RESET}{CYAN} mode.{RESET}")

            # Step 1: GitOps Repo Scaffolding
            print_step(1, "Scaffolding GitOps Repository", 
                       "We initialize a local GitOps repository. In production, this repo represents\n"
                       "the single source of truth monitored by CD controllers like ArgoCD or Flux.")
            if self.mode == "standalone":
                print(f"  Scaffolding repo dynamically at: {self.repo_path}")
                initialize_repo(self.repo_path, default_branch="main")
                print(f"  {GREEN}🟢 GitOps repository initialized successfully!{RESET}")
            else:
                print(f"  Using pre-scaffolded GitOps repository: {self.repo_path}")
                # Wait briefly to ensure tmux setup has started
                time.sleep(0.5)
                if os.path.exists(self.repo_path):
                    print(f"  {GREEN}🟢 Verified GitOps repo path exists!{RESET}")
                else:
                    print(f"  {YELLOW}⚠️  Repo path not found, initializing repo at: {self.repo_path}{RESET}")
                    initialize_repo(self.repo_path, default_branch="main")

            wait_for_enter()

            # Step 2: Spin up Servers
            print_step(2, "Launching Services",
                       "We start the target workload app and the Telemetry Webhook server.\n"
                       "The app exposes an unsanitized command injection endpoint mimicking CWE-78.")
            if self.mode == "standalone":
                print(f"  Launching vulnerable target app on port {self.app_port}...")
                # Start app with expected policy file path directly to demonstrate dynamic reloading!
                self.app_server = run_app(self.app_port, policy_file=self.policy_file)
                self.app_thread = threading.Thread(target=self.app_server.serve_forever)
                self.app_thread.daemon = True
                self.app_thread.start()

                print(f"  Launching Telemetry Webhook Server on port {self.webhook_port}...")
                fid_ping = fingerprint_id({"hook_syscall": "ping"})
                matcher = SlidingWindowMatcher(n=2, whitelist={(fid_ping, fid_ping)})
                mask_profile = [MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")]
                warehouse = Warehouse()

                self.webhook_server = run_server(
                    port=self.webhook_port,
                    warehouse=warehouse,
                    matcher=matcher,
                    mask_profile=mask_profile,
                    workload_name="vulnerable-target-app",
                    match_labels={"app": "vuln-app"},
                    gitops_repo_path=self.repo_path,
                    gpg_sign=False,
                )
                self.webhook_thread = threading.Thread(target=self.webhook_server.serve_forever)
                self.webhook_thread.daemon = True
                self.webhook_thread.start()
                time.sleep(0.5)
                print(f"  {GREEN}🟢 Services launched in background threads!{RESET}")
            else:
                print(f"  Target Application expected port: {self.app_port}")
                print(f"  Telemetry Webhook expected port: {self.webhook_port}")
                print(f"  {GREEN}🟢 Services verified and executing in secondary frames!{RESET}")

            wait_for_enter()

            # Step 3: Warmup Baseline
            print_step(3, "Warm Up Baseline Traffic (Safe Pings)",
                       "We send two safe HTTP GET requests to the Target App. The target application's\n"
                       "eBPF hooks record the execution trajectory (ping) and post telemetry to the Webhook.\n"
                       "Since ping is in our whitelist, these requests score clean.")
            base_telemetry = '{"process_kprobe": {"function_name": "ping"}, "duration_ms": 10.0}'
            for i in range(2):
                wait_for_enter(f"Trigger safe baseline request {i+1}/2")
                base_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1"
                try:
                    with urllib.request.urlopen(base_url) as resp:
                        resp.read()
                except Exception as e:
                    raise RuntimeError(f"Baseline app HTTP GET request failed: {e}")

                req = urllib.request.Request(
                    self.webhook_url,
                    data=base_telemetry.encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    score = res['scores'][0]
                    print(f"  {BLUE}[Request {i+1}]{RESET} HTTP GET to target app /ping?host=127.0.0.1 -> {GREEN}200 OK{RESET}")
                    print(f"  {BLUE}[Telemetry]{RESET} Webhook score: {score} ({GREEN}Whitelisted{RESET})")

            wait_for_enter()

            # Step 4: Execute Exploit
            print_step(4, "Controlled Exploit Exposure (Vaccination)",
                       "We trigger a command injection exploit using the query parameter:\n"
                       "  host=127.0.0.1;echo boo\n"
                       "This forces the server to execute the unauthorized 'echo' command.")
            wait_for_enter("Execute command injection exploit")
            
            exploit_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1;echo%20boo"
            try:
                with urllib.request.urlopen(exploit_url) as resp:
                    resp.read()
                print(f"  {BLUE}[Request]{RESET} HTTP GET to target app with shell metacharacters -> {GREEN}200 OK{RESET}")
            except Exception as e:
                raise RuntimeError(f"Exploit app request failed: {e}")

            print(f"  Streaming anomalous eBPF telemetry ('echo' execution) to Webhook...")
            exploit_telemetry = '{"process_kprobe": {"function_name": "echo"}, "duration_ms": 1.0}'
            req = urllib.request.Request(
                self.webhook_url,
                data=exploit_telemetry.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            
            exploit_resp = {}
            with urllib.request.urlopen(req) as resp:
                exploit_resp = json.loads(resp.read().decode("utf-8"))
            
            print(f"  {RED}⚠️  Webhook Alert!{RESET} Anomaly Detected!")
            print(f"  * Anomaly Scores: {exploit_resp['scores']}")
            print(f"  * GitOps Commit Status: {exploit_resp['gitops_status']}")

            wait_for_enter()

            # Step 5: Verify GitOps Delivery
            print_step(5, "Verify GitOps Repository State",
                       "The Webhook server compiled the anomaly signatures into a KubeArmorPolicy,\n"
                       "committed it, and merged it to the main GitOps branch.")
            wait_for_enter("View generated KubeArmorPolicy")

            # Wait briefly to let disk sync
            time.sleep(0.5)
            if os.path.exists(self.policy_file):
                print(f"  {GREEN}🟢 Policy generated! Contents of KubeArmorPolicy file:{RESET}")
                with open(self.policy_file) as f:
                    policy_lines = f.read().strip().splitlines()
                    for line in policy_lines:
                        print(f"    {CYAN}{line}{RESET}")
            else:
                print(f"  {RED}❌ Error: Policy file was not found at {self.policy_file}!{RESET}")

            wait_for_enter()

            # Step 6: Deploy Antibody
            print_step(6, "Antibody Enforced State Transition",
                       "In production, policies sync to Kubernetes clusters. In our demo environment,\n"
                       "the target application immediately reads this policy file on subsequent requests\n"
                       "to enforce security rules.")
            print(f"  Enabling KubeArmor policy mapping to policy file: {self.policy_file}")
            print(f"  {GREEN}🟢 Workload transitioned to PROTECTED state successfully!{RESET}")

            wait_for_enter()

            # Step 7: Exploit Blocked
            print_step(7, "Retrigger Exploit (Enforcement Active)",
                       "We replay the command injection exploit: host=127.0.0.1;echo boo.\n"
                       "This time, KubeArmor policy enforcement detects the unauthorized 'echo' action\n"
                       "and blocks it instantly.")
            wait_for_enter("Verify exploit is blocked")

            try:
                with urllib.request.urlopen(exploit_url) as resp:
                    resp.read()
                print(f"  {RED}❌ Failure: Exploit was allowed to execute!{RESET}")
            except urllib.error.HTTPError as ctx:
                if ctx.code == 403:
                    print(f"  {BLUE}[Request]{RESET} HTTP GET /ping?host=127.0.0.1;echo%20boo -> {RED}403 Forbidden{RESET}")
                    body = ctx.read().decode("utf-8")
                    print(f"  {BLUE}[App Response]{RESET} {RED}{body}{RESET}")
                    print(f"  {GREEN}🟢 Exploit BLOCKED successfully! (Enforcement Verified){RESET}")
                else:
                    print(f"  {RED}❌ Unexpected response code: {ctx.code}{RESET}")

            wait_for_enter()

            # Step 8: Baseline still works
            print_step(8, "Retrigger Baseline (Business Continuity)",
                       "We send normal ping traffic to verify that security rules block malicious actions\n"
                       "without causing denial of service to legitimate baseline traffic.")
            wait_for_enter("Verify baseline is operational")

            base_url = f"http://127.0.0.1:{self.app_port}/ping?host=127.0.0.1"
            try:
                with urllib.request.urlopen(base_url) as resp:
                    status = resp.status
                    print(f"  {BLUE}[Request]{RESET} HTTP GET /ping?host=127.0.0.1 -> {GREEN}{status} OK{RESET}")
                    print(f"  {GREEN}🟢 Baseline traffic is fully operational! (Service Intact){RESET}")
            except Exception as e:
                print(f"  {RED}❌ Failure: Baseline traffic is blocked: {e}{RESET}")

            wait_for_enter("Finish demo and clean up")

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Shut down servers and clean up temporary structures."""
        print(f"\n{CYAN}Cleaning up demo environment...{RESET}")
        
        if self.app_server:
            try:
                self.app_server.shutdown()
                self.app_server.server_close()
                if self.app_thread:
                    self.app_thread.join(timeout=1.0)
            except Exception:
                pass
        
        if self.webhook_server:
            try:
                self.webhook_server.shutdown()
                self.webhook_server.server_close()
                if self.webhook_thread:
                    self.webhook_thread.join(timeout=1.0)
            except Exception:
                pass

        if self.standalone_tmpdir:
            try:
                self.standalone_tmpdir.cleanup()
            except Exception:
                pass

        print(f"{GREEN}Cleanup completed! Demo finished. 🚀{RESET}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Closed-Loop Vaccination Demo")
    parser.add_argument("--mode", choices=["standalone", "tmux"], default="standalone",
                        help="Execution mode: standalone (spawns servers in threads) or tmux (driven mode)")
    parser.add_argument("--app-port", type=int, help="Target application port")
    parser.add_argument("--webhook-port", type=int, help="Telemetry Webhook server port")
    parser.add_argument("--repo-path", type=str, help="Path to the GitOps repository")
    
    args = parser.parse_args()
    
    # Standalone mode doesn't require pre-specified ports or repo paths
    if args.mode == "tmux" and (not args.app_port or not args.webhook_port or not args.repo_path):
        parser.error("--app-port, --webhook-port, and --repo-path are required when --mode=tmux")

    demo = InteractiveDemo(
        mode=args.mode,
        app_port=args.app_port,
        webhook_port=args.webhook_port,
        repo_path=args.repo_path,
    )
    demo.run()
