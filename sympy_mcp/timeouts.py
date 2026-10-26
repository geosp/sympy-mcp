"""
Per-call time limits for SymPy computations.

SymPy work is CPU-bound pure Python, so it can't be cancelled from another
thread. The limit is a SIGALRM timer instead, which interrupts the
computation in the thread that runs it. Tools run on the event-loop thread,
which is the main thread in both stdio and http mode. Where SIGALRM is not
available (Windows, or a call off the main thread) calls run without a
limit, and a warning is logged once.
"""

import contextlib
import logging
import signal
import threading
import time
from typing import Iterator, Optional

logger = logging.getLogger(__name__)

DEFAULT_SECONDS = 30.0
_default_seconds = DEFAULT_SECONDS
_warned = False


class ComputationTimeout(BaseException):
    """Raised inside a computation when its time limit expires.

    A BaseException, so SymPy's internal `except Exception` blocks can't swallow it.
    """


def configure(default_seconds: float) -> None:
    """Set the server-wide default limit (0 disables it)."""
    global _default_seconds
    _default_seconds = default_seconds


def resolve(seconds: Optional[float]) -> float:
    """The limit for one call: the per-call value, or the server default when None."""
    return _default_seconds if seconds is None else seconds


def _supported() -> bool:
    return hasattr(signal, "SIGALRM") and threading.current_thread() is threading.main_thread()


@contextlib.contextmanager
def time_limit(seconds: float) -> Iterator[None]:
    """Raise ComputationTimeout in the body if it runs longer than `seconds` (<= 0: no limit)."""
    global _warned
    if seconds <= 0:
        yield
        return
    if not _supported():
        if not _warned:
            logger.warning("Time limits need SIGALRM on the main thread; running without one")
            _warned = True
        yield
        return

    def expire(signum, frame):
        raise ComputationTimeout()

    previous_handler = signal.signal(signal.SIGALRM, expire)
    previous_delay, _ = signal.setitimer(signal.ITIMER_REAL, seconds)
    started = time.monotonic()
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_delay:
            # An enclosing limit was running; give it back what it had left
            elapsed = time.monotonic() - started
            signal.setitimer(signal.ITIMER_REAL, max(previous_delay - elapsed, 0.001))


def timeout_message(seconds: float) -> str:
    return (
        f"Error: Computation timed out after {seconds:g} seconds. Retry with a larger "
        "timeout_seconds (0 means no limit), or simplify the input first."
    )


def run_limited(call, timeout_seconds: Optional[float] = None) -> str:
    """Run call() under the resolved time limit; return its value or the timeout error."""
    seconds = resolve(timeout_seconds)
    try:
        with time_limit(seconds):
            return call()
    except ComputationTimeout:
        return timeout_message(seconds)
