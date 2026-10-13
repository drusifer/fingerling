"""The fingerprint tool lives in `fingerprint_sampler`; `fingerling` re-exports it.

These tests cover what stayed on the fingerling side of the split: the
compatibility imports, the telemetry aggregate set, the N-gram baseline
helper, the eBPF example profile and the `fingerling fingerprint` alias.
"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

import yaml

import fingerling.aggregators
import fingerling.profile
import fingerling.tokenizer
import fingerling.warehouse
import fingerprint_sampler
from fingerling.cli import main as fingerling_main
from fingerling.tokenizer import MaskEntry, tokenize
from fingerling.warehouse import TELEMETRY_AGGREGATES, Warehouse, build_whitelist, fingerprint_id
from fingerprint_sampler import aggregators as fs_aggregators
from fingerprint_sampler import profile as fs_profile
from fingerprint_sampler import tokenizer as fs_tokenizer
from fingerprint_sampler import warehouse as fs_warehouse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_EXAMPLES = os.path.join(REPO_ROOT, "packages", "fingerprint-sampler", "examples")


class ShimTests(unittest.TestCase):
    def test_fingerling_names_are_the_fingerprint_sampler_objects(self):
        self.assertIs(fingerling.tokenizer.tokenize, fs_tokenizer.tokenize)
        self.assertIs(fingerling.tokenizer.MaskEntry, fs_tokenizer.MaskEntry)
        self.assertIs(fingerling.tokenizer._MISSING, fs_tokenizer._MISSING)
        self.assertIs(fingerling.aggregators.make_entry, fs_aggregators.make_entry)
        self.assertIs(fingerling.profile.load_profile, fs_profile.load_profile)
        self.assertIs(fingerling.warehouse.Warehouse, fs_warehouse.Warehouse)
        self.assertIs(fingerling.warehouse.fingerprint_id, fs_warehouse.fingerprint_id)
        self.assertIs(fingerling.warehouse.ProfileMismatchError, fs_warehouse.ProfileMismatchError)

    def test_telemetry_helpers_do_not_ship_in_the_fingerprint_package(self):
        self.assertFalse(hasattr(fs_warehouse, "TELEMETRY_AGGREGATES"))
        self.assertFalse(hasattr(fs_warehouse, "build_whitelist"))
        self.assertFalse(hasattr(fingerprint_sampler, "build_whitelist"))


class TelemetryAggregatesTests(unittest.TestCase):
    def test_tracks_duration_bounds_and_last_three_raw_events(self):
        wh = Warehouse(aggregates=TELEMETRY_AGGREGATES)
        tokens = {"a": "1"}
        for i, duration in enumerate((5.0, 1.0, 9.0, 3.0)):
            wh.upsert(tokens, {"seq": i, "duration_ms": duration}, timestamp=f"t{i}")

        aggregates = wh.get(fingerprint_id(tokens)).aggregates
        self.assertEqual(aggregates["duration_ms"], {"MIN": 1.0, "MAX": 9.0})
        self.assertEqual([s["seq"] for s in aggregates["samples"]["LAST"]], [1, 2, 3])


class BuildWhitelistTests(unittest.TestCase):
    def test_builds_correct_whitelisted_ngrams(self):
        records = [
            {"process_kprobe": {"function_name": "sys_connect"}},
            {"process_kprobe": {"function_name": "sys_write"}},
            {"process_kprobe": {"function_name": "sys_close"}},
        ]
        profile = [MaskEntry("sys", "$.process_kprobe.function_name", "DEFAULT")]

        whitelist = build_whitelist(records, profile, n=2)

        fids = [fingerprint_id(tokenize(r, profile)) for r in records]
        self.assertEqual(whitelist, {(fids[0], fids[1]), (fids[1], fids[2])})


class EbpfProfileTests(unittest.TestCase):
    def test_shipped_ebpf_profile_loads(self):
        path = os.path.join(REPO_ROOT, "examples", "profiles", "ebpf_telemetry.yaml")
        profile = fingerling.profile.load_profile(path)
        self.assertEqual(
            [f.key for f in profile.fields], ["hook_syscall", "exec_target", "kernel_return_state"]
        )


class FingerlingAliasTests(unittest.TestCase):
    def run_alias(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = fingerling_main(list(argv))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_fingerling_fingerprint_still_merges(self):
        with tempfile.TemporaryDirectory() as tmp:
            set_path = os.path.join(tmp, "set.yaml")
            code, _, err = self.run_alias(
                "fingerprint",
                "-p",
                os.path.join(PACKAGE_EXAMPLES, "access_log.yaml"),
                "-s",
                set_path,
                os.path.join(PACKAGE_EXAMPLES, "access_log.jsonl"),
            )
            self.assertEqual(code, 0, err)
            with open(set_path) as f:
                self.assertEqual(len(yaml.safe_load(f)["fingerprints"]), 4)

    def test_alias_help_names_the_alias(self):
        code, out, _ = self.run_alias("fingerprint", "--help")
        self.assertEqual(code, 0)
        self.assertIn("usage: fingerling fingerprint", out)

    def test_anything_else_says_what_to_run_instead(self):
        for argv in ((), ("merge",), ("bogus",)):
            with self.subTest(argv=argv):
                code, _, err = self.run_alias(*argv)
                self.assertEqual(code, 2)
                self.assertIn("fingerprint merge", err)

    def test_missing_environment_gives_install_hint_not_traceback(self):
        # Simulate a Python without the project's packages (e.g. the system interpreter).
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "fingerprint_sampler.py"), "w") as f:
                f.write(
                    "raise ModuleNotFoundError(\"No module named 'fingerprint_sampler'\","
                    " name='fingerprint_sampler')\n"
                )
            result = subprocess.run(
                [sys.executable, "-m", "fingerling", "fingerprint", "--help"],
                cwd=REPO_ROOT,
                env=dict(os.environ, PYTHONPATH=tmp),
                capture_output=True,
                text=True,
                timeout=60,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("make install", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
