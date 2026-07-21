"""Tests for STORY-FING-02: stateful append-only upsert warehouse."""

import os
import tempfile
import unittest

from fingerling.warehouse import Warehouse, fingerprint_id


class FingerprintIdTests(unittest.TestCase):
    def test_sorts_keys_before_hashing_serialization_drift_prevention(self):
        # AC1: alphabetical sort by key before flattening - insertion order must not matter.
        tokens_a = {"b_key": "1", "a_key": "2"}
        tokens_b = {"a_key": "2", "b_key": "1"}
        self.assertEqual(fingerprint_id(tokens_a), fingerprint_id(tokens_b))

    def test_returns_32_char_hex_md5(self):
        fid = fingerprint_id({"a": "1"})
        self.assertEqual(len(fid), 32)
        int(fid, 16)  # raises ValueError if not valid hex

    def test_different_tokens_yield_different_ids(self):
        self.assertNotEqual(fingerprint_id({"a": "1"}), fingerprint_id({"a": "2"}))


class UpsertReconciliationTests(unittest.TestCase):
    def test_match_state_increments_occurrences_without_new_record(self):
        wh = Warehouse()
        tokens = {"hook_syscall": "sys_connect"}

        wh.upsert(tokens, duration_ms=1.0, raw_record={"n": 1}, timestamp="t1")
        wh.upsert(tokens, duration_ms=2.0, raw_record={"n": 2}, timestamp="t2")
        wh.upsert(tokens, duration_ms=3.0, raw_record={"n": 3}, timestamp="t3")

        self.assertEqual(len(wh), 1)  # entry list count stays flat
        record = wh.get(fingerprint_id(tokens))
        self.assertEqual(record.total_occurrences, 3)
        self.assertEqual(record.last_seen, "t3")
        self.assertEqual(record.first_seen, "t1")

    def test_drift_state_creates_new_record_block(self):
        wh = Warehouse()
        wh.upsert({"a": "1"}, duration_ms=1.0, raw_record={}, timestamp="t1")
        wh.upsert({"a": "2"}, duration_ms=1.0, raw_record={}, timestamp="t1")

        self.assertEqual(len(wh), 2)

    def test_updates_moving_min_max_duration_bounds(self):
        wh = Warehouse()
        tokens = {"a": "1"}
        wh.upsert(tokens, duration_ms=5.0, raw_record={}, timestamp="t1")
        wh.upsert(tokens, duration_ms=1.0, raw_record={}, timestamp="t2")
        wh.upsert(tokens, duration_ms=9.0, raw_record={}, timestamp="t3")

        record = wh.get(fingerprint_id(tokens))
        self.assertEqual(record.min_duration_ms, 1.0)
        self.assertEqual(record.max_duration_ms, 9.0)

    def test_sample_ring_caps_at_three_and_rotates_oldest(self):
        wh = Warehouse()
        tokens = {"a": "1"}
        for i in range(5):
            wh.upsert(tokens, duration_ms=1.0, raw_record={"seq": i}, timestamp=f"t{i}")

        record = wh.get(fingerprint_id(tokens))
        self.assertEqual(len(record.samples), 3)
        # oldest (seq 0, 1) rotated out; newest 3 retained in order
        self.assertEqual([s["seq"] for s in record.samples], [2, 3, 4])


class PersistenceTests(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        wh = Warehouse()
        tokens = {"a": "1"}
        wh.upsert(tokens, duration_ms=1.0, raw_record={"x": 1}, timestamp="t1")
        wh.upsert(tokens, duration_ms=2.0, raw_record={"x": 2}, timestamp="t2")

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fingerprints.yaml")
            wh.save(path)

            reloaded = Warehouse()
            reloaded.load(path)

        original = wh.get(fingerprint_id(tokens))
        restored = reloaded.get(fingerprint_id(tokens))
        self.assertEqual(restored.total_occurrences, original.total_occurrences)
        self.assertEqual(restored.samples, original.samples)


class BuildWhitelistTests(unittest.TestCase):
    def test_builds_correct_whitelisted_ngrams(self):
        from fingerling.tokenizer import MaskEntry
        from fingerling.warehouse import build_whitelist, fingerprint_id
        from fingerling.tokenizer import tokenize

        records = [
            {"process_kprobe": {"function_name": "sys_connect"}},
            {"process_kprobe": {"function_name": "sys_write"}},
            {"process_kprobe": {"function_name": "sys_close"}},
        ]
        profile = [MaskEntry("sys", "$.process_kprobe.function_name", "DEFAULT")]

        whitelist = build_whitelist(records, profile, n=2)

        fids = [fingerprint_id(tokenize(r, profile)) for r in records]
        expected = {
            (fids[0], fids[1]),
            (fids[1], fids[2]),
        }
        self.assertEqual(whitelist, expected)


if __name__ == "__main__":
    unittest.main()

