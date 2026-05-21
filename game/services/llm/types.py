"""LLM service DTOs (PROJ-296).

Frozen dataclasses describing messages, token usage, and completion
results. All values are JSON-serializable via the str-enum trick on
`Role` and `FinishReason`.

See `Projects/active_projects/PROJ-296/design.md` for the full API
surface and the rationale behind each field.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Role(str, Enum):
    """OpenAI-chat-completion-compatible message role.

    `TOOL` is included for forward compatibility with tool / function
    calling. PROJ-296 v1 does not emit or consume `tool` messages.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """Why the completion ended.

    `STOP`      — model emitted its end-of-turn token cleanly.
    `LENGTH`    — hit the `max_tokens` cap mid-output.
    `CANCELLED` — the call was cancelled via `cancel_token`.
    `ERROR`     — provider failed; see the raised LLMException for details.
    """
    STOP = "stop"
    LENGTH = "length"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass(frozen=True)
class Message:
    """A single message in a chat completion request."""
    role: Role
    content: str

    def __repr__(self) -> str:
        # PROJ-466: never dump the full prompt content in repr (logs,
        # tracebacks, debuggers). Report role + length only.
        role = self.role.value if isinstance(self.role, Role) else self.role
        return f"Message(role={role!r}, content_len={len(self.content)})"


@dataclass(frozen=True)
class TokenUsage:
    """Token accounting reported by the provider.

    `cached_prompt_tokens` defaults to 0 and is set by providers that
    report prompt-cache hits (e.g., Anthropic, DeepSeek with caching
    enabled). The three other fields are required and follow the
    OpenAI convention.
    """
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_prompt_tokens: int = 0


@dataclass(frozen=True)
class CompletionResult:
    """Provider-agnostic chat-completion result.

    Attributes:
        text: The assistant's reply.
        usage: Token accounting (see TokenUsage).
        model: Concrete model identifier returned by the provider
            (may differ from the requested model when an alias was used).
        finish_reason: Why the completion ended (see FinishReason).
        latency_seconds: Wall time of the underlying HTTP call,
            measured client-side. Useful for observability and
            consumer UX (e.g. "show retry dialog after 30s").
        provider: Short provider identifier (e.g. "deepseek").
        request_id: Provider's request id for support traces. None
            when the provider did not return one.
    """
    text: str
    usage: TokenUsage
    model: str
    finish_reason: FinishReason
    latency_seconds: float
    provider: str
    request_id: Optional[str] = None

    def __repr__(self) -> str:
        # PROJ-466: never dump the full response text in repr. Report
        # safe metadata only (text length, model, finish reason, latency,
        # token usage).
        finish = (
            self.finish_reason.value
            if isinstance(self.finish_reason, FinishReason)
            else self.finish_reason
        )
        return (
            f"CompletionResult(text_len={len(self.text)}, "
            f"model={self.model!r}, finish_reason={finish!r}, "
            f"latency_seconds={self.latency_seconds}, "
            f"total_tokens={self.usage.total_tokens})"
        )


__all__ = [
    "Role",
    "FinishReason",
    "Message",
    "TokenUsage",
    "CompletionResult",
]
