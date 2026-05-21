"""Image service DTOs (PROJ-314).

Frozen dataclasses describing image-generation results.

See `Projects/active_projects/PROJ-314/design.md` for the full API
surface and the rationale behind each field.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ImageResult:
    """Provider-agnostic image-generation result.

    Attributes:
        image_bytes: Raw PNG bytes returned by the provider.
        size: The ACTUAL `(width, height)` of the returned image. May
            differ from the requested size — callers must validate and
            decide whether to re-request, upscale, or accept. Never
            silently mutated by the provider.
        model: Concrete model identifier returned by the provider.
        latency_ms: Wall time of the underlying HTTP call in
            milliseconds, measured client-side.
        provider: Short provider identifier (e.g. "openai").
        request_id: Provider's request id for support traces. None
            when the provider did not return one.
        revised_prompt: The provider's interpretation/expansion of the
            input prompt (gpt-image-2 returns this when it rewrites
            the user's prompt). None when not provided.
    """
    image_bytes: bytes
    size: tuple[int, int]
    model: str
    latency_ms: float
    provider: str
    request_id: Optional[str] = None
    revised_prompt: Optional[str] = None

    def __repr__(self) -> str:
        # PROJ-466: never dump raw image bytes or the revised prompt in
        # repr. Report safe metadata only.
        return (
            f"ImageResult(model={self.model!r}, size={self.size!r}, "
            f"latency_ms={self.latency_ms}, provider={self.provider!r}, "
            f"bytes_len={len(self.image_bytes)})"
        )


__all__ = ["ImageResult"]
