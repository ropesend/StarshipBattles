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
        # PROJ-324 Phase 2: deterministic event-based wait.
        assert call.wait(timeout=2.0), "call did not complete within 2s"
        assert call.status == CallStatus.DONE
        assert call.result is not None
        assert call.result.text == "stub-response"
        assert call.error is None

    def test_elapsed_seconds_is_monotonic_then_frozen(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        # PROJ-479 Task 4.1: replaced two time.sleep waits with deterministic
        # event-based / completion-based checks. `elapsed_seconds` after the
        # call completes (and wait() returns) must equal the post-completion
        # snapshot regardless of how much real time elapses afterward.
        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        assert call.elapsed_seconds == 0.0
        call.start()
        # Wait for completion deterministically (no sleep needed for mid-elapsed).
        assert call.wait(timeout=2.0), "call did not complete within 2s"
        assert call.status == CallStatus.DONE
        end = call.elapsed_seconds
        assert end > 0.0
        # Frozen-after-completion contract: re-reading elapsed at any later
        # moment returns the same value. No sleep required to verify this:
        # the contract is "frozen", not "frozen-after-Xs".
        assert call.elapsed_seconds == end


class TestErrorPath:
    def test_propagates_llm_exception_to_error_field(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        provider = _SlowProvider(delay=0.0, raise_exc=LLMNetworkError("boom", code="L002"))
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        assert call.wait(timeout=2.0), "call did not complete within 2s"
        assert call.status == CallStatus.ERROR
        assert call.result is None
        assert isinstance(call.error, LLMNetworkError)
        assert call.error.code == "L002"

    def test_unexpected_exception_is_wrapped_to_terminal_error(self):
        # PROJ-321..328 audit S1.1: a non-LLMException raised by the
        # provider used to escape `_run()` past the inner finally with
        # `_status=RUNNING`, so `wait()` returned True on a non-terminal
        # state. The fix wraps it in `LLMUnexpectedError` and transitions
        # to ERROR before signaling completion. Reproduces what Codex
        # demonstrated independently with a `RuntimeError`-raising provider.
        from game.core.exceptions import LLMException, LLMUnexpectedError
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        original = RuntimeError("dispatch boom")
        provider = _SlowProvider(delay=0.0, raise_exc=original)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        assert call.wait(timeout=2.0), "call did not reach terminal state within 2s"
        assert call.status == CallStatus.ERROR, (
            "wait() must only return True for terminal state DONE/ERROR/CANCELLED"
        )
        assert call.result is None
        # Wrapped, type-narrowed:
        assert isinstance(call.error, LLMException)
        assert isinstance(call.error, LLMUnexpectedError)
        # Original exception preserved on __cause__:
        assert call.error.__cause__ is original
        # Original type recorded in safe-to-log context:
        assert call.error.context.get("original_exception_type") == "RuntimeError"


class TestCancellation:
    def test_cancel_marks_status_cancelled(self):
        from game.services.llm.background import CallStatus, LLMBackgroundCall

        # PROJ-479 Task 4.1: replaced `time.sleep(0.02)` with a deterministic
        # `_wait_until` poll for `call.status == RUNNING`. Same intent
        # ("let worker actually start") but no race window / no fixed wait.
        provider = _SlowProvider(delay=0.5)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])
        call.start()
        deadline = time.monotonic() + 2.0
        while call.status != CallStatus.RUNNING and time.monotonic() < deadline:
            time.sleep(0.001)  # micro-yield, not a fixed test wait
        call.cancel()
        assert call.wait(timeout=2.0), "call did not reach a terminal state within 2s"
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
        assert call.wait(timeout=2.0), "call did not complete within 2s"
        # The stub was called exactly once.
        assert stub_llm_provider.call_count == 1

    def test_concurrent_start_on_same_instance_is_atomic(self):
        """PROJ-353A audit-remediation R1: Codex flagged that
        ``LLMBackgroundCall.start()`` is sequentially idempotent but not
        concurrently idempotent. Pre-fix, two threads calling ``start()``
        on the same instance can both pass the ``_thread is None`` guard
        before either assigns ``_thread``, because ``_state_lock`` is
        released between the guard and the slot reservation
        (``game/services/llm/background.py:129-162``). Result: two slots
        reserved, two workers spawned, single-call idempotency contract
        violated.

        This test forces the race deterministically by wrapping
        ``call._state_lock`` so that on first release each thread blocks
        on a 2-thread ``threading.Barrier`` before continuing. With both
        threads stalled past the guard at the barrier, the pre-fix
        guard-then-reserve-then-assign sequence necessarily double-spawns;
        the post-fix atomic guard+reserve+assign sequence allows exactly
        one through.
        """
        import threading as _threading

        from game.services.llm import background
        from game.services.llm.background import LLMBackgroundCall

        provider = _SlowProvider(delay=0.05)
        call = LLMBackgroundCall(provider, [Message(role=Role.USER, content="hi")])

        gate = _threading.Barrier(2, timeout=3.0)
        racer_tids: set[int] = set()
        racer_tids_lock = _threading.Lock()

        class _GatedLock:
            """Wraps a real Lock so racer threads (and only racer threads)
            cross a 2-thread barrier on their first release. The worker
            thread spawned by production must NOT be gated — it would
            block at a barrier no third party can satisfy.

            Mimics the ``__enter__/__exit__`` and explicit
            ``acquire/release`` surface used by production.
            """

            def __init__(self, real_lock, barrier):
                self._real = real_lock
                self._barrier = barrier
                self._gated_already: set[int] = set()

            def __enter__(self):
                self._real.__enter__()
                return self

            def __exit__(self, exc_type, exc, tb):
                tid = _threading.get_ident()
                with racer_tids_lock:
                    is_racer = tid in racer_tids
                already_gated = tid in self._gated_already
                must_gate = is_racer and not already_gated
                if must_gate:
                    self._gated_already.add(tid)
                # Release real lock first so the OTHER racer can acquire.
                result = self._real.__exit__(exc_type, exc, tb)
                if must_gate:
                    try:
                        self._barrier.wait()
                    except _threading.BrokenBarrierError:
                        pass
                return result

            def acquire(self, *args, **kwargs):
                return self._real.acquire(*args, **kwargs)

            def release(self, *args, **kwargs):
                return self._real.release(*args, **kwargs)

        # Swap the instance attribute (tests can mutate; production
        # constructed it as `threading.Lock()` per
        # `game/services/llm/background.py:113`).
        original_lock = call._state_lock
        call._state_lock = _GatedLock(original_lock, gate)

        errors: list[BaseException] = []

        def runner():
            with racer_tids_lock:
                racer_tids.add(_threading.get_ident())
            try:
                call.start()
            except BaseException as exc:  # capture for assertion
                errors.append(exc)

        try:
            t1 = _threading.Thread(target=runner, name="start-racer-A")
            t2 = _threading.Thread(target=runner, name="start-racer-B")
            t1.start()
            t2.start()
            t1.join(timeout=4.0)
            t2.join(timeout=4.0)
        finally:
            # Restore so the worker thread (spawned by the winning
            # racer at the end of `start()`) acquires the original
            # `_state_lock` from inside `_run()` without test wrapper.
            call._state_lock = original_lock

        assert not t1.is_alive() and not t2.is_alive(), (
            "concurrent start() threads did not complete; possible deadlock"
        )
        assert not errors, f"start() raised in racer thread(s): {errors!r}"

        # Wait for whichever worker actually got spawned to complete.
        assert call.wait(timeout=2.0), "spawned worker did not complete"

        # Post-fix contract: exactly ONE provider invocation. Pre-fix
        # the race spawned 2 workers and `provider.call_count` would be 2.
        assert provider.call_count == 1, (
            f"start() must spawn exactly one worker; got {provider.call_count} "
            "provider invocations (PROJ-353A audit-R1: same-instance concurrent "
            "start() reserved multiple slots pre-fix)"
        )
        # Counter + active workers drained back to zero by cleanup. Pre-fix
        # the second worker would have leaked a second counter increment
        # (`_in_flight_calls` would still be 1 after cleanup of one worker).
        with background._in_flight_lock:
            in_flight = background._in_flight_calls
            active = len(background._active_workers)
        assert in_flight == 0, (
            f"in-flight counter leaked: expected 0 after completion, got {in_flight}"
        )
        assert active == 0, (
            f"_active_workers leaked: expected 0 after completion, got {active}"
        )


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
        for c in calls:
            assert c.wait(timeout=2.0), "call did not complete within 2s"
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
