import json
import os
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from game.assets.component_derivatives import (
    MANIFEST_NAME,
    component_filename,
    ensure_component_derivatives,
)


def _write_master(path: Path, color: tuple[int, int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (1024, 1024), color).save(path)


def test_component_filename_replaces_leading_resolution() -> None:
    assert (
        component_filename("1024Portrait_Comp_007.png", 64)
        == "64Portrait_Comp_007.png"
    )


def test_generates_missing_derivatives_and_manifest(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    _write_master(root / "1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    result = ensure_component_derivatives(root, sizes=(64, 128))

    assert result.sources == 1
    assert result.generated == 2
    assert result.skipped == 0
    assert (root / "64" / "64Portrait_Comp_001.png").exists()
    assert (root / "128" / "128Portrait_Comp_001.png").exists()

    with Image.open(root / "64" / "64Portrait_Comp_001.png") as image:
        assert image.size == (64, 64)

    manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert "1024Portrait_Comp_001.png" in manifest["sources"]


def test_skips_when_hash_and_outputs_are_current(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    _write_master(root / "1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    first = ensure_component_derivatives(root, sizes=(64,))
    target = root / "64" / "64Portrait_Comp_001.png"
    first_mtime = target.stat().st_mtime_ns

    second = ensure_component_derivatives(root, sizes=(64,))

    assert first.generated == 1
    assert second.generated == 0
    assert second.skipped == 1
    assert target.stat().st_mtime_ns == first_mtime


def test_regenerates_when_master_hash_changes(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    master = root / "1024" / "1024Portrait_Comp_001.png"
    _write_master(master, (255, 0, 0, 255))
    ensure_component_derivatives(root, sizes=(64,))

    target = root / "64" / "64Portrait_Comp_001.png"
    first_mtime = target.stat().st_mtime_ns
    # PROJ-322 Task 4.2 (S06-CAT7-001): use os.utime to backdate the
    # master file so the rebuild's mtime is unambiguously newer,
    # avoiding the time.sleep(0.01) timer-resolution dependency on
    # Windows.
    backdated_ns = first_mtime - 1_000_000_000  # 1 s earlier
    os.utime(master, ns=(backdated_ns, backdated_ns))
    _write_master(master, (0, 255, 0, 255))

    result = ensure_component_derivatives(root, sizes=(64,))

    assert result.generated == 1
    assert target.stat().st_mtime_ns > first_mtime
    with Image.open(target).convert("RGBA") as image:
        assert image.getpixel((0, 0))[:3] == (0, 255, 0)


def test_fast_path_skips_sha_and_decode_when_mtime_unchanged(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    _write_master(root / "1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    ensure_component_derivatives(root, sizes=(64,))

    def _boom(*_args, **_kwargs):
        raise AssertionError("must not be called on the cached-hit fast path")

    with (
        patch("game.assets.component_derivatives._sha256", side_effect=_boom),
        patch("game.assets.component_derivatives.Image.open", side_effect=_boom),
    ):
        second = ensure_component_derivatives(root, sizes=(64,))

    assert second.generated == 0
    assert second.skipped == 1


def test_fast_path_invalidated_when_source_mtime_changes(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    master = root / "1024" / "1024Portrait_Comp_001.png"
    _write_master(master, (255, 0, 0, 255))

    ensure_component_derivatives(root, sizes=(64,))

    stat = master.stat()
    new_mtime = stat.st_mtime_ns + 5_000_000_000
    os.utime(master, ns=(new_mtime, new_mtime))

    calls: list[Path] = []
    from game.assets import component_derivatives as cd_module

    real_sha256 = cd_module._sha256

    def _tracking_sha256(path: Path) -> str:
        calls.append(path)
        return real_sha256(path)

    with patch.object(cd_module, "_sha256", side_effect=_tracking_sha256):
        result = ensure_component_derivatives(root, sizes=(64,))

    assert calls, "mtime change must invalidate the fast path and force a rehash"
    assert result.generated == 0
    assert result.skipped == 1


def test_fast_path_invalidated_when_target_missing(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    _write_master(root / "1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    ensure_component_derivatives(root, sizes=(64, 128))

    missing = root / "64" / "64Portrait_Comp_001.png"
    missing.unlink()

    result = ensure_component_derivatives(root, sizes=(64, 128))

    assert result.generated == 1
    assert result.skipped == 1
    assert missing.exists()
