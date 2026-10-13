#!/usr/bin/env python3
"""CLI runner helper for fingerling.server (STORY-FING-19)."""

from __future__ import annotations

import argparse
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.server import run_server
from fingerling.tokenizer import MaskEntry
from fingerling.warehouse import TELEMETRY_AGGREGATES, Warehouse, fingerprint_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Telemetry Webhook Server Runner")
    parser.add_argument("--port", type=int, default=8081, help="Server port")
    parser.add_argument("--repo-path", type=str, required=True, help="Path to the GitOps repository")
    args = parser.parse_args()

    # Pre-seed whitelist with (ping, ping)
    fid_ping = fingerprint_id({"hook_syscall": "ping"})
    matcher = SlidingWindowMatcher(n=2, whitelist={(fid_ping, fid_ping)})
    mask_profile = [
        MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT")
    ]
    warehouse = Warehouse(aggregates=TELEMETRY_AGGREGATES)

    server = run_server(
        port=args.port,
        warehouse=warehouse,
        matcher=matcher,
        mask_profile=mask_profile,
        workload_name="vulnerable-target-app",
        match_labels={"app": "vuln-app"},
        gitops_repo_path=args.repo_path,
        gpg_sign=False,
    )
    print(f"Telemetry Webhook server running on port {args.port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Webhook server...")
        sys.exit(0)


if __name__ == "__main__":
    main()
