"""Tests for the repo-local codex ship-theme creator scripts."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / ".agents" / "skills" / "codex-ship-theme-creator" / "scripts"
CREATE_MANIFEST = SCRIPT_DIR / "create_manifest.py"
VALIDATE_THEME = SCRIPT_DIR / "validate_theme.py"
TARGET_SIZE = (2048, 2048)


def _run_script(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _write_assets(theme_root: Path) -> None:
    manifest = json.loads((theme_root / "theme.json").read_text(encoding="utf-8"))
    source = theme_root / "source.png"
    Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0)).save(source)
    for entry in manifest["assets"].values():
        for relpath in (entry["skin"], entry["portrait"]):
            target = theme_root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    source.unlink()


def test_create_manifest_writes_assets_schema(tmp_path: Path) -> None:
    theme_root = tmp_path / "TestTheme"

    result = _run_script(
        CREATE_MANIFEST,
        "--theme-root",
        str(theme_root),
        "--name",
        "TestTheme",
        "--description",
        "Synthetic test theme",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((theme_root / "theme.json").read_text(encoding="utf-8"))
    assert "images" not in manifest
    assert manifest["schema_version"] == 1
    assert manifest["image_sizes"] == {"skin": [2048, 2048], "portrait": [2048, 2048]}
    assert set(manifest["assets"]) == SHIP_CLASSES_WITH_VISUAL_THEMES
    assert manifest["assets"]["Battleship"] == {
        "skin": "skins/battleship.png",
        "scale": 1.0,
        "portrait": "portraits/battleship.png",
    }
    assert manifest["assets"]["Fighter (Medium)"]["skin"] == "skins/medium_fighter.png"


def test_validate_theme_accepts_generated_assets_schema_from_any_cwd(tmp_path: Path) -> None:
    theme_root = tmp_path / "TestTheme"
    create_result = _run_script(CREATE_MANIFEST, "--theme-root", str(theme_root), "--name", "TestTheme")
    assert create_result.returncode == 0, create_result.stderr
    _write_assets(theme_root)

    result = _run_script(
        VALIDATE_THEME,
        "--theme-root",
        str(theme_root),
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validation passed" in result.stdout
    assert "skin coverage: 19/19" in result.stdout
    assert "portrait coverage: 19/19" in result.stdout


def test_create_manifest_can_omit_portrait_paths(tmp_path: Path) -> None:
    theme_root = tmp_path / "SkinOnlyTheme"

    result = _run_script(
        CREATE_MANIFEST,
        "--theme-root",
        str(theme_root),
        "--name",
        "SkinOnlyTheme",
        "--omit-portraits",
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((theme_root / "theme.json").read_text(encoding="utf-8"))
    assert all("portrait" not in entry for entry in manifest["assets"].values())


def test_validate_theme_rejects_legacy_images_schema(tmp_path: Path) -> None:
    theme_root = tmp_path / "LegacyTheme"
    (theme_root / "Skins").mkdir(parents=True)
    (theme_root / "theme.json").write_text(
        json.dumps({
            "name": "LegacyTheme",
            "images": {"Battleship": "skins/battleship.png"},
        }),
        encoding="utf-8",
    )

    result = _run_script(VALIDATE_THEME, "--theme-root", str(theme_root))

    assert result.returncode == 1
    assert "legacy 'images' schema is not supported" in result.stdout
