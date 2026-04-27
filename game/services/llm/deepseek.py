"""DeepSeek concrete provider (PROJ-296).

Implements `LLMProvider` using DeepSeek's OpenAI-compatible
chat-completions endpoint.

Security model (mirrors design.md):
- API key read from `os.environ["DEEPSEEK_API_KEY"]` per-request,
  never cached on the instance.
- `__repr__` / `__str__` redact the key.
- Logs and exception `context` dicts NEVER include the key, the
  Authorization header, the request body, or the response body.
- SSL verification ON (default), `timeout=(connect, read)` always set,
  custom User-Agent header.
- Retry on 5xx only (max `LLMConfig.MAX_RETRIES_5XX` attempts with
  exponential backoff). Never retry 429 — rate-limit is a clear
  back-off signal that auto-retry would worsen.
"""
import logging
import os
import time
from typing import Any, Dict, List, Optional
import threading

import requests

from game.core.config import LLMConfig
from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    LLMConfigError,
    LLMNetworkError,
    LLMRateLimited,
    LLMResponseError,
    LLMTimeoutError,
)
from game.services.llm.factory import register_provider
from game.services.llm.types import (
    CompletionResult,
    FinishReason,
    Message,
    TokenUsage,
)

logger = logging.getLogger(__name__)

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
PROVIDER_NAME = "deepseek"

# Map DeepSeek's finish_reason strings → FinishReason enum.
_FINISH_REASON_MAP: Dict[str, FinishReason] = {
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
    # DeepSeek may return others (e.g., "tool_calls", "content_filter");
    # treat unknown as STOP so the consumer still sees a usable result.
}


class DeepSeekProvider:
    """DeepSeek chat-completions provider.

    Stateless — the API key is read from the environment on every
    request. Construct once and reuse across calls.

    Construction does NOT validate the key (the env var may be set
    later). The first `complete()` call raises `LLMConfigError` if
    no key is available.
    """

    def __init__(self) -> None:
        # Intentionally empty. Per the security model (PROJ-296), the
        # API key is read from os.environ on every request rather than
        # being cached as an instance attribute.
        pass

    # -- Identity hygiene ----------------------------------------------------

    def __repr__(self) -> str:
        return "DeepSeekProvider(api_key=<REDACTED>)"

    def __str__(self) -> str:
        return self.__repr__()

    # -- Public API ----------------------------------------------------------

    def complete(
        self,
        messages: List[Message],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
        cancel_token: Optional[threading.Event] = None,
        **opts: Any,
    ) -> CompletionResult:
        """See `LLMProvider.complete()` for the full contract."""
        api_key = self._read_api_key()
        body = self._build_body(messages, model, temperature, max_tokens, opts)
        headers = self._build_headers(api_key)
        timeout = (
            LLMConfig.CONNECT_TIMEOUT_SECONDS,
            timeout_seconds if timeout_seconds is not None
            else LLMConfig.DEFAULT_TIMEOUT_SECONDS,
        )

        max_attempts = LLMConfig.MAX_RETRIES_5XX + 1  # initial + retries
        last_5xx_status: Optional[int] = None
        for attempt in range(1, max_attempts + 1):
            if cancel_token is not None and cancel_token.is_set():
                from game.core.exceptions import LLMCancelled
                raise LLMCancelled(
                    "cancelled before attempt",
                    code=ErrorCode.LLM_CANCELLED.value,
                    context={"attempt": attempt},
                )

            start = time.monotonic()
            try:
                response = requests.post(
                    DEEPSEEK_ENDPOINT,
                    json=body,
                    headers=headers,
                    timeout=timeout,
                )
            except requests.Timeout as e:
                logger.error(
                    "DeepSeek request timed out: attempt=%d", attempt
                )
                raise LLMTimeoutError(
                    "DeepSeek request timed out",
                    code=ErrorCode.LLM_TIMEOUT.value,
                    context={"attempt": attempt, "model": body["model"]},
                ) from e
            except requests.ConnectionError as e:
                logger.error(
                    "DeepSeek connection error: attempt=%d type=%s",
                    attempt, type(e).__name__,
                )
                raise LLMNetworkError(
                    "DeepSeek connection error",
                    code=ErrorCode.LLM_NETWORK_ERROR.value,
                    context={
                        "attempt": attempt,
                        "model": body["model"],
                        "error_type": type(e).__name__,
                    },
                ) from e
            except requests.exceptions.SSLError as e:
                logger.error("DeepSeek SSL error: attempt=%d", attempt)
                raise LLMNetworkError(
                    "DeepSeek SSL error",
                    code=ErrorCode.LLM_NETWORK_ERROR.value,
                    context={"attempt": attempt, "model": body["model"]},
                ) from e

            latency = time.monotonic() - start
            status = response.status_code

            # 200 — parse and return.
            if 200 <= status < 300:
                return self._parse_response(response, model_in_body=body["model"], latency=latency)

            # 429 — rate limit. Never retry; surface immediately.
            if status == 429:
                logger.error("DeepSeek rate-limited: status=%d", status)
                raise LLMRateLimited(
                    "DeepSeek rate-limit (429)",
                    code=ErrorCode.LLM_RATE_LIMITED.value,
                    context={
                        "status_code": status,
                        "model": body["model"],
                        "request_duration_ms": int(latency * 1000),
                    },
                )

            # 401 / 403 — auth / config failure.
            if status in (401, 403):
                logger.error("DeepSeek auth failure: status=%d", status)
                raise LLMConfigError(
                    f"DeepSeek auth failure ({status})",
                    code=ErrorCode.LLM_CONFIG_MISSING.value,
                    context={
                        "status_code": status,
                        "model": body["model"],
                    },
                )

            # Other 4xx — bad request, malformed input, etc.
            if 400 <= status < 500:
                logger.error("DeepSeek bad request: status=%d", status)
                raise LLMResponseError(
                    f"DeepSeek bad request ({status})",
                    code=ErrorCode.LLM_BAD_RESPONSE.value,
                    context={
                        "status_code": status,
                        "model": body["model"],
                    },
                )

            # 5xx — retry with exponential backoff.
            if 500 <= status < 600:
                last_5xx_status = status
                if attempt < max_attempts:
                    backoff = (
                        LLMConfig.RETRY_BACKOFF_BASE_SECONDS
                        * (2 ** (attempt - 1))
                    )
                    logger.warning(
                        "DeepSeek 5xx, retrying: status=%d attempt=%d backoff=%.2fs",
                        status, attempt, backoff,
                    )
                    time.sleep(backoff)
                    continue
                # Exhausted.
                logger.error(
                    "DeepSeek 5xx exhausted: status=%d attempts=%d",
                    status, attempt,
                )
                break

            # Anything else — treat as bad response.
            logger.error("DeepSeek unexpected status: status=%d", status)
            raise LLMResponseError(
                f"DeepSeek unexpected status ({status})",
                code=ErrorCode.LLM_BAD_RESPONSE.value,
                context={"status_code": status, "model": body["model"]},
            )

        # Fell through — exhausted retries on 5xx.
        raise LLMNetworkError(
            f"DeepSeek 5xx after {max_attempts} attempts",
            code=ErrorCode.LLM_NETWORK_ERROR.value,
            context={
                "status_code": last_5xx_status,
                "attempts": max_attempts,
                "model": body["model"],
            },
        )

    # -- Private helpers -----------------------------------------------------

    def _read_api_key(self) -> str:
        """Read the API key from the environment per-request.

        Never cached on the instance — see security model in module docstring.
        """
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            raise LLMConfigError(
                "DEEPSEEK_API_KEY environment variable is not set",
                code=ErrorCode.LLM_CONFIG_MISSING.value,
                context={"provider": PROVIDER_NAME},
            )
        return key

    def _build_body(
        self,
        messages: List[Message],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        opts: Dict[str, Any],
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": model or LLMConfig.DEFAULT_MODEL,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": (
                temperature if temperature is not None
                else LLMConfig.DEFAULT_TEMPERATURE
            ),
            "max_tokens": (
                max_tokens if max_tokens is not None
                else LLMConfig.DEFAULT_MAX_TOKENS
            ),
        }
        # Provider-specific extras (top_p, presence_penalty, etc.).
        # Unknown keys are passed through; DeepSeek ignores those it doesn't recognize.
        body.update(opts)
        return body

    def _build_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": LLMConfig.USER_AGENT,
        }

    def _parse_response(
        self,
        response: requests.Response,
        *,
        model_in_body: str,
        latency: float,
    ) -> CompletionResult:
        try:
            data = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as e:
            raise LLMResponseError(
                "DeepSeek returned non-JSON body",
                code=ErrorCode.LLM_BAD_RESPONSE.value,
                context={
                    "status_code": response.status_code,
                    "model": model_in_body,
                },
            ) from e

        try:
            choices = data["choices"]
            choice = choices[0]
            content = choice["message"]["content"]
            finish_str = choice.get("finish_reason", "stop")
            usage_data = data.get("usage", {})
            response_model = data.get("model", model_in_body)
            request_id = data.get("id")
        except (KeyError, IndexError, TypeError) as e:
            raise LLMResponseError(
                "DeepSeek response missing expected fields",
                code=ErrorCode.LLM_BAD_RESPONSE.value,
                context={
                    "status_code": response.status_code,
                    "model": model_in_body,
                    "missing_field": str(e),
                },
            ) from e

        usage = TokenUsage(
            prompt_tokens=int(usage_data.get("prompt_tokens", 0)),
            completion_tokens=int(usage_data.get("completion_tokens", 0)),
            total_tokens=int(usage_data.get("total_tokens", 0)),
            cached_prompt_tokens=int(usage_data.get("cached_prompt_tokens", 0)),
        )

        finish_reason = _FINISH_REASON_MAP.get(finish_str, FinishReason.STOP)

        logger.info(
            "DeepSeek call ok: model=%s tokens=%d latency_ms=%d",
            response_model, usage.total_tokens, int(latency * 1000),
        )

        return CompletionResult(
            text=content,
            usage=usage,
            model=response_model,
            finish_reason=finish_reason,
            latency_seconds=latency,
            provider=PROVIDER_NAME,
            request_id=request_id,
        )


# Auto-register with the factory at import time.
register_provider(PROVIDER_NAME, DeepSeekProvider)


__all__ = ["DeepSeekProvider", "DEEPSEEK_ENDPOINT", "PROVIDER_NAME"]
