"""Stateful sliding-window memory ring buffer matcher (STORY-FING-03).

Feeds a stream of Fingerprint IDs into a fixed-depth FIFO window and checks
each resulting N-gram trajectory against a pre-compiled whitelist,
independent of process/thread execution-block boundaries.
"""

from __future__ import annotations

from collections import deque


class SlidingWindowMatcher:
    """FIFO window of depth `n` that scores each contiguous N-gram against a whitelist."""

    def __init__(self, n: int, whitelist: set[tuple[str, ...]]) -> None:
        if n < 1:
            raise ValueError("n must be >= 1")
        self._n = n
        self._whitelist = whitelist
        self._window: deque[str] = deque(maxlen=n)

    @property
    def warm(self) -> bool:
        """True once the window has filled to depth `n` at least once.

        Distinguishes "not enough data yet" from a genuine whitelist match —
        `push()` returns 0.0 for both, per the story's external contract, so
        callers that need to tell them apart check this instead.
        """
        return len(self._window) == self._n

    def push(self, fingerprint_id: str) -> float:
        """Push one Fingerprint ID and return the anomaly score for the current window.

        0.0 during warm-up (window not yet full) or when the current N-gram is
        whitelisted. 1.0 when the window is full and the N-gram is not whitelisted.
        """
        self._window.append(fingerprint_id)
        if not self.warm:
            return 0.0
        return 0.0 if tuple(self._window) in self._whitelist else 1.0
