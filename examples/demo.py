"""End-to-end demo of the Project Fingerling POC pipeline.

Walks through the full flow documented in docs/ARCH.md Section 3:

    telemetry (JSONL) -> tokenizer -> warehouse -> ring buffer -> policy

Scenario: "checkout-backend" is observed during a clean baseline window
(connect -> read -> write, repeated). Later, a live session includes one
extra syscall never seen in the baseline. The ring buffer flags the
resulting trajectory as anomalous, and the policy compiler turns that
anomaly into a KubeArmorPolicy manifest.

Run it with:

    python -m examples.demo

Note: the POC has no "observe clean traffic -> build a whitelist" helper
yet (see docs/USER_STORIES.md backlog) - this script builds the whitelist
by hand from the baseline fingerprint stream, which is exactly the manual
step a real caller has to do today.
"""

from __future__ import annotations

import json

from fingerling.policy import compile_policy
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.tokenizer import MaskEntry, parse_jsonl, tokenize
from fingerling.warehouse import Warehouse

WINDOW_N = 2

MASK_PROFILE = [
    MaskEntry("hook_syscall", "$.process_kprobe.function_name", "DEFAULT"),
    MaskEntry(
        "dest_port",
        "$.process_kprobe.args[0].sock_arg.dport",
        "ANY(80, 443, 6379)",
    ),
    MaskEntry("kernel_return_state", "$.process_kprobe.return_value", "IN_RANGE(-999, 0)"),
]


def _telemetry_line(syscall: str, dport: int, duration_ms: float) -> str:
    return json.dumps(
        {
            "process_exec": {"process": {"pid": 14205, "binary": "/usr/bin/node"}},
            "process_kprobe": {
                "function_name": syscall,
                "return_value": 0,
                "args": [{"sock_arg": {"dport": dport}}],
            },
            "duration_ms": duration_ms,
        }
    )


# A "clean" baseline window: connect -> read -> write, twice.
BASELINE_JSONL = "\n".join(
    [
        _telemetry_line("sys_connect", 6379, 1.2),
        _telemetry_line("sys_read", 6379, 0.4),
        _telemetry_line("sys_write", 6379, 0.9),
        _telemetry_line("sys_connect", 6379, 1.1),
        _telemetry_line("sys_read", 6379, 0.3),
        _telemetry_line("sys_write", 6379, 0.8),
    ]
)

# A live session: same pattern, but with an unexpected sys_execve spliced in.
LIVE_JSONL = "\n".join(
    [
        _telemetry_line("sys_connect", 6379, 1.3),
        _telemetry_line("sys_read", 6379, 0.4),
        _telemetry_line("sys_execve", 6379, 4.5),  # never seen during baseline
        _telemetry_line("sys_write", 6379, 0.9),
    ]
)


def build_baseline_whitelist(warehouse: Warehouse, jsonl_text: str) -> set[tuple[str, ...]]:
    """Tokenize + upsert every baseline record, then collect every N-gram observed."""
    records = parse_jsonl(jsonl_text)
    fingerprint_ids = [
        warehouse.upsert(tokenize(r, MASK_PROFILE), duration_ms=r["duration_ms"], raw_record=r)
        for r in records
    ]
    return {
        tuple(fingerprint_ids[i : i + WINDOW_N])
        for i in range(len(fingerprint_ids) - WINDOW_N + 1)
    }


def main() -> None:
    print("=== Stage 1: Baseline (training) telemetry ===")
    warehouse = Warehouse()
    whitelist = build_baseline_whitelist(warehouse, BASELINE_JSONL)
    print(f"Warehouse learned {len(warehouse)} distinct fingerprints from the baseline.")
    print(f"Compiled whitelist of {len(whitelist)} whitelisted {WINDOW_N}-grams.")

    print("\n=== Stage 2: Live telemetry, scored against the baseline ===")
    live_records = parse_jsonl(LIVE_JSONL)
    matcher = SlidingWindowMatcher(n=WINDOW_N, whitelist=whitelist)
    anomalous_ids: list[str] = []

    for record in live_records:
        tokens = tokenize(record, MASK_PROFILE)
        fid = warehouse.upsert(tokens, duration_ms=record["duration_ms"], raw_record=record)
        score = matcher.push(fid)
        syscall = record["process_kprobe"]["function_name"]
        status = "ANOMALOUS" if (matcher.warm and score > 0.05) else "clean/warm-up"
        print(f"  syscall={syscall:<12} fingerprint={fid[:8]}...  score={score}  [{status}]")
        if matcher.warm and score > 0.05:
            anomalous_ids.append(fid)

    print("\n=== Stage 3: Compile a KubeArmorPolicy for the anomalous trajectory ===")
    if not anomalous_ids:
        print("No anomaly detected - nothing to compile.")
        return

    manifest = compile_policy(
        workload_name="checkout-backend",
        match_labels={"app": "checkout-backend"},
        anomalous_trajectory=",".join(anomalous_ids),
    )
    print(manifest)


if __name__ == "__main__":
    main()
