"""Tests for STORY-FING-03: sliding window ring buffer matcher."""

import unittest

from fingerling.ringbuffer import SlidingWindowMatcher


class SlidingWindowMatcherTests(unittest.TestCase):
    def test_warmup_phase_returns_zero_for_first_n_minus_one_pushes(self):
        # Verification Task: N=3, first 2 pushed tokens return 0.0 (warm-up).
        whitelist = {("a", "b", "c")}
        matcher = SlidingWindowMatcher(n=3, whitelist=whitelist)

        self.assertEqual(matcher.push("a"), 0.0)
        self.assertEqual(matcher.push("b"), 0.0)
        self.assertFalse(matcher.warm)  # AC1/AC3: not warm until depth n reached

    def test_becomes_warm_once_window_fills(self):
        matcher = SlidingWindowMatcher(n=3, whitelist={("a", "b", "c")})
        matcher.push("a")
        matcher.push("b")
        self.assertFalse(matcher.warm)
        matcher.push("c")
        self.assertTrue(matcher.warm)

    def test_whitelisted_trajectory_scores_zero(self):
        matcher = SlidingWindowMatcher(n=3, whitelist={("a", "b", "c")})
        matcher.push("a")
        matcher.push("b")
        self.assertEqual(matcher.push("c"), 0.0)

    def test_departure_from_whitelist_scores_one(self):
        # Verification Task: a sequence departing the whitelisted trajectory -> 1.0 anomaly.
        matcher = SlidingWindowMatcher(n=3, whitelist={("a", "b", "c")})
        matcher.push("a")
        matcher.push("b")
        self.assertEqual(matcher.push("x"), 1.0)

    def test_evaluates_contiguous_ngram_at_every_step_past_warmup(self):
        # AC2/AC4: continuous stream, each step past warm-up gets its own evaluation,
        # independent of any single block boundary.
        matcher = SlidingWindowMatcher(n=2, whitelist={("a", "b"), ("b", "c")})
        matcher.push("a")
        self.assertEqual(matcher.push("b"), 0.0)  # ("a","b") whitelisted
        self.assertEqual(matcher.push("c"), 0.0)  # ("b","c") whitelisted
        self.assertEqual(matcher.push("z"), 1.0)  # ("c","z") not whitelisted

    def test_rejects_non_positive_window_size(self):
        with self.assertRaises(ValueError):
            SlidingWindowMatcher(n=0, whitelist=set())


if __name__ == "__main__":
    unittest.main()
