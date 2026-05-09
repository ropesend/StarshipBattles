"""Image provider selection by env var (PROJ-314).

:meth:`ImageProviderFactory.create` reads ``IMAGE_PROVIDER`` from the
environment (default ``"openai"``), looks up the registered class, and
constructs it.

Two intentional behaviors mirror the LLM factory:

1. **Unknown provider name → raise ImageConfigError** with code ``I001``
   and a context dict listing the registered names. Catches typos like
   ``IMAGE_PROVIDER=opnai`` loudly.

2. **Provider constructor raising ImageConfigError (e.g. no API key) →
   create() returns None** (deferred validation). Consumers check
   ``if provider is not None:`` before showing a UI affordance.

Provider classes register at import time::

    # in game/ui/services/image/openai_provider.py
    register_image_provider("openai", OpenAIImageProvider)
"""
from __future__ import annotations

from typing import Optional, Type

from game.core.error_codes import ErrorCode
from game.core.exceptions import ImageConfigError
from game.services.provider_factory import resolve_provider
from game.ui.services.image.provider import ImageProvider

_PROVIDERS: dict[str, Type[ImageProvider]] = {}


def register_image_provider(name: str, provider_cls: Type[ImageProvider]) -> None:
    """Register a provider implementation under a string name.

    Called from each provider module at import time so the factory
    can look it up by ``IMAGE_PROVIDER`` env var.
    """
    _PROVIDERS[name] = provider_cls


class ImageProviderFactory:
    """Stateless factory for resolving the configured image provider."""

    @staticmethod
    def create(name: Optional[str] = None) -> Optional[ImageProvider]:
        """Construct the provider named ``name`` (or ``IMAGE_PROVIDER`` env, default ``"openai"``).

        Returns:
            An :class:`ImageProvider` on success.
            ``None`` when the registered provider's constructor raises
            :class:`ImageConfigError` (e.g., no API key set).

        Raises:
            ImageConfigError: When ``name`` (or ``IMAGE_PROVIDER``) refers
                to a provider that isn't registered. The exception's
                ``context`` includes ``provider`` and ``registered``.
        """
        return resolve_provider(
            name,
            providers=_PROVIDERS,
            env_var="IMAGE_PROVIDER",
            default="openai",
            config_error_cls=ImageConfigError,
            error_code=ErrorCode.IMAGE_CONFIG_MISSING.value,
            label="image provider",
        )


__all__ = ["ImageProviderFactory", "register_image_provider"]
