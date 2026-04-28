"""Image provider protocol (PROJ-314).

Defines the pluggable contract every concrete image provider must
satisfy. Mirrors :mod:`game.services.llm.provider` for shape, but
returns bytes instead of text.

Concrete providers (e.g. :class:`OpenAIImageProvider`) live in sibling
modules and are wired into :class:`ImageProviderFactory` (see
``factory.py``).

The protocol is ``@runtime_checkable`` so isinstance() checks work in
tests; production code typically just calls ``.generate_image()``.
"""
from __future__ import annotations

import pathlib
import threading
from typing import Any, Optional, Protocol, runtime_checkable

from game.ui.services.image.types import ImageResult


@runtime_checkable
class ImageProvider(Protocol):
    """Pluggable image-generation provider interface.

    Synchronous; threading is the caller's responsibility (see
    :class:`ImageBackgroundCall` in ``background.py`` for the standard
    pattern).

    Implementations may not honor the requested ``size`` exactly. Callers
    must inspect ``result.size`` and re-request or upscale if a strict
    dimension is required. Errors raise :class:`ImageException`; never
    return :class:`ImageResult` with empty bytes.
    """

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
        """Generate an image from a text prompt (and optional edit base).

        Args:
            prompt: Text description of the desired image.
            size: Requested ``"<W>x<H>"`` size string. The provider may
                return a different size — the result's ``size`` field
                reports the actual dimensions.
            model: Model identifier (default ``"gpt-image-2"``).
            edit_image: Optional source image for image-to-image edits;
                routed to the provider's ``/edits`` endpoint when set.
            mask: Optional mask for inpainting (requires ``edit_image``).
            timeout_seconds: Read-side request timeout. Connect-side
                timeout is fixed by ``ImageConfig.CONNECT_TIMEOUT_SECONDS``.
            cancel_token: Optional :class:`threading.Event` checked
                between retries. Setting the event signals the provider
                to stop ASAP and raise :class:`ImageCancelled`.
            **opts: Provider-specific extras (e.g. OpenAI's ``style``,
                ``quality``). Unknown opts must be ignored silently.

        Returns:
            A populated :class:`ImageResult`.

        Raises:
            ImageConfigError:    No API key, unknown provider, or auth failure.
            ImageNetworkError:   Connection / DNS / SSL / exhausted retries.
            ImageResponseError:  Malformed body or non-2xx (other than 429).
            ImageRateLimited:    Provider returned 429.
            ImageTimeoutError:   Request exceeded the configured timeout.
            ImageCancelled:      ``cancel_token`` was set during the call.
        """
        ...


__all__ = ["ImageProvider"]
