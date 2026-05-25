"""Star image derivative generation.

Per-family wrapper over ``game.assets.image_derivatives`` for star
portraits. Masters live at ``Stellar Objects/Stars/1024/``; smaller
sizes (512/256/128) are generated at startup.

See ``docs/03_CONVENTIONS.md`` for the canonical asset-derivative pattern.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from game.assets.image_derivatives import (
    DerivativeFamilySpec,
    ensure_image_derivatives,
)
from game.core.paths import Paths

MASTER_SIZE = 1024
DERIVATIVE_SIZES: tuple[int, ...] = (512, 256, 128)
MANIFEST_NAME = ".star_derivatives_manifest.json"


@dataclass(frozen=True)
class StarDerivativeResult:
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def _star_spec(
    stars_root: Path | str | None,
    sizes: Iterable[int],
) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="star",
        root_dir=stars_root if stars_root is not None else Paths.STARS_DIR,
        master_size=MASTER_SIZE,
        derivative_sizes=sizes,
        master_glob="{master_size}/*.png",
        manifest_name=MANIFEST_NAME,
    )


def ensure_star_derivatives(
    stars_root: Path | str | None = None,
    sizes: Iterable[int] = DERIVATIVE_SIZES,
) -> StarDerivativeResult:
    """Create or refresh generated star image sizes from the tracked 1024px masters."""
    spec = _star_spec(stars_root, sizes)
    result = ensure_image_derivatives(spec)
    return StarDerivativeResult(
        generated=result.generated,
        skipped=result.skipped,
        sources=result.sources,
        manifest_path=result.manifest_path,
    )
