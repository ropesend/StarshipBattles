"""Module-level default image provider slot (PROJ-314).

Mirrors :mod:`game.services.llm.defaults`.
:meth:`ApplicationContext.create_production` calls
:func:`set_default_image_provider` once at startup so that
:func:`get_default_image_provider` and ``ctx.image_provider`` return the
same instance.

:func:`get_default_image_provider` returns ``None`` when no provider has
been configured (deferred validation pattern). Consumers must check
``if provider is not None:`` before using.
"""
from __future__ import annotations

from typing import Optional

from game.ui.services.image.provider import ImageProvider

_default_image_provider: Optional[ImageProvider] = None


def get_default_image_provider() -> Optional[ImageProvider]:
    """Return the application-wide default image provider, or ``None``.

    ``None`` means no provider could be constructed (e.g. no API key
    set). Consumers (portrait regenerator, race-art generator) should
    treat ``None`` as "this feature is not available right now" —
    typically by disabling the UI affordance with a tooltip rather than
    raising.
    """
    return _default_image_provider


def set_default_image_provider(provider: Optional[ImageProvider]) -> None:
    """Set the application-wide default image provider.

    Called by :meth:`ApplicationContext.create_production` at startup,
    or by tests that want to inject a mock provider into code that
    uses the module-level accessor.
    """
    global _default_image_provider
    _default_image_provider = provider


__all__ = ["get_default_image_provider", "set_default_image_provider"]
