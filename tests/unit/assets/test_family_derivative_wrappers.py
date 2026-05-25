"""Tests for the per-family derivative wrappers (flag, star, planet).

Verifies the per-family ``_spec()`` configuration glues the right
master directory and glob to the shared engine. The engine itself is
covered in ``test_image_derivatives.py``.
"""
from pathlib import Path

from PIL import Image

from game.assets.flag_derivatives import (
    MASTER_SIZE as FLAG_MASTER_SIZE,
    ensure_flag_derivatives,
)
from game.assets.planet_derivatives import (
    MASTER_SIZE as PLANET_MASTER_SIZE,
    ensure_planet_derivatives,
)
from game.assets.star_derivatives import (
    MASTER_SIZE as STAR_MASTER_SIZE,
    ensure_star_derivatives,
)


def _write_png(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (size, size), (123, 45, 67, 255)).save(path)


def test_flag_wrapper_generates_per_flag_size_subdirs(tmp_path: Path) -> None:
    """Flag masters at <root>/<flag_id>/1024/{shape}.png produce derivative size dirs."""
    root = tmp_path / "Flags" / "Processed"
    # Two flags, three shapes each at the master resolution.
    for flag_id in ("flag_abc", "flag_xyz"):
        for shape in ("rectangle", "shield", "triangle"):
            _write_png(root / flag_id / str(FLAG_MASTER_SIZE) / f"{shape}.png", FLAG_MASTER_SIZE)

    result = ensure_flag_derivatives(flags_root=root, sizes=(128, 256))

    assert result.sources == 6  # 2 flags × 3 shapes
    assert result.generated == 12  # 6 sources × 2 sizes
    for flag_id in ("flag_abc", "flag_xyz"):
        for shape in ("rectangle", "shield", "triangle"):
            assert (root / flag_id / "128" / f"{shape}.png").exists()
            assert (root / flag_id / "256" / f"{shape}.png").exists()


def test_flag_wrapper_noops_when_root_missing(tmp_path: Path) -> None:
    result = ensure_flag_derivatives(flags_root=tmp_path / "absent")
    assert result.sources == 0
    assert result.generated == 0


def test_star_wrapper_generates_size_subdirs(tmp_path: Path) -> None:
    """Star masters at <root>/1024/Star*.png produce <root>/<size>/Star*.png."""
    root = tmp_path / "Stars"
    _write_png(root / str(STAR_MASTER_SIZE) / "StarBlueAsset.png", STAR_MASTER_SIZE)
    _write_png(root / str(STAR_MASTER_SIZE) / "StarRedAsset.png", STAR_MASTER_SIZE)

    result = ensure_star_derivatives(stars_root=root, sizes=(128, 512))

    assert result.sources == 2
    assert result.generated == 4
    assert (root / "128" / "StarBlueAsset.png").exists()
    assert (root / "512" / "StarRedAsset.png").exists()


def test_star_wrapper_noops_when_root_missing(tmp_path: Path) -> None:
    result = ensure_star_derivatives(stars_root=tmp_path / "absent")
    assert result.sources == 0


def test_planet_wrapper_generates_from_2048_master(tmp_path: Path) -> None:
    """Planet masters at <root>/2048/planet_*.png produce smaller size dirs."""
    root = tmp_path / "Planets"
    _write_png(root / str(PLANET_MASTER_SIZE) / "planet_5_001.png", PLANET_MASTER_SIZE)

    result = ensure_planet_derivatives(planets_root=root, sizes=(128, 1024))

    assert result.sources == 1
    assert result.generated == 2
    assert (root / "128" / "planet_5_001.png").exists()
    assert (root / "1024" / "planet_5_001.png").exists()
    with Image.open(root / "1024" / "planet_5_001.png") as img:
        assert img.size == (1024, 1024)


def test_planet_wrapper_noops_when_root_missing(tmp_path: Path) -> None:
    result = ensure_planet_derivatives(planets_root=tmp_path / "absent")
    assert result.sources == 0


def test_planet_master_size_is_2048() -> None:
    """Sanity: planet master is the largest (2048), not the components' 1024."""
    assert PLANET_MASTER_SIZE == 2048


def test_flag_and_star_master_size_is_1024() -> None:
    """Sanity: flags and stars use 1024 masters, matching components."""
    assert FLAG_MASTER_SIZE == 1024
    assert STAR_MASTER_SIZE == 1024
