"""Null image provider (PROJ-314).

Default in :meth:`ApplicationContext.create_test` and a useful
production fallback when ``OPENAI_API_KEY`` is unset. Always raises
:class:`ImageConfigError` from :meth:`generate_image`, ensuring tests
that accidentally call out to the real network are caught loudly
rather than burning tokens.
"""
from __future__ import annotations

import pathlib
import threading
from typing import Any, Optional

from game.core.error_codes import ErrorCode
from game.core.exceptions import ImageConfigError
from game.ui.services.image.types import ImageResult

PROVIDER_NAME = "null"


class NullImageProvider:
    """No-op provider that always raises on :meth:`generate_image`.

    Useful for tests (default in
    :meth:`ApplicationContext.create_test`) and as a safe production
    fallback when no API key is configured. Construction never fails;
    only the actual generation call fails.
    """

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "NullImageProvider()"

    def __str__(self) -> str:
        return self.__repr__()

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
        """Always raises :class:`ImageConfigError`."""
        raise ImageConfigError(
            "NullImageProvider does not generate images. "
            "Configure a real provider (e.g. OpenAI) via the IMAGE_PROVIDER "
            "env var to use this feature.",
            code=ErrorCode.IMAGE_CONFIG_MISSING.value,
            context={"provider": PROVIDER_NAME, "model": model, "size": size},
        )


__all__ = ["NullImageProvider", "PROVIDER_NAME"]
