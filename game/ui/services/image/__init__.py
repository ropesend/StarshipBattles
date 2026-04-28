"""Image-generation provider abstraction (PROJ-314).

Public API:

* :class:`ImageProvider` — pluggable provider protocol.
* :class:`ImageResult` — frozen result DTO.
* :class:`OpenAIImageProvider` — concrete provider for ``gpt-image-2``.
* :class:`NullImageProvider` — default in tests; raises on call.
* :class:`ImageProviderFactory` / :func:`register_image_provider` —
  env-var-driven dispatch.
* :func:`get_default_image_provider` /
  :func:`set_default_image_provider` — module-level singleton accessors.
* :class:`ImageBackgroundCall` / :class:`CallStatus` /
  :func:`shutdown_all_image_calls` — threading helper.

See ``Projects/active_projects/PROJ-314/design.md`` for design notes
and the rationale behind each contract.
"""
from game.ui.services.image.background import (
    CallStatus,
    ImageBackgroundCall,
    shutdown_all_image_calls,
)
from game.ui.services.image.defaults import (
    get_default_image_provider,
    set_default_image_provider,
)
from game.ui.services.image.factory import (
    ImageProviderFactory,
    register_image_provider,
)
from game.ui.services.image.null_provider import NullImageProvider
from game.ui.services.image.provider import ImageProvider
from game.ui.services.image.types import ImageResult

# Side-effect imports: register concrete providers at package import time.
from game.ui.services.image import null_provider as _null_provider  # noqa: F401
from game.ui.services.image import openai_provider  # noqa: F401

# null_provider is also registered with the factory so tests can
# request it explicitly via IMAGE_PROVIDER=null.
register_image_provider("null", NullImageProvider)


__all__ = [
    # types
    "ImageResult",
    # protocol
    "ImageProvider",
    # concrete providers
    "NullImageProvider",
    # factory
    "ImageProviderFactory",
    "register_image_provider",
    # default-provider accessors
    "get_default_image_provider",
    "set_default_image_provider",
    # background helper
    "CallStatus",
    "ImageBackgroundCall",
    "shutdown_all_image_calls",
]
