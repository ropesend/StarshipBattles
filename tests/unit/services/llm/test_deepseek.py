"""Tests for DeepSeekProvider (PROJ-296 Phase 4).

All HTTP is mocked via `unittest.mock.patch('requests.post', ...)`.
The autouse `_block_real_http` fixture in tests/conftest.py guarantees
no real call escapes.
"""
from unittest.mock import MagicMock, patch

import pytest
import requests

from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    LLMConfigError,
    LLMNetworkError,
    LLMRateLimited,
    LLMResponseError,
    LLMTimeoutError,
)


_FAKE_KEY = "ds-fake-test-key-not-real-12345"


def _make_response(*, status_code=200, json_body=None, text=""):
    """Build a MagicMock that quacks like requests.Response."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if json_body is not None:
        resp.json = MagicMock(return_value=json_body)
    else:
        resp.json = MagicMock(side_effect=ValueError("no json"))
    resp.text = text or (str(json_body) if json_body else "")
    resp.headers = {}
    return resp


def _ok_body(text="hello"):
    return {
        "id": "req_xyz",
        "model": "deepseek-chat",
        "choices": [
            {
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 3,
            "total_tokens": 8,
        },
    }


# ===========================================================================
# Construction & repr
# ===========================================================================


class TestConstruction:
    def test_construct_with_no_env_var(self, monkeypatch):
        """Provider constructs OK even when key is unset; key is read per-call."""
        from game.services.llm.deepseek import DeepSeekProvider

        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        provider = DeepSeekProvider()  # MUST NOT raise
        assert provider is not None

    def test_repr_redacts_api_key(self, monkeypatch):
        """repr() must NEVER include the API key."""
        from game.services.llm.deepseek import DeepSeekProvider

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        text = repr(provider)
        assert _FAKE_KEY not in text
        assert "REDACTED" in text or "redacted" in text.lower()

    def test_str_redacts_api_key(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        text = str(provider)
        assert _FAKE_KEY not in text


# ===========================================================================
# complete() happy path
# ===========================================================================


class TestCompleteHappyPath:
    def test_returns_completion_result(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import FinishReason, Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", return_value=_make_response(json_body=_ok_body("hi"))) as mock_post:
            result = provider.complete([Message(role=Role.USER, content="say hi")])

        assert result.text == "hi"
        assert result.usage.prompt_tokens == 5
        assert result.usage.completion_tokens == 3
        assert result.usage.total_tokens == 8
        assert result.model == "deepseek-chat"
        assert result.finish_reason == FinishReason.STOP
        assert result.provider == "deepseek"
        assert result.request_id == "req_xyz"
        assert result.latency_seconds >= 0.0
        mock_post.assert_called_once()

    def test_request_body_shape(self, monkeypatch):
        """Request body uses OpenAI-compatible chat completion shape."""
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        msgs = [
            Message(role=Role.SYSTEM, content="be brief"),
            Message(role=Role.USER, content="say hi"),
        ]
        with patch("requests.post", return_value=_make_response(json_body=_ok_body())) as mock_post:
            provider.complete(msgs, model="deepseek-chat", temperature=0.5, max_tokens=10)

        kwargs = mock_post.call_args.kwargs
        body = kwargs["json"]
        assert body["model"] == "deepseek-chat"
        assert body["temperature"] == 0.5
        assert body["max_tokens"] == 10
        assert body["messages"] == [
            {"role": "system", "content": "be brief"},
            {"role": "user", "content": "say hi"},
        ]

    def test_request_headers_include_auth_and_user_agent(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", return_value=_make_response(json_body=_ok_body())) as mock_post:
            provider.complete([Message(role=Role.USER, content="x")])

        headers = mock_post.call_args.kwargs["headers"]
        assert headers["Authorization"] == f"Bearer {_FAKE_KEY}"
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "starship-battles-llm/1.0"

    def test_request_uses_configured_timeout(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", return_value=_make_response(json_body=_ok_body())) as mock_post:
            provider.complete([Message(role=Role.USER, content="x")], timeout_seconds=42.0)

        timeout = mock_post.call_args.kwargs["timeout"]
        # (connect, read) tuple
        assert timeout[0] == 5.0  # CONNECT_TIMEOUT_SECONDS
        assert timeout[1] == 42.0  # explicit override

    def test_request_default_timeout_when_unspecified(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", return_value=_make_response(json_body=_ok_body())) as mock_post:
            provider.complete([Message(role=Role.USER, content="x")])

        timeout = mock_post.call_args.kwargs["timeout"]
        assert timeout == (5.0, 60.0)  # CONNECT, DEFAULT_TIMEOUT


# ===========================================================================
# Configuration errors
# ===========================================================================


class TestConfigErrors:
    def test_missing_key_raises_config_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        provider = DeepSeekProvider()
        with pytest.raises(LLMConfigError) as exc_info:
            provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_CONFIG_MISSING.value

    def test_empty_key_raises_config_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", "")
        provider = DeepSeekProvider()
        with pytest.raises(LLMConfigError):
            provider.complete([Message(role=Role.USER, content="x")])

    def test_401_raises_config_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", return_value=_make_response(status_code=401, json_body={})):
            with pytest.raises(LLMConfigError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_CONFIG_MISSING.value


# ===========================================================================
# Retry & rate-limit semantics
# ===========================================================================


class TestRetrySemantics:
    def test_retries_on_5xx_and_succeeds(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        responses = [
            _make_response(status_code=503, json_body={"error": "down"}),
            _make_response(status_code=503, json_body={"error": "down"}),
            _make_response(status_code=200, json_body=_ok_body("recovered")),
        ]
        with patch("requests.post", side_effect=responses) as mock_post, \
                patch("time.sleep") as mock_sleep:  # don't actually wait
            result = provider.complete([Message(role=Role.USER, content="x")])

        assert result.text == "recovered"
        assert mock_post.call_count == 3
        # Backoff was called twice (after attempts 1 and 2)
        assert mock_sleep.call_count == 2

    def test_5xx_exhausted_raises_network_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch(
            "requests.post",
            return_value=_make_response(status_code=503, json_body={"error": "down"}),
        ) as mock_post, patch("time.sleep"):
            with pytest.raises(LLMNetworkError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_NETWORK_ERROR.value
        # Initial attempt + MAX_RETRIES_5XX(2) = 3 calls
        assert mock_post.call_count == 3

    def test_429_is_not_retried(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch(
            "requests.post",
            return_value=_make_response(status_code=429, json_body={"error": "rate"}),
        ) as mock_post:
            with pytest.raises(LLMRateLimited) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_RATE_LIMITED.value
        assert mock_post.call_count == 1


# ===========================================================================
# Other 4xx, malformed responses, network errors
# ===========================================================================


class TestErrorPaths:
    def test_400_raises_response_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch(
            "requests.post",
            return_value=_make_response(status_code=400, json_body={"error": "bad"}),
        ):
            with pytest.raises(LLMResponseError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_BAD_RESPONSE.value

    def test_malformed_response_raises_response_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        # Missing 'choices' key
        with patch(
            "requests.post",
            return_value=_make_response(status_code=200, json_body={"id": "x"}),
        ):
            with pytest.raises(LLMResponseError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_BAD_RESPONSE.value

    def test_non_json_response_raises_response_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        # json_body=None makes resp.json() raise ValueError
        with patch("requests.post", return_value=_make_response(status_code=200, text="<html/>")):
            with pytest.raises(LLMResponseError):
                provider.complete([Message(role=Role.USER, content="x")])

    def test_timeout_raises_timeout_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", side_effect=requests.Timeout("read timed out")):
            with pytest.raises(LLMTimeoutError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_TIMEOUT.value

    def test_connection_error_raises_network_error(self, monkeypatch):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", side_effect=requests.ConnectionError("DNS")):
            with pytest.raises(LLMNetworkError) as exc_info:
                provider.complete([Message(role=Role.USER, content="x")])
        assert exc_info.value.code == ErrorCode.LLM_NETWORK_ERROR.value


# ===========================================================================
# Logging hygiene — API key must NEVER appear in log records
# ===========================================================================


class TestLoggingHygiene:
    def test_error_logs_do_not_contain_api_key(self, monkeypatch, caplog):
        from game.services.llm.deepseek import DeepSeekProvider
        from game.services.llm.types import Message, Role

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        provider = DeepSeekProvider()
        with patch("requests.post", side_effect=requests.ConnectionError("DNS")), \
                caplog.at_level("DEBUG", logger="game.services.llm.deepseek"):
            with pytest.raises(LLMNetworkError):
                provider.complete([Message(role=Role.USER, content="x")])

        for record in caplog.records:
            assert _FAKE_KEY not in record.getMessage()
            for value in (record.args or ()):
                assert _FAKE_KEY not in str(value)


# ===========================================================================
# Factory registration
# ===========================================================================


class TestFactoryRegistration:
    def test_deepseek_is_registered_with_factory(self, monkeypatch):
        # Force import of the deepseek module so its register_provider() runs.
        import importlib

        from game.services.llm import factory
        from game.services.llm import deepseek
        importlib.reload(deepseek)  # idempotent self-registration

        monkeypatch.setenv("DEEPSEEK_API_KEY", _FAKE_KEY)
        from game.services.llm.factory import LLMProviderFactory

        provider = LLMProviderFactory.create("deepseek")
        assert provider is not None
        from game.services.llm.deepseek import DeepSeekProvider
        assert isinstance(provider, DeepSeekProvider)

    def test_factory_returns_none_when_deepseek_has_no_key(self, monkeypatch):
        """deepseek constructor itself doesn't raise, so factory returns the
        instance — but the instance fails on first call. This test verifies
        the constructor's no-raise contract via factory dispatch."""
        from game.services.llm import deepseek  # noqa: F401  (force registration)
        from game.services.llm.factory import LLMProviderFactory

        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        # Constructor doesn't raise (key checked per-call), so factory returns
        # an instance, not None. Document the actual behavior:
        provider = LLMProviderFactory.create("deepseek")
        assert provider is not None  # construction succeeds
