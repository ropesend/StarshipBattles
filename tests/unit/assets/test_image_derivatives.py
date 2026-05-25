"""Tests for the generic image-derivative engine.

Covers the family-agnostic engine in ``game.assets.image_derivatives``.
Per-family wrapper tests (flag/star/planet/component) live alongside this
file and verify the spec wiring + family-specific behavior.
"""
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from game.assets import image_derivatives as img_mod
from game.assets.image_derivatives import (
    DerivativeFamilySpec,
    ensure_image_derivatives,
)


def _write_master(path: Path, size: int, color: tuple[int, int, int, int] = (255, 0, 0, 255)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (size, size), color).save(path)


def _flat_spec(root: Path, sizes: tuple[int, ...] = (64, 128)) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="test",
        root_dir=root,
        master_size=512,
        derivative_sizes=sizes,
        master_glob="{master_size}/*.png",
        manifest_name=".test_derivatives_manifest.json",
    )


def _nested_spec(root: Path, sizes: tuple[int, ...] = (64, 128)) -> DerivativeFamilySpec:
    return DerivativeFamilySpec(
        name="test",
        root_dir=root,
        master_size=512,
        derivative_sizes=sizes,
        master_glob="bundle_*/{master_size}/*.png",
        manifest_name=".test_derivatives_manifest.json",
    )


def test_engine_generates_flat_derivatives(tmp_path: Path) -> None:
    """Flat structure: <root>/<master_size>/*.png → <root>/<size>/*.png."""
    root = tmp_path / "Family"
    _write_master(root / "512" / "asset_001.png", 512)

    result = ensure_image_derivatives(_flat_spec(root))

    assert result.sources == 1
    assert result.generated == 2
    assert (root / "64" / "asset_001.png").exists()
    assert (root / "128" / "asset_001.png").exists()
    with Image.open(root / "64" / "asset_001.png") as img:
        assert img.size == (64, 64)


def test_engine_generates_nested_derivatives(tmp_path: Path) -> None:
    """Nested structure: <root>/<bundle_id>/<master_size>/*.png → <root>/<bundle_id>/<size>/*.png."""
    root = tmp_path / "Family"
    _write_master(root / "bundle_abc" / "512" / "shape.png", 512)
    _write_master(root / "bundle_xyz" / "512" / "shape.png", 512)

    result = ensure_image_derivatives(_nested_spec(root))

    assert result.sources == 2
    assert result.generated == 4  # 2 bundles × 2 sizes
    assert (root / "bundle_abc" / "64" / "shape.png").exists()
    assert (root / "bundle_xyz" / "128" / "shape.png").exists()


def test_engine_skips_when_master_unchanged(tmp_path: Path) -> None:
    """Second run hits the fast path: no regeneration, no SHA, no PIL."""
    root = tmp_path / "Family"
    _write_master(root / "512" / "asset_001.png", 512)
    ensure_image_derivatives(_flat_spec(root, sizes=(64,)))

    def _boom(*_a, **_k):
        raise AssertionError("must not be called on fast-path hit")

    with patch.object(img_mod, "_sha256", side_effect=_boom), \
         patch("game.assets.image_derivatives.Image.open", side_effect=_boom):
        second = ensure_image_derivatives(_flat_spec(root, sizes=(64,)))

    assert second.generated == 0
    assert second.skipped == 1


def test_engine_regenerates_when_master_changes(tmp_path: Path) -> None:
    """A master with a new mtime forces hash + regeneration."""
    import os

    root = tmp_path / "Family"
    master = root / "512" / "asset_001.png"
    _write_master(master, 512, color=(255, 0, 0, 255))
    ensure_image_derivatives(_flat_spec(root, sizes=(64,)))

    # Rewrite the master with different content + bump mtime to invalidate
    # the fast path.
    backdated_ns = master.stat().st_mtime_ns - 1_000_000_000
    os.utime(master, ns=(backdated_ns, backdated_ns))
    _write_master(master, 512, color=(0, 255, 0, 255))

    result = ensure_image_derivatives(_flat_spec(root, sizes=(64,)))

    assert result.generated == 1
    with Image.open(root / "64" / "asset_001.png").convert("RGBA") as img:
        assert img.getpixel((0, 0))[:3] == (0, 255, 0)


def test_engine_regenerates_when_target_missing(tmp_path: Path) -> None:
    """A deleted derivative file forces regeneration even if master is stable."""
    root = tmp_path / "Family"
    _write_master(root / "512" / "asset_001.png", 512)
    ensure_image_derivatives(_flat_spec(root, sizes=(64, 128)))

    (root / "64" / "asset_001.png").unlink()

    result = ensure_image_derivatives(_flat_spec(root, sizes=(64, 128)))

    assert result.generated == 1
    assert result.skipped == 1
    assert (root / "64" / "asset_001.png").exists()


def test_engine_writes_manifest_with_relative_keys(tmp_path: Path) -> None:
    """Manifest keys are POSIX-style paths relative to root_dir."""
    root = tmp_path / "Family"
    _write_master(root / "bundle_abc" / "512" / "shape.png", 512)
    spec = _nested_spec(root, sizes=(64,))

    ensure_image_derivatives(spec)
    manifest = json.loads((root / spec.manifest_name).read_text(encoding="utf-8"))

    assert "bundle_abc/512/shape.png" in manifest["sources"]
    assert manifest["master_size"] == 512
    assert manifest["sizes"] == [64]


def test_engine_noops_when_root_missing(tmp_path: Path) -> None:
    """Missing root dir is treated as 'no masters'; no manifest is written."""
    root = tmp_path / "DoesNotExist"
    spec = _flat_spec(root)

    result = ensure_image_derivatives(spec)

    assert result.sources == 0
    assert result.generated == 0
    assert not (root / spec.manifest_name).exists()


def test_engine_noops_when_root_exists_but_empty(tmp_path: Path) -> None:
    """Root exists but no masters → no work, no manifest churn."""
    root = tmp_path / "Family"
    root.mkdir()
    (root / "512").mkdir()
    spec = _flat_spec(root)

    result = ensure_image_derivatives(spec)

    assert result.sources == 0
    assert result.generated == 0


def test_derivative_path_replaces_rightmost_master_segment() -> None:
    """derivative_path swaps the right-most segment equal to master_size."""
    spec = _flat_spec(Path("/family"))
    master = Path("/family/512/asset.png")
    assert spec.derivative_path(master, 64) == Path("/family/64/asset.png")


def test_derivative_path_handles_nested_path() -> None:
    spec = _nested_spec(Path("/family"))
    master = Path("/family/bundle_abc/512/shape.png")
    assert spec.derivative_path(master, 64) == Path("/family/bundle_abc/64/shape.png")


def test_filename_transform_used_for_size_encoded_names(tmp_path: Path) -> None:
    """Custom filename_transform rewrites size-encoded filenames."""
    def _swap_size(name: str, size: int) -> str:
        return name.replace("512", str(size), 1)

    root = tmp_path / "Family"
    _write_master(root / "512" / "512asset_001.png", 512)
    spec = DerivativeFamilySpec(
        name="test",
        root_dir=root,
        master_size=512,
        derivative_sizes=(64,),
        master_glob="{master_size}/*.png",
        manifest_name=".test_derivatives_manifest.json",
        filename_transform=_swap_size,
    )

    ensure_image_derivatives(spec)

    assert (root / "64" / "64asset_001.png").exists()
