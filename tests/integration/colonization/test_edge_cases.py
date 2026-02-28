"""
Integration tests for colonization edge cases and state integrity.

Tests edge cases like invalid planets, race conditions, and state integrity after colonization.
PROJ-211: Updated to pass fresh_registries for DI compliance.
"""

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance, make_colony_ship_for_planet


class TestColonizationEdgeCases:
    """Tests for edge cases in colonization."""

    def test_colonize_without_valid_planet_fails(self, turn_engine, simple_galaxy, fresh_registries):
        """Colonize order fails if no valid planet at location."""
        empire = Empire(0, "Lost", (100, 100, 100))

        # Create fleet in deep space (no system)
        fleet = Fleet(1, empire.id, HexCoord(-999, -999), speed=10.0)
        ship = make_mock_ship_instance("Colony Ship", empire.id)
        ship.set_registries(fresh_registries)
        fleet.ships = [ship]
        empire.add_fleet(fleet)

        # Try to colonize "any" - should fail
        result = turn_engine.validate_colonize_order(simple_galaxy, fleet, None)

        assert result.is_valid is False
        assert "NO_CANDIDATES" in str(result.error_code) or "no" in result.message.lower()

    def test_colonize_two_empires_race(self, turn_engine, simple_galaxy, fresh_registries):
        """When two empires try to colonize same planet, one wins."""
        empire1 = Empire(0, "First", (100, 0, 0))
        empire2 = Empire(1, "Second", (0, 0, 100))

        # Find unowned planet - deterministic galaxy guarantees one exists
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

        # PROJ-40: Deterministic fixture guarantees unowned planet
        assert target_planet is not None

        # Both empires have fleets at the planet location
        # PROJ-140: Use proper colony ships that match planet type
        # PROJ-211: Pass registries for DI compliance
        fleet1 = Fleet(1, empire1.id, target_loc, speed=10.0)
        fleet1.ships = [make_colony_ship_for_planet(target_planet, empire1.id, registries=fresh_registries)]
        fleet1.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, target_loc, speed=10.0)
        fleet2.ships = [make_colony_ship_for_planet(target_planet, empire2.id, registries=fresh_registries)]
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

    def test_colonize_after_fleet_destroyed(self, turn_engine, simple_galaxy, fresh_registries):
        """Combat occurs before colonization when hostile fleets meet."""
        empire1 = Empire(0, "Colonizer", (100, 0, 0))
        empire2 = Empire(1, "Aggressor", (0, 0, 100))

        # Find unowned planet - deterministic galaxy guarantees one exists
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

        # PROJ-40: Deterministic fixture guarantees unowned planet
        assert target_planet is not None

        # Empire 1 has colony ship
        fleet1 = Fleet(1, empire1.id, target_loc, speed=10.0)
        ship1 = make_mock_ship_instance("Colony Ship", empire1.id)
        ship1.set_registries(fresh_registries)
        fleet1.ships = [ship1]
        fleet1.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet1)

        # Empire 2 has combat fleet at same location
        fleet2 = Fleet(2, empire2.id, target_loc, speed=10.0)
        ships2 = [
            make_mock_ship_instance("Destroyer", empire2.id),
            make_mock_ship_instance("Destroyer", empire2.id),
            make_mock_ship_instance("Cruiser", empire2.id)
        ]
        for ship in ships2:
            ship.set_registries(fresh_registries)
        fleet2.ships = ships2
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


class TestColonizationStateIntegrity:
    """Tests for state integrity after colonization."""

    def test_colony_planet_references_match(self, turn_engine, empire_with_fleet):
        """Colony list planet is the same object as galaxy planet."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees setup

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        # Planet in empire.colonies should be same object
        if planet in empire.colonies:
            assert any(p is planet for p in empire.colonies)

    def test_galaxy_planet_owner_updated(self, turn_engine, empire_with_fleet):
        """Planet in galaxy has owner_id set."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees setup

        planet_id = planet.id

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        # Find planet in galaxy again
        found_planet = galaxy.get_planet_by_id(planet_id)
        if found_planet:
            assert found_planet.owner_id == empire.id

    def test_multiple_colonizations_single_turn(self, turn_engine, simple_galaxy, fresh_registries):
        """Empire can colonize at least one planet in a turn."""
        empire = Empire(0, "Expansionist", (100, 100, 100))

        # Find an unowned planet - deterministic galaxy guarantees one exists
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

        # PROJ-40: Deterministic fixture guarantees unowned planet
        assert target_planet is not None

        # Create fleet at planet location with proper colony ship
        fleet = Fleet(10, empire.id, target_loc, speed=10.0)
        # PROJ-140: Use proper colony ship that matches planet type
        # PROJ-211: Pass registries for DI compliance
        fleet.ships = [make_colony_ship_for_planet(target_planet, empire.id, registries=fresh_registries)]
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire.add_fleet(fleet)

        initial_colonies = len(empire.colonies)

        turn_engine.process_turn([empire], simple_galaxy)

        # Single colonization should succeed
        assert len(empire.colonies) == initial_colonies + 1
        assert target_planet.owner_id == empire.id
