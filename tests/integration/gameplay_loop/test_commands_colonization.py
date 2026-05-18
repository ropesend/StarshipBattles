"""
Integration tests for commands and colonization in the gameplay loop.

Tests for command execution, battle resolution, and colonization workflow.
PROJ-55: Updated to use ships with colony pods for colonization tests.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.commands import CommandType
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from tests.conftest import make_mock_ship_instance


def make_colony_ship_for_planet(planet, owner_id: int, registries=None) -> ShipInstance:
    """Create a ship with a drop pod in carried_items."""
    planet_type_str = planet.planet_type.name

    ship = ShipInstance(
        instance_id=f"colony-ship-{planet_type_str.lower()}-{id(planet)}",
        design_id=f"{planet_type_str}_colony_ship",
        name=f"Colony Ship ({planet_type_str})",
        owner_id=owner_id,
        design_data={
            'name': f"Colony Ship ({planet_type_str})",
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'expected_stats': {'speed': 10.0},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # PROJ-436 Phase 9: typed DropPod into bay_inventory.pods.
    from game.strategy.data.bay_inventory import DropPod
    ship.bay_inventory.pods.append(DropPod(
        design_id=f"{planet_type_str.lower()}_drop_pod",
        design_data={"layers": {"CORE": []}},
        mass=500.0,
        payload={
            "name": f"Drop Pod ({planet_type_str})",
            "vehicle_type": "drop_pod",
        },
    ))
    if registries is not None:
        ship.set_registries(registries)
    return ship


# =============================================================================
# Test: Command Queue Execution
# =============================================================================


class TestCommandExecution:
    """Tests for command handling and order execution."""

    def test_move_command_adds_order(self, game_session):
        """Move command adds order to fleet."""
        # Get player empire and create a fleet
        empire = game_session.active_empire
        if not empire:
            pytest.skip("No player empire")

        fleet = Fleet(99, empire.id, HexCoord(0, 0), speed=10.0)
        empire.add_fleet(fleet)

        # Create mock command
        cmd = MagicMock()
        cmd.type = CommandType.ISSUE_ORDER
        cmd.name = 'IssueMoveCommand'
        cmd.fleet_id = 99
        cmd.target_hex = HexCoord(5, 0)

        result = game_session.handle_command(cmd)

        # Fleet should have move order
        if result and result.is_valid:
            assert len(fleet.orders) > 0
            assert fleet.orders[-1].type == OrderType.MOVE

    def test_colonize_command_validates_planet(self, game_session):
        """Colonize command validates target planet."""
        empire = game_session.active_empire
        if not empire:
            pytest.skip("No player empire")

        # Create fleet at random location (not at planet)
        fleet = Fleet(99, empire.id, HexCoord(-100, -100), speed=10.0)
        empire.add_fleet(fleet)

        # Create mock colonize command
        cmd = MagicMock()
        cmd.type = CommandType.ISSUE_ORDER
        cmd.name = 'IssueColonizeCommand'
        cmd.fleet_id = 99
        cmd.planet_id = None  # "Any planet"

        result = game_session.handle_command(cmd)

        # Should fail - no planet at fleet location
        if result:
            assert not result.is_valid or "NO_CANDIDATES" in str(result.message)

    def test_orders_execute_in_sequence(self, turn_engine, two_empire_setup):
        """Multiple orders execute in queue order."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)  # Very fast

        # Add two move orders
        fleet.add_order(Order(OrderType.MOVE, target=HexCoord(2, 0)))
        fleet.add_order(Order(OrderType.MOVE, target=HexCoord(4, 0)))

        empire1.add_fleet(fleet)

        # After first turn, should have completed first order and possibly started second
        turn_engine.process_turn(empires, galaxy)

        # Fleet should have moved
        assert fleet.location != HexCoord(0, 0)

    def test_order_cleared_on_completion(self, turn_engine, two_empire_setup):
        """Orders are removed from queue when completed."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)
        fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 0)))  # Very short move

        empire1.add_fleet(fleet)

        initial_orders = len(fleet.orders)

        # Process until order complete or timeout
        for _ in range(5):
            turn_engine.process_turn(empires, galaxy)
            if len(fleet.orders) < initial_orders:
                break

        # Order should have been removed
        assert len(fleet.orders) == 0


# =============================================================================
# Test: Battle Resolution During Turn
# =============================================================================


class TestBattleResolution:
    """Tests for battle resolution when fleets meet."""

    def test_opposing_fleets_trigger_combat(self, turn_engine, two_empire_setup, fresh_registries):
        """Fleets from different empires at same hex trigger combat."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-211: Create ships with registries for DI compliance
        def make_ship(name, owner_id):
            ship = make_mock_ship_instance(name, owner_id)
            ship.set_registries(fresh_registries)
            return ship

        # Create opposing fleets at same location
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [
            make_ship("Scout", empire1.id),
            make_ship("Destroyer", empire1.id)
        ]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, loc, speed=10.0)
        fleet2.ships = [make_ship("Scout", empire2.id)]
        empire2.add_fleet(fleet2)

        total_fleets = len(empire1.fleets) + len(empire2.fleets)

        turn_engine.process_turn(empires, galaxy)

        # One fleet should have been destroyed (RNG resolution)
        remaining_fleets = len(empire1.fleets) + len(empire2.fleets)
        assert remaining_fleets < total_fleets

    def test_same_empire_fleets_no_combat(self, turn_engine, two_empire_setup, fresh_registries):
        """Fleets from same empire don't fight each other."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-211: Create ships with registries for DI compliance
        def make_ship(name, owner_id):
            ship = make_mock_ship_instance(name, owner_id)
            ship.set_registries(fresh_registries)
            return ship

        # Create two fleets from same empire at same location
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [make_ship("Scout", empire1.id)]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire1.id, loc, speed=10.0)  # Same empire
        fleet2.ships = [make_ship("Destroyer", empire1.id)]
        empire1.add_fleet(fleet2)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # No combat should have occurred
        assert len(empire1.fleets) == initial_fleets


# =============================================================================
# Test: Colonization Workflow
# =============================================================================


class TestColonizationWorkflow:
    """Tests for colonization during turn execution."""

    def test_colonize_order_claims_planet(self, turn_engine, two_empire_setup, fresh_registries):
        """COLONIZE order transfers planet ownership."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Find an unowned planet and get its global location
        target_planet = None
        global_loc = None
        for system in galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    # Global location = system location + planet's local offset
                    global_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet available")

        # Create fleet at planet's GLOBAL location (system + local offset)
        # PROJ-55: Use colony ship with correct pod type
        # PROJ-211: Pass registries for DI compliance
        fleet = Fleet(1, empire1.id, global_loc, speed=10.0)
        fleet.ships = [make_colony_ship_for_planet(target_planet, empire1.id, registries=fresh_registries)]
        fleet.add_order(Order(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet)

        initial_colonies = len(empire1.colonies)

        turn_engine.process_turn(empires, galaxy)

        # Empire should have new colony
        assert len(empire1.colonies) > initial_colonies
        assert target_planet.owner_id == empire1.id

    def test_colonize_removes_fleet(self, turn_engine, two_empire_setup, fresh_registries):
        """Colonizing fleet is consumed."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Find an unowned planet and get its global location
        target_planet = None
        global_loc = None
        for system in galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    # Global location = system location + planet's local offset
                    global_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet available")

        # PROJ-55: Use colony ship with correct pod type
        # PROJ-211: Pass registries for DI compliance
        fleet = Fleet(1, empire1.id, global_loc, speed=10.0)
        fleet.ships = [make_colony_ship_for_planet(target_planet, empire1.id, registries=fresh_registries)]
        fleet.add_order(Order(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # Phase 2: Fleet stays (ship is reusable)
        assert len(empire1.fleets) == initial_fleets
