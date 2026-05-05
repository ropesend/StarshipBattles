"""Threading helper for non-blocking LLM calls (PROJ-296 Pattern #28).

Wraps a `LLMProvider.complete()` invocation on a worker thread. The
caller polls `.status` / `.result` / `.error` / `.elapsed_seconds` from
the pygame `update()` loop each frame. Cancellation via `.cancel()`
sets a `threading.Event` that the underlying provider checks between
retries; in-flight HTTP work completes in the background and is
discarded.

Concurrency safeguards:
- All shared state guarded by an instance `threading.Lock`.
- Module-level counter enforces `LLMConfig.MAX_CONCURRENT_CALLS`.
- Workers are non-daemon; `shutdown_all_calls()` joins them with a
  timeout before `pygame.quit()`.
- Each call has a logical "logical cancel" semantic: the result is
  dropped even if the HTTP call eventually returns.

See `Projects/active_projects/PROJ-296/design.md` for the full design.
"""
from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any, List, Optional, Set

from game.core.config import LLMConfig
from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    LLMCancelled,
    LLMConfigError,
    LLMException,
    LLMUnexpectedError,
    ValidationException,
)
from game.services.llm.provider import LLMProvider
from game.services.llm.types import CompletionResult, Message

logger = logging.getLogger(__name__)


class CallStatus(str, Enum):
    """Lifecycle status of an `LLMBackgroundCall`."""
    PENDING = "pending"      # Created but not started.
    RUNNING = "running"      # Worker thread is executing.
    DONE = "done"            # Completed successfully; .result is set.
    ERROR = "error"          # Failed with LLMException; .error is set.
    CANCELLED = "cancelled"  # Cancelled before completion.


# ---------------------------------------------------------------------------
# Module-level concurrent-call accounting
# ---------------------------------------------------------------------------

_in_flight_calls: int = 0
_in_flight_lock: threading.Lock = threading.Lock()
# PROJ-353A Tier-7 (T2.1): mutations of `_active_workers` are serialized via
# `_in_flight_lock`. The set is read via `list(_active_workers)` in
# `shutdown_all_calls`, which is also taken under the lock so the snapshot
# is consistent with the in-flight counter.
_active_workers: Set[threading.Thread] = set()


class LLMBackgroundCall:
    """Background-thread wrapper around `LLMProvider.complete()`.

    Usage:

        call = LLMBackgroundCall(provider, messages, model="x")
        call.start()
        # ... in pygame update loop, each frame:
        if call.status == CallStatus.DONE:
            consume(call.result)
        elif call.status == CallStatus.ERROR:
            show_error(call.error)
        elif call.elapsed_seconds > 30:
            offer_user_a_cancel_button()
    """

    def __init__(
        self,
        provider: LLMProvider,
        messages: List[Message],
        **complete_kwargs: Any,
    ) -> None:
        # Precondition validation per Pattern 19/20.
        if provider is None:
            raise ValidationException(
                "LLMBackgroundCall requires a non-None provider",
                code=ErrorCode.VALIDATION_FAILED.value,
            )
        if not messages:
            raise ValidationException(
                "LLMBackgroundCall requires at least one message",
                code=ErrorCode.VALIDATION_FAILED.value,
            )

        self._provider = provider
        self._messages = list(messages)
        self._kwargs = dict(complete_kwargs)
        self._cancel_event = threading.Event()
        # PROJ-324 Phase 2: terminal-state completion signal. Set in
        # `_run()` (and `cancel()` for the cancel-before-start path)
        # OUTSIDE `_state_lock` to avoid waiter-starvation. Allows
        # `wait(timeout)` to block deterministically instead of
        # polling `status` with `time.sleep`.
        self._done_event = threading.Event()
        # Inject our cancel_event into the kwargs the provider receives.
        self._kwargs["cancel_token"] = self._cancel_event

        # Mutable state — guarded by _state_lock.
        self._state_lock = threading.Lock()
        self._status: CallStatus = CallStatus.PENDING
        self._result: Optional[CompletionResult] = None
        self._error: Optional[LLMException] = None
        self._started_at: Optional[float] = None
        self._finished_at: Optional[float] = None
        self._thread: Optional[threading.Thread] = None

    # -- Public API ----------------------------------------------------------

    def start(self) -> None:
        """Spawn the worker thread. Idempotent — second call is a no-op.

        Idempotency holds for both sequential AND concurrent same-instance
        callers. Pre-PROJ-353A-audit-R1 the guard, slot reservation, and
        ``_thread`` assignment lived in three separate critical sections,
        so two threads racing into ``start()`` could both pass the
        ``_thread is None`` guard before either reserved a slot — burning
        two slots and spawning two workers. The fix runs the entire
        guard-then-reserve-then-assign sequence under ``_state_lock``.

        Raises `LLMConfigError` if starting would exceed
        `LLMConfig.MAX_CONCURRENT_CALLS`.

        Lock-ordering note: ``_in_flight_lock`` is acquired INSIDE
        ``_state_lock`` here. The reverse ordering (``_in_flight_lock``
        held while waiting on ``_state_lock``) does not occur anywhere
        else in this module — ``_run()`` cleanup at lines ~313-315 only
        acquires ``_in_flight_lock``, and ``shutdown_all_calls`` likewise.
        No inversion risk.
        """
        global _in_flight_calls
        with self._state_lock:
            if self._thread is not None:
                # Already started — sequential or concurrent caller's
                # second invocation. No-op per the idempotency contract.
                return

            with _in_flight_lock:
                if _in_flight_calls >= LLMConfig.MAX_CONCURRENT_CALLS:
                    raise LLMConfigError(
                        f"max concurrent LLM calls ({LLMConfig.MAX_CONCURRENT_CALLS}) reached",
                        code=ErrorCode.LLM_CONFIG_MISSING.value,
                        context={
                            "in_flight": _in_flight_calls,
                            "max": LLMConfig.MAX_CONCURRENT_CALLS,
                        },
                    )
                _in_flight_calls += 1
                # Track for shutdown_all_calls(). Add before the OS
                # spawn so the worker can never finish before it is
                # registered. PROJ-353A T2.1 ordering preserved: this
                # serialization keeps the worker set consistent with
                # the in-flight counter; a finishing worker must see
                # itself in the set when it decrements the counter.
                self._started_at = time.monotonic()
                self._thread = threading.Thread(
                    target=self._run,
                    name=f"LLMBackgroundCall-{id(self):x}",
                    daemon=False,
                )
                _active_workers.add(self._thread)

        # OS thread spawn happens OUTSIDE the lock so we never hold it
        # during the kernel call. By this point ``self._thread`` is the
        # canonical reference (set under both locks); a concurrent
        # second ``start()`` saw it non-None and returned at the guard.
        self._thread.start()

    def cancel(self) -> None:
        """Logical cancel. Idempotent. Safe to call before start().

        Sets the cancel event; the worker will mark CANCELLED on its
        next check. The in-flight HTTP request itself may still complete
        in the background and is discarded.
        """
        self._cancel_event.set()
        with self._state_lock:
            # Only transition to CANCELLED from non-terminal states.
            if self._status in (CallStatus.PENDING, CallStatus.RUNNING):
                self._status = CallStatus.CANCELLED
                if self._finished_at is None:
                    self._finished_at = time.monotonic()
        # PROJ-324 Phase 2: signal completion outside the lock.
        # `Event.set()` is internally thread-safe; releasing the lock
        # first prevents a `wait()`-er from racing into a re-acquire
        # while we still hold it. Idempotent on a re-call (double-set is
        # a no-op). For the cancel-before-start path the worker never
        # runs, so this is the only set; for cancel-mid-run, `_run()`
        # also sets it on its terminal transition (no-op duplicate).
        self._done_event.set()

    @property
    def status(self) -> CallStatus:
        with self._state_lock:
            return self._status

    @property
    def result(self) -> Optional[CompletionResult]:
        """Set only when status == DONE."""
        with self._state_lock:
            return self._result

    @property
    def error(self) -> Optional[LLMException]:
        """Set only when status == ERROR."""
        with self._state_lock:
            return self._error

    def wait(self, timeout: float | None = None) -> bool:
        """Block until the call reaches a terminal state, or until ``timeout`` seconds elapse.

        Returns ``True`` if a terminal state (DONE, ERROR, or CANCELLED)
        was reached, ``False`` if the timeout expired first. Returns
        immediately if already in a terminal state. ``timeout=None``
        blocks indefinitely.

        PROJ-324 Phase 2: deterministic alternative to polling
        ``status`` with ``time.sleep`` from the test thread. The done
        event is set by ``_run()``'s terminal branches and by
        ``cancel()`` (for the cancel-before-start path).
        """
        return self._done_event.wait(timeout)

    @property
    def elapsed_seconds(self) -> float:
        """Wall time since start(). 0 before start; frozen after terminal state."""
        with self._state_lock:
            if self._started_at is None:
                return 0.0
            end = self._finished_at if self._finished_at is not None else time.monotonic()
            return end - self._started_at

    # -- Worker --------------------------------------------------------------

    def _run(self) -> None:
        # PROJ-324 Phase 2 / PROJ-353A Tier-7 T2.1: every code path through
        # `_run()` must signal completion via `self._done_event.set()` so
        # callers blocked on `wait(timeout)` unblock deterministically.
        # The OUTER `try/finally` below sets the event regardless of which
        # terminal branch we took (CANCELLED, ERROR, DONE) and only AFTER
        # the inner finally has released the in-flight slot and removed
        # the worker from `_active_workers`. That ordering guarantees a
        # `wait()`-er observing the terminal state also sees the slot
        # released. `Event.set()` is idempotent and internally
        # thread-safe; we set it OUTSIDE all locks to prevent
        # waiter-starvation if a `wait()`-er re-acquires immediately.
        try:
            try:
                with self._state_lock:
                    # Don't transition to RUNNING if already cancelled.
                    if self._status == CallStatus.CANCELLED:
                        return
                    self._status = CallStatus.RUNNING

                try:
                    result = self._provider.complete(self._messages, **self._kwargs)
                except LLMCancelled as e:
                    with self._state_lock:
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.CANCELLED
                        self._error = e
                        self._finished_at = time.monotonic()
                    return
                except LLMException as e:
                    with self._state_lock:
                        # Cancel wins — if user cancelled mid-call, keep CANCELLED.
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.ERROR
                            self._error = e
                        self._finished_at = time.monotonic()
                    return
                except Exception as e:  # PROJ-321..328 audit S1.1: catch unexpected non-LLM provider exceptions; preserves wait() contract
                    # Wrap as LLMUnexpectedError so `_error` stays typed as
                    # LLMException; the original exception is preserved on
                    # `__cause__` and its type name in `context` for safe
                    # logging. Without this branch the exception escaped past
                    # the inner finally with `_status=RUNNING`, causing
                    # `wait()` to return True on a non-terminal state.
                    logger.exception(
                        "LLMBackgroundCall worker raised non-LLM exception: %r",
                        e,
                    )
                    wrapped = LLMUnexpectedError(
                        f"Provider raised unexpected {type(e).__name__}: {e}",
                        context={"original_exception_type": type(e).__name__},
                    )
                    wrapped.__cause__ = e
                    with self._state_lock:
                        # Cancel wins — if user cancelled mid-call, keep CANCELLED.
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.ERROR
                            self._error = wrapped
                        self._finished_at = time.monotonic()
                    return

                # Success.
                with self._state_lock:
                    # Cancel wins.
                    if self._status != CallStatus.CANCELLED:
                        self._result = result
                        self._status = CallStatus.DONE
                    self._finished_at = time.monotonic()

            finally:
                # PROJ-353A Tier-7 T2.1: release the in-flight slot and
                # de-register the worker BEFORE signalling completion.
                # Previously `_done_event.set()` ran first (in the inner
                # `finally`), so a `wait()`-er observing the terminal
                # state could race ahead while `_active_workers` still
                # contained the worker and `_in_flight_calls` was still
                # incremented. Tests asserting "after wait() returns, a
                # new call can be started without exceeding the cap"
                # were therefore flake-prone. Cleaning up first makes
                # observed terminal state and resource accounting
                # consistent.
                global _in_flight_calls
                current = threading.current_thread()
                with _in_flight_lock:
                    _in_flight_calls = max(0, _in_flight_calls - 1)
                    _active_workers.discard(current)
        finally:
            # Signal terminal-state completion outside any lock so a
            # `wait()`-er never re-enters a held lock. Idempotent.
            self._done_event.set()


# ---------------------------------------------------------------------------
# Shutdown hook
# ---------------------------------------------------------------------------


def shutdown_all_calls(timeout: float = 5.0) -> None:
    """Join all in-flight worker threads.

    Called from `game/app.py` before `pygame.quit()` to ensure clean
    shutdown. Workers that don't finish within `timeout` seconds are
    logged as a warning and the function returns — better than hanging
    the game forever on shutdown.
    """
    # PROJ-353A T2.1: snapshot under the lock so we don't iterate a set
    # being mutated by a concurrently-finishing worker.
    with _in_flight_lock:
        workers = list(_active_workers)
    if not workers:
        return

    deadline = time.monotonic() + timeout
    for worker in workers:
        remaining = max(0.0, deadline - time.monotonic())
        worker.join(timeout=remaining)
        if worker.is_alive():
            logger.warning(
                "LLM worker %s did not finish within %.1fs; abandoning",
                worker.name, timeout,
            )


__all__ = [
    "CallStatus",
    "LLMBackgroundCall",
    "shutdown_all_calls",
]
