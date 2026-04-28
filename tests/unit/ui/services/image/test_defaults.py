"""Tests for module-level image-provider singleton accessors (PROJ-314)."""
from __future__ import annotations

from game.ui.services.image import (
    NullImageProvider,
    get_default_image_provider,
    set_default_image_provider,
)


class TestDefaults:
    """Get/set singleton accessor pair."""

    def test_get_returns_what_set_set(self) -> None:
        provider = NullImageProvider()
        set_default_image_provider(provider)
        assert get_default_image_provider() is provider

    def test_set_none_returns_none(self) -> None:
        set_default_image_provider(None)
        assert get_default_image_provider() is None

    def test_default_after_conftest_reset_is_null_provider(self) -> None:
        # The autouse fixture in tests/conftest.py installs a fresh
        # NullImageProvider before every test.
        provider = get_default_image_provider()
        assert isinstance(provider, NullImageProvider)
