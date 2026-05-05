"""Tests for OpenAIImageProvider (PROJ-314).

All HTTP calls are mocked. The session-level real-HTTP block in
``tests/conftest.py`` would fail loudly if any test escapes to the
real network.
"""
from __future__ import annotations

import base64
import pathlib
from unittest.mock import MagicMock, patch

import pytest
import requests

from game.core.exceptions import (
    ImageCancelled,
    ImageConfigError,
    ImageNetworkError,
    ImageRateLimited,
    ImageResponseError,
    ImageTimeoutError,
)
from game.ui.services.image import ImageResult
from game.ui.services.image.openai_provider import (
    OPENAI_EDITS_ENDPOINT,
    OPENAI_GENERATIONS_ENDPOINT,
    OpenAIImageProvider,
)


def _b64_blank_png() -> str:
    """Return a base64-encoded 1x1 transparent PNG."""
    # 1x1 transparent PNG (smallest valid file).
    raw = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\rIDATx\x9cc\xfc\xff\xff?\x03\x00\x05\xfe"
        b"\x02\xfe\xa14\x18\xfa\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return base64.b64encode(raw).decode("ascii")


def _ok_response() -> MagicMock:
    response = MagicMock()
    response.status_code = 200
    response.headers = {"x-request-id": "req-test-1"}
    response.json.return_value = {
        "data": [
            {
                "b64_json": _b64_blank_png(),
                "revised_prompt": "a starship",
            }
        ],
        "id": "img-1",
    }
    return response


class TestOpenAIImageProviderHappyPath:
    def test_generate_image_returns_image_result(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=_ok_response()) as mock_post:
            result = provider.generate_image(
                "a starship", size="1024x1024", model="gpt-image-2",
            )
        assert isinstance(result, ImageResult)
        assert result.size == (1, 1)  # the actual size of the test PNG.
        assert result.model == "gpt-image-2"
        assert result.provider == "openai"
        assert result.revised_prompt == "a starship"
        assert result.image_bytes.startswith(b"\x89PNG")
        # Verify the endpoint and headers.
        args, kwargs = mock_post.call_args
        assert args[0] == OPENAI_GENERATIONS_ENDPOINT
        assert "Bearer test-key" in kwargs["headers"]["Authorization"]

    def test_generate_image_with_edit_image_posts_to_edits_endpoint(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        edit_image = tmp_path / "source.png"
        mask = tmp_path / "mask.png"
        edit_image.write_bytes(b"source-bytes")
        mask.write_bytes(b"mask-bytes")

        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=_ok_response()) as mock_post:
            result = provider.generate_image(
                "paint a cruiser",
                size="1024x1024",
                model="gpt-image-2",
                edit_image=edit_image,
                mask=mask,
                quality="high",
            )

        assert result.provider == "openai"
        args, kwargs = mock_post.call_args
        assert args[0] == OPENAI_EDITS_ENDPOINT
        assert kwargs["data"] == {
            "model": "gpt-image-2",
            "prompt": "paint a cruiser",
            "size": "1024x1024",
            "response_format": "b64_json",
            "n": 1,
            "quality": "high",
        }
        assert kwargs["files"]["image"] == ("image.png", b"source-bytes", "image/png")
        assert kwargs["files"]["mask"] == ("mask.png", b"mask-bytes", "image/png")
        assert "Content-Type" not in kwargs["headers"]


class TestOpenAIImageProviderErrors:
    def test_no_api_key_raises_image_config_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        provider = OpenAIImageProvider()
        with pytest.raises(ImageConfigError):
            provider.generate_image("a starship")

    def test_rate_limit_raises_immediately(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        response = MagicMock()
        response.status_code = 429
        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=response):
            with pytest.raises(ImageRateLimited):
                provider.generate_image("x")

    def test_auth_failure_raises_image_config_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "bad")
        response = MagicMock()
        response.status_code = 401
        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=response):
            with pytest.raises(ImageConfigError):
                provider.generate_image("x")

    def test_400_raises_image_response_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        response = MagicMock()
        response.status_code = 400
        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=response):
            with pytest.raises(ImageResponseError):
                provider.generate_image("x")

    def test_timeout_raises_image_timeout_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        import requests

        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        provider = OpenAIImageProvider()
        with patch("requests.post", side_effect=requests.Timeout("slow")):
            with pytest.raises(ImageTimeoutError):
                provider.generate_image("x")

    def test_connection_error_raises_image_network_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        provider = OpenAIImageProvider()
        with patch("requests.post", side_effect=requests.ConnectionError("dns")):
            with pytest.raises(ImageNetworkError):
                provider.generate_image("x")

    def test_ssl_error_raises_specific_image_network_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        provider = OpenAIImageProvider()
        with patch("requests.post", side_effect=requests.exceptions.SSLError("cert")):
            with pytest.raises(ImageNetworkError) as exc_info:
                provider.generate_image("x")
        assert "SSL" in str(exc_info.value)

    def test_5xx_retries_then_raises(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        # Make backoff instant to keep the test fast.
        from game.core.config import ImageConfig

        monkeypatch.setattr(ImageConfig, "RETRY_BACKOFF_BASE_SECONDS", 0.0)
        response = MagicMock()
        response.status_code = 503
        provider = OpenAIImageProvider()
        with patch("requests.post", return_value=response) as mock_post:
            with pytest.raises(ImageNetworkError):
                provider.generate_image("x")
        # Initial + MAX_RETRIES_5XX retries.
        assert mock_post.call_count == ImageConfig.MAX_RETRIES_5XX + 1

    def test_cancel_token_set_before_call_raises_image_cancelled(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        import threading

        monkeypatch.setenv("OPENAI_API_KEY", "ok")
        provider = OpenAIImageProvider()
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(ImageCancelled):
            provider.generate_image("x", cancel_token=cancel)

    def test_repr_redacts_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "secret-key")
        provider = OpenAIImageProvider()
        assert "secret-key" not in repr(provider)
        assert "REDACTED" in repr(provider)

    def test_parse_response_rejects_non_json(self) -> None:
        response = MagicMock()
        response.status_code = 200
        response.json.side_effect = ValueError("not json")

        provider = OpenAIImageProvider()
        with pytest.raises(ImageResponseError) as exc_info:
            provider._parse_response(response, model_in_request="gpt-image-2", latency=0.1)

        assert "non-JSON" in str(exc_info.value)
        assert exc_info.value.context == {"status_code": 200, "model": "gpt-image-2"}

    def test_parse_response_rejects_missing_b64_json(self) -> None:
        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {"data": [{}]}

        provider = OpenAIImageProvider()
        with pytest.raises(ImageResponseError) as exc_info:
            provider._parse_response(response, model_in_request="gpt-image-2", latency=0.1)

        assert "missing expected fields" in str(exc_info.value)
        assert exc_info.value.context["missing_field"] == "'b64_json'"

    def test_parse_response_rejects_invalid_base64(self) -> None:
        response = MagicMock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {"data": [{"b64_json": "!!!!"}]}

        provider = OpenAIImageProvider()
        with pytest.raises(ImageResponseError) as exc_info:
            provider._parse_response(response, model_in_request="gpt-image-2", latency=0.1)

        assert "invalid base64" in str(exc_info.value)

    def test_read_actual_size_falls_back_when_pil_cannot_decode(self) -> None:
        assert OpenAIImageProvider._read_actual_size(b"not a png") == (0, 0)
