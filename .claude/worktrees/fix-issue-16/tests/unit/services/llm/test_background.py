"""Tests for LLMBackgroundCall (PROJ-296 Phase 5)."""
import threading
import time
from typing import Any, List, Optional

import pytest

from game.core.exceptions import LLMConfigError, LLMNetworkError
from game.services.llm.types import (
    CompletionResult,
    FinishReason,
    Message,
    Role,
    TokenUsage,
)


def _ok_result(text="ok"):
    return CompletionResult(
        text=text,
        usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        model="test-model",
        finish_reason=FinishReason.STOP,
        latency_seconds=0.01,
        provider="test",
    )


class _SlowProvider:
    """Provider that sleeps for `delay` then returns ok_result.

    Honors `cancel_token` between sleep slices for cancel testing.
    """

    def __init__(self, delay: float = 0.1, raise_exc: Optional[Exception] = None):
        self.delay = delay
        self.raise_exc = raise_exc
        self.call_count = 0
        self.last_kwargs: dict = {}

    def complete(
        self,
        messages: List[Message],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
        cancel_token: Optional[threading.Event] = None,
        **opts: Any,
    ) -> CompletionResult:
        self.call_count += 1
        self.last_kwargs = {"model": model, "opts": dict(opts)}
        end = time.monotonic() + self.delay
        while time.monotonic() < end:
            if cancel_token is not None and cancel_token.is_set():
                from game.core.exceptions import LLMCancelled
                from game.core.error_codes import ErrorCode
                raise LLMCancelled(
                    "cancelled mid-call",
                    code=ErrorCode.LLM_CANCELLED.value,
                )
            time.sleep(0.005)
        if self.raise_exc is not None:
            raise self.raise_exc
        return _ok_result()


@pytest.fixture(autouse=True)
def _reset_inflight_counter():
    """Reset the module-level concurrent-call counter between tests."""
    from game.services.llm import background

    with background._in_flight_lock:
        background._in_flight_calls = 0
        background._active_workers.clear()
    yield
    # Best effort: join any leftover workers so they don't leak between tests.
    from game.services.llm.background import shutdown_all_calls
    shutdown_all_calls(timeout=2.0)


class TestCallStatusEnum:
    def test_has_expected_members(self):
        from game.services.llm.background import CallStatus

        assert {s.name for s in CallStatus} == {
            "PENDING", "RUNNING", "DONE", "ERROR", "CANCELLED",
        }


class TestConstructionAndValidation:
    def test_initial_status_is_pending(self, stub_llm_provider):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        call = LLMBackgroundCall(
            stub_llm_provider, [Message(role=Role.USER, content="hi")]
        )
        assert call.status == CallStatus.PENDING
        assert call.result is None
        assert call.error is None
        assert call.elapsed_seconds == 0.0

    def test_empty_messages_raises(self, stub_llm_provider):
        from game.core.exceptions import ValidationException
        from game.services.llm.background import LLMBackgroundCall

        with pytest.raises(ValidationException):
            LLMBackgroundCall(stub_llm_provider, [])

    def test_none_provider_raises(self):
        from game.core.exceptions import ValidationException
        from game.services.llm.background import LLMBackgroundCall

        with pytest.raises(ValidationException):
            LLMBackgroundCall(None, [Message(role=Role.USER, content="hi")])  # type: ignore[arg-type]


class TestSuccessPath:
    def test_completes_with_result(self, stub_llm_provider):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        call = LLMBackgroundCall(
            stub_llm_provider, [Message(role=Role.USER, content="hi")]
        )
        call.start()
        # Wait up to 2s for completion.
        deadline = time.monotonic() + 2.0
        while call.status not in (CallStatus.DONE, CallStatus.ERROR) and time.monotonic() < deadline:
            time.sleep(0.01)
        assert call.status == CallStatus.DONE
        assert call.result is not None
        assert call.result.text == "stub-response"
        assert call.error is None

    def test_elapsed_seconds_is_monotonic_then_frozen(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        assert call.elapsed_seconds == 0.0
        call.start()
        time.sleep(0.01)
        mid = call.elapsed_seconds
        assert mid > 0.0
        # Wait for completion.
        deadline = time.monotonic() + 2.0
        while call.status != CallStatus.DONE and time.monotonic() < deadline:
            time.sleep(0.01)
        end = call.elapsed_seconds
        # Frozen after completion: another sleep doesn't increase elapsed.
        time.sleep(0.05)
        assert call.elapsed_seconds == end


class TestErrorPath:
    def test_propagates_llm_exception_to_error_field(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        provider = _SlowProvider(delay=0.0, raise_exc=LLMNetworkError("boom", code="L002"))
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        deadline = time.monotonic() + 2.0
        while call.status not in (CallStatus.DONE, CallStatus.ERROR) and time.monotonic() < deadline:
            time.sleep(0.01)
        assert call.status == CallStatus.ERROR
        assert call.result is None
        assert isinstance(call.error, LLMNetworkError)
        assert call.error.code == "L002"


class TestCancellation:
    def test_cancel_marks_status_cancelled(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        provider = _SlowProvider(delay=0.5)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        time.sleep(0.02)  # let worker actually start
        call.cancel()
        deadline = time.monotonic() + 2.0
        while call.status not in (CallStatus.DONE, CallStatus.ERROR, CallStatus.CANCELLED) \
                and time.monotonic() < deadline:
            time.sleep(0.01)
        assert call.status == CallStatus.CANCELLED
        assert call.result is None

    def test_cancel_is_idempotent(self):
        from game.services.llm.background import LLMBackgroundCall

        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        call.cancel()
        call.cancel()  # MUST NOT raise

    def test_cancel_before_start_is_safe(self, stub_llm_provider):
        from game.services.llm.background import LLMBackgroundCall

        call = LLMBackgroundCall(stub_llm_provider, [Message(role=Role.USER, content="hi")])
        call.cancel()  # MUST NOT raise


class TestStartIdempotency:
    def test_double_start_does_not_spawn_two_workers(self, stub_llm_provider):
        from game.services.llm.background import LLMBackgroundCall

        call = LLMBackgroundCall(stub_llm_provider, [Message(role=Role.USER, content="hi")])
        call.start()
        call.start()  # second call MUST be a no-op
        # Wait for completion.
        deadline = time.monotonic() + 2.0
        while call.status.name not in ("DONE", "ERROR") and time.monotonic() < deadline:
            time.sleep(0.01)
        # The stub was called exactly once.
        assert stub_llm_provider.call_count == 1


class TestConcurrentCallLimit:
    def test_creating_calls_up_to_max_is_ok(self):
        """Constructing up to MAX_CONCURRENT_CALLS calls is OK."""
        from game.core.config import LLMConfig
        from game.services.llm.background import LLMBackgroundCall

        provider = _SlowProvider(delay=0.5)
        calls = []
        for _ in range(LLMConfig.MAX_CONCURRENT_CALLS):
            call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
            call.start()
            calls.append(call)
        # All got past start() without raising.
        assert len(calls) == LLMConfig.MAX_CONCURRENT_CALLS

        # Cleanup.
        for call in calls:
            call.cancel()

    def test_exceeding_max_raises(self):
        from game.core.config import LLMConfig
        from game.core.exceptions import LLMConfigError
        from game.services.llm.background import LLMBackgroundCall

        provider = _SlowProvider(delay=0.5)
        calls = []
        for _ in range(LLMConfig.MAX_CONCURRENT_CALLS):
            call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
            call.start()
            calls.append(call)
        # The (N+1)th must raise.
        extra = LLMBackgroundCall(provider, [Message(role=Role.USER, content="x")])
        with pytest.raises(LLMConfigError):
            extra.start()

        for call in calls:
            call.cancel()

    def test_completed_calls_free_up_slots(self):
        """When an in-flight call completes, a new one CAN start."""
        from game.core.config import LLMConfig
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        # Use fast provider to free slots quickly.
        provider = _SlowProvider(delay=0.0)
        calls = []
        for _ in range(LLMConfig.MAX_CONCURRENT_CALLS):
            call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
            call.start()
            calls.append(call)
        # Wait for them all.
        deadline = time.monotonic() + 2.0
        while not all(c.status in (CallStatus.DONE, CallStatus.ERROR, CallStatus.CANCELLED)
                      for c in calls) and time.monotonic() < deadline:
            time.sleep(0.01)
        # Now we can start another one.
        extra = LLMBackgroundCall(provider, [Message(role=Role.USER, content="x")])
        extra.start()  # MUST NOT raise


class TestLockSafety:
    def test_concurrent_status_reads_do_not_corrupt_state(self):
        """100 concurrent reads of status from different threads while
        the worker mutates it never raise / never see torn state."""
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()

        valid = {CallStatus.PENDING, CallStatus.RUNNING, CallStatus.DONE,
                 CallStatus.ERROR, CallStatus.CANCELLED}
        seen = []
        barrier = threading.Barrier(10)

        def reader():
            barrier.wait()
            for _ in range(20):
                seen.append(call.status)

        threads = [threading.Thread(target=reader) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2.0)

        for s in seen:
            assert s in valid


class TestShutdownAllCalls:
    def test_joins_in_flight_workers(self):
        from game.services.llm.background import (
            CallStatus,
            LLMBackgroundCall,
            shutdown_all_calls,
        )

        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        shutdown_all_calls(timeout=2.0)
        # Worker has finished.
        assert call.status in (CallStatus.DONE, CallStatus.CANCELLED)

    def test_empty_shutdown_is_noop(self):
        from game.services.llm.background import shutdown_all_calls

        # No calls in flight; should return cleanly.
        shutdown_all_calls(timeout=0.1)
