"""Smoke imports for the new game.services.llm package (PROJ-296)."""


def test_llm_package_exports_phase_2_symbols():
    """After Phase 2, the public API includes types + protocol."""
    from game.services.llm import (
        CompletionResult,
        FinishReason,
        LLMProvider,
        Message,
        Role,
        TokenUsage,
    )
    # All must be types/classes.
    for sym in (CompletionResult, FinishReason, LLMProvider,
                Message, Role, TokenUsage):
        assert isinstance(sym, type), f"{sym!r} should be a type"


def test_llm_package_exports_phase_3_symbols():
    """After Phase 3, the public API includes the factory."""
    from game.services.llm import LLMProviderFactory, register_provider

    assert isinstance(LLMProviderFactory, type)
    assert callable(register_provider)


def test_llm_package_exports_phase_5_symbols():
    """After Phase 5, the public API includes the background helper."""
    from game.services.llm import (
        CallStatus,
        LLMBackgroundCall,
        shutdown_all_calls,
    )

    assert isinstance(CallStatus, type)
    assert isinstance(LLMBackgroundCall, type)
    assert callable(shutdown_all_calls)
