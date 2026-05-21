"""Threading helper for non-blocking image-generation calls (PROJ-314).

Wraps an :meth:`ImageProvider.generate_image` invocation on a worker
thread. Mirrors :class:`game.services.llm.background.LLMBackgroundCall`
shape for shape — same status enum, same lifecycle, same shutdown
semantics.

See `Projects/active_projects/PROJ-314/design.md` for design rationale.
"""
from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any, Optional, Set

from game.core.config import ImageConfig
from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    ImageCancelled,
    ImageConfigError,
    ImageException,
    ImageUnexpectedError,
    ValidationException,
)
from game.ui.services.image.provider import ImageProvider
from game.ui.services.image.types import ImageResult

logger = logging.getLogger(__name__)


class CallStatus(str, Enum):
    """Lifecycle status of an :class:`ImageBackgroundCall`."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Module-level concurrent-call accounting
# ---------------------------------------------------------------------------

_in_flight_calls: int = 0
_in_flight_lock: threading.Lock = threading.Lock()
_active_workers: Set[threading.Thread] = set()


class ImageBackgroundCall:
    """Background-thread wrapper around :meth:`ImageProvider.generate_image`.

    Usage::

        call = ImageBackgroundCall(provider, "a Federation battleship",
                                   model="gpt-image-2")
        call.start()
        # ... in pygame update loop:
        if call.status == CallStatus.DONE:
            consume(call.result)
        elif call.status == CallStatus.ERROR:
            show_error(call.error)
    """

    def __init__(
        self,
        provider: ImageProvider,
        prompt: str,
        **generate_kwargs: Any,
    ) -> None:
        if provider is None:
            raise ValidationException(
                "ImageBackgroundCall requires a non-None provider",
                code=ErrorCode.VALIDATION_FAILED.value,
            )
        if not prompt:
            raise ValidationException(
                "ImageBackgroundCall requires a non-empty prompt",
                code=ErrorCode.VALIDATION_FAILED.value,
            )

        self._provider = provider
        self._prompt = prompt
        self._kwargs = dict(generate_kwargs)
        self._cancel_event = threading.Event()
        self._kwargs["cancel_token"] = self._cancel_event

        self._state_lock = threading.Lock()
        self._status: CallStatus = CallStatus.PENDING
        self._result: Optional[ImageResult] = None
        self._error: Optional[ImageException] = None
        self._started_at: Optional[float] = None
        self._finished_at: Optional[float] = None
        self._thread: Optional[threading.Thread] = None
        # PROJ-381 Phase 3 (LLM-3): mirror LLMBackgroundCall PROJ-324
        # Phase 2 — terminal-state event lets `wait()` block
        # deterministically instead of forcing tests to poll `status`
        # with `time.sleep`. Set OUTSIDE the state lock from cancel() and
        # from every terminal branch in _run().
        self._done_event = threading.Event()

    # -- Public API ----------------------------------------------------------

    def start(self) -> None:
        """Spawn the worker thread. Idempotent — second call is a no-op.

        Raises :class:`ImageConfigError` if starting would exceed
        ``ImageConfig.MAX_CONCURRENT_CALLS``.
        """
        with self._state_lock:
            if self._thread is not None:
                return

        global _in_flight_calls
        with _in_flight_lock:
            if _in_flight_calls >= ImageConfig.MAX_CONCURRENT_CALLS:
                raise ImageConfigError(
                    f"max concurrent image calls ({ImageConfig.MAX_CONCURRENT_CALLS}) reached",
                    code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                    context={
                        "in_flight": _in_flight_calls,
                        "max": ImageConfig.MAX_CONCURRENT_CALLS,
                    },
                )
            _in_flight_calls += 1

        with self._state_lock:
            self._started_at = time.monotonic()
            self._thread = threading.Thread(
                target=self._run,
                name=f"ImageBackgroundCall-{id(self):x}",
                daemon=False,
            )

        _active_workers.add(self._thread)
        self._thread.start()

    def cancel(self) -> None:
        """Logical cancel. Idempotent. Safe to call before start()."""
        self._cancel_event.set()
        with self._state_lock:
            if self._status in (CallStatus.PENDING, CallStatus.RUNNING):
                self._status = CallStatus.CANCELLED
                if self._finished_at is None:
                    self._finished_at = time.monotonic()
        # PROJ-381 Phase 3 (LLM-3): signal completion outside the lock so
        # `wait()` waiters never re-enter a held lock. Idempotent on
        # re-call; double-set is a no-op.
        self._done_event.set()

    @property
    def status(self) -> CallStatus:
        with self._state_lock:
            return self._status

    @property
    def result(self) -> Optional[ImageResult]:
        with self._state_lock:
            return self._result

    @property
    def error(self) -> Optional[ImageException]:
        with self._state_lock:
            return self._error

    def wait(self, timeout: float | None = None) -> bool:
        """Block until the call reaches a terminal state, or until ``timeout`` seconds elapse.

        Returns ``True`` if a terminal state (DONE, ERROR, or CANCELLED)
        was reached, ``False`` if the timeout expired first. Returns
        immediately if already in a terminal state. ``timeout=None``
        blocks indefinitely.

        PROJ-381 Phase 3 (LLM-3): mirror of
        :meth:`LLMBackgroundCall.wait` — deterministic alternative to
        polling ``status`` with ``time.sleep``. The done event is set by
        ``_run()``'s terminal branches and by ``cancel()`` (for the
        cancel-before-start path).
        """
        return self._done_event.wait(timeout)

    @property
    def elapsed_seconds(self) -> float:
        with self._state_lock:
            if self._started_at is None:
                return 0.0
            end = self._finished_at if self._finished_at is not None else time.monotonic()
            return end - self._started_at

    # -- Worker --------------------------------------------------------------

    def _run(self) -> None:
        try:
            try:
                with self._state_lock:
                    if self._status == CallStatus.CANCELLED:
                        return
                    self._status = CallStatus.RUNNING

                try:
                    result = self._provider.generate_image(self._prompt, **self._kwargs)
                except ImageCancelled as e:
                    with self._state_lock:
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.CANCELLED
                        self._error = e
                        self._finished_at = time.monotonic()
                    return
                except ImageException as e:
                    with self._state_lock:
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.ERROR
                            self._error = e
                        self._finished_at = time.monotonic()
                    return
                except Exception as e:  # Intentional broad catch: provider escape — wrap as ImageUnexpectedError so worker-thread crashes don't leave caller polling forever.
                    # PROJ-381 Phase 2 (B-10): mirror LLMUnexpectedError
                    # treatment from PROJ-321..328. Any non-ImageException
                    # escape from the provider previously left `_status`
                    # at RUNNING with the worker thread leaked; wrap the
                    # exception so the call still reaches a terminal
                    # ERROR state and `_error` stays typed as
                    # ImageException.
                    logger.exception(
                        "ImageBackgroundCall worker raised non-Image exception: %s",
                        e,
                    )
                    wrapped = ImageUnexpectedError(
                        f"Provider raised unexpected {type(e).__name__}: {e}",
                        context={"original_exception_type": type(e).__name__},
                    )
                    wrapped.__cause__ = e
                    with self._state_lock:
                        if self._status != CallStatus.CANCELLED:
                            self._status = CallStatus.ERROR
                            self._error = wrapped
                        self._finished_at = time.monotonic()
                    return

                with self._state_lock:
                    if self._status != CallStatus.CANCELLED:
                        self._result = result
                        self._status = CallStatus.DONE
                    self._finished_at = time.monotonic()

            finally:
                global _in_flight_calls
                with _in_flight_lock:
                    _in_flight_calls = max(0, _in_flight_calls - 1)
                current = threading.current_thread()
                _active_workers.discard(current)
        finally:
            # PROJ-381 Phase 3 (LLM-3): mirror PROJ-324 Phase 2 — signal
            # terminal completion OUTSIDE any lock so a `wait()`-er never
            # re-enters a held lock. Idempotent. Cleanup must complete
            # before this set so an observer of terminal status sees
            # consistent in-flight accounting.
            self._done_event.set()


# ---------------------------------------------------------------------------
# Shutdown hook
# ---------------------------------------------------------------------------


def shutdown_all_image_calls(timeout: float = 5.0) -> None:
    """Join all in-flight image-call worker threads."""
    workers = list(_active_workers)
    if not workers:
        return

    deadline = time.monotonic() + timeout
    for worker in workers:
        remaining = max(0.0, deadline - time.monotonic())
        worker.join(timeout=remaining)
        if worker.is_alive():
            logger.warning(
                "Image worker %s did not finish within %.1fs; abandoning",
                worker.name, timeout,
            )


__all__ = [
    "CallStatus",
    "ImageBackgroundCall",
    "shutdown_all_image_calls",
]
