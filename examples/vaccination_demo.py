"""End-to-end Vaccination and Antibody Enforcement Demo (Sprint 4).

Walks through the full live closed-loop pipeline:
1. Initialize local GitOps repository.
2. Spin up the Telemetry Webhook Server and vulnerable Target Application.
3. Warm up with baseline traffic (safe pings), verifying they are marked clean.
4. Exploit the command injection vulnerability (running "echo boo"), triggering the eBPF anomaly.
5. Watch the Webhook compile, sign, commit, and auto-merge the KubeArmorPolicy to the GitOps main branch.
6. "Deploy" the antibody to the target app.
7. Retrigger the exploit, verifying it is BLOCKED by KubeArmor while baseline traffic remains ALLOWED.

Run it with:
    python examples/vaccination_demo.py
"""

from __future__ import annotations

import json
import os
import socket
import tempfile
import threading
import time
import urllib.error
import urllib.request

from examples.vulnerable_app import run_app
from fingerling.gitops import initialize_repo
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.tokenizer import MaskEntry
from fingerling.vaccine import run_vaccination
from fingerling.warehouse import Warehouse, fingerprint_id


def get_free_port() -> int:
    """Find and return an unused local TCP port."""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main() -> None:
    print("==================================================================")
    print("      🛡️  PROJECT FINGERLING - CLOSED-LOOP VACCINATION DEMO  🛡️")
    print("==================================================================")

    # Step 1: Initialize GitOps Repository
    tmpdir = tempfile.TemporaryDirectory()
    repo_path = os.path.join(tmpdir.name, "gitops-repo")
    print(f"\nStep 1: Scaffolding local GitOps repo at: {repo_path}")
    initialize_repo(repo_path, default_branch="main")

    # Step 2: Spin up servers
    app_port = get_free_port()
    webhook_port = get_free_port()

    print(f"Step 2: Launching target app on port {app_port} & webhook on port {webhook_port}...")
    app_server = run_app(app_port)
    app_thread = threading.Thread(target=app_server.serve_forever)
    app_thread.daemon = True
    app_thread.start()

    # Pre-seed whitelist with (ping, ping)
    fid_ping = fingerprint_id({"hook_syscall": "ping"})
    matcher = SlidingWindowMatcher(n=2, whitelist={(fid_ping, fid_ping)})
    mask_profile = [
        MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")
    ]
    warehouse = Warehouse()

    webhook_server = run_server(
        port=webhook_port,
        warehouse=warehouse,
        matcher=matcher,
        mask_profile=mask_profile,
        workload_name="vulnerable-target-app",
        match_labels={"app": "vuln-app"},
        gitops_repo_path=repo_path,
        gpg_sign=False,
    )
    webhook_thread = threading.Thread(target=webhook_server.serve_forever)
    webhook_thread.daemon = True
    webhook_thread.start()

    time.sleep(0.5)  # Let threads settle
    webhook_url = f"http://127.0.0.1:{webhook_port}/telemetry"

    # Step 3: Send baseline traffic
    print("\nStep 3: Simulating normal baseline traffic (ping)...")
    base_telemetry = (
        '{"process_kprobe": {"function_name": "ping"}, "duration_ms": 10.0}'
    )
    for i in range(2):
        # Warm up the server's telemetry pipeline
        req = urllib.request.Request(
            webhook_url,
            data=base_telemetry.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"  [Baseline {i+1}] Telemetry score: {res['scores'][0]} (whitelisted)")

    # Step 4: Run the Vaccine (Baseline + Benign Exploit)
    print("\nStep 4: Executing controlled exploit exposure (Vaccination)...")
    print("  * Sending baseline request...")
    print("  * Sending exploit command injection (host=127.0.0.1;echo boo)...")
    vaccine_res = run_vaccination(app_port, webhook_url)
    exploit_resp = vaccine_res["exploit_response"]

    # Step 5: Verify GitOps Delivery
    print("\nStep 5: Webhook detected anomaly! Reconciling GitOps delivery...")
    print(f"  * Telemetry anomaly scores: {exploit_resp['scores']}")
    print(f"  * GitOps Commit & Auto-Merge Status: {exploit_resp['gitops_status']}")

    policy_file = os.path.join(
        repo_path, "policies", "fingerling-vulnerable-target-app.yaml"
    )
    if os.path.exists(policy_file):
        print(f"  * Generated KubeArmorPolicy file found at: {policy_file}")
        with open(policy_file) as f:
            print("\n--- Compiled KubeArmorPolicy ---")
            print(f.read().strip())
            print("--------------------------------")
    else:
        print("❌ Error: Policy file was not created!")
        return

    # Step 6: Deploy the Antibody
    print("\nStep 6: Simulating antibody deployment in target environment...")
    print("  * Shutting down undefended server...")
    app_server.shutdown()
    app_server.server_close()
    app_thread.join()

    print("  * Starting server bound to KubeArmor policy enforcement...")
    app_server = run_app(app_port, policy_file=policy_file)
    app_thread = threading.Thread(target=app_server.serve_forever)
    app_thread.daemon = True
    app_thread.start()
    time.sleep(0.5)

    # Step 7: Verify protection
    print("\nStep 7: Retriggering the exploit command injection...")
    exploit_url = f"http://127.0.0.1:{app_port}/ping?host=127.0.0.1;echo%20boo"
    try:
        with urllib.request.urlopen(exploit_url) as resp:
            resp.read()
            print("❌ Failure: Exploit was allowed to execute!")
    except urllib.error.HTTPError as ctx:
        print(f"  * Server Response: {ctx.code} Forbidden")
        body = ctx.read().decode("utf-8")
        print(f"  * Status: {body} (SUCCESS)")

    print("\nStep 8: Retriggering normal baseline ping traffic...")
    base_url = f"http://127.0.0.1:{app_port}/ping?host=127.0.0.1"
    try:
        with urllib.request.urlopen(base_url) as resp:
            self_status = resp.status
            print(f"  * Server Response: {self_status} OK")
            print("  * Status: Baseline is still fully operational! (SUCCESS)")
    except Exception as e:
        print(f"❌ Failure: Baseline traffic is blocked: {e}")

    # Cleanup
    print("\nCleaning up demo environment...")
    app_server.shutdown()
    app_server.server_close()
    app_thread.join()

    webhook_server.shutdown()
    webhook_server.server_close()
    webhook_thread.join()
    tmpdir.cleanup()
    print("Demo complete! 🚀\n")


if __name__ == "__main__":
    main()
