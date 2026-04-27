"""Tests for the LLMProvider protocol (PROJ-296)."""
import inspect
import threading
from typing import Any, List, Optional


class TestLLMProviderProtocol:
    def test_protocol_is_runtime_checkable(self):
        from game.services.llm.provider import LLMProvider
        from game.services.llm.types import (
            CompletionResult,
            FinishReason,
            Message,
            TokenUsage,
        )

        class _Dummy:
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
                return CompletionResult(
                    text="",
                    usage=TokenUsage(0, 0, 0),
                    model="x",
                    finish_reason=FinishReason.STOP,
                    latency_seconds=0.0,
                    provider="dummy",
                )

        assert isinstance(_Dummy(), LLMProvider)

    def test_class_missing_complete_does_not_satisfy(self):
        from game.services.llm.provider import LLMProvider

        class _Empty:
            pass

        assert not isinstance(_Empty(), LLMProvider)

    def test_protocol_complete_signature_documents_kwargs(self):
        """The Protocol's complete() method must accept the documented kwargs."""
        from game.services.llm.provider import LLMProvider

        sig = inspect.signature(LLMProvider.complete)
        params = sig.parameters

        # `messages` is positional-or-keyword
        assert "messages" in params
        # All optional knobs are keyword-only with default None
        for name in (
            "model",
            "temperature",
            "max_tokens",
            "timeout_seconds",
            "cancel_token",
        ):
            assert name in params, f"missing kwarg {name}"
            assert params[name].kind == inspect.Parameter.KEYWORD_ONLY, (
                f"{name} should be keyword-only"
            )
            assert params[name].default is None, (
                f"{name} should default to None"
            )
        # **opts escape hatch
        opts = params.get("opts")
        assert opts is not None
        assert opts.kind == inspect.Parameter.VAR_KEYWORD
