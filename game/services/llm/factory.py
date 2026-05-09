"""Provider selection by env var (PROJ-296).

`LLMProviderFactory.create()` reads `LLM_PROVIDER` from the environment
(default `"deepseek"`), looks up the registered class in `_PROVIDERS`,
and constructs it.

Two intentional behaviors worth knowing:

1. **Unknown provider name → raise `LLMConfigError`** with `code=L001`
   and a context dict listing the registered names. This catches typos
   like `LLM_PROVIDER=deepseekk` loudly.

2. **Provider constructor raising `LLMConfigError` (e.g. no API key) →
   `create()` returns `None`** rather than re-raising. This is the
   "deferred validation" pattern — consumers check
   `if provider is not None:` before showing the UI affordance, which
   is better UX than crashing the app at startup when the key is unset.

Other exceptions from the constructor propagate.

Provider classes register themselves at import time:

    # in game/services/llm/deepseek.py
    register_provider("deepseek", DeepSeekProvider)

Per `docs/03_CONVENTIONS.md` §6.5, dispatch is a dict, not an if/elif
chain — adding a provider is a one-line registration.
"""
from typing import Dict, Optional, Type

from game.core.error_codes import ErrorCode
from game.core.exceptions import LLMConfigError
from game.services.llm.provider import LLMProvider
from game.services.provider_factory import resolve_provider

_PROVIDERS: Dict[str, Type[LLMProvider]] = {}


def register_provider(name: str, provider_cls: Type[LLMProvider]) -> None:
    """Register a provider implementation under a string name.

    Called from each provider module at import time so the factory
    can look it up by `LLM_PROVIDER` env var.
    """
    _PROVIDERS[name] = provider_cls


class LLMProviderFactory:
    """Stateless factory for resolving the configured LLM provider."""

    @staticmethod
    def create(name: Optional[str] = None) -> Optional[LLMProvider]:
        """Construct the provider named `name` (or `LLM_PROVIDER` env, default `"deepseek"`).

        Returns:
            A `LLMProvider` instance on success.
            `None` when the registered provider's constructor raises
            `LLMConfigError` (e.g., no API key set) — consumers must
            check `if provider is not None:` before use.

        Raises:
            LLMConfigError: When `name` (or `LLM_PROVIDER`) refers to
                a provider that isn't registered. The exception's
                `context` includes `provider` and `registered`.
            Exception: Any other exception from the provider's
                constructor propagates unchanged.
        """
        return resolve_provider(
            name,
            providers=_PROVIDERS,
            env_var="LLM_PROVIDER",
            default="deepseek",
            config_error_cls=LLMConfigError,
            error_code=ErrorCode.LLM_CONFIG_MISSING.value,
            label="LLM provider",
        )


__all__ = ["LLMProviderFactory", "register_provider"]
