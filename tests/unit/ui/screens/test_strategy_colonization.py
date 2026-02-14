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
        mock_dyson.diameter_hexes = 11.0

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
        mock_facade.can_colonize.return_value = mock_validation_result
        mock_facade.get_fleet_remaining_pods.return_value = {"DYSON_SPHERE": 1}

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
        mock_facade.get_fleet_remaining_pods.return_value = {}

        system = ColonizationSystem(mock_scene, mock_facade)
        system._get_system_at_hex = MagicMock(return_value=mock_system)

        result = system.on_colonize_click(mock_fleet)

        assert result is None
