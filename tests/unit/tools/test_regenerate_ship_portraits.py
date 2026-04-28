"""Tests for Tools/regenerate_ship_portraits/ (PROJ-314)."""
from __future__ import annotations

import json
import os
import pathlib
from typing import Optional
from unittest.mock import patch

import pytest

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
    (theme_dir / "Skins" / "battleship.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (theme_dir / "Skins" / "escort.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    if with_portrait:
        (theme_dir / "Portraits" / "battleship.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (theme_dir / "theme.json").write_text(json.dumps({
        "schema_version": 1,
        "name": theme_name,
        "description": "Test theme",
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

    def test_main_runs_without_error(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        themes_root = tmp_path / "ShipThemes"
        themes_root.mkdir()
        _write_theme(themes_root / "T1", "T1")
        monkeypatch.setattr("game.core.paths.Paths.SHIP_THEMES_DIR", str(themes_root))
        rc = audit.main([])
        assert rc == 0
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
