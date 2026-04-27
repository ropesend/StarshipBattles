"""Tests for module-level get/set_default_llm_provider() (PROJ-296 Phase 6)."""
import pytest


@pytest.fixture(autouse=True)
def _reset_default_provider():
    """Snapshot+restore the module-level default LLM provider slot."""
    from game.services.llm import defaults

    snapshot = defaults._default_llm_provider
    yield
    defaults._default_llm_provider = snapshot


class TestDefaultProviderAccessors:
    def test_unset_returns_none(self):
        from game.services.llm import set_default_llm_provider, get_default_llm_provider

        set_default_llm_provider(None)
        assert get_default_llm_provider() is None

    def test_set_then_get_returns_same_instance(self, stub_llm_provider):
        from game.services.llm import set_default_llm_provider, get_default_llm_provider

        set_default_llm_provider(stub_llm_provider)
        assert get_default_llm_provider() is stub_llm_provider

    def test_set_none_clears_slot(self, stub_llm_provider):
        from game.services.llm import set_default_llm_provider, get_default_llm_provider

        set_default_llm_provider(stub_llm_provider)
        set_default_llm_provider(None)
        assert get_default_llm_provider() is None
