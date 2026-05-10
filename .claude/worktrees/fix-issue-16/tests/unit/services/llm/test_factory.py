"""Tests for LLMProviderFactory (PROJ-296 Phase 3)."""
import pytest


class TestProviderRegistration:
    def test_register_provider_adds_to_registry(self, reset_llm_factory):
        from game.services.llm import factory
        from tests.unit.services.llm.conftest import _StubProvider

        factory.register_provider("stub", _StubProvider)
        assert "stub" in factory._PROVIDERS
        assert factory._PROVIDERS["stub"] is _StubProvider


class TestFactoryCreate:
    def test_create_returns_registered_instance(self, reset_llm_factory):
        from game.services.llm import factory
        from game.services.llm.factory import LLMProviderFactory
        from tests.unit.services.llm.conftest import _StubProvider

        factory.register_provider("stub", _StubProvider)
        provider = LLMProviderFactory.create("stub")
        assert isinstance(provider, _StubProvider)

    def test_create_reads_env_var_when_name_omitted(
        self, monkeypatch, reset_llm_factory
    ):
        from game.services.llm import factory
        from game.services.llm.factory import LLMProviderFactory
        from tests.unit.services.llm.conftest import _StubProvider

        factory.register_provider("stub", _StubProvider)
        monkeypatch.setenv("LLM_PROVIDER", "stub")
        provider = LLMProviderFactory.create()
        assert isinstance(provider, _StubProvider)

    def test_create_defaults_to_deepseek_name(
        self, monkeypatch, reset_llm_factory
    ):
        """When LLM_PROVIDER is unset, the factory tries 'deepseek'.

        Phase 4 wires DeepSeek into the registry, so this resolves to a
        real provider construction. The DeepSeek constructor doesn't
        validate the key (per security model), so we get back a
        DeepSeekProvider instance regardless of env state.
        """
        # Force deepseek import + self-registration.
        from game.services.llm import deepseek  # noqa: F401
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.factory import LLMProviderFactory

        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        provider = LLMProviderFactory.create()
        assert isinstance(provider, DeepSeekProvider)

    def test_create_unknown_default_when_nothing_registered(
        self, monkeypatch, reset_llm_factory
    ):
        """If no providers are registered AND LLM_PROVIDER is unset,
        factory raises LLMConfigError naming 'deepseek' as the default."""
        from game.core.exceptions import LLMConfigError
        from game.services.llm import factory
        from game.services.llm.factory import LLMProviderFactory

        # Wipe the registry for this test (reset_llm_factory restores after).
        factory._PROVIDERS.clear()
        monkeypatch.delenv("LLM_PROVIDER", raising=False)

        with pytest.raises(LLMConfigError) as exc_info:
            LLMProviderFactory.create()
        assert exc_info.value.context["provider"] == "deepseek"

    def test_create_unknown_provider_raises_config_error(self, reset_llm_factory):
        from game.core.error_codes import ErrorCode
        from game.core.exceptions import LLMConfigError
        from game.services.llm.factory import LLMProviderFactory

        with pytest.raises(LLMConfigError) as exc_info:
            LLMProviderFactory.create("unknown-model")
        exc = exc_info.value
        assert exc.code == ErrorCode.LLM_CONFIG_MISSING.value
        assert exc.context["provider"] == "unknown-model"
        assert "registered" in exc.context

    def test_create_returns_none_when_provider_init_raises_config_error(
        self, reset_llm_factory
    ):
        """If a registered provider's constructor raises LLMConfigError
        (typically: no API key), factory returns None for deferred validation."""
        from game.core.exceptions import LLMConfigError
        from game.services.llm import factory
        from game.services.llm.factory import LLMProviderFactory

        class _NoKeyProvider:
            def __init__(self):
                raise LLMConfigError("no key", code="L001")

        factory.register_provider("nokey", _NoKeyProvider)
        result = LLMProviderFactory.create("nokey")
        assert result is None

    def test_create_propagates_non_config_errors(self, reset_llm_factory):
        """Other exceptions during construction propagate (do not silently None)."""
        from game.services.llm import factory
        from game.services.llm.factory import LLMProviderFactory

        class _BrokenProvider:
            def __init__(self):
                raise RuntimeError("boom")

        factory.register_provider("broken", _BrokenProvider)
        with pytest.raises(RuntimeError, match="boom"):
            LLMProviderFactory.create("broken")


class TestProvidersIsADict:
    """Per docs/03_CONVENTIONS.md §6.5 — no hardcoded type lists.

    Provider dispatch must be a dict, not an if/elif chain.
    """

    def test_providers_is_a_dict(self):
        from game.services.llm import factory

        assert isinstance(factory._PROVIDERS, dict)
