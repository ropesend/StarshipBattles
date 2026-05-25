"""Characterization tests for ShipThemeManager (PROJ-340).

Pins observed behavior of the ship-theme asset loader at
``game/ui/assets/ship_theme_manager.py``. Tests:

* Build hand-written ``theme.json`` files in a ``tmp_path`` fake themes
  tree (rather than touching the real ``assets/Images/ShipThemes`` tree).
* Monkeypatch ``Paths.SHIP_THEMES_DIR`` to that fake tree (PROJ-340 D-003).
* Patch ``pygame.image.load`` to return a synthetic SRCALPHA Surface
  whose ``.convert_alpha()`` returns itself, so disk PNGs are never
  needed (PROJ-340 D-004).
"""
from __future__ import annotations

import json
from pathlib import Path

import pygame
import pytest

from game.ui.assets import ship_theme_manager as stm_module
from game.ui.assets.ship_theme_manager import (
    ShipThemeManager,
    get_default_ship_theme_manager,
    set_default_ship_theme_manager,
)


# ----------------------------------------------------------------------------
# Fixture helpers
# ----------------------------------------------------------------------------


def _minimal_theme_json(name: str = "TestTheme", *, with_portrait: bool = True) -> dict:
    """Build a minimal valid theme.json payload that registers one ship class.

    Uses ``Frigate`` (a member of ``SHIP_CLASSES_WITH_VISUAL_THEMES``) so the
    canonical-keys validator does not log spurious 'unknown class' warnings.
    """
    entry = {"skin": "skin_frigate.png", "scale": 1.0}
    if with_portrait:
        entry["portrait"] = "portrait_frigate.png"
    return {
        "schema_version": 1,
        "name": name,
        "description": "test",
        "image_sizes": {},
        "assets": {"Frigate": entry},
    }


def _write_theme(themes_dir: Path, theme_name: str, payload: dict,
                 *, write_skin: bool = True, write_portrait: bool = True) -> Path:
    """Materialize a single theme directory under themes_dir."""
    theme_dir = themes_dir / theme_name
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "theme.json").write_text(json.dumps(payload), encoding="utf-8")
    if write_skin:
        (theme_dir / "skin_frigate.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    if write_portrait:
        (theme_dir / "portrait_frigate.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return theme_dir


@pytest.fixture
def fake_themes_dir(tmp_path: Path, monkeypatch):
    """Redirect Paths.SHIP_THEMES_DIR at the import site to a tmp tree."""
    fake_dir = tmp_path / "ShipThemes"
    fake_dir.mkdir()
    monkeypatch.setattr(stm_module.Paths, "SHIP_THEMES_DIR", str(fake_dir))
    yield fake_dir


@pytest.fixture
def synthetic_image_load(monkeypatch):
    """Patch pygame.image.load so we never read real PNGs.

    Returns a stand-in SRCALPHA Surface whose ``.convert_alpha()`` returns
    itself; this satisfies the ``pygame.image.load(path).convert_alpha()``
    chain in ``_load_single_image`` and ``_load_portrait_image``.
    """
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    monkeypatch.setattr(
        stm_module.pygame.image, "load", lambda _path: surface
    )
    yield surface


# ----------------------------------------------------------------------------
# Discovery / initialize() behaviors
# ----------------------------------------------------------------------------


class TestInitialize:
    def test_initialize_early_returns_when_themes_dir_missing(
        self, tmp_path: Path, monkeypatch
    ):
        missing = tmp_path / "does_not_exist"
        monkeypatch.setattr(stm_module.Paths, "SHIP_THEMES_DIR", str(missing))

        mgr = ShipThemeManager()
        mgr.initialize()

        assert mgr.discovery_complete is False
        assert mgr.theme_data == {}

    def test_initialize_skips_theme_with_invalid_theme_json(
        self, fake_themes_dir: Path
    ):
        # Invalid: write a theme dir whose theme.json is not parseable JSON.
        bad_dir = fake_themes_dir / "Broken"
        bad_dir.mkdir()
        (bad_dir / "theme.json").write_text("not-json{", encoding="utf-8")

        # Also write a valid theme alongside.
        _write_theme(fake_themes_dir, "Good", _minimal_theme_json("Good"))

        mgr = ShipThemeManager()
        mgr.initialize()

        # Good theme registered; broken theme silently skipped (load_json
        # returns None on JSONDecodeError).
        assert "Good" in mgr.theme_data
        assert "Broken" not in mgr.theme_data
        assert mgr.discovery_complete is True

    def test_initialize_warns_and_continues_on_unknown_schema_version(
        self, fake_themes_dir: Path, caplog
    ):
        payload = _minimal_theme_json("Future")
        payload["schema_version"] = 99
        _write_theme(fake_themes_dir, "Future", payload)

        mgr = ShipThemeManager()
        with caplog.at_level("WARNING", logger=stm_module.logger.name):
            mgr.initialize()

        assert "Future" in mgr.theme_data
        # Theme is registered despite the unknown schema_version warning.
        assert any(
            "unknown schema_version" in rec.message
            for rec in caplog.records
        )

    def test_initialize_skips_ship_class_when_skin_file_missing(
        self, fake_themes_dir: Path
    ):
        payload = _minimal_theme_json("NoSkin")
        # Write theme.json but NOT the skin_frigate.png file.
        _write_theme(
            fake_themes_dir, "NoSkin", payload,
            write_skin=False, write_portrait=True,
        )

        mgr = ShipThemeManager()
        mgr.initialize()

        # Theme is registered, but the Frigate entry is dropped because
        # skin_path resolution failed.
        assert "NoSkin" in mgr.theme_data
        assert mgr.theme_data["NoSkin"] == {}


# ----------------------------------------------------------------------------
# load_image / fallback behaviors
# ----------------------------------------------------------------------------


class TestLoadImage:
    def test_load_image_falls_back_to_default_theme_for_unknown_theme(
        self, fake_themes_dir: Path, synthetic_image_load: pygame.Surface
    ):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )

        mgr = ShipThemeManager()
        mgr.initialize()

        # Asking for a theme that does not exist falls back to default_theme
        # ("Federation"), so the call resolves to the Federation/Frigate
        # entry rather than the placeholder. The cached entry is registered
        # under the default theme name, not the requested-but-unknown name.
        surf = mgr.load_image("DoesNotExist", "Frigate")
        assert isinstance(surf, pygame.Surface)
        # Default theme is "Federation"; once loaded, the cache is populated
        # under that key.
        assert "Federation" in mgr.themes
        assert "Frigate" in mgr.themes["Federation"]
        assert mgr.themes["Federation"]["Frigate"] is surf

    def test_load_image_returns_synthetic_surface_for_unknown_ship_class(
        self, fake_themes_dir: Path, synthetic_image_load: pygame.Surface
    ):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()

        # Unknown ship class -> fallback (100x100 SRCALPHA placeholder).
        surf = mgr.load_image("Federation", "NotARealClass")
        assert isinstance(surf, pygame.Surface)
        assert surf.get_size() == (100, 100)

    def test_load_image_caches_surface_and_does_not_reload_on_second_call(
        self, fake_themes_dir: Path, monkeypatch
    ):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )

        load_calls: list[str] = []
        synthetic = pygame.Surface((100, 100), pygame.SRCALPHA)

        def _tracked_load(path):
            load_calls.append(str(path))
            return synthetic

        monkeypatch.setattr(stm_module.pygame.image, "load", _tracked_load)

        mgr = ShipThemeManager()
        mgr.initialize()

        first = mgr.load_image("Federation", "Frigate")
        second = mgr.load_image("Federation", "Frigate")

        assert first is second  # Same Surface returned from cache.
        assert len(load_calls) == 1  # Disk read only once.


class TestImageMetrics:
    def test_get_image_metrics_returns_none_before_initialize(self):
        mgr = ShipThemeManager()
        # discovery_complete is False on a fresh instance.
        assert mgr.get_image_metrics("Federation", "Frigate") is None


class TestPortrait:
    def test_get_portrait_image_returns_fallback_surface_when_portrait_missing(
        self, fake_themes_dir: Path, synthetic_image_load: pygame.Surface
    ):
        # Theme.json declares no portrait entry at all.
        payload = _minimal_theme_json("NoPortrait", with_portrait=False)
        _write_theme(
            fake_themes_dir, "NoPortrait", payload,
            write_portrait=False,
        )

        mgr = ShipThemeManager()
        mgr.initialize()

        surf = mgr.get_portrait_image("NoPortrait", "Frigate")
        # Fallback is a 100x100 Surface; synthetic_image_load is also 100x100
        # but the fallback comes from _create_fallback_image (SRCALPHA), not
        # from pygame.image.load. We characterize the size + that it's a
        # Surface.
        assert isinstance(surf, pygame.Surface)
        assert surf.get_size() == (100, 100)


# ----------------------------------------------------------------------------
# Lifecycle / module-singleton accessors
# ----------------------------------------------------------------------------


class TestLifecycle:
    def test_clear_resets_caches_and_discovery_complete_flag(
        self, fake_themes_dir: Path, synthetic_image_load: pygame.Surface
    ):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()
        # Force a load so caches are populated.
        mgr.load_image("Federation", "Frigate")

        assert mgr.discovery_complete is True
        assert mgr.theme_data
        assert mgr.themes  # at least one cached surface

        mgr.clear()

        assert mgr.discovery_complete is False
        assert mgr.theme_data == {}
        assert mgr.themes == {}
        assert mgr.image_metrics == {}
        assert mgr.portraits == {}
        assert mgr.theme_metadata == {}

    def test_get_available_themes_reflects_current_theme_data_keys(
        self, fake_themes_dir: Path
    ):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )
        _write_theme(
            fake_themes_dir, "Klingon", _minimal_theme_json("Klingon"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()

        names = mgr.get_available_themes()

        assert set(names) == {"Federation", "Klingon"}


class TestModuleSingleton:
    def test_set_default_ship_theme_manager_swaps_module_singleton(self):
        original = get_default_ship_theme_manager()
        replacement = ShipThemeManager()
        try:
            set_default_ship_theme_manager(replacement)
            assert get_default_ship_theme_manager() is replacement
            assert get_default_ship_theme_manager() is not original
        finally:
            # Restore for downstream tests.
            set_default_ship_theme_manager(original)


# ----------------------------------------------------------------------------
# PROJ-346 / PROJ-340: characterization for previously zero-coverage paths
# ----------------------------------------------------------------------------


class TestValidateDeclaredKeys:
    """Pin ``_validate_declared_keys`` (ship_theme_manager.py:220-236).

    Two log paths:
      * ``extras = declared - canonical`` -> WARNING
      * ``missing = canonical - declared`` -> INFO
    Empty diffs on either side log nothing on that side.
    """

    def test_unknown_class_in_assets_logs_warning_naming_extras(
        self, fake_themes_dir: Path, caplog,
    ):
        # Real canonical class plus an alien one to trigger the extras branch.
        payload = _minimal_theme_json("ExtrasTheme")
        payload["assets"]["NotARealClass"] = {
            "skin": "skin_frigate.png", "scale": 1.0,
        }
        _write_theme(fake_themes_dir, "ExtrasTheme", payload)

        mgr = ShipThemeManager()
        with caplog.at_level("WARNING", logger=stm_module.logger.name):
            mgr.initialize()

        warnings = [
            r for r in caplog.records
            if r.levelname == "WARNING"
            and "unknown ship classes" in r.message
        ]
        assert warnings, (
            "extras branch must emit WARNING naming the unknown class"
        )
        # The warning lists the offending class.
        assert any("NotARealClass" in r.message for r in warnings)

    def test_missing_canonical_class_logs_info_naming_count_and_classes(
        self, fake_themes_dir: Path, caplog,
    ):
        # _minimal_theme_json declares ONLY 'Frigate'. SHIP_CLASSES_WITH_VISUAL_THEMES
        # has many more, so missing != empty -> INFO branch fires.
        from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES

        _write_theme(
            fake_themes_dir, "MissingTheme", _minimal_theme_json("MissingTheme"),
        )

        mgr = ShipThemeManager()
        with caplog.at_level("INFO", logger=stm_module.logger.name):
            mgr.initialize()

        infos = [
            r for r in caplog.records
            if r.levelname == "INFO"
            and "missing" in r.message
            and "canonical ship class" in r.message
        ]
        assert infos, (
            "missing branch must emit INFO naming the count and classes; "
            f"records={[r.message for r in caplog.records]}"
        )
        # The numeric count appears: |canonical - {Frigate}|.
        expected_missing = len(SHIP_CLASSES_WITH_VISUAL_THEMES - {"Frigate"})
        assert any(str(expected_missing) in r.message for r in infos)

    def test_extras_and_missing_paths_are_independent(
        self, fake_themes_dir: Path, caplog,
    ):
        """Both branches fire when the theme has both extras and missing."""
        payload = _minimal_theme_json("MixedTheme")
        payload["assets"]["NotARealClass"] = {
            "skin": "skin_frigate.png", "scale": 1.0,
        }
        _write_theme(fake_themes_dir, "MixedTheme", payload)

        mgr = ShipThemeManager()
        with caplog.at_level("INFO", logger=stm_module.logger.name):
            mgr.initialize()

        has_extras_warn = any(
            r.levelname == "WARNING" and "unknown ship classes" in r.message
            for r in caplog.records
        )
        has_missing_info = any(
            r.levelname == "INFO" and "canonical ship class" in r.message
            for r in caplog.records
        )
        assert has_extras_warn
        assert has_missing_info


class TestMissingAssetsBlockRejection:
    """Pin the rejection at ship_theme_manager.py:139-145.

    ``_discover_theme`` requires ``assets`` to be a dict; missing key,
    None, or wrong-type all log ERROR and skip the theme so it does NOT
    register in ``theme_data``.
    """

    def test_missing_assets_key_logs_error_and_skips_theme(
        self, fake_themes_dir: Path, caplog,
    ):
        # Theme.json with NO 'assets' key at all.
        payload = {
            "schema_version": 1,
            "name": "NoAssets",
            "description": "missing assets block",
            "image_sizes": {},
        }
        _write_theme(fake_themes_dir, "NoAssets", payload, write_skin=False)

        mgr = ShipThemeManager()
        with caplog.at_level("ERROR", logger=stm_module.logger.name):
            mgr.initialize()

        # Theme NOT registered.
        assert "NoAssets" not in mgr.theme_data
        # Error log fired naming the offense.
        assert any(
            "missing or invalid 'assets:' block" in r.message
            for r in caplog.records if r.levelname == "ERROR"
        )

    def test_assets_as_list_is_rejected(
        self, fake_themes_dir: Path, caplog,
    ):
        """``assets: []`` -> not a dict -> logged + skipped."""
        payload = _minimal_theme_json("ListAssets")
        payload["assets"] = []  # Wrong type.
        _write_theme(fake_themes_dir, "ListAssets", payload, write_skin=False)

        mgr = ShipThemeManager()
        with caplog.at_level("ERROR", logger=stm_module.logger.name):
            mgr.initialize()

        assert "ListAssets" not in mgr.theme_data
        assert any(
            "missing or invalid 'assets:' block" in r.message
            for r in caplog.records if r.levelname == "ERROR"
        )


class TestNonDictAssetsEntryRejection:
    """Pin the per-entry rejection at ship_theme_manager.py:166-171.

    ``assets[<class>]`` that isn't a dict (string, list, etc.) is logged
    and skipped. The theme itself still registers; only the offending
    class is dropped.
    """

    def test_string_entry_is_skipped_with_error_log(
        self, fake_themes_dir: Path, caplog,
    ):
        payload = _minimal_theme_json("StringEntry")
        # Override the Frigate entry with a string instead of a dict.
        payload["assets"]["Frigate"] = "skin_frigate.png"
        _write_theme(
            fake_themes_dir, "StringEntry", payload, write_skin=True,
        )

        mgr = ShipThemeManager()
        with caplog.at_level("ERROR", logger=stm_module.logger.name):
            mgr.initialize()

        # Theme registered (per-entry skip, not whole-theme skip).
        assert "StringEntry" in mgr.theme_data
        # Frigate dropped because the entry wasn't a dict.
        assert "Frigate" not in mgr.theme_data["StringEntry"]
        # Error log fired naming the offense.
        assert any(
            "is not an object" in r.message
            for r in caplog.records if r.levelname == "ERROR"
        )

    def test_list_entry_is_skipped_with_error_log(
        self, fake_themes_dir: Path, caplog,
    ):
        payload = _minimal_theme_json("ListEntry")
        payload["assets"]["Frigate"] = ["skin_frigate.png"]
        _write_theme(
            fake_themes_dir, "ListEntry", payload, write_skin=True,
        )

        mgr = ShipThemeManager()
        with caplog.at_level("ERROR", logger=stm_module.logger.name):
            mgr.initialize()

        assert "ListEntry" in mgr.theme_data
        assert "Frigate" not in mgr.theme_data["ListEntry"]
        assert any(
            "is not an object" in r.message
            for r in caplog.records if r.levelname == "ERROR"
        )


class TestGetManualScale:
    """Pin ``get_manual_scale`` (ship_theme_manager.py:345-353)."""

    def test_returns_one_before_initialize(self):
        mgr = ShipThemeManager()
        # discovery_complete is False on a fresh instance.
        assert mgr.get_manual_scale("Federation", "Frigate") == 1.0

    def test_returns_declared_scale_for_known_theme_and_class(
        self, fake_themes_dir: Path,
    ):
        payload = _minimal_theme_json("ScaleTheme")
        payload["assets"]["Frigate"]["scale"] = 2.5
        _write_theme(fake_themes_dir, "ScaleTheme", payload)

        mgr = ShipThemeManager()
        mgr.initialize()

        assert mgr.get_manual_scale("ScaleTheme", "Frigate") == 2.5

    def test_falls_back_to_default_theme_for_unknown_theme(
        self, fake_themes_dir: Path,
    ):
        # Build the default ("Federation") theme with scale 0.75.
        payload = _minimal_theme_json("Federation")
        payload["assets"]["Frigate"]["scale"] = 0.75
        _write_theme(fake_themes_dir, "Federation", payload)

        mgr = ShipThemeManager()
        mgr.initialize()

        # Unknown theme falls back to default_theme="Federation".
        assert mgr.get_manual_scale("UnknownTheme", "Frigate") == 0.75

    def test_returns_one_for_unknown_ship_class(self, fake_themes_dir: Path):
        _write_theme(
            fake_themes_dir, "Federation", _minimal_theme_json("Federation"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()
        # Federation has Frigate but not 'NotAClass' -> default 1.0.
        assert mgr.get_manual_scale("Federation", "NotAClass") == 1.0


class TestGetSkinPath:
    """Pin ``get_skin_path`` (ship_theme_manager.py:428-431)."""

    def test_returns_absolute_path_for_known_theme_and_class(
        self, fake_themes_dir: Path,
    ):
        _write_theme(fake_themes_dir, "PathTheme", _minimal_theme_json("PathTheme"))
        mgr = ShipThemeManager()
        mgr.initialize()

        skin_path = mgr.get_skin_path("PathTheme", "Frigate")
        assert skin_path is not None
        # Path resolves under the fake themes dir.
        assert "skin_frigate.png" in skin_path
        assert "PathTheme" in skin_path

    def test_returns_none_for_unknown_theme(self, fake_themes_dir: Path):
        # fake_themes_dir is empty -> no themes registered.
        assert fake_themes_dir.exists()
        mgr = ShipThemeManager()
        mgr.initialize()
        # No themes registered -> None (note: get_skin_path does NOT
        # fall back to default_theme; it returns None).
        assert mgr.get_skin_path("DoesNotExist", "Frigate") is None

    def test_returns_none_for_unknown_ship_class(self, fake_themes_dir: Path):
        _write_theme(fake_themes_dir, "PathTheme", _minimal_theme_json("PathTheme"))
        mgr = ShipThemeManager()
        mgr.initialize()
        assert mgr.get_skin_path("PathTheme", "NotAClass") is None


class TestGetPortraitPath:
    """Pin ``get_portrait_path`` (ship_theme_manager.py:433-439)."""

    def test_returns_absolute_path_when_portrait_declared(
        self, fake_themes_dir: Path,
    ):
        _write_theme(
            fake_themes_dir, "PortraitTheme",
            _minimal_theme_json("PortraitTheme"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()

        portrait_path = mgr.get_portrait_path("PortraitTheme", "Frigate")
        assert portrait_path is not None
        assert "portrait_frigate.png" in portrait_path

    def test_returns_none_when_portrait_omitted(self, fake_themes_dir: Path):
        # No portrait key on the entry, no portrait file on disk.
        payload = _minimal_theme_json("NoPortrait", with_portrait=False)
        _write_theme(
            fake_themes_dir, "NoPortrait", payload, write_portrait=False,
        )
        mgr = ShipThemeManager()
        mgr.initialize()

        assert mgr.get_portrait_path("NoPortrait", "Frigate") is None

    def test_returns_none_for_unknown_theme(self):
        mgr = ShipThemeManager()
        # Pre-initialize: theme_data is empty.
        assert mgr.get_portrait_path("Anything", "Frigate") is None

    def test_returns_none_for_unknown_ship_class(self, fake_themes_dir: Path):
        _write_theme(
            fake_themes_dir, "PortraitTheme",
            _minimal_theme_json("PortraitTheme"),
        )
        mgr = ShipThemeManager()
        mgr.initialize()
        assert mgr.get_portrait_path("PortraitTheme", "NotAClass") is None
