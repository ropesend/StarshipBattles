"""LLM provider abstraction (PROJ-296).

Public API populated incrementally across PROJ-296 phases:
- Phase 2: types + provider protocol     ← landed
- Phase 3: provider factory              ← landed
- Phase 4: DeepSeek concrete provider    ← landed
- Phase 5: background-call helper        ← landed
- Phase 6: module-level default-provider accessors
"""
from game.services.llm.background import (
    CallStatus,
    LLMBackgroundCall,
    shutdown_all_calls,
)
from game.services.llm.defaults import (
    get_default_llm_provider,
    set_default_llm_provider,
)
from game.services.llm.factory import LLMProviderFactory, register_provider
from game.services.llm.provider import LLMProvider
from game.services.llm.types import (
    CompletionResult,
    FinishReason,
    Message,
    Role,
    TokenUsage,
)

# Side-effect import: registers `deepseek` with the factory.
from game.services.llm import deepseek  # noqa: F401

__all__ = [
    # types
    "Role",
    "FinishReason",
    "Message",
    "TokenUsage",
    "CompletionResult",
    # protocol
    "LLMProvider",
    # factory (Phase 3)
    "LLMProviderFactory",
    "register_provider",
    # background helper (Phase 5)
    "CallStatus",
    "LLMBackgroundCall",
    "shutdown_all_calls",
    # default-provider accessors (Phase 6)
    "get_default_llm_provider",
    "set_default_llm_provider",
]
