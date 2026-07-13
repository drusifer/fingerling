"""Tests for real eBPF capture parsing (fingerling.capture).

Exercises only the pure parsing/pairing logic against canned bpftrace output
lines -- no root, no bpftrace, no Linux-specific behavior required, keeping
`make test` fully offline per the project's existing convention.
"""

import json
import unittest

from fingerling.capture import ProbeEvent, pair_events, parse_line, parse_stream, to_jsonl

ENTER_SH = "ENTER\texecve\t100\tpython3\t1000\t/bin/sh"
EXIT_SH = "EXIT\texecve\t100\tsh\t1200\t0"
ENTER_PING = "ENTER\texecve\t101\tsh\t1300\t/usr/bin/ping"
EXIT_PING = "EXIT\texecve\t101\tping\t7300\t0"


class ParseLineTests(unittest.TestCase):
    def test_parses_enter_line(self):
        event = parse_line(ENTER_SH)
        self.assertEqual(
            event,
            ProbeEvent(kind="ENTER", syscall="execve", pid=100, comm="python3", nsecs=1000, extra="/bin/sh"),
        )

    def test_parses_exit_line(self):
        event = parse_line(EXIT_SH)
        self.assertEqual(
            event,
            ProbeEvent(kind="EXIT", syscall="execve", pid=100, comm="sh", nsecs=1200, extra="0"),
        )


class PairEventsTests(unittest.TestCase):
    def test_pairs_enter_exit_into_tetragon_shaped_record(self):
        events = [parse_line(ENTER_SH), parse_line(EXIT_SH)]
        records = list(pair_events(events))

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["process_exec"]["process"], {"pid": 100, "binary": "python3"})
        self.assertEqual(record["process_kprobe"]["function_name"], "sys_execve")
        self.assertEqual(record["process_kprobe"]["return_value"], 0)
        self.assertEqual(record["process_kprobe"]["args"][0]["exec_arg"]["filename"], "/bin/sh")
        self.assertAlmostEqual(record["duration_ms"], 0.0002)  # (1200-1000) ns -> ms

    def test_pairs_two_independent_pids_in_order(self):
        events = [parse_line(l) for l in (ENTER_SH, EXIT_SH, ENTER_PING, EXIT_PING)]
        records = list(pair_events(events))

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["process_kprobe"]["args"][0]["exec_arg"]["filename"], "/bin/sh")
        self.assertEqual(records[1]["process_kprobe"]["args"][0]["exec_arg"]["filename"], "/usr/bin/ping")

    def test_nested_same_syscall_same_pid_pairs_lifo(self):
        # Two execve ENTERs on the same pid before either EXIT (re-exec chain) must pair
        # innermost-first: the second ENTER's EXIT comes first in a LIFO nesting.
        events = [
            ProbeEvent("ENTER", "execve", 5, "a", 100, "/bin/outer"),
            ProbeEvent("ENTER", "execve", 5, "b", 110, "/bin/inner"),
            ProbeEvent("EXIT", "execve", 5, "inner", 120, "0"),
            ProbeEvent("EXIT", "execve", 5, "outer", 200, "0"),
        ]
        records = list(pair_events(events))

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["process_kprobe"]["args"][0]["exec_arg"]["filename"], "/bin/inner")
        self.assertEqual(records[1]["process_kprobe"]["args"][0]["exec_arg"]["filename"], "/bin/outer")

    def test_unmatched_exit_is_skipped_not_raised(self):
        events = [ProbeEvent("EXIT", "execve", 5, "a", 100, "0")]
        self.assertEqual(list(pair_events(events)), [])

    def test_unmatched_enter_at_stream_end_is_dropped_not_raised(self):
        events = [ProbeEvent("ENTER", "execve", 5, "a", 100, "/bin/sh")]
        self.assertEqual(list(pair_events(events)), [])


class ToJsonlTests(unittest.TestCase):
    def test_renders_one_compact_json_line_per_record(self):
        records = [{"a": 1}, {"b": 2}]
        lines = list(to_jsonl(records))
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), {"a": 1})
        self.assertEqual(json.loads(lines[1]), {"b": 2})


class ParseStreamTests(unittest.TestCase):
    def test_skips_ready_line_and_blank_lines(self):
        lines = ["READY\n", "\n", ENTER_SH + "\n", EXIT_SH + "\n"]
        records = list(parse_stream(lines))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["process_kprobe"]["function_name"], "sys_execve")

    def test_skips_unsuppressed_map_dump_line_without_raising(self):
        # Real-world bpftrace can print a non-tab-delimited exit-time map dump
        # (e.g. "@target[1234]: 1") if a global map isn't cleared in an END
        # block -- must not crash the parser.
        lines = ["READY\n", ENTER_SH + "\n", EXIT_SH + "\n", "@target[1234]: 1\n"]
        records = list(parse_stream(lines))
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
