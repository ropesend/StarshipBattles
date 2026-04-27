"""Module-level default LLM provider slot (PROJ-296 Phase 6).

Mirrors the pattern used by `game.core.profiling`, `game.core.registry`,
etc. (see PROJ-258). `ApplicationContext.create_production()` calls
`set_default_llm_provider()` once at startup so that
`get_default_llm_provider()` and `ctx.llm_provider` return the same
instance.

`get_default_llm_provider()` returns `None` when no provider has been
configured (deferred validation pattern). Consumers must check
`if provider is not None:` before using.
"""
from typing import Optional

from game.services.llm.provider import LLMProvider

_default_llm_provider: Optional[LLMProvider] = None


def get_default_llm_provider() -> Optional[LLMProvider]:
    """Return the application-wide default LLM provider, or None.

    None means no provider could be constructed (e.g. no API key set).
    Consumers (race description, diplomacy) should treat None as "this
    feature is not available right now" — typically by disabling the
    UI affordance with a tooltip explanation rather than raising.
    """
    return _default_llm_provider


def set_default_llm_provider(provider: Optional[LLMProvider]) -> None:
    """Set the application-wide default LLM provider.

    Called by `ApplicationContext.create_production()` at startup, or
    by tests that want to inject a mock provider into code that uses
    the module-level accessor.
    """
    global _default_llm_provider
    _default_llm_provider = provider


__all__ = ["get_default_llm_provider", "set_default_llm_provider"]
