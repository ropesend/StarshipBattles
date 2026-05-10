"""Contract tests for ImageProvider Protocol + ImageResult DTO (PROJ-314)."""
from __future__ import annotations

import pytest

from game.ui.services.image import ImageProvider, ImageResult


class TestImageResult:
    """Frozen DTO contract."""

    def test_minimum_construction(self) -> None:
        result = ImageResult(
            image_bytes=b"\x89PNG",
            size=(2048, 2048),
            model="gpt-image-2",
            latency_ms=1234.5,
            provider="openai",
        )
        assert result.image_bytes == b"\x89PNG"
        assert result.size == (2048, 2048)
        assert result.model == "gpt-image-2"
        assert result.latency_ms == 1234.5
        assert result.provider == "openai"
        assert result.request_id is None
        assert result.revised_prompt is None

    def test_full_construction(self) -> None:
        result = ImageResult(
            image_bytes=b"x",
            size=(1024, 1024),
            model="gpt-image-2",
            latency_ms=500.0,
            provider="openai",
            request_id="req-abc",
            revised_prompt="a battleship",
        )
        assert result.request_id == "req-abc"
        assert result.revised_prompt == "a battleship"

    def test_is_frozen(self) -> None:
        result = ImageResult(
            image_bytes=b"x", size=(1, 1), model="m",
            latency_ms=0.0, provider="p",
        )
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError.
            result.image_bytes = b"y"  # type: ignore[misc]


class TestImageProviderProtocol:
    """Runtime-checkable protocol shape."""

    def test_class_with_generate_image_satisfies_protocol(self) -> None:
        class _Stub:
            def generate_image(self, prompt: str, **kwargs: object) -> ImageResult:
                return ImageResult(
                    image_bytes=b"", size=(0, 0), model="x",
                    latency_ms=0.0, provider="stub",
                )

        assert isinstance(_Stub(), ImageProvider)

    def test_class_without_generate_image_fails_protocol(self) -> None:
        class _Stub:
            pass

        assert not isinstance(_Stub(), ImageProvider)
