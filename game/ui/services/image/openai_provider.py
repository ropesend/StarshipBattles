"""OpenAI image provider (PROJ-314).

Implements :class:`ImageProvider` using OpenAI's images endpoint.
Mirrors the security model and retry policy of
:class:`game.services.llm.deepseek.DeepSeekProvider`.

Security model:

* API key read from ``os.environ["OPENAI_API_KEY"]`` per-request,
  never cached on the instance.
* ``__repr__`` / ``__str__`` redact the key.
* Logs and exception ``context`` dicts NEVER include the key, the
  Authorization header, the request body, or the response body.
* SSL verification ON (default), ``timeout=(connect, read)`` always set,
  custom User-Agent header.
* Retry on 5xx only (max ``ImageConfig.MAX_RETRIES_5XX`` attempts with
  exponential backoff). Never retry 429.

Endpoints:

* ``POST /v1/images/generations`` — text→image (default).
* ``POST /v1/images/edits`` — image→image edits when ``edit_image`` is
  provided. Mask is optional inpainting.
"""
from __future__ import annotations

import base64
import binascii
import logging
import os
import pathlib
import threading
import time
from io import BytesIO
from typing import Any, Optional

import requests

from game.core.config import ImageConfig
from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    ImageCancelled,
    ImageConfigError,
    ImageNetworkError,
    ImageRateLimited,
    ImageResponseError,
    ImageTimeoutError,
)
from game.ui.services.image.factory import register_image_provider
from game.ui.services.image.types import ImageResult

logger = logging.getLogger(__name__)

OPENAI_GENERATIONS_ENDPOINT = "https://api.openai.com/v1/images/generations"
OPENAI_EDITS_ENDPOINT = "https://api.openai.com/v1/images/edits"
PROVIDER_NAME = "openai"


class OpenAIImageProvider:
    """OpenAI image-generation provider.

    Stateless — the API key is read from the environment on every
    request. Construct once and reuse across calls.

    Construction does NOT validate the key (the env var may be set
    later). The first :meth:`generate_image` call raises
    :class:`ImageConfigError` if no key is available.
    """

    def __init__(self) -> None:
        # Intentionally empty. Per the security model (PROJ-314), the
        # API key is read from os.environ on every request rather than
        # being cached as an instance attribute.
        pass

    # -- Identity hygiene ----------------------------------------------------

    def __repr__(self) -> str:
        return "OpenAIImageProvider(api_key=<REDACTED>)"

    def __str__(self) -> str:
        return self.__repr__()

    # -- Public API ----------------------------------------------------------

    def generate_image(
        self,
        prompt: str,
        *,
        size: str = "2048x2048",
        model: str = "gpt-image-2",
        edit_image: Optional[pathlib.Path] = None,
        mask: Optional[pathlib.Path] = None,
        timeout_seconds: Optional[float] = None,
        cancel_token: Optional[threading.Event] = None,
        **opts: Any,
    ) -> ImageResult:
        """See :meth:`ImageProvider.generate_image` for the full contract."""
        api_key = self._read_api_key()
        timeout = (
            ImageConfig.CONNECT_TIMEOUT_SECONDS,
            timeout_seconds if timeout_seconds is not None
            else ImageConfig.DEFAULT_TIMEOUT_SECONDS,
        )
        headers = self._build_headers(api_key)

        is_edit = edit_image is not None
        endpoint = OPENAI_EDITS_ENDPOINT if is_edit else OPENAI_GENERATIONS_ENDPOINT

        max_attempts = ImageConfig.MAX_RETRIES_5XX + 1
        last_5xx_status: Optional[int] = None
        for attempt in range(1, max_attempts + 1):
            if cancel_token is not None and cancel_token.is_set():
                raise ImageCancelled(
                    "cancelled before attempt",
                    code=ErrorCode.IMAGE_CANCELLED.value,
                    context={"attempt": attempt},
                )

            start = time.monotonic()
            try:
                if is_edit:
                    response = self._post_edit(
                        endpoint, headers, timeout,
                        prompt=prompt, size=size, model=model,
                        edit_image=edit_image, mask=mask, opts=opts,
                    )
                else:
                    response = self._post_generation(
                        endpoint, headers, timeout,
                        prompt=prompt, size=size, model=model, opts=opts,
                    )
            except requests.Timeout as e:
                logger.error("OpenAI image request timed out: attempt=%d", attempt)
                raise ImageTimeoutError(
                    "OpenAI image request timed out",
                    code=ErrorCode.IMAGE_TIMEOUT.value,
                    context={"attempt": attempt, "model": model, "endpoint": endpoint},
                ) from e
            except requests.exceptions.SSLError as e:
                logger.error("OpenAI SSL error: attempt=%d", attempt)
                raise ImageNetworkError(
                    "OpenAI SSL error",
                    code=ErrorCode.IMAGE_NETWORK_ERROR.value,
                    context={"attempt": attempt, "model": model, "endpoint": endpoint},
                ) from e
            except requests.ConnectionError as e:
                logger.error(
                    "OpenAI connection error: attempt=%d type=%s",
                    attempt, type(e).__name__,
                )
                raise ImageNetworkError(
                    "OpenAI connection error",
                    code=ErrorCode.IMAGE_NETWORK_ERROR.value,
                    context={
                        "attempt": attempt, "model": model, "endpoint": endpoint,
                        "error_type": type(e).__name__,
                    },
                ) from e

            latency = time.monotonic() - start
            status = response.status_code

            if 200 <= status < 300:
                return self._parse_response(
                    response, model_in_request=model, latency=latency,
                )

            if status == 429:
                logger.error("OpenAI rate-limited: status=%d", status)
                raise ImageRateLimited(
                    "OpenAI rate-limit (429)",
                    code=ErrorCode.IMAGE_RATE_LIMITED.value,
                    context={
                        "status_code": status, "model": model,
                        "request_duration_ms": int(latency * 1000),
                    },
                )

            if status in (401, 403):
                logger.error("OpenAI auth failure: status=%d", status)
                raise ImageConfigError(
                    f"OpenAI auth failure ({status})",
                    code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                    context={"status_code": status, "model": model},
                )

            if 400 <= status < 500:
                logger.error("OpenAI bad request: status=%d", status)
                raise ImageResponseError(
                    f"OpenAI bad request ({status})",
                    code=ErrorCode.IMAGE_BAD_RESPONSE.value,
                    context={"status_code": status, "model": model},
                )

            if 500 <= status < 600:
                last_5xx_status = status
                if attempt < max_attempts:
                    backoff = (
                        ImageConfig.RETRY_BACKOFF_BASE_SECONDS
                        * (2 ** (attempt - 1))
                    )
                    logger.warning(
                        "OpenAI 5xx, retrying: status=%d attempt=%d backoff=%.2fs",
                        status, attempt, backoff,
                    )
                    time.sleep(backoff)
                    continue
                logger.error(
                    "OpenAI 5xx exhausted: status=%d attempts=%d",
                    status, attempt,
                )
                break

            logger.error("OpenAI unexpected status: status=%d", status)
            raise ImageResponseError(
                f"OpenAI unexpected status ({status})",
                code=ErrorCode.IMAGE_BAD_RESPONSE.value,
                context={"status_code": status, "model": model},
            )

        raise ImageNetworkError(
            f"OpenAI 5xx after {max_attempts} attempts",
            code=ErrorCode.IMAGE_NETWORK_ERROR.value,
            context={
                "status_code": last_5xx_status,
                "attempts": max_attempts,
                "model": model,
            },
        )

    # -- Private helpers -----------------------------------------------------

    def _read_api_key(self) -> str:
        """Read the API key from the environment per-request."""
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise ImageConfigError(
                "OPENAI_API_KEY environment variable is not set",
                code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                context={"provider": PROVIDER_NAME},
            )
        return key

    def _build_headers(self, api_key: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": ImageConfig.USER_AGENT,
        }

    def _post_generation(
        self,
        endpoint: str,
        headers: dict[str, str],
        timeout: tuple[float, float],
        *,
        prompt: str,
        size: str,
        model: str,
        opts: dict[str, Any],
    ) -> requests.Response:
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "b64_json",
            "n": 1,
        }
        body.update(opts)
        json_headers = {**headers, "Content-Type": "application/json"}
        return requests.post(endpoint, json=body, headers=json_headers, timeout=timeout)

    def _post_edit(
        self,
        endpoint: str,
        headers: dict[str, str],
        timeout: tuple[float, float],
        *,
        prompt: str,
        size: str,
        model: str,
        edit_image: Optional[pathlib.Path],
        mask: Optional[pathlib.Path],
        opts: dict[str, Any],
    ) -> requests.Response:
        if edit_image is None:
            raise ImageConfigError(
                "edit_image is required for OpenAI image edits",
                code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                context={"endpoint": endpoint},
            )
        data: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "b64_json",
            "n": 1,
        }
        data.update(opts)
        files: dict[str, Any] = {
            "image": (
                "image.png",
                self._read_edit_file(edit_image, field_name="image", endpoint=endpoint),
                "image/png",
            ),
        }
        if mask is not None:
            files["mask"] = (
                "mask.png",
                self._read_edit_file(mask, field_name="mask", endpoint=endpoint),
                "image/png",
            )
        return requests.post(endpoint, data=data, files=files, headers=headers, timeout=timeout)

    def _read_edit_file(
        self,
        path: pathlib.Path,
        *,
        field_name: str,
        endpoint: str,
    ) -> bytes:
        try:
            return path.read_bytes()
        except OSError as e:
            logger.error(
                "OpenAI image edit file read failed: field=%s path=%s error_type=%s",
                field_name,
                path,
                type(e).__name__,
            )
            raise ImageConfigError(
                "OpenAI image edit file could not be read",
                code=ErrorCode.IMAGE_CONFIG_MISSING.value,
                context={
                    "endpoint": endpoint,
                    "field": field_name,
                    "path": str(path),
                    "error_type": type(e).__name__,
                },
            ) from e

    def _parse_response(
        self,
        response: requests.Response,
        *,
        model_in_request: str,
        latency: float,
    ) -> ImageResult:
        try:
            data = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as e:
            raise ImageResponseError(
                "OpenAI returned non-JSON body",
                code=ErrorCode.IMAGE_BAD_RESPONSE.value,
                context={"status_code": response.status_code, "model": model_in_request},
            ) from e

        try:
            first = data["data"][0]
            b64 = first["b64_json"]
            revised_prompt = first.get("revised_prompt")
            request_id = data.get("id") or response.headers.get("x-request-id")
        except (KeyError, IndexError, TypeError) as e:
            raise ImageResponseError(
                "OpenAI image response missing expected fields",
                code=ErrorCode.IMAGE_BAD_RESPONSE.value,
                context={
                    "status_code": response.status_code,
                    "model": model_in_request,
                    "missing_field": str(e),
                },
            ) from e

        try:
            image_bytes = base64.b64decode(b64, validate=True)
        except (binascii.Error, ValueError, TypeError) as e:
            raise ImageResponseError(
                "OpenAI image response had invalid base64 payload",
                code=ErrorCode.IMAGE_BAD_RESPONSE.value,
                context={"status_code": response.status_code, "model": model_in_request},
            ) from e

        size = self._read_actual_size(image_bytes)

        logger.info(
            "OpenAI image ok: model=%s size=%dx%d latency_ms=%d",
            model_in_request, size[0], size[1], int(latency * 1000),
        )

        return ImageResult(
            image_bytes=image_bytes,
            size=size,
            model=model_in_request,
            latency_ms=latency * 1000.0,
            provider=PROVIDER_NAME,
            request_id=request_id,
            revised_prompt=revised_prompt,
        )

    @staticmethod
    def _read_actual_size(image_bytes: bytes) -> tuple[int, int]:
        """Decode the PNG header to read actual width/height.

        Uses PIL since it is already a project dependency for asset
        I/O. Falls back to ``(0, 0)`` if decoding fails — callers that
        care about the size will treat ``(0, 0)`` as a validation
        miss.
        """
        try:
            from PIL import Image
            with Image.open(BytesIO(image_bytes)) as img:
                return (int(img.width), int(img.height))
        except Exception:  # Intentional broad catch: image-size detection is best-effort; failure must not block return.
            return (0, 0)


# Auto-register with the factory at import time.
register_image_provider(PROVIDER_NAME, OpenAIImageProvider)


__all__ = [
    "OpenAIImageProvider",
    "OPENAI_GENERATIONS_ENDPOINT",
    "OPENAI_EDITS_ENDPOINT",
    "PROVIDER_NAME",
]
