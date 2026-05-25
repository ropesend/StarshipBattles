"""Component-portrait derivative generation.

Thin per-family wrapper over ``game.assets.image_derivatives``. Components
are special in that the resolution is encoded in the filename
(``1024Portrait_Comp_001.png`` becomes ``64Portrait_Comp_001.png``), so a
custom ``filename_transform`` is supplied to the shared engine.

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
DERIVATIVE_SIZES: tuple[int, ...] = (2048, 512, 256, 128, 64)
MANIFEST_NAME = ".component_derivatives_manifest.json"


@dataclass(frozen=True)
class ComponentDerivativeResult:
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def component_filename(source_name: str, size: int) -> str:
    """Compute derivative filename for a component master at a target size.

    Components encode the size in the filename: a master named
    ``1024Portrait_Comp_007.png`` produces ``64Portrait_Comp_007.png`` at
    the 64px derivative. Files that don't match the canonical prefix are
    given a ``<size>_`` prefix as a defensive fallback.
    """
    prefix = f"{MASTER_SIZE}Portrait_Comp_"
    if source_name.startswith(prefix):
        return source_name.replace(str(MASTER_SIZE), str(size), 1)
    return f"{size}_{source_name}"


def _component_spec(
    components_root: Path | str | None,
    sizes: Iterable[int],
) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="component",
        root_dir=components_root if components_root is not None else Paths.COMPONENTS_IMAGES_DIR,
        master_size=MASTER_SIZE,
        derivative_sizes=sizes,
        master_glob="{master_size}/" + f"{MASTER_SIZE}Portrait_Comp_*.png",
        manifest_name=MANIFEST_NAME,
        filename_transform=component_filename,
    )


def ensure_component_derivatives(
    components_root: Path | str | None = None,
    sizes: Iterable[int] = DERIVATIVE_SIZES,
) -> ComponentDerivativeResult:
    """Create or refresh generated component image sizes from tracked 1024px masters."""
    spec = _component_spec(components_root, sizes)
    if not spec.root_dir.exists():
        raise FileNotFoundError(
            f"Component root directory not found: {spec.root_dir}"
        )
    master_dir = spec.root_dir / str(MASTER_SIZE)
    if not master_dir.exists():
        raise FileNotFoundError(
            f"Component master directory not found: {master_dir}"
        )
    result = ensure_image_derivatives(spec)
    return ComponentDerivativeResult(
        generated=result.generated,
        skipped=result.skipped,
        sources=result.sources,
        manifest_path=result.manifest_path,
    )
