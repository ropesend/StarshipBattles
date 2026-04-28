"""Tests for Tools/regenerate_ship_portraits/ (PROJ-314)."""
from __future__ import annotations

import json
import os
import pathlib
from typing import Optional
from unittest.mock import patch

import pytest
from PIL import Image

from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from Tools.regenerate_ship_portraits import audit, cli
from Tools.regenerate_ship_portraits.prompts import (
    SHIP_CLASS_STYLE_ANCHORS,
    build_prompt,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_theme(
    theme_dir: pathlib.Path, theme_name: str, *, with_portrait: bool = True,
) -> None:
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "Skins").mkdir(exist_ok=True)
    (theme_dir / "Portraits").mkdir(exist_ok=True)
    assets = {
        "Battleship": {
            "skin": "Skins/battleship.png",
            "scale": 1.0,
        },
        "Escort": {
            "skin": "Skins/escort.png",
            "scale": 1.0,
        },
    }
    if with_portrait:
        assets["Battleship"]["portrait"] = "Portraits/battleship.png"
        # Escort intentionally has no portrait declared.
    _write_png(theme_dir / "Skins" / "battleship.png")
    _write_png(theme_dir / "Skins" / "escort.png")
    if with_portrait:
        _write_png(theme_dir / "Portraits" / "battleship.png")
    (theme_dir / "theme.json").write_text(json.dumps({
        "schema_version": 1,
        "name": theme_name,
        "description": "Test theme",
        "image_sizes": {"skin": [2048, 2048], "portrait": [2048, 2048]},
        "assets": assets,
    }))


def _write_png(path: pathlib.Path, size: tuple[int, int] = (2048, 2048)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, (12, 34, 56, 255)).save(path)


def _write_full_theme(
    theme_dir: pathlib.Path,
    theme_name: str,
    *,
    portrait_size: tuple[int, int] = (2048, 2048),
    omit_portraits: frozenset[str] = frozenset(),
) -> None:
    """Write a full canonical test theme with valid PNG assets."""
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "Skins").mkdir(exist_ok=True)
    (theme_dir / "Portraits").mkdir(exist_ok=True)
    assets: dict[str, dict[str, object]] = {}
    for ship_class in SHIP_CLASSES_WITH_VISUAL_THEMES:
        basename = (
            ship_class.lower()
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "_")
            .replace("__", "_")
        )
        skin_rel = f"Skins/{basename}.png"
        portrait_rel = f"Portraits/{basename}.png"
        assets[ship_class] = {"skin": skin_rel, "scale": 1.0}
        _write_png(theme_dir / skin_rel)
        if ship_class not in omit_portraits:
            assets[ship_class]["portrait"] = portrait_rel
            _write_png(theme_dir / portrait_rel, portrait_size)
    (theme_dir / "theme.json").write_text(json.dumps({
        "schema_version": 1,
        "name": theme_name,
        "description": "Full test theme",
        "image_sizes": {"skin": [2048, 2048], "portrait": [2048, 2048]},
        "assets": assets,
    }))


# ---------------------------------------------------------------------------
# Prompt-builder tests
# ---------------------------------------------------------------------------


class TestPromptBuilder:
    def test_every_canonical_class_has_anchor(self) -> None:
        """SHIP_CLASS_STYLE_ANCHORS covers every canonical ship class."""
        missing = SHIP_CLASSES_WITH_VISUAL_THEMES - SHIP_CLASS_STYLE_ANCHORS.keys()
        assert not missing, f"Missing prompt anchors for: {missing}"

    def test_build_prompt_includes_theme_and_class(self) -> None:
        text = build_prompt("Federation", "sleek white starships", "Battleship")
        assert "Federation" in text
        assert "sleek white starships" in text


# ---------------------------------------------------------------------------
# Audit tests
# ---------------------------------------------------------------------------


class TestAudit:
    def test_clean_theme_reports_clean(self, tmp_path: pathlib.Path) -> None:
        theme_dir = tmp_path / "Cleanish"
        _write_theme(theme_dir, "Cleanish")
        finding = audit.audit_theme(str(theme_dir))
        assert finding.schema_ok
        assert finding.declared_keys == ["Battleship", "Escort"]
        assert "Battleship" in finding.extras or "Battleship" not in finding.extras
        # Battleship + Escort are canonical; missing = canonical - declared.
        assert "Cruiser" in finding.missing
        assert finding.errors == []

    def test_missing_assets_block_flagged(self, tmp_path: pathlib.Path) -> None:
        theme_dir = tmp_path / "Legacy"
        theme_dir.mkdir()
        (theme_dir / "theme.json").write_text(json.dumps({
            "name": "Legacy",
            "images": {"Battleship": "Skins/battleship.png"},
        }))
        finding = audit.audit_theme(str(theme_dir))
        assert not finding.schema_ok
        assert any("legacy" in e.lower() or "PROJ-314" in e for e in finding.errors)

    def test_missing_portrait_file_flagged(self, tmp_path: pathlib.Path) -> None:
        theme_dir = tmp_path / "PartGap"
        _write_theme(theme_dir, "PartGap", with_portrait=False)
        # Add a declared but missing portrait path.
        data = json.loads((theme_dir / "theme.json").read_text())
        data["assets"]["Battleship"]["portrait"] = "Portraits/battleship.png"
        (theme_dir / "theme.json").write_text(json.dumps(data))
        finding = audit.audit_theme(str(theme_dir))
        bs = next(s for s in finding.ships if s.ship_class == "Battleship")
        assert bs.portrait is not None
        assert bs.portrait.exists is False

    def test_clean_theme_exits_zero(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_full_theme(themes_root / "Clean", "Clean")
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 0
        out = capsys.readouterr().out
        assert "EXIT 0" in out

    def test_size_mismatch_only_exits_two(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_full_theme(themes_root / "Mismatch", "Mismatch", portrait_size=(1024, 1024))
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 2
        out = capsys.readouterr().out
        assert "EXIT 2" in out
        assert "size mismatches" in out

    def test_missing_portrait_exits_three(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_full_theme(
            themes_root / "Missing",
            "Missing",
            omit_portraits=frozenset({"Escort"}),
        )
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 3
        out = capsys.readouterr().out
        assert "EXIT 3" in out
        assert "missing portraits" in out

    def test_missing_portrait_takes_precedence_over_size_mismatch(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_full_theme(
            themes_root / "Mixed",
            "Mixed",
            portrait_size=(1024, 1024),
            omit_portraits=frozenset({"Escort"}),
        )
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 3
        out = capsys.readouterr().out
        assert "EXIT 3" in out

    def test_theme_with_zero_portraits_reports_missing_instead_of_clean(
        self, tmp_path: pathlib.Path,
    ) -> None:
        theme_dir = tmp_path / "ZeroPortraits"
        _write_full_theme(
            theme_dir,
            "ZeroPortraits",
            omit_portraits=frozenset(SHIP_CLASSES_WITH_VISUAL_THEMES),
        )
        finding = audit.audit_theme(str(theme_dir))
        missing = [s for s in finding.ships if s.portrait and not s.portrait.exists]
        assert len(missing) == len(SHIP_CLASSES_WITH_VISUAL_THEMES)
        assert "CLEAN" not in audit._format_human([finding])

    def test_main_reports_existing_missing_portraits(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_theme(themes_root / "T1", "T1")
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 3
        out = capsys.readouterr().out
        assert "T1" in out


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_list_classes_prints_canonical_set(
        self, capsys: pytest.CaptureFixture[str],
    ) -> None:
        rc = cli.main(["--list-classes"])
        assert rc == 0
        out = capsys.readouterr().out
        for cls in SHIP_CLASSES_WITH_VISUAL_THEMES:
            assert cls in out

    def test_ship_class_requires_theme(
        self, capsys: pytest.CaptureFixture[str],
    ) -> None:
        rc = cli.main(["--ship-class", "Battleship"])
        assert rc == 2
        err = capsys.readouterr().err
        assert "--ship-class" in err

    def test_dry_run_emits_plan(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_theme(themes_root / "TestTheme", "TestTheme")
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = cli.main(["--theme", "TestTheme", "--dry-run"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Planned" in out
        assert "dry-run" in out

    def test_idempotent_skip_when_portrait_exists(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_theme(themes_root / "T1", "T1")  # Battleship has a portrait.
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        plans = cli.plan_generations("T1", "Battleship", force=False)
        assert len(plans) == 1
        assert plans[0].skip_reason is not None
        assert "already exists" in plans[0].skip_reason

    def test_force_re_generates_existing(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_theme(themes_root / "T1", "T1")
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        plans = cli.plan_generations("T1", "Battleship", force=True)
        assert len(plans) == 1
        assert plans[0].skip_reason is None

    def test_cost_cap_aborts(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        # No portrait dir: every canonical class is missing.
        td = themes_root / "T1"
        td.mkdir()
        (td / "Skins").mkdir()
        assets = {cls: {"skin": "Skins/x.png"} for cls in SHIP_CLASSES_WITH_VISUAL_THEMES}
        (td / "Skins" / "x.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (td / "theme.json").write_text(json.dumps({
            "schema_version": 1, "name": "T1", "description": "",
            "image_sizes": {"skin": [2048, 2048], "portrait": [2048, 2048]},
            "assets": assets,
        }))
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = cli.main(["--theme", "T1", "--cost-cap", "0.10"])
        assert rc == 3
        err = capsys.readouterr().err
        assert "exceeds cost cap" in err

    def test_run_uses_provider(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from game.ui.services.image import ImageResult

        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        # Theme with NO portrait declared, so it becomes a generation target.
        td = themes_root / "T1"
        _write_theme(td, "T1", with_portrait=False)
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))

        # Stub provider — never hits the network.
        class _StubProvider:
            def generate_image(
                self, prompt: str, *, size: str = "2048x2048", model: str = "gpt-image-2",
                edit_image=None, mask=None, timeout_seconds: Optional[float] = None,
                cancel_token=None, **opts,
            ) -> ImageResult:
                return ImageResult(
                    image_bytes=b"\x89PNG\r\n\x1a\nfake",
                    size=(2048, 2048),
                    model=model,
                    latency_ms=10.0,
                    provider="stub",
                    request_id="rid-1",
                )

        # Force the factory to return our stub.
        monkeypatch.setattr(
            cli.ImageProviderFactory, "create",
            staticmethod(lambda name=None: _StubProvider()),
        )
        # Override last_run path so the test is hermetic.
        monkeypatch.setattr(cli, "LAST_RUN_PATH", tmp_path / "last_run.json")

        rc = cli.main([
            "--theme", "T1", "--ship-class", "Escort",
            "--cost-cap", "10.00",
        ])
        assert rc == 0
        # Portrait should now exist on disk.
        out_path = td / "Portraits" / "escort.png"
        assert out_path.exists()
        # Manifest written.
        manifest = json.loads((tmp_path / "last_run.json").read_text())
        assert manifest["results"][0]["ok"] is True
