"""
Integration tests for colonization validation.

Tests validation of colonize orders including ownership checks and location validation.
"""

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance


class TestColonizationValidation:
    """Tests for colonization order validation."""

    def test_validate_colonize_unowned_planet(self, turn_engine, empire_with_fleet):
        """Valid colonize order on unowned planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees fleet and planet exist

        result = turn_engine.validate_colonize_order(galaxy, fleet, planet)

        assert result.is_valid is True

    def test_validate_colonize_owned_planet_fails(self, turn_engine, empire_with_fleet):
        """Cannot colonize already-owned planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees fleet and planet exist

        # Claim the planet first
        planet.owner_id = 1  # Different empire

        result = turn_engine.validate_colonize_order(galaxy, fleet, planet)

        assert result.is_valid is False
        assert "ALREADY_OWNED" in str(result.error_code) or "owned" in result.message.lower()

    def test_validate_colonize_wrong_location_fails(self, turn_engine, simple_galaxy):
        """Cannot colonize planet from different location."""
        empire = Empire(0, "Test", (100, 100, 100))

        # Find planet - deterministic galaxy guarantees planets exist
        planet = None
        for system in simple_galaxy.systems.values():
            if system.planets:
                planet = system.planets[0]
                break

        # PROJ-40: Deterministic fixture guarantees at least one planet
        assert planet is not None

        # Create fleet at different location (far away)
        fleet = Fleet(1, empire.id, HexCoord(-1000, -1000), speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)

        result = turn_engine.validate_colonize_order(simple_galaxy, fleet, planet)

        assert result.is_valid is False
        assert "WRONG_LOCATION" in str(result.error_code) or "location" in result.message.lower()

    def test_validate_colonize_any_planet(self, turn_engine, empire_with_fleet):
        """Validate colonize order with 'Any' planet (None target)."""
        empire, fleet, _, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees fleet exists

        # Pass None for "any planet at location"
        result = turn_engine.validate_colonize_order(galaxy, fleet, None)

        # Should find a valid candidate
        assert result.is_valid is True

    def test_validate_colonize_no_fleet_fails(self, turn_engine, simple_galaxy):
        """Validation fails when fleet is None."""
        planet = None
        for system in simple_galaxy.systems.values():
            if system.planets:
                planet = system.planets[0]
                break

        result = turn_engine.validate_colonize_order(simple_galaxy, None, planet)

        assert result.is_valid is False
        assert "fleet" in result.message.lower()
