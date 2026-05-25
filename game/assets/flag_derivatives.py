"""Flag image derivative generation.

Per-family wrapper over ``game.assets.image_derivatives`` for race-flag
shape PNGs. Each flag's master art (rectangle/shield/triangle shapes at
1024 px) lives under ``Flags/Processed/<flag_id>/1024/``; smaller sizes
are generated at startup.

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
# Sizes the runtime actually loads (race_flag_gallery uses 256/128; the
# race-setup full-size view uses 1024 with 512 fallback). 32 and 64 are
# generated only as small fallback variants; drop them if unused later.
DERIVATIVE_SIZES: tuple[int, ...] = (512, 256, 128, 64, 32)
MANIFEST_NAME = ".flag_derivatives_manifest.json"


@dataclass(frozen=True)
class FlagDerivativeResult:
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def _flag_spec(
    flags_root: Path | str | None,
    sizes: Iterable[int],
) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="flag",
        root_dir=flags_root if flags_root is not None else Paths.FLAGS_PROCESSED_DIR,
        master_size=MASTER_SIZE,
        derivative_sizes=sizes,
        master_glob="flag_*/{master_size}/*.png",
        manifest_name=MANIFEST_NAME,
    )


def ensure_flag_derivatives(
    flags_root: Path | str | None = None,
    sizes: Iterable[int] = DERIVATIVE_SIZES,
) -> FlagDerivativeResult:
    """Create or refresh generated flag image sizes from tracked 1024px masters.

    No-ops cleanly when the flags root doesn't exist (fresh checkout
    without the asset folder).
    """
    spec = _flag_spec(flags_root, sizes)
    result = ensure_image_derivatives(spec)
    return FlagDerivativeResult(
        generated=result.generated,
        skipped=result.skipped,
        sources=result.sources,
        manifest_path=result.manifest_path,
    )
