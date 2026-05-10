"""PROJ-381 Phase 2 (B-10) + Phase 3 (LLM-3): ImageBackgroundCall parity tests.

Mirrors the LLMBackgroundCall PROJ-321..328 + PROJ-324 audits:

- B-10 (Phase 2): a non-ImageException escape from ``generate_image``
  must be wrapped as ``ImageUnexpectedError`` so the worker thread does
  not leak and ``_status`` reliably reaches ERROR.
- LLM-3 (Phase 3): ``_done_event`` + ``wait()`` mirror so callers and
  tests can block on terminal state instead of polling.
"""

from __future__ import annotations

import time
from threading import Event

import pytest

from game.core.exceptions import (
    ImageException,
    ImageNetworkError,
    ImageUnexpectedError,
)
from game.ui.services.image.background import (
    CallStatus,
    ImageBackgroundCall,
)
from game.ui.services.image.types import ImageResult


class _BoomProvider:
    """Stub provider that raises a non-ImageException type."""

    def generate_image(self, prompt, **kwargs):  # noqa: ANN001
        raise RuntimeError("simulated provider crash")


class _SlowSuccessProvider:
    """Provider that sleeps then returns a valid result."""

    def __init__(self, delay: float = 0.05) -> None:
        self._delay = delay

    def generate_image(self, prompt, **kwargs):  # noqa: ANN001
        time.sleep(self._delay)
        return ImageResult(
            image_bytes=b"\x89PNG",
            size=(64, 64),
            model="stub",
            latency_ms=10.0,
            provider="stub",
        )


class _ImageExceptionProvider:
    """Stub provider that raises a real ImageException subclass."""

    def __init__(self, exc: ImageException) -> None:
        self._exc = exc

    def generate_image(self, prompt, **kwargs):  # noqa: ANN001
        raise self._exc


class TestImageUnexpectedErrorWrap:
    """B-10: provider escape produces ImageUnexpectedError + ERROR status."""

    def test_non_image_exception_is_wrapped(self) -> None:
        call = ImageBackgroundCall(_BoomProvider(), "test prompt")
        call.start()
        terminal = call.wait(timeout=2.0)

        assert terminal is True, "wait() should return True on terminal state"
        assert call.status == CallStatus.ERROR
        assert isinstance(call.error, ImageException)
        assert isinstance(call.error, ImageUnexpectedError)
        ctx = call.error.context or {}
        assert ctx.get("original_exception_type") == "RuntimeError"

    def test_image_exception_passes_through_unwrapped(self) -> None:
        """PROJ-395 MAJ-009: a real ImageException subclass raised by
        the provider must NOT be wrapped as ImageUnexpectedError.

        The B-10 wrap is specifically a safety net for non-strategy
        exception types (RuntimeError, TypeError, etc.). Provider
        errors that are already ImageException instances should reach
        the caller unchanged so callers can branch on the original
        type / code.
        """
        original = ImageNetworkError(
            "simulated network failure",
            context={"provider": "stub"},
        )
        call = ImageBackgroundCall(
            _ImageExceptionProvider(original), "test prompt"
        )
        call.start()
        terminal = call.wait(timeout=2.0)

        assert terminal is True
        assert call.status == CallStatus.ERROR
        assert isinstance(call.error, ImageException)
        # The MUST-NOT: we never see the unexpected-wrapper for an
        # already-typed ImageException.
        assert not isinstance(call.error, ImageUnexpectedError), (
            f"ImageException must pass through unwrapped; got "
            f"{type(call.error).__name__}"
        )
        # Identity preserved — the exact instance the provider raised.
        assert call.error is original


class TestWaitParity:
    """LLM-3: wait() returns False while running, True after a terminal."""

    def test_wait_false_while_running_then_true_after_done(self) -> None:
        call = ImageBackgroundCall(_SlowSuccessProvider(delay=0.2), "test")
        call.start()
        # Worker is sleeping ~200ms; a 50ms wait must time out (False).
        early = call.wait(timeout=0.05)
        assert early is False
        # A longer wait must reach the terminal DONE state (True).
        late = call.wait(timeout=2.0)
        assert late is True
        assert call.status == CallStatus.DONE

    def test_wait_returns_true_after_cancel_before_start(self) -> None:
        """cancel() before start() must still set the done event."""
        call = ImageBackgroundCall(_SlowSuccessProvider(), "test")
        call.cancel()
        # No start() — wait must still return True because cancel sets
        # the event for the cancel-before-start path.
        assert call.wait(timeout=0.5) is True
        assert call.status == CallStatus.CANCELLED

    def test_wait_returns_true_after_error(self) -> None:
        """Error terminal state also sets the done event."""
        call = ImageBackgroundCall(_BoomProvider(), "test")
        call.start()
        assert call.wait(timeout=2.0) is True
        assert call.status == CallStatus.ERROR
