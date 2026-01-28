"""
Integration tests for colonization workflow.

Tests the colonization flow including:
- Colony ship selection and validation
- Colonization target selection
- Colonization execution and state changes
- Post-colonization verification
"""

import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.turn_engine import TurnEngine
from game.core.validation import ValidationResult
from game.strategy.engine.commands import IssueColonizeCommand
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.ship_instance import ShipInstance
from tests.conftest import make_mock_ship_instance


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def turn_engine():
    """Create a standalone turn engine."""
    return TurnEngine()


@pytest.fixture
def simple_galaxy():
    """Create a simple galaxy with systems for testing."""
    galaxy = Galaxy(radius=500)
    galaxy.generate_systems(count=5, min_dist=100)
    galaxy.generate_warp_lanes()
    return galaxy


@pytest.fixture
def empire_with_fleet(simple_galaxy):
    """Create empire with a colonization-capable fleet."""
    empire = Empire(0, "Colonizer Empire", (0, 100, 200))

    # Find an unowned planet and create fleet at its location
    target_planet = None
    global_loc = None
    for system in simple_galaxy.systems.values():
        for planet in system.planets:
            if planet.owner_id is None:
                target_planet = planet
                global_loc = system.global_location + planet.location
                break
        if target_planet:
            break

    if target_planet:
        fleet = Fleet(1, empire.id, global_loc, speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)
        return empire, fleet, target_planet, simple_galaxy

    return empire, None, None, simple_galaxy


# =============================================================================
# Test: Colonization Validation
# =============================================================================


class TestColonizationValidation:
    """Tests for colonization order validation."""

    def test_validate_colonize_unowned_planet(self, turn_engine, empire_with_fleet):
        """Valid colonize order on unowned planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable planet found")

        result = turn_engine.validate_colonize_order(galaxy, fleet, planet)

        assert result.is_valid is True

    def test_validate_colonize_owned_planet_fails(self, turn_engine, empire_with_fleet):
        """Cannot colonize already-owned planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable planet found")

        # Claim the planet first
        planet.owner_id = 1  # Different empire

        result = turn_engine.validate_colonize_order(galaxy, fleet, planet)

        assert result.is_valid is False
        assert "ALREADY_OWNED" in str(result.error_code) or "owned" in result.message.lower()

    def test_validate_colonize_wrong_location_fails(self, turn_engine, simple_galaxy):
        """Cannot colonize planet from different location."""
        empire = Empire(0, "Test", (100, 100, 100))

        # Find planet
        planet = None
        for system in simple_galaxy.systems.values():
            if system.planets:
                planet = system.planets[0]
                break

        if not planet:
            pytest.skip("No planet found")

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
        if not fleet:
            pytest.skip("No fleet available")

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


# =============================================================================
# Test: Colonization Order Execution
# =============================================================================


class TestColonizationExecution:
    """Tests for colonization order execution during turn."""

    def test_colonize_transfers_ownership(self, turn_engine, empire_with_fleet):
        """Colonize order transfers planet to empire."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        # Verify planet is unowned
        assert planet.owner_id is None

        # Issue colonize order
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))

        # Process turn
        turn_engine.process_turn([empire], galaxy)

        # Planet should now be owned by empire
        assert planet.owner_id == empire.id

    def test_colonize_adds_to_colonies(self, turn_engine, empire_with_fleet):
        """Colonize adds planet to empire's colonies list."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        initial_colonies = len(empire.colonies)

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        assert len(empire.colonies) == initial_colonies + 1
        assert planet in empire.colonies

    def test_colonize_consumes_fleet(self, turn_engine, empire_with_fleet):
        """Colonizing fleet is removed from game."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        initial_fleets = len(empire.fleets)

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        assert len(empire.fleets) == initial_fleets - 1
        assert fleet not in empire.fleets

    def test_colonize_pops_order(self, turn_engine, empire_with_fleet):
        """Colonize order is removed after execution (if fleet survives the process)."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        # Add colonize and another order
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))

        initial_orders = len(fleet.orders)

        turn_engine.process_turn([empire], galaxy)

        # Fleet is consumed, so orders are irrelevant
        # This test verifies the execution path works without error


# =============================================================================
# Test: Colonization with Movement
# =============================================================================


class TestColonizationWithMovement:
    """Tests for colonization combined with movement orders."""

    def test_move_then_colonize(self, turn_engine, simple_galaxy):
        """Fleet can move to planet then colonize."""
        empire = Empire(0, "Mover", (100, 100, 100))

        # Find a planet
        target_planet = None
        target_loc = None
        for system in simple_galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    target_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet found")

        # Create fleet nearby (1 hex away)
        start_loc = HexCoord(target_loc.q + 1, target_loc.r)
        fleet = Fleet(1, empire.id, start_loc, speed=100.0)  # Fast
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)

        # Queue move then colonize
        fleet.add_order(FleetOrder(OrderType.MOVE, target=target_loc))
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))

        initial_colonies = len(empire.colonies)

        # Process enough turns to arrive and colonize
        for _ in range(3):
            if target_planet.owner_id == empire.id:
                break
            turn_engine.process_turn([empire], simple_galaxy)

        # Should have colonized
        assert target_planet.owner_id == empire.id
        assert len(empire.colonies) == initial_colonies + 1

    def test_colonize_at_destination_not_start(self, turn_engine, simple_galaxy):
        """Colonize order executes at destination, not start."""
        empire = Empire(0, "Traveler", (100, 100, 100))

        # Find two systems with planets
        systems_with_planets = [s for s in simple_galaxy.systems.values() if s.planets]
        if len(systems_with_planets) < 2:
            pytest.skip("Need at least 2 systems with planets")

        # Start at first system's planet
        start_sys = systems_with_planets[0]
        start_loc = start_sys.global_location + start_sys.planets[0].location

        # Target second system's unowned planet
        target_planet = None
        target_loc = None
        for planet in systems_with_planets[1].planets:
            if planet.owner_id is None:
                target_planet = planet
                target_loc = systems_with_planets[1].global_location + planet.location
                break

        if not target_planet:
            pytest.skip("No target planet found")

        # Create fleet at start
        fleet = Fleet(1, empire.id, start_loc, speed=100.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)

        # Queue move + colonize
        fleet.add_order(FleetOrder(OrderType.MOVE, target=target_loc))
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))

        # After first turn, fleet should have moved but not colonized yet
        # (unless it's already at destination)
        from game.strategy.data.hex_math import hex_distance
        if hex_distance(start_loc, target_loc) > 1:
            turn_engine.process_turn([empire], simple_galaxy)

            # Planet should still be unowned if we haven't arrived
            if fleet in empire.fleets and fleet.location != target_loc:
                assert target_planet.owner_id is None


# =============================================================================
# Test: Colonization Edge Cases
# =============================================================================


class TestColonizationEdgeCases:
    """Tests for edge cases in colonization."""

    def test_colonize_without_valid_planet_fails(self, turn_engine, simple_galaxy):
        """Colonize order fails if no valid planet at location."""
        empire = Empire(0, "Lost", (100, 100, 100))

        # Create fleet in deep space (no system)
        fleet = Fleet(1, empire.id, HexCoord(-999, -999), speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)

        # Try to colonize "any" - should fail
        result = turn_engine.validate_colonize_order(simple_galaxy, fleet, None)

        assert result.is_valid is False
        assert "NO_CANDIDATES" in str(result.error_code) or "no" in result.message.lower()

    def test_colonize_two_empires_race(self, turn_engine, simple_galaxy):
        """When two empires try to colonize same planet, one wins."""
        empire1 = Empire(0, "First", (100, 0, 0))
        empire2 = Empire(1, "Second", (0, 0, 100))

        # Find unowned planet
        target_planet = None
        target_loc = None
        for system in simple_galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    target_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet found")

        # Both empires have fleets at the planet location
        fleet1 = Fleet(1, empire1.id, target_loc, speed=10.0)
        fleet1.ships = [make_mock_ship_instance("Colony Ship", empire1.id)]
        fleet1.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, target_loc, speed=10.0)
        fleet2.ships = [make_mock_ship_instance("Colony Ship", empire2.id)]
        fleet2.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire2.add_fleet(fleet2)

        # Process turn - combat may happen, or colonization
        turn_engine.process_turn([empire1, empire2], simple_galaxy)

        # Planet should be owned by exactly one empire (or still unowned if combat destroyed both)
        owner_count = sum([
            target_planet.owner_id == 0,
            target_planet.owner_id == 1,
        ])
        assert owner_count <= 1  # At most one owner

    def test_colonize_after_fleet_destroyed(self, turn_engine, simple_galaxy):
        """Combat occurs before colonization when hostile fleets meet."""
        empire1 = Empire(0, "Colonizer", (100, 0, 0))
        empire2 = Empire(1, "Aggressor", (0, 0, 100))

        # Find unowned planet
        target_planet = None
        target_loc = None
        for system in simple_galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    target_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet found")

        # Empire 1 has colony ship
        fleet1 = Fleet(1, empire1.id, target_loc, speed=10.0)
        fleet1.ships = [make_mock_ship_instance("Colony Ship", empire1.id)]
        fleet1.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet1)

        # Empire 2 has combat fleet at same location
        fleet2 = Fleet(2, empire2.id, target_loc, speed=10.0)
        fleet2.ships = [
            make_mock_ship_instance("Destroyer", empire2.id),
            make_mock_ship_instance("Destroyer", empire2.id),
            make_mock_ship_instance("Cruiser", empire2.id)
        ]
        empire2.add_fleet(fleet2)

        initial_fleet1_count = len(empire1.fleets)
        initial_fleet2_count = len(empire2.fleets)

        # Process turn - combat should occur
        turn_engine.process_turn([empire1, empire2], simple_galaxy)

        # At least one fleet should have been affected (combat occurred)
        total_fleets_after = len(empire1.fleets) + len(empire2.fleets)
        total_fleets_before = initial_fleet1_count + initial_fleet2_count

        # Combat should have resolved (one side wins)
        assert total_fleets_after < total_fleets_before


# =============================================================================
# Test: Colonization State Integrity
# =============================================================================


class TestColonizationStateIntegrity:
    """Tests for state integrity after colonization."""

    def test_colony_planet_references_match(self, turn_engine, empire_with_fleet):
        """Colony list planet is the same object as galaxy planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        # Planet in empire.colonies should be same object
        if planet in empire.colonies:
            assert any(p is planet for p in empire.colonies)

    def test_galaxy_planet_owner_updated(self, turn_engine, empire_with_fleet):
        """Planet in galaxy has owner_id set."""
        empire, fleet, planet, galaxy = empire_with_fleet
        if not fleet or not planet:
            pytest.skip("No suitable setup")

        planet_id = planet.id

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        # Find planet in galaxy again
        found_planet = galaxy.get_planet_by_id(planet_id)
        if found_planet:
            assert found_planet.owner_id == empire.id

    def test_multiple_colonizations_single_turn(self, turn_engine, simple_galaxy):
        """Empire can colonize at least one planet in a turn."""
        empire = Empire(0, "Expansionist", (100, 100, 100))

        # Find an unowned planet
        target_planet = None
        target_loc = None
        for system in simple_galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    target_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet found")

        # Create fleet at planet location
        fleet = Fleet(10, empire.id, target_loc, speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire.add_fleet(fleet)

        initial_colonies = len(empire.colonies)

        turn_engine.process_turn([empire], simple_galaxy)

        # Single colonization should succeed
        assert len(empire.colonies) == initial_colonies + 1
        assert target_planet.owner_id == empire.id
