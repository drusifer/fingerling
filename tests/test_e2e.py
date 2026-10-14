"""End-to-end pipeline test: telemetry -> tokens -> fingerprint -> sequence score -> policy.

Exercises all 4 POC modules together the way a real caller would wire them,
per the data flow in docs/ARCH.md §3/§5. Each module already has its own
focused unit tests (test_tokenizer/warehouse/ringbuffer/policy.py); this
test exists to catch integration seams those miss (e.g. a token dict shape
one module produces not matching what the next module expects).
"""

import unittest

import yaml

from fingerling.policy import compile_policy
from fingerling.ringbuffer import SlidingWindowMatcher
from fingerling.tokenizer import parse_jsonl, tokenize
from fingerprint_sampler import Field, FingerprintSet

TELEMETRY_JSONL = "\n".join(
    [
        '{"process_exec": {"process": {"pid": 14205, "binary": "/usr/bin/node"}}, '
        '"process_kprobe": {"function_name": "sys_connect", "return_value": 0, '
        '"args": [{"sock_arg": {"dport": 6379}}]}, "duration_ms": 1.84}',
        '{"process_exec": {"process": {"pid": 14205, "binary": "/usr/bin/node"}}, '
        '"process_kprobe": {"function_name": "sys_write", "return_value": 0, '
        '"args": [{"sock_arg": {"dport": 6379}}]}, "duration_ms": 0.9}',
    ]
)

MASK_PROFILE = [
    Field("hook_syscall", "$.process_kprobe.function_name", "DEFAULT"),
    Field(
        "dest_port",
        "$.process_kprobe.args[0].sock_arg.dport",
        {"name": "ANY", "values": [80, 443, 6379]},
    ),
    Field(
        "kernel_return_state",
        "$.process_kprobe.return_value",
        {"name": "IN_RANGE", "low": -999, "high": 0},
    ),
]


class EndToEndPipelineTests(unittest.TestCase):
    def test_clean_trajectory_stays_below_anomaly_threshold(self):
        records = parse_jsonl(TELEMETRY_JSONL)
        warehouse = FingerprintSet()
        fingerprint_ids = [
            warehouse.upsert(tokenize(record, MASK_PROFILE), record, timestamp=f"t{i}")
            for i, record in enumerate(records)
        ]

        # A matcher whose whitelist contains exactly the observed 2-gram trajectory.
        matcher = SlidingWindowMatcher(n=2, whitelist={tuple(fingerprint_ids)})
        scores = [matcher.push(fid) for fid in fingerprint_ids]

        self.assertEqual(scores, [0.0, 0.0])
        self.assertTrue(matcher.warm)
        self.assertEqual(len(warehouse), 2)  # two distinct syscalls -> two distinct fingerprints

    def test_anomalous_trajectory_triggers_policy_compilation(self):
        records = parse_jsonl(TELEMETRY_JSONL)
        warehouse = FingerprintSet()
        fingerprint_ids = [
            warehouse.upsert(tokenize(record, MASK_PROFILE), record, timestamp="t")
            for record in records
        ]

        # Whitelist only knows a *different* trajectory than what was observed.
        matcher = SlidingWindowMatcher(n=2, whitelist={("unrelated_a", "unrelated_b")})
        scores = [matcher.push(fid) for fid in fingerprint_ids]
        self.assertEqual(scores, [0.0, 1.0])  # warm-up, then anomalous

        anomalous_trajectory = tuple(fingerprint_ids)
        manifest_text = compile_policy(
            workload_name="checkout-backend",
            match_labels={"app": "checkout-backend"},
            anomalous_trajectory=anomalous_trajectory,
        )
        manifest = yaml.safe_load(manifest_text)

        self.assertEqual(manifest["kind"], "KubeArmorPolicy")
        self.assertEqual(manifest["spec"]["selector"]["matchLabels"], {"app": "checkout-backend"})
        self.assertEqual(manifest["spec"]["action"], "Block")
        self.assertEqual(
            manifest["metadata"]["annotations"]["fingerling.io/anomalous-trajectory"],
            ",".join(fingerprint_ids),
        )

    def test_repeated_telemetry_reconciles_as_match_not_drift(self):
        # Same record processed twice end-to-end -> same fingerprint, occurrence count grows,
        # warehouse entry count does not.
        record = parse_jsonl(TELEMETRY_JSONL)[0]
        warehouse = FingerprintSet()

        fid_1 = warehouse.upsert(tokenize(record, MASK_PROFILE), record, timestamp="t1")
        fid_2 = warehouse.upsert(tokenize(record, MASK_PROFILE), record, timestamp="t2")

        self.assertEqual(fid_1, fid_2)
        self.assertEqual(len(warehouse), 1)
        self.assertEqual(warehouse.get(fid_1).total_occurrences, 2)


if __name__ == "__main__":
    unittest.main()
