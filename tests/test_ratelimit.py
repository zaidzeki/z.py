"""Tests for z.ratelimit – sliding-window rate limiter."""

import time
import threading

import pytest

from z.ratelimit import RateLimitExceeded, limit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_counter():
    """Return a limited function and a call-count list."""
    calls = []

    @limit(cphs=3, delay=False)
    def fn():
        calls.append(time.time())
        return len(calls)

    return fn, calls


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


class TestLimitBasic:
    def test_calls_within_limit_succeed(self):
        fn, calls = make_counter()
        results = [fn() for _ in range(3)]
        assert results == [1, 2, 3]

    def test_fourth_call_is_silently_dropped(self):
        fn, calls = make_counter()
        for _ in range(3):
            fn()
        result = fn()
        assert result is None
        assert len(calls) == 3

    def test_raise_exception_when_exceeded(self):
        @limit(cphs=2, delay=False, raise_exception=True)
        def fn():
            return True

        fn()
        fn()
        with pytest.raises(RateLimitExceeded):
            fn()

    def test_no_limits_passes_through(self):
        """With no rate limits specified every call succeeds."""

        @limit(delay=False)
        def fn():
            return 42

        # Should never block or raise
        assert fn() == 42
        assert fn() == 42


# ---------------------------------------------------------------------------
# Window sliding
# ---------------------------------------------------------------------------


class TestSlidingWindow:
    def test_calls_allowed_after_window_expires(self):
        @limit(cphs=2, delay=False)
        def fn():
            return True

        assert fn() is True
        assert fn() is True
        assert fn() is None  # window saturated

        time.sleep(0.55)  # window has passed

        assert fn() is True  # should succeed again

    def test_multiple_windows_enforced_independently(self):
        """cpm=1 blocks while cphs window is fresh but cpm limit not hit yet."""
        calls = []

        @limit(cphs=5, cpm=2, delay=False)
        def fn():
            calls.append(1)

        fn()
        fn()  # 2 calls – hits cpm limit
        fn()  # should be dropped by cpm
        assert len(calls) == 2


# ---------------------------------------------------------------------------
# Delay mode
# ---------------------------------------------------------------------------


class TestDelayMode:
    def test_delay_mode_eventually_succeeds(self):
        @limit(cphs=1, delay=True, delay_duration=0.1)
        def fn():
            return True

        fn()  # consume the single slot
        # Second call should block and then succeed
        result = fn()
        assert result is True

    def test_delay_duration_string_parsed(self):
        @limit(cphs=1, delay=True, delay_duration="0.1s")
        def fn():
            return "ok"

        fn()
        assert fn() == "ok"

    def test_invalid_delay_duration_raises(self):
        with pytest.raises(ValueError):
            limit(cphs=1, delay_duration="bad_value")


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_calls_respect_limit(self):
        """Under heavy concurrent load the limit is never breached."""
        max_per_half_sec = 5
        results = []
        lock = threading.Lock()

        @limit(cphs=max_per_half_sec, delay=False)
        def fn():
            return True

        def task():
            r = fn()
            with lock:
                results.append(r)

        threads = [threading.Thread(target=task) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        successes = [r for r in results if r is True]
        # At most max_per_half_sec calls can succeed within one window
        assert len(successes) <= max_per_half_sec


# ---------------------------------------------------------------------------
# Decorator metadata preservation
# ---------------------------------------------------------------------------


class TestMetadata:
    def test_wraps_preserves_name(self):
        @limit(cpm=10, delay=False)
        def my_function():
            """My docstring."""

        assert my_function.__name__ == "my_function"

    def test_wraps_preserves_docstring(self):
        @limit(cpm=10, delay=False)
        def my_function():
            """My docstring."""

        assert my_function.__doc__ == "My docstring."


# ---------------------------------------------------------------------------
# All window types accepted
# ---------------------------------------------------------------------------


class TestAllWindowTypes:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"cphs": 5},
            {"cpm": 100},
            {"cph": 1000},
            {"cpd": 5000},
            {"cpw": 10000},
        ],
    )
    def test_window_type_accepted(self, kwargs):
        @limit(**kwargs, delay=False)
        def fn():
            return True

        assert fn() is True
