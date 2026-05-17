"""
Tests for ColonizationSystem (strategy_colonization.py).

PROJ-139: Zone-aware colonization targeting.
"""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


class TestColonizationSystemZone:
    """Tests for zone-aware planet detection in ColonizationSystem."""

    def test_on_colonize_click_finds_dyson_sphere_via_zone(self):
        """Should find Dyson Sphere when fleet is in its zone."""
        from game.ui.screens.strategy_colonization import ColonizationSystem
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        # Create mock Dyson Sphere at center (0,0)
        mock_dyson = MagicMock()
        mock_dyson.id = 1
        mock_dyson.name = "Dyson Sphere"
        mock_dyson.location = HexCoord(0, 0)  # Local location in system
        mock_dyson.owner_id = None
        mock_dyson.planet_type = MockPlanetType.DYSON_SPHERE
        mock_dyson.radius_hexes = 6

        # Create mock system
        mock_system = MagicMock()
        mock_system.global_location = HexCoord(100, 100)
        mock_system.planets = [mock_dyson]

        # Fleet at zone hex (2, 0) - inside zone but not at center
        mock_fleet = MagicMock()
        mock_fleet.id = 1
        mock_fleet.location = HexCoord(102, 100)  # global = system (100,100) + local (2,0)

        # Create mock scene
        mock_scene = MagicMock()
        mock_scene.systems = [mock_system]

        # Mock galaxy with zone registry
        mock_galaxy = MagicMock()
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[mock_dyson])
        mock_scene.galaxy = mock_galaxy

        # Create mock facade
        mock_facade = MagicMock()
        # Validation passes for Dyson Sphere
        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = True
        mock_facade.validation.can_colonize.return_value = mock_validation_result
        mock_facade.fleets.remaining_pods.return_value = {"drop_pod": 1}

        # Create system
        system = ColonizationSystem(mock_scene, mock_facade)

        # Mock _get_system_at_hex to return our system
        system._get_system_at_hex = MagicMock(return_value=mock_system)

        # Execute
        result = system.on_colonize_click(mock_fleet)

        # Verify: Should find the Dyson Sphere as a candidate
        assert result is not None
        # Either prompt (multiple) or success (single)
        assert result['type'] in ('prompt', 'success')

    def test_on_colonize_click_no_zone_planets_found(self):
        """Should return None when no planets at fleet location or zone."""
        from game.ui.screens.strategy_colonization import ColonizationSystem

        # Empty system
        mock_system = MagicMock()
        mock_system.global_location = HexCoord(100, 100)
        mock_system.planets = []

        mock_fleet = MagicMock()
        mock_fleet.id = 1
        mock_fleet.location = HexCoord(102, 100)

        mock_scene = MagicMock()
        mock_scene.systems = [mock_system]

        mock_galaxy = MagicMock()
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[])
        mock_scene.galaxy = mock_galaxy

        mock_facade = MagicMock()
        mock_facade.fleets.remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = MagicMock(return_value=mock_system)

        result = system.on_colonize_click(mock_fleet)

        assert result is None


class TestHandleColonizeDesignation:
    """Tests for `handle_colonize_designation` (PROJ-398 / FND-017).

    Covers the screen-click colonize-designation entry point. Previously
    untested — `on_colonize_click` (fleet-location based) was tested but the
    screen-click variant that reads from `camera.hex_at_screen` was not.
    """

    @staticmethod
    def _build_system(planets: list, *, global_location: HexCoord = HexCoord(100, 100)):
        sys_mock = MagicMock()
        sys_mock.global_location = global_location
        sys_mock.planets = planets
        return sys_mock

    @staticmethod
    def _build_scene(*, galaxy=None):
        scene = MagicMock()
        scene.camera = MagicMock()
        scene.galaxy = galaxy
        scene.hex_size = 10
        return scene

    def _make_system_under_test(self, scene, system_at_hex):
        from game.ui.screens.strategy_colonization import ColonizationSystem

        facade = MagicMock()
        sut = ColonizationSystem(scene, facade)
        sut._get_system_at_hex = MagicMock(return_value=system_at_hex)
        return sut

    def test_returns_none_when_fleet_is_none(self):
        scene = self._build_scene()
        sut = self._make_system_under_test(scene, system_at_hex=None)

        assert sut.handle_colonize_designation(100, 200, None) is None

    def test_returns_none_when_no_system_at_target_hex(self):
        scene = self._build_scene()
        scene.camera.hex_at_screen.return_value = HexCoord(50, 50)
        sut = self._make_system_under_test(scene, system_at_hex=None)

        result = sut.handle_colonize_designation(10, 10, MagicMock(id=1))

        assert result is None
        scene.camera.hex_at_screen.assert_called_once_with(10, 10, 10)

    def test_returns_none_when_no_colonizable_planets_at_hex(self):
        # System has a planet, but it's owned (not colonizable) and at the wrong local hex.
        owned_planet = MagicMock()
        owned_planet.owner_id = 7
        owned_planet.location = HexCoord(0, 0)
        system = self._build_system([owned_planet])
        scene = self._build_scene(galaxy=None)
        scene.camera.hex_at_screen.return_value = HexCoord(105, 105)

        sut = self._make_system_under_test(scene, system_at_hex=system)

        assert sut.handle_colonize_designation(0, 0, MagicMock(id=1)) is None

    def test_returns_prompt_with_unowned_planet_at_hex(self):
        """Unowned planet whose local hex matches click resolves to a prompt."""
        target_global = HexCoord(105, 105)
        local = target_global - HexCoord(100, 100)  # = HexCoord(5, 5)

        unowned = MagicMock()
        unowned.owner_id = None
        unowned.location = local
        system = self._build_system([unowned])

        scene = self._build_scene(galaxy=None)
        scene.camera.hex_at_screen.return_value = target_global

        fleet = MagicMock(id=1)
        sut = self._make_system_under_test(scene, system_at_hex=system)

        result = sut.handle_colonize_designation(0, 0, fleet)

        assert result is not None
        assert result['type'] == 'prompt'
        assert unowned in result['planets']
        assert result['target_hex'] == target_global
        assert result['fleet'] is fleet
