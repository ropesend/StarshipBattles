"""Planet image derivative generation.

Per-family wrapper over ``game.assets.image_derivatives`` for planet
portraits. Masters live at ``stellar_objects/planets/2048/``; smaller
sizes (1024/512/256/128) are generated at startup. The runtime loader
in ``AssetManager.load_planet_image`` walks the size chain, so all four
derivative sizes need to exist on disk by the time strategy rendering
begins.

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

MASTER_SIZE = 2048
DERIVATIVE_SIZES: tuple[int, ...] = (1024, 512, 256, 128)
MANIFEST_NAME = ".planet_derivatives_manifest.json"


@dataclass(frozen=True)
class PlanetDerivativeResult:
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def _planet_spec(
    planets_root: Path | str | None,
    sizes: Iterable[int],
) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="planet",
        root_dir=planets_root if planets_root is not None else Paths.PLANETS_DIR,
        master_size=MASTER_SIZE,
        derivative_sizes=sizes,
        master_glob="{master_size}/*.png",
        manifest_name=MANIFEST_NAME,
    )


def ensure_planet_derivatives(
    planets_root: Path | str | None = None,
    sizes: Iterable[int] = DERIVATIVE_SIZES,
) -> PlanetDerivativeResult:
    """Create or refresh generated planet image sizes from the tracked 2048px masters."""
    spec = _planet_spec(planets_root, sizes)
    result = ensure_image_derivatives(spec)
    return PlanetDerivativeResult(
        generated=result.generated,
        skipped=result.skipped,
        sources=result.sources,
        manifest_path=result.manifest_path,
    )
