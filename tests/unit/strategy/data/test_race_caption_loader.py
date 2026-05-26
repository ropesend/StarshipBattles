"""Tests for RaceCaptionLoader (PROJ-299 Phase 2)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "captions"


@pytest.fixture
def fake_assets(tmp_path: Path):
    """Build a temporary `assets/` tree mirroring the real layout."""
    flags_dir = tmp_path / "images" / "flags" / "Processed"
    portraits_dir = tmp_path / "images" / "race_portraits"
    themes_dir = tmp_path / "images" / "ship_themes"
    flags_dir.mkdir(parents=True)
    portraits_dir.mkdir(parents=True)
    themes_dir.mkdir(parents=True)
    return {
        "root": tmp_path,
        "flags": flags_dir,
        "portraits": portraits_dir,
        "themes": themes_dir,
    }


@pytest.fixture
def loader_at(fake_assets):
    """Construct a `RaceCaptionLoader` rooted at the temp assets dir."""
    from game.strategy.data.race_caption_loader import RaceCaptionLoader

    return RaceCaptionLoader(assets_dir=fake_assets["root"])


# ============================================================================
# Flag captions
# ============================================================================


class TestLoadFlag:
    def test_returns_dict_when_sidecar_exists(self, fake_assets, loader_at):
        flag_id = "flag_abc"
        flag_dir = fake_assets["flags"] / flag_id
        flag_dir.mkdir()
        sidecar = flag_dir / f"{flag_id}.caption.json"
        shutil.copy(FIXTURES_DIR / "flag_full.caption.json", sidecar)

        result = loader_at.load_flag(flag_id)

        assert result is not None
        assert result["mood"] == "aggressive"
        assert result["geometry"].startswith("Vertical tricolour")

    def test_returns_none_when_sidecar_missing(self, fake_assets, loader_at):
        flag_id = "flag_does_not_exist"
        result = loader_at.load_flag(flag_id)
        assert result is None

    def test_returns_none_on_malformed_json(self, fake_assets, loader_at, caplog):
        flag_id = "flag_bad"
        flag_dir = fake_assets["flags"] / flag_id
        flag_dir.mkdir()
        sidecar = flag_dir / f"{flag_id}.caption.json"
        shutil.copy(FIXTURES_DIR / "malformed.caption.json", sidecar)

        result = loader_at.load_flag(flag_id)
        assert result is None
        # Loader should log something at WARNING or below
        assert any("flag_bad" in r.message or "malformed" in r.message.lower()
                   for r in caplog.records)

    def test_returns_none_when_schema_version_missing(self, fake_assets, loader_at):
        flag_id = "flag_noversion"
        flag_dir = fake_assets["flags"] / flag_id
        flag_dir.mkdir()
        sidecar = flag_dir / f"{flag_id}.caption.json"
        sidecar.write_text(json.dumps({"geometry": "x"}), encoding="utf-8")

        result = loader_at.load_flag(flag_id)
        assert result is None

    def test_returns_none_when_sidecar_is_not_json_object(self, fake_assets, loader_at):
        flag_id = "flag_array"
        flag_dir = fake_assets["flags"] / flag_id
        flag_dir.mkdir()
        sidecar = flag_dir / f"{flag_id}.caption.json"
        sidecar.write_text(json.dumps(["not", "a", "caption"]), encoding="utf-8")

        result = loader_at.load_flag(flag_id)
        assert result is None


# ============================================================================
# Portrait captions
# ============================================================================


class TestLoadPortrait:
    def test_returns_dict_when_sidecar_exists(self, fake_assets, loader_at):
        portrait_filename = "alien_portrait.jpg"
        sidecar = fake_assets["portraits"] / f"{portrait_filename}.caption.json"
        shutil.copy(FIXTURES_DIR / "portrait_full.caption.json", sidecar)

        result = loader_at.load_portrait(portrait_filename)
        assert result is not None
        assert result["technology_level_hint"] == "industrial"

    def test_returns_none_when_sidecar_missing(self, loader_at):
        result = loader_at.load_portrait("missing_portrait.jpg")
        assert result is None


# ============================================================================
# Theme captions
# ============================================================================


class TestLoadTheme:
    def test_returns_dict_when_sidecar_exists(self, fake_assets, loader_at):
        theme_id = "Atlantians"
        theme_dir = fake_assets["themes"] / theme_id
        theme_dir.mkdir()
        sidecar = theme_dir / "theme.caption.json"
        shutil.copy(FIXTURES_DIR / "theme_full.caption.json", sidecar)

        result = loader_at.load_theme(theme_id)
        assert result is not None
        assert result["technology_level_hint"] == "advanced"

    def test_returns_none_when_sidecar_missing(self, loader_at):
        result = loader_at.load_theme("NonexistentTheme")
        assert result is None


# ============================================================================
# Stateless / DI properties
# ============================================================================


class TestStateless:
    def test_two_instances_do_not_share_state(self, fake_assets):
        from game.strategy.data.race_caption_loader import RaceCaptionLoader

        a = RaceCaptionLoader(assets_dir=fake_assets["root"])
        b = RaceCaptionLoader(assets_dir=fake_assets["root"])

        # Setting up a sidecar visible to both
        flag_id = "flag_xyz"
        (fake_assets["flags"] / flag_id).mkdir()
        (fake_assets["flags"] / flag_id / f"{flag_id}.caption.json").write_text(
            json.dumps({"schema_version": 1, "geometry": "x", "color_palette": "x",
                       "symbolism": "x", "cultural_hints": "x", "mood": "peaceful",
                       "distinctive_traits": "x"}),
            encoding="utf-8",
        )

        assert a.load_flag(flag_id) is not None
        assert b.load_flag(flag_id) is not None

    def test_default_assets_dir_is_paths_asset_dir(self):
        """When constructed without assets_dir, defaults to game.core.paths.Paths.ASSET_DIR."""
        from game.core.paths import Paths
        from game.strategy.data.race_caption_loader import RaceCaptionLoader

        loader = RaceCaptionLoader()
        assert str(loader.assets_dir) == Paths.ASSET_DIR
