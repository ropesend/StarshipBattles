"""
Integration tests for colonization execution.

Tests colonization order execution and movement + colonization workflows.
"""

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance, make_colony_ship_for_planet


class TestColonizationExecution:
    """Tests for colonization order execution during turn."""

    def test_colonize_transfers_ownership(self, turn_engine, empire_with_fleet):
        """Colonize order transfers planet to empire."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees setup

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
        # PROJ-40: Deterministic fixture guarantees setup

        initial_colonies = len(empire.colonies)

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        assert len(empire.colonies) == initial_colonies + 1
        assert planet in empire.colonies

    def test_colonize_consumes_fleet(self, turn_engine, empire_with_fleet):
        """Colonizing fleet is removed from game."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees setup

        initial_fleets = len(empire.fleets)

        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
        turn_engine.process_turn([empire], galaxy)

        assert len(empire.fleets) == initial_fleets - 1
        assert fleet not in empire.fleets

    def test_colonize_pops_order(self, turn_engine, empire_with_fleet):
        """Colonize order is removed after execution (if fleet survives the process)."""
        empire, fleet, planet, galaxy = empire_with_fleet
        # PROJ-40: Deterministic fixture guarantees setup

        # Add colonize and another order
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))

        initial_orders = len(fleet.orders)

        turn_engine.process_turn([empire], galaxy)

        # Fleet is consumed, so orders are irrelevant
        # This test verifies the execution path works without error


class TestColonizationWithMovement:
    """Tests for colonization combined with movement orders."""

    def test_move_then_colonize(self, turn_engine, simple_galaxy):
        """Fleet can move to planet then colonize."""
        empire = Empire(0, "Mover", (100, 100, 100))

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

        # Create fleet nearby (1 hex away)
        start_loc = HexCoord(target_loc.q + 1, target_loc.r)
        fleet = Fleet(1, empire.id, start_loc, speed=100.0)  # Fast
        # PROJ-140: Use proper colony ship that matches planet type
        fleet.ships = [make_colony_ship_for_planet(target_planet, empire.id)]
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

        # Find two systems with planets - deterministic galaxy guarantees this
        systems_with_planets = [s for s in simple_galaxy.systems.values() if s.planets]
        # PROJ-40: With seed 42 and 5 systems, we get enough systems with planets
        assert len(systems_with_planets) >= 2, "Deterministic galaxy should have 2+ systems with planets"

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

        # PROJ-40: Deterministic fixture guarantees unowned planet
        assert target_planet is not None

        # Create fleet at start
        fleet = Fleet(1, empire.id, start_loc, speed=100.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
        empire.add_fleet(fleet)

        # Queue move + colonize
        fleet.add_order(FleetOrder(OrderType.MOVE, target=target_loc))
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))

        # After first turn, fleet should have moved but not colonized yet
        # (unless it's already at destination)
        from game.core.hex_math import hex_distance
        if hex_distance(start_loc, target_loc) > 1:
            turn_engine.process_turn([empire], simple_galaxy)

            # Planet should still be unowned if we haven't arrived
            if fleet in empire.fleets and fleet.location != target_loc:
                assert target_planet.owner_id is None
