"""Controlled exposure (vaccine) replay engine (STORY-FING-15)."""

from __future__ import annotations

import json
import urllib.request


def run_vaccination(app_port: int, webhook_url: str) -> dict:
    """Send baseline and exploit requests to vulnerable app and stream telemetry."""
    # 1. Baseline Requests (Send 2 to warm up target environment)
    base_url = f"http://127.0.0.1:{app_port}/ping?host=127.0.0.1"
    base_telemetry = '{"process_kprobe": {"function_name": "ping"}, "duration_ms": 10.0}'
    for _ in range(2):
        try:
            with urllib.request.urlopen(base_url) as resp:
                resp.read()
        except Exception as e:
            raise RuntimeError(f"Baseline app request failed: {e}")

        # Forward simulated baseline telemetry to webhook (simulating eBPF capture)
        try:
            req = urllib.request.Request(
                webhook_url,
                data=base_telemetry.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                resp.read()
        except Exception as e:
            raise RuntimeError(f"Baseline telemetry posting failed: {e}")

    # 2. Exploit Request
    exploit_url = f"http://127.0.0.1:{app_port}/ping?host=127.0.0.1;echo%20boo"
    try:
        with urllib.request.urlopen(exploit_url) as resp:
            resp.read()
    except Exception as e:
        raise RuntimeError(f"Exploit app request failed: {e}")

    # Forward simulated exploit telemetry to webhook
    exploit_telemetry = '{"process_kprobe": {"function_name": "echo"}, "duration_ms": 1.0}'
    try:
        req = urllib.request.Request(
            webhook_url,
            data=exploit_telemetry.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            exploit_resp = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"Exploit telemetry posting failed: {e}")

    return {"status": "success", "exploit_response": exploit_resp}
