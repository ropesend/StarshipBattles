"""Shared fixtures for LLM service tests (PROJ-296)."""
import threading
from typing import Any, List, Optional
from unittest.mock import MagicMock

import pytest

from game.services.llm.provider import LLMProvider
from game.services.llm.types import (
    CompletionResult,
    FinishReason,
    Message,
    TokenUsage,
)


class _StubProvider:
    """Test-only LLM provider that returns a hardcoded CompletionResult.

    Satisfies the LLMProvider protocol structurally. Records the most
    recent call's kwargs on `last_call_kwargs` for assertions.
    """

    def __init__(self, response_text: str = "stub-response") -> None:
        self._response_text = response_text
        self.last_call_kwargs: dict = {}
        self.call_count: int = 0

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
        self.last_call_kwargs = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout_seconds": timeout_seconds,
            "cancel_token": cancel_token,
            "opts": dict(opts),
        }
        return CompletionResult(
            text=self._response_text,
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            model=model or "stub-model",
            finish_reason=FinishReason.STOP,
            latency_seconds=0.0,
            provider="stub",
            request_id="stub-req-1",
        )


@pytest.fixture
def stub_llm_provider():
    """Fresh stub provider per test."""
    return _StubProvider()


@pytest.fixture
def mock_llm_provider():
    """MagicMock specced to LLMProvider for call-shape assertions."""
    return MagicMock(spec=LLMProvider)


@pytest.fixture
def reset_llm_factory():
    """Snapshot + restore the factory's _PROVIDERS registry between tests.

    Phase 3 introduces module-level state (`_PROVIDERS`) on
    `game.services.llm.factory`. Tests that mutate it must run in
    isolation; use this fixture to snapshot at start and restore at
    teardown.
    """
    from game.services.llm import factory

    snapshot = dict(factory._PROVIDERS)
    yield
    factory._PROVIDERS.clear()
    factory._PROVIDERS.update(snapshot)
