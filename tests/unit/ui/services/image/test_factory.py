"""Tests for ImageProviderFactory (PROJ-314)."""
from __future__ import annotations

import pytest

from game.core.exceptions import ImageConfigError
from game.ui.services.image import (
    ImageProviderFactory,
    NullImageProvider,
    register_image_provider,
)
from game.ui.services.image.factory import _PROVIDERS


class TestImageProviderFactory:
    """Env-var dispatch + deferred-validation contract."""

    def test_default_creates_openai_or_null(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # No env, no key — OpenAI provider raises ImageConfigError on
        # construction, factory returns None (deferred validation).
        monkeypatch.delenv("IMAGE_PROVIDER", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        provider = ImageProviderFactory.create()
        # OpenAIImageProvider's constructor doesn't read the env, so it
        # actually constructs successfully. The first generate_image call
        # is what raises. So `create()` returns the provider.
        assert provider is not None  # construction itself doesn't fail.

    def test_create_with_explicit_null_name(self) -> None:
        provider = ImageProviderFactory.create("null")
        assert isinstance(provider, NullImageProvider)

    def test_create_unknown_provider_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("IMAGE_PROVIDER", raising=False)
        with pytest.raises(ImageConfigError) as exc_info:
            ImageProviderFactory.create("does-not-exist")
        assert "registered" in (exc_info.value.context or {})
        assert "does-not-exist" in str(exc_info.value)

    def test_env_var_dispatch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("IMAGE_PROVIDER", "null")
        provider = ImageProviderFactory.create()
        assert isinstance(provider, NullImageProvider)

    def test_register_image_provider(self) -> None:
        class _CustomProvider:
            def generate_image(self, prompt, **kwargs):
                raise NotImplementedError

        try:
            register_image_provider("test-custom-x", _CustomProvider)
            provider = ImageProviderFactory.create("test-custom-x")
            assert isinstance(provider, _CustomProvider)
        finally:
            _PROVIDERS.pop("test-custom-x", None)

    def test_constructor_image_config_error_returns_none(self) -> None:
        from game.core.error_codes import ErrorCode

        class _FailingProvider:
            def __init__(self) -> None:
                raise ImageConfigError(
                    "no key",
                    code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                    context={},
                )

            def generate_image(self, prompt, **kwargs):  # pragma: no cover
                raise NotImplementedError

        try:
            register_image_provider("test-failing-x", _FailingProvider)
            provider = ImageProviderFactory.create("test-failing-x")
            assert provider is None  # deferred validation.
        finally:
            _PROVIDERS.pop("test-failing-x", None)
