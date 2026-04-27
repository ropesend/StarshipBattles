from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from game.core.paths import Paths

logger = logging.getLogger(__name__)

MASTER_SIZE = 1024
DERIVATIVE_SIZES = (2048, 512, 256, 128, 64)
MANIFEST_NAME = ".component_derivatives_manifest.json"


@dataclass(frozen=True)
class ComponentDerivativeResult:
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def component_filename(source_name: str, size: int) -> str:
    prefix = f"{MASTER_SIZE}Portrait_Comp_"
    if source_name.startswith(prefix):
        return source_name.replace(str(MASTER_SIZE), str(size), 1)
    return f"{size}_{source_name}"


def ensure_component_derivatives(
    components_root: Path | str | None = None,
    sizes: Iterable[int] = DERIVATIVE_SIZES,
) -> ComponentDerivativeResult:
    """Create or refresh generated component image sizes from tracked 1024px masters."""
    root = Path(components_root or Paths.COMPONENTS_IMAGES_DIR)
    source_dir = root / f"Components {MASTER_SIZE}"
    if not source_dir.exists():
        raise FileNotFoundError(f"Component master directory not found: {source_dir}")

    manifest_path = root / MANIFEST_NAME
    manifest = _read_manifest(manifest_path)
    manifest.setdefault("version", 1)
    manifest.setdefault("sources", {})
    generated = 0
    skipped = 0

    source_paths = sorted(source_dir.glob(f"{MASTER_SIZE}Portrait_Comp_*.png"))
    for source_path in source_paths:
        source_hash = _sha256(source_path)
        source_key = source_path.name
        source_entry = manifest["sources"].setdefault(source_key, {})
        previous_hash = source_entry.get("sha256")

        with Image.open(source_path).convert("RGBA") as master:
            for size in sizes:
                target_dir = root / f"Components {size}"
                target_path = target_dir / component_filename(source_path.name, size)
                needs_generation = (
                    previous_hash != source_hash
                    or not target_path.exists()
                    or not _has_expected_size(target_path, size)
                )

                if needs_generation:
                    _write_derivative(master, target_path, size)
                    generated += 1
                else:
                    skipped += 1

        source_entry["sha256"] = source_hash

    manifest["sizes"] = list(sizes)
    manifest["source_dir"] = str(source_dir)
    _write_manifest(manifest_path, manifest)
    logger.info(
        "Component derivatives ready: generated=%s skipped=%s sources=%s",
        generated,
        skipped,
        len(source_paths),
    )
    return ComponentDerivativeResult(
        generated=generated,
        skipped=skipped,
        sources=len(source_paths),
        manifest_path=manifest_path,
    )


def _read_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Ignoring invalid component derivative manifest: %s", path)
        return {}


def _write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    os.replace(temp_path, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _has_expected_size(path: Path, size: int) -> bool:
    try:
        with Image.open(path) as image:
            return image.size == (size, size)
    except OSError:
        return False


def _write_derivative(master: Image.Image, target_path: Path, size: int) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if master.size == (size, size):
        derivative = master.copy()
    else:
        derivative = master.resize((size, size), Image.Resampling.LANCZOS)

    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        derivative.save(temp_path, format="PNG")
        os.replace(temp_path, target_path)
    finally:
        derivative.close()
        if temp_path.exists():
            temp_path.unlink()
