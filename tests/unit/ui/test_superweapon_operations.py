"""Tests for SuperweaponOperations UI module (PROJ-102 Phase 8).

Tests superweapon designation handlers, fleet capability checks,
and command creation.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock, patch
import pygame


def make_mock_fleet(abilities: list = None, owner_id: int = 0, fleet_id: int = 1):
    """Create a mock fleet with specified abilities."""
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = MagicMock()
    fleet.location.q = 0
    fleet.location.r = 0

    # Set up capabilities
    capabilities = MagicMock()
    capabilities.has_ability = MagicMock(
        side_effect=lambda name: name in (abilities or [])
    )
    capabilities.ships_with_ability = MagicMock(
        return_value=[MagicMock(id=100)] if abilities else []
    )
    fleet.capabilities = capabilities

    return fleet


def make_mock_scene():
    """Create a mock scene with required properties."""
    scene = MagicMock()
    scene.camera = MagicMock()
    scene.camera.screen_to_world = MagicMock(
        return_value=MagicMock(x=100, y=100)
    )
    scene.hex_size = 10
    scene.systems = []
    scene.galaxy = MagicMock()
    scene.galaxy.systems = {}
    scene.galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    scene.ui = MagicMock()
    scene.on_ui_selection = MagicMock()
    return scene


def make_mock_facade():
    """Create a mock facade."""
    facade = MagicMock()
    result = MagicMock()
    result.is_valid = True
    result.message = ""
    facade.handle_command = MagicMock(return_value=result)
    return facade


class TestSuperweaponOperationsInit:
    """Tests for SuperweaponOperations initialization."""

    def test_init_stores_scene_and_facade(self):
        """SuperweaponOperations stores scene and facade references."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()

        ops = SuperweaponOperations(scene, facade)

        assert ops.scene is scene
        assert ops.facade is facade

    def test_properties_delegate_to_scene(self):
        """Properties delegate to scene."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()

        ops = SuperweaponOperations(scene, facade)

        assert ops.camera is scene.camera
        assert ops.hex_size is scene.hex_size
        assert ops.galaxy is scene.galaxy


class TestImplodePlanetDesignation:
    """Tests for handle_implode_planet_designation."""

    def test_returns_none_if_no_fleet(self):
        """Returns None when no fleet provided."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        result = ops.handle_implode_planet_designation(100, 100, None)
        assert result is None

    def test_returns_error_if_fleet_lacks_ability(self):
        """Returns error when fleet has no DestroyPlanet ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])

        result = ops.handle_implode_planet_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'Planet Imploder' in result['message']

    def test_returns_error_if_no_planet_at_hex(self):
        """Returns error when no planet at target hex."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        scene.galaxy.get_planets_at_global_hex.return_value = []
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=["DestroyPlanet"])

        with patch('game.ui.screens.strategy_superweapons.pixel_to_hex'):
            result = ops.handle_implode_planet_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'No planet' in result['message']


class TestStellerateStarDesignation:
    """Tests for handle_stellerate_star_designation."""

    def test_returns_error_if_fleet_lacks_ability(self):
        """Returns error when fleet has no DestroyStar ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])

        result = ops.handle_stellerate_star_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'Stellerator' in result['message']

    def test_returns_error_if_no_system_at_hex(self):
        """Returns error when no star system at target hex."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=["DestroyStar"])

        with patch('game.ui.screens.strategy_superweapons.pixel_to_hex'):
            with patch.object(ops, '_get_system_at_hex', return_value=None):
                result = ops.handle_stellerate_star_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'No star system' in result['message']


class TestOpenWarpDesignation:
    """Tests for handle_open_warp_designation."""

    def test_returns_error_if_fleet_lacks_ability(self):
        """Returns error when fleet has no OpenWarpPoint ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])

        result = ops.handle_open_warp_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'Quantum Tunneling Inducer' in result['message']


class TestCloseWarpDesignation:
    """Tests for handle_close_warp_designation."""

    def test_returns_error_if_fleet_lacks_ability(self):
        """Returns error when fleet has no CloseWarpPoint ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])

        result = ops.handle_close_warp_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'Quantum Tunneling Disruptor' in result['message']

    def test_returns_error_if_no_warp_point_at_hex(self):
        """Returns error when no warp point at target hex."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=["CloseWarpPoint"])

        with patch('game.ui.screens.strategy_superweapons.pixel_to_hex'):
            with patch.object(ops, '_get_warp_point_at_hex', return_value=None):
                result = ops.handle_close_warp_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'No warp point' in result['message']


class TestDysonSphereDesignation:
    """Tests for handle_dyson_sphere_designation."""

    def test_returns_error_if_fleet_lacks_ability(self):
        """Returns error when fleet has no CreateDysonSphere ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])

        result = ops.handle_dyson_sphere_designation(100, 100, fleet)
        assert result['type'] == 'error'
        assert 'Dyson Sphere Constructor' in result['message']


class TestSelfDestruct:
    """Tests for handle_self_destruct."""

    def test_returns_error_if_no_ships_with_ability(self):
        """Returns error when no ships have SelfDestruct ability."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=[])
        fleet.capabilities.ships_with_ability.return_value = []

        result = ops.handle_self_destruct(fleet)
        assert result['type'] == 'error'
        assert 'Self-Destruct Device' in result['message']

    def test_returns_prompt_when_ships_found(self):
        """Returns prompt when ships with SelfDestruct found."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        fleet = make_mock_fleet(abilities=["SelfDestruct"])
        mock_ship = MagicMock(id=123)
        fleet.capabilities.ships_with_ability.return_value = [mock_ship]

        result = ops.handle_self_destruct(fleet)
        assert result['type'] == 'prompt'

    def test_returns_none_if_no_fleet(self):
        """Returns None when no fleet provided."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        result = ops.handle_self_destruct(None)
        assert result is None


class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_system_at_hex_delegates_to_pathfinding(self):
        """_get_system_at_hex delegates to pathfinding module."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations
        from game.core.hex_math import HexCoord

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        mock_system = MagicMock()
        with patch(
            'game.strategy.data.pathfinding.get_system_at_hex',
            return_value=mock_system
        ) as mock_func:
            result = ops._get_system_at_hex(HexCoord(1, 2))
            mock_func.assert_called_once_with(scene.galaxy, HexCoord(1, 2))
            assert result is mock_system

    def test_get_warp_point_at_hex_returns_matching_warp_point(self):
        """_get_warp_point_at_hex returns warp point at the hex."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations
        from game.core.hex_math import HexCoord

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        # Create mock system with warp point
        mock_system = MagicMock()
        mock_system.global_location = HexCoord(10, 10)
        mock_wp = MagicMock()
        mock_wp.location = HexCoord(0, 0)  # Local position
        mock_wp.destination_id = "Alpha"
        mock_system.warp_points = [mock_wp]

        with patch.object(ops, '_get_system_at_hex', return_value=mock_system):
            result = ops._get_warp_point_at_hex(HexCoord(10, 10))
            assert result is mock_wp

    def test_get_warp_point_at_hex_returns_none_if_no_system(self):
        """_get_warp_point_at_hex returns None if no system at hex."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations
        from game.core.hex_math import HexCoord

        scene = make_mock_scene()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        with patch.object(ops, '_get_system_at_hex', return_value=None):
            result = ops._get_warp_point_at_hex(HexCoord(10, 10))
            assert result is None


class TestConfirmationDialogs:
    """Tests for confirmation dialog helpers."""

    def test_show_confirmation_calls_ui_dialog(self):
        """_show_confirmation calls UI's show_confirmation_dialog."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        scene.ui.show_confirmation_dialog = MagicMock()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        callback = MagicMock()
        ops._show_confirmation("Title", "Message", callback, is_warning=True)

        scene.ui.show_confirmation_dialog.assert_called_once_with(
            "Title", "Message", callback, is_warning=True
        )

    def test_show_confirmation_fallback_executes_callback(self):
        """_show_confirmation executes callback if no dialog available."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        del scene.ui.show_confirmation_dialog  # Remove method
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        callback = MagicMock()
        ops._show_confirmation("Title", "Message", callback)

        callback.assert_called_once()

    def test_show_system_picker_calls_ui_method(self):
        """_show_system_picker calls UI's show_system_picker."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        scene.ui.show_system_picker = MagicMock()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        systems = [MagicMock(name="Alpha"), MagicMock(name="Beta")]
        current = MagicMock()
        callback = MagicMock()

        ops._show_system_picker(systems, current, callback)

        scene.ui.show_system_picker.assert_called_once_with(systems, current, callback)

    def test_show_ship_picker_calls_ui_method(self):
        """_show_ship_picker calls UI's show_ship_picker."""
        from game.ui.screens.strategy_superweapons import SuperweaponOperations

        scene = make_mock_scene()
        scene.ui.show_ship_picker = MagicMock()
        facade = make_mock_facade()
        ops = SuperweaponOperations(scene, facade)

        ships = [MagicMock(id=1), MagicMock(id=2)]
        callback = MagicMock()

        ops._show_ship_picker(ships, "SelfDestruct", callback)

        scene.ui.show_ship_picker.assert_called_once_with(ships, "SelfDestruct", callback)
