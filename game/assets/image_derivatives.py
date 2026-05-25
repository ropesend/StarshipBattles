"""Generic image-derivative generation engine.

The canonical Stellar Hegemony asset-derivative pattern is:

1. Track exactly one canonical "master" PNG per source (typically the
   largest practical resolution).
2. At startup, generate all sibling sizes locally from the master.
3. Generated sizes are gitignored.
4. Subsequent runs use a per-family hash manifest to skip regeneration
   when the master is unchanged on disk.

Each asset family (components, flags, stars, planets) configures a
``DerivativeFamilySpec`` and calls ``ensure_image_derivatives(spec)``.
See ``docs/03_CONVENTIONS.md`` for the user-facing pattern doc, and
``game/assets/{component,flag,star,planet}_derivatives.py`` for the
per-family wrappers.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from PIL import Image

logger = logging.getLogger(__name__)


def _identity_filename(name: str, size: int) -> str:
    return name


class DerivativeFamilySpec:
    """Configuration for one asset family's derivative pipeline.

    Args:
        name: Short identifier used in logs (e.g., ``"component"``).
        root_dir: Top-level dir holding both the master subdir and the
            generated size subdirs. The manifest also lives here.
        master_size: Pixel size of the tracked master images (e.g., 1024).
        derivative_sizes: Sizes to generate from the master at startup.
        master_glob: Glob pattern (relative to ``root_dir``) for finding
            master files. Use the literal placeholder ``{master_size}``
            in the pattern; it is substituted at glob time. Examples:
            ``"{master_size}/*.png"`` (flat: components, stars, planets),
            ``"flag_*/{master_size}/*.png"`` (nested: flags).
        manifest_name: Filename for the per-family manifest under
            ``root_dir``. Should start with ``"."`` so it's hidden.
        filename_transform: Optional ``(name, size) -> name`` for asset
            families that encode the size in the filename (components).
            Defaults to identity (most families).
    """

    def __init__(
        self,
        name: str,
        root_dir: Path | str,
        master_size: int,
        derivative_sizes: Iterable[int],
        master_glob: str,
        manifest_name: str,
        filename_transform: Callable[[str, int], str] | None = None,
    ) -> None:
        self.name = name
        self.root_dir = Path(root_dir)
        self.master_size = master_size
        self.derivative_sizes: tuple[int, ...] = tuple(derivative_sizes)
        self.master_glob = master_glob
        self.manifest_name = manifest_name
        self._filename_transform = filename_transform or _identity_filename

    def find_masters(self) -> list[Path]:
        if not self.root_dir.exists():
            return []
        pattern = self.master_glob.format(master_size=self.master_size)
        return sorted(self.root_dir.glob(pattern))

    def derivative_path(self, master_path: Path, size: int) -> Path:
        """Compute target derivative path for a master + target size.

        Replaces the right-most path segment equal to ``str(master_size)``
        with ``str(size)``, then applies ``filename_transform``.
        """
        parts = list(master_path.parts)
        master_str = str(self.master_size)
        for i in range(len(parts) - 1, -1, -1):
            if parts[i] == master_str:
                parts[i] = str(size)
                break
        else:
            raise ValueError(
                f"Master path {master_path} has no segment equal to master "
                f"size {master_str}; cannot compute derivative path."
            )
        new_name = self._filename_transform(master_path.name, size)
        return Path(*parts[:-1], new_name)


@dataclass(frozen=True)
class DerivativeResult:
    name: str
    generated: int
    skipped: int
    sources: int
    manifest_path: Path


def ensure_image_derivatives(spec: DerivativeFamilySpec) -> DerivativeResult:
    """Create or refresh generated derivative sizes for one asset family.

    Idempotent: a content-stable master is fast-pathed via the manifest
    (stat-based check). A content-changed master forces a fresh SHA256
    and resize. Missing derivative files always force regeneration.
    """
    masters = spec.find_masters()
    manifest_path = spec.root_dir / spec.manifest_name
    if not masters:
        # Either the family root doesn't exist (fresh checkout without LFS,
        # or family not present in this build) or the master glob matched
        # nothing. Either way there's nothing to derive; don't write a
        # manifest for a non-existent root.
        logger.debug(
            "%s derivatives: no masters found under %s (pattern=%s)",
            spec.name, spec.root_dir, spec.master_glob,
        )
        return DerivativeResult(spec.name, 0, 0, 0, manifest_path)

    manifest = _read_manifest(manifest_path, spec.name)
    manifest.setdefault("version", 1)
    manifest.setdefault("sources", {})
    sizes = spec.derivative_sizes

    generated = 0
    skipped = 0

    for master_path in masters:
        # Manifest key is the master path relative to root_dir so nested
        # structures (e.g., flag_<id>/1024/x.png) get unique keys.
        source_key = master_path.relative_to(spec.root_dir).as_posix()
        source_entry = manifest["sources"].setdefault(source_key, {})
        source_stat = master_path.stat()

        if _fast_path_hit(spec, master_path, source_entry, sizes, source_stat):
            skipped += len(sizes)
            continue

        source_hash = _sha256(master_path)
        previous_hash = source_entry.get("sha256")

        with Image.open(master_path).convert("RGBA") as master_img:
            for size in sizes:
                target_path = spec.derivative_path(master_path, size)
                needs_generation = (
                    previous_hash != source_hash
                    or not target_path.exists()
                    or not _has_expected_size(target_path, size)
                )
                if needs_generation:
                    _write_derivative(master_img, target_path, size)
                    generated += 1
                else:
                    skipped += 1

        source_entry["sha256"] = source_hash
        source_entry["size"] = source_stat.st_size
        source_entry["mtime_ns"] = source_stat.st_mtime_ns

    manifest["sizes"] = list(sizes)
    manifest["master_size"] = spec.master_size
    _write_manifest(manifest_path, manifest)
    logger.info(
        "%s derivatives ready: generated=%s skipped=%s sources=%s",
        spec.name, generated, skipped, len(masters),
    )
    return DerivativeResult(
        name=spec.name,
        generated=generated,
        skipped=skipped,
        sources=len(masters),
        manifest_path=manifest_path,
    )


def _fast_path_hit(
    spec: DerivativeFamilySpec,
    master_path: Path,
    source_entry: dict[str, Any],
    sizes: tuple[int, ...],
    source_stat: os.stat_result,
) -> bool:
    """Return True when the manifest already records this source up-to-date.

    A hit means we can skip SHA hashing and PIL decode entirely. We trust
    the manifest's recorded size+mtime as a proxy for "content unchanged"
    — a cheap stat is enough; a content-changing edit (or git checkout)
    updates mtime, which forces the slow path.
    """
    if not source_entry.get("sha256"):
        return False
    if source_entry.get("size") != source_stat.st_size:
        return False
    if source_entry.get("mtime_ns") != source_stat.st_mtime_ns:
        return False
    for size in sizes:
        target = spec.derivative_path(master_path, size)
        try:
            if target.stat().st_size <= 0:
                return False
        except FileNotFoundError:
            return False
    return True


def _read_manifest(path: Path, family_name: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result
    except json.JSONDecodeError:
        logger.warning("Ignoring invalid %s derivative manifest: %s", family_name, path)
        return {}


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
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
