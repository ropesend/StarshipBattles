"""Shared env-var-driven provider factory machinery (PROJ-380, DUP-X-02).

Both :class:`game.services.llm.factory.LLMProviderFactory` and
:class:`game.ui.services.image.factory.ImageProviderFactory` share the
same shape:

1. Read a name from the caller, defaulting to an env var, defaulting to a
   string literal.
2. Look the name up in a module-scoped registry dict.
3. Raise a *config* exception with a registered-list context if missing.
4. Construct the provider; if the constructor raises that *same* config
   exception class (deferred validation — e.g. missing API key), return
   ``None`` instead of crashing.

The two intentional behaviors — unknown name raises loudly, deferred
validation returns ``None`` — must stay identical across factories so
consumers can rely on the contract. This module captures the skeleton
once.
"""
from __future__ import annotations

import os
from typing import Optional, TypeVar

from game.core.exceptions import GameException

T = TypeVar("T")


def resolve_provider(
    name: Optional[str],
    *,
    providers: dict[str, type[T]],
    env_var: str,
    default: str,
    config_error_cls: type[GameException],
    error_code: str,
    label: str,
) -> Optional[T]:
    """Resolve and instantiate the named provider, mirroring the shared contract.

    Args:
        name: Provider name; when ``None`` the value of ``env_var`` is read
            from the environment, defaulting to ``default``.
        providers: Module-scoped registry mapping name → provider class.
        env_var: Environment variable to fall back to (e.g. ``"LLM_PROVIDER"``).
        default: String literal default when both ``name`` and the env var
            are unset (e.g. ``"deepseek"``).
        config_error_cls: Exception class to raise on unknown name AND to
            catch on deferred-validation failure of the constructor.
        error_code: Error-code value for the ``code=`` kwarg of the raised
            ``config_error_cls`` (e.g. ``ErrorCode.LLM_CONFIG_MISSING.value``).
        label: Human-readable noun for the error message
            (e.g. ``"LLM provider"``, ``"image provider"``).

    Returns:
        A provider instance on success. ``None`` when the constructor
        raised ``config_error_cls`` (deferred validation).

    Raises:
        config_error_cls: When the resolved name is not registered.
        Exception: Any other exception from the provider constructor
            propagates unchanged.
    """
    if name is None:
        name = os.environ.get(env_var, default)

    provider_cls = providers.get(name)
    if provider_cls is None:
        raise config_error_cls(
            f"Unknown {label} {name!r}. "
            f"Registered providers: {sorted(providers)}",
            code=error_code,
            context={
                "provider": name,
                "registered": sorted(providers),
            },
        )

    try:
        return provider_cls()
    except config_error_cls:
        # Deferred validation: consumer checks `if provider is not None`.
        return None


__all__ = ["resolve_provider"]
