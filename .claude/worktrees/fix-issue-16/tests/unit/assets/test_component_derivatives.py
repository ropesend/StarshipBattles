import json
import time
from pathlib import Path

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
    _write_master(root / "Components 1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    result = ensure_component_derivatives(root, sizes=(64, 128))

    assert result.sources == 1
    assert result.generated == 2
    assert result.skipped == 0
    assert (root / "Components 64" / "64Portrait_Comp_001.png").exists()
    assert (root / "Components 128" / "128Portrait_Comp_001.png").exists()

    with Image.open(root / "Components 64" / "64Portrait_Comp_001.png") as image:
        assert image.size == (64, 64)

    manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert "1024Portrait_Comp_001.png" in manifest["sources"]


def test_skips_when_hash_and_outputs_are_current(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    _write_master(root / "Components 1024" / "1024Portrait_Comp_001.png", (255, 0, 0, 255))

    first = ensure_component_derivatives(root, sizes=(64,))
    target = root / "Components 64" / "64Portrait_Comp_001.png"
    first_mtime = target.stat().st_mtime_ns

    second = ensure_component_derivatives(root, sizes=(64,))

    assert first.generated == 1
    assert second.generated == 0
    assert second.skipped == 1
    assert target.stat().st_mtime_ns == first_mtime


def test_regenerates_when_master_hash_changes(tmp_path: Path) -> None:
    root = tmp_path / "Components"
    master = root / "Components 1024" / "1024Portrait_Comp_001.png"
    _write_master(master, (255, 0, 0, 255))
    ensure_component_derivatives(root, sizes=(64,))

    target = root / "Components 64" / "64Portrait_Comp_001.png"
    first_mtime = target.stat().st_mtime_ns
    time.sleep(0.01)
    _write_master(master, (0, 255, 0, 255))

    result = ensure_component_derivatives(root, sizes=(64,))

    assert result.generated == 1
    assert target.stat().st_mtime_ns > first_mtime
    with Image.open(target).convert("RGBA") as image:
        assert image.getpixel((0, 0))[:3] == (0, 255, 0)
