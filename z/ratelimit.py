"""Rate-limiting decorator for ``z``.

Provides :func:`limit`, a sliding-window rate-limiter that supports multiple
simultaneous time-window constraints.

Supported windows
-----------------
``cphs``  – calls per half-second  (0.5 s)
``cpm``   – calls per minute       (60 s)
``cph``   – calls per hour         (3 600 s)
``cpd``   – calls per day          (86 400 s)
``cpw``   – calls per week         (604 800 s)

Examples
--------
>>> from z.ratelimit import limit
>>>
>>> @limit(cpm=10, raise_exception=True)
... def fetch(url):
...     return url
"""

import time
import threading
from functools import wraps


class RateLimitExceeded(Exception):
    """Raised when a rate limit is breached and ``raise_exception=True``."""


def limit(
    cphs=None,
    cpm=None,
    cph=None,
    cpd=None,
    cpw=None,
    raise_exception=False,
    delay=True,
    delay_duration=1.0,
):
    """Sliding-window rate-limiting decorator.

    At least one of ``cphs``, ``cpm``, ``cph``, ``cpd``, or ``cpw`` must be
    provided.  Multiple limits are checked together; the call is blocked (or
    rejected) if *any* of them is exceeded.

    Parameters
    ----------
    cphs:
        Maximum calls per half-second (0.5 s window).
    cpm:
        Maximum calls per minute (60 s window).
    cph:
        Maximum calls per hour (3 600 s window).
    cpd:
        Maximum calls per day (86 400 s window).
    cpw:
        Maximum calls per week (604 800 s window).
    raise_exception:
        When ``delay=False`` and the limit is exceeded, raise
        :exc:`RateLimitExceeded` instead of silently returning ``None``.
    delay:
        When ``True`` (default) the wrapper blocks until the call can proceed.
        When ``False`` the call is either rejected silently or raises
        :exc:`RateLimitExceeded` depending on ``raise_exception``.
    delay_duration:
        Seconds to sleep between re-checks when ``delay=True``.  Accepts a
        ``float`` or a string like ``"0.5s"``.

    Returns
    -------
    Callable
        A decorator that wraps the target function with the rate-limiting logic.

    Raises
    ------
    RateLimitExceeded
        If ``delay=False`` and ``raise_exception=True`` when the limit is hit.
    ValueError
        If ``delay_duration`` is a string that cannot be parsed.
    """
    window_durations = {
        "cphs": 0.5,
        "cpm": 60.0,
        "cph": 3_600.0,
        "cpd": 86_400.0,
        "cpw": 604_800.0,
    }

    # ------------------------------------------------------------------ #
    # Resolve delay_duration                                               #
    # ------------------------------------------------------------------ #
    actual_delay: float
    if isinstance(delay_duration, str):
        raw = delay_duration.rstrip("s") if delay_duration.endswith("s") else delay_duration
        try:
            actual_delay = float(raw)
        except ValueError as exc:
            raise ValueError(f"Could not parse delay_duration string: {delay_duration!r}") from exc
    else:
        actual_delay = float(delay_duration)

    # ------------------------------------------------------------------ #
    # Build active-limits list                                             #
    # ------------------------------------------------------------------ #
    active_limits: list[tuple[str, float, int]] = []
    for name, val in (("cphs", cphs), ("cpm", cpm), ("cph", cph), ("cpd", cpd), ("cpw", cpw)):
        if val is not None:
            active_limits.append((name, window_durations[name], int(val)))

    def decorator(func):
        history: list[float] = []
        lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal history

            while True:
                now = time.time()

                with lock:
                    max_window = max((win for _, win, _ in active_limits), default=0.0)
                    # Evict timestamps outside every active window
                    history = [t for t in history if now - t <= max_window]

                    limit_exceeded = any(
                        sum(1 for t in history if now - t <= duration) >= limit_val
                        for _, duration, limit_val in active_limits
                    )

                    if not limit_exceeded:
                        history.append(now)
                        break

                # ---- Rate limited: handle outside the lock ---- #
                if delay:
                    time.sleep(actual_delay)
                elif raise_exception:
                    raise RateLimitExceeded(f"Rate limit exceeded on function '{func.__name__}'")
                else:
                    return None  # silently swallow the call

            return func(*args, **kwargs)

        return wrapper

    return decorator
