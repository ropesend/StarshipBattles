"""LLM provider protocol (PROJ-296).

Defines the pluggable contract every concrete provider must satisfy.

Concrete providers (e.g. `DeepSeekProvider`) live in sibling modules
and are wired into `LLMProviderFactory` (see `factory.py`).

The protocol is `@runtime_checkable` so isinstance() checks work,
which is occasionally useful in tests; production code typically
just calls `.complete()` directly without an isinstance check.
"""
import threading
from typing import Any, List, Optional, Protocol, runtime_checkable

from game.services.llm.types import CompletionResult, Message


@runtime_checkable
class LLMProvider(Protocol):
    """Pluggable LLM provider interface.

    Synchronous; threading is the caller's responsibility (see
    `LLMBackgroundCall` in `background.py` for the standard pattern).

    Implementations MUST raise `LLMException` (or a subclass) on
    failure rather than returning a sentinel.
    """

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
        """Send messages, return the assistant's reply.

        Args:
            messages: Ordered chat history. The first message MAY be a
                system prompt (`role=Role.SYSTEM`); the remainder
                alternate user/assistant.
            model: Override the provider's default model
                (`LLMConfig.DEFAULT_MODEL` when None).
            temperature: Sampling temperature. Provider-specific range
                (typically 0.0-2.0).
            max_tokens: Cap on completion length in tokens.
            timeout_seconds: Read-side request timeout. Connect-side
                timeout is fixed by `LLMConfig.CONNECT_TIMEOUT_SECONDS`.
            cancel_token: Optional `threading.Event` the implementation
                checks between retries. Setting the event signals the
                provider to stop ASAP and raise `LLMCancelled`. The
                in-flight HTTP request itself may still complete in the
                background (the response is then discarded).
            **opts: Provider-specific extras (e.g. DeepSeek's `top_p`,
                Anthropic's `metadata`). Unknown opts must be ignored
                silently rather than raising.

        Returns:
            A populated `CompletionResult`.

        Raises:
            LLMConfigError:    No API key, unknown provider, or auth failure.
            LLMNetworkError:   Connection / DNS / SSL / exhausted retries.
            LLMResponseError:  Malformed body or non-2xx (other than 429).
            LLMRateLimited:    Provider returned 429.
            LLMTimeoutError:   Request exceeded the configured timeout.
            LLMCancelled:      `cancel_token` was set during the call.
        """
        ...


__all__ = ["LLMProvider"]
