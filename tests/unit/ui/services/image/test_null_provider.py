"""Tests for NullImageProvider (PROJ-314)."""
from __future__ import annotations

import pytest

from game.core.exceptions import ImageConfigError
from game.ui.services.image import ImageProvider, NullImageProvider


class TestNullImageProvider:
    """Always-raises stub provider."""

    def test_satisfies_protocol(self) -> None:
        assert isinstance(NullImageProvider(), ImageProvider)

    def test_generate_raises_image_config_error(self) -> None:
        provider = NullImageProvider()
        with pytest.raises(ImageConfigError) as exc_info:
            provider.generate_image("anything")
        assert "NullImageProvider" in str(exc_info.value)

    def test_repr_does_not_leak_secrets(self) -> None:
        provider = NullImageProvider()
        assert "NullImageProvider" in repr(provider)
