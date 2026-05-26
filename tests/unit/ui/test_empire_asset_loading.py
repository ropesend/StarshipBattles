"""
Unit tests for empire asset loading logic.

PROJ-37 Phase 5: Updated tests for RaceAssetLoader-based implementation.
These tests verify that StrategyScreen delegates empire asset loading to
RaceAssetLoader.load_all_empire_assets().
"""

import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_asset_manager():
    """Create a mock AssetManager that tracks loaded images."""
    am = MagicMock()

    def load_external_image_side_effect(path):
        """Return a mock surface tagged with the loaded path."""
        surface = MagicMock(spec=pygame.Surface)
        surface.loaded_from_path = path
        return surface

    am.load_external_image.side_effect = load_external_image_side_effect
    am.load_manifest = MagicMock()
    return am


@pytest.fixture
def mock_empire_factory():
    """Factory for creating mock Empire objects."""
    def _create_empire(empire_id, flag_id="", empire_theme_id="Federation"):
        """Create a mock Empire with the given attributes."""
        empire = MagicMock()
        empire.id = empire_id
        empire.flag_id = flag_id
        empire.empire_theme_id = empire_theme_id
        return empire
    return _create_empire


@pytest.fixture
def mock_game_config():
    """Mock GameConfig that returns a known asset base path."""
    config = MagicMock()
    config.asset_base_path = os.path.join("C:", "TestAssets")
    return config


def _normalize_path(path):
    """Helper to normalize path separators for comparison."""
    return path.replace("\\", "/").lower()


# =============================================================================
# Test: Race Flag Loading via RaceAssetLoader
# =============================================================================

class TestRaceFlagLoading:
    """Tests that RaceAssetLoader is used for loading race-specific flags."""

    def test_load_race_flag_rectangle_from_256_dir(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When flag_id exists with 256 subdir, loads rectangle.png from 256/."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="flag_test123", empire_theme_id="Federation")

        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.loaded_from_path = "assets/images/flags/Processed/flag_test123/256/rectangle.png"

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {'colony': mock_surface, 'fleet_flag': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify RaceAssetLoader was called with the empire (PROJ-314 / BUG-124:
        # ShipThemeManager owns the asset directory, so asset_base is gone).
        mock_race_loader.load_all_empire_assets.assert_called_once_with(empire)

        # Verify colony flag was loaded
        assert 'colony' in scene.empire_assets[1]

    def test_load_race_flag_rectangle_fallback_to_root(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """RaceAssetLoader handles fallback logic internally."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="flag_rootonly", empire_theme_id="Federation")

        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.loaded_from_path = "assets/images/flags/Processed/flag_rootonly/rectangle.png"

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {'colony': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify colony flag was loaded
        assert 'colony' in scene.empire_assets[1]

    def test_load_race_flag_shield(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When flag_id exists, loads shield.png as 'fleet_flag'."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="flag_shield", empire_theme_id="Federation")

        mock_surface = MagicMock(spec=pygame.Surface)

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {'colony': mock_surface, 'fleet_flag': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify fleet_flag was loaded
        assert 'fleet_flag' in scene.empire_assets[1]


# =============================================================================
# Test: Theme Flag Loading
# =============================================================================

class TestThemeFlagLoading:
    """Tests for loading flags from empire theme directory via RaceAssetLoader."""

    def test_load_fleet_icon_from_theme(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When empire_theme_id exists, loads Battlecruiser.png as 'fleet'."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="", empire_theme_id="Federation")

        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.loaded_from_path = "C:/TestAssets/Federation/skins/Battlecruiser.png"

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {'fleet': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify fleet icon was loaded
        assert 'fleet' in scene.empire_assets[1]

    def test_load_colony_flag_from_theme_when_no_race_flag(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When no race flag_id, loads Colony_Flag.jpg from theme as 'colony'."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="", empire_theme_id="Romulan")

        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.loaded_from_path = "C:/TestAssets/Romulan/Flags/Colony_Flag.jpg"

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {'colony': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify colony flag was loaded from theme
        assert 'colony' in scene.empire_assets[1]


# =============================================================================
# Test: Flag Precedence (Race vs Theme) - now handled by RaceAssetLoader
# =============================================================================

class TestFlagPrecedence:
    """Tests that RaceAssetLoader handles race vs theme precedence correctly."""

    def test_race_flag_precedence_over_theme(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """RaceAssetLoader returns race flag over theme when both exist."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="flag_race", empire_theme_id="Federation")

        race_surface = MagicMock(spec=pygame.Surface)
        race_surface.loaded_from_path = "assets/images/flags/Processed/flag_race/256/rectangle.png"

        mock_race_loader = MagicMock()
        # RaceAssetLoader returns race flag (it handles precedence internally)
        mock_race_loader.load_all_empire_assets.return_value = {
            'colony': race_surface,
            'fleet_flag': race_surface,
            'fleet': MagicMock(spec=pygame.Surface)  # Fleet icon from theme
        }

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify colony flag came from race flag (has loaded_from_path with flag_race)
        assert 'colony' in scene.empire_assets[1]
        assert scene.empire_assets[1]['colony'] == race_surface

    def test_fallback_to_theme_when_race_flag_dir_missing(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When race flag directory doesn't exist, uses theme assets."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="flag_missing", empire_theme_id="Klingon")

        theme_surface = MagicMock(spec=pygame.Surface)
        theme_surface.loaded_from_path = "C:/TestAssets/Klingon/Flags/Colony_Flag.jpg"

        mock_race_loader = MagicMock()
        # RaceAssetLoader returns theme flag when race flag doesn't exist
        mock_race_loader.load_all_empire_assets.return_value = {'colony': theme_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Verify colony flag came from theme fallback
        assert 'colony' in scene.empire_assets[1]
        assert scene.empire_assets[1]['colony'] == theme_surface


# =============================================================================
# Test: Missing Assets
# =============================================================================

class TestMissingAssets:
    """Tests for behavior when assets don't exist."""

    def test_missing_all_assets_leaves_empty_dict(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When no assets exist, empire_assets[id] is an empty dict."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="", empire_theme_id="NonExistentTheme")

        mock_race_loader = MagicMock()
        mock_race_loader.load_all_empire_assets.return_value = {}  # Nothing found

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Empire entry should exist but be empty
        assert 1 in scene.empire_assets
        assert scene.empire_assets[1] == {}

    def test_missing_fleet_icon_only(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """When theme exists but Battlecruiser.png missing, 'fleet' key is not set."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire = mock_empire_factory(empire_id=1, flag_id="", empire_theme_id="PartialTheme")

        mock_surface = MagicMock(spec=pygame.Surface)

        mock_race_loader = MagicMock()
        # Only colony loaded, no fleet
        mock_race_loader.load_all_empire_assets.return_value = {'colony': mock_surface}

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Colony flag should be loaded
        assert 'colony' in scene.empire_assets[1]
        # Fleet icon should NOT be set
        assert 'fleet' not in scene.empire_assets[1]


# =============================================================================
# Test: Multiple Empires
# =============================================================================

class TestMultipleEmpires:
    """Tests for loading assets for multiple empires."""

    def test_loads_assets_for_multiple_empires(self, mock_asset_manager, mock_empire_factory, mock_game_config):
        """Each empire gets its own asset dict entry from RaceAssetLoader."""
        from game.ui.screens.strategy_screen import StrategyScreen

        empire1 = mock_empire_factory(empire_id=1, flag_id="", empire_theme_id="Federation")
        empire2 = mock_empire_factory(empire_id=2, flag_id="flag_custom", empire_theme_id="Romulan")

        theme_surface = MagicMock(spec=pygame.Surface)
        theme_surface.name = "theme_colony"
        race_surface = MagicMock(spec=pygame.Surface)
        race_surface.name = "race_colony"

        mock_race_loader = MagicMock()

        def load_all_empire_assets_side_effect(emp):
            if emp.id == 1:
                return {'colony': theme_surface}  # Empire 1: theme colony flag
            elif emp.id == 2:
                return {'colony': race_surface, 'fleet_flag': race_surface}  # Empire 2: race flag
            return {}

        mock_race_loader.load_all_empire_assets.side_effect = load_all_empire_assets_side_effect

        scene = MagicMock(spec=StrategyScreen)
        scene.empires = [empire1, empire2]
        # PROJ-477 Phase 4: load_assets iterates scene.world.iter_empires.
        scene.world.iter_empires.side_effect = lambda: iter(scene.empires)
        scene.empire_assets = {}
        scene._race_loader = mock_race_loader

        with patch('game.assets.asset_manager.get_default_asset_manager', return_value=mock_asset_manager):
            with patch('game.strategy.engine.game_config.GameConfig', return_value=mock_game_config):
                StrategyScreen._load_assets(scene)

        # Both empires should have entries
        assert 1 in scene.empire_assets
        assert 2 in scene.empire_assets

        # Empire 1 should have theme colony flag
        assert 'colony' in scene.empire_assets[1]
        assert scene.empire_assets[1]['colony'] == theme_surface

        # Empire 2 should have race colony flag
        assert 'colony' in scene.empire_assets[2]
        assert scene.empire_assets[2]['colony'] == race_surface
