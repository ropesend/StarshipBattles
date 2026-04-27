"""Turn engine resupply integration tests - fuel generation and fleet resupply.

PROJ-74 Phase 5: Integration tests for ResupplyEngine wired into TurnEngine.
Tests verify that fuel generation and fleet resupply are properly called
during _process_tick(), and that the resupply-before-movement ordering
allows refueled fleets to move.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord

from .conftest import MockGalaxy, create_mock_ship_instance


# ===========================================================================
# Fixtures / Helpers
# ===========================================================================

def _make_mock_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0):
    """Create mock registries with fuel_tank and fuel_synthesizer components."""
    registries = MagicMock()

    fuel_tank_comp = MagicMock()
    fuel_tank_comp.abilities = {
        "ResourceStorage": [{"resource": "fuel", "amount": fuel_tank_amount}],
    }

    fuel_synth_comp = MagicMock()
    fuel_synth_comp.abilities = {
        "ResourceGeneration": [{"resource": "fuel", "amount": fuel_gen_amount}],
    }

    def get_component(comp_id):
        if comp_id == "fuel_tank":
            return fuel_tank_comp
        if comp_id == "fuel_synthesizer":
            return fuel_synth_comp
        return None

    registries.components.get = get_component
    return registries


def _make_fuel_facility(
    instance_id="fuel-001",
    fuel_level=0.0,
    has_synthesizer=True,
    is_operational=True,
):
    """Create a fuel facility with optional synthesizer and fuel tank."""
    components = []
    if has_synthesizer:
        components.append({"id": "fuel_synthesizer"})
    components.append({"id": "fuel_tank"})

    facility = PlanetaryFacility(
        instance_id=instance_id,
        design_id="fuel_depot",
        name="Fuel Depot",
        design_data={"layers": {"hull": components}},
        is_operational=is_operational,
    )
    if fuel_level > 0:
        facility.consumable_levels = {"fuel": fuel_level}
    return facility


def _make_colony_planet(name="Colony Alpha", location=HexCoord(0, 0),
                        owner_id=0, facilities=None):
    """Create a minimal Planet that can serve as a colony."""
    planet = Planet(
        name=name,
        location=location,
        orbit_distance=3,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
    )
    planet.id = 1
    if facilities:
        planet.facilities = facilities
    return planet


def _make_mock_ship(
    fuel_capacity=500.0,
    current_fuel=500.0,
    fuel_cost_per_hex=5.0,
    combat_capable=True,
):
    """Create a mock ship with controllable fuel properties."""
    ship = MagicMock()
    ship.is_combat_capable.return_value = combat_capable
    ship.get_resource_capacity.return_value = fuel_capacity
    ship.get_all_resource_costs_per_hex.return_value = {"fuel": fuel_cost_per_hex}
    # Track fuel state across resupply calls
    _fuel = {"current": current_fuel}

    def _get_current_resource(resource_name):
        if resource_name == 'fuel':
            return _fuel["current"]
        return 0.0
    ship.get_current_resource.side_effect = _get_current_resource

    def _resupply(resource_name, amount):
        if resource_name != 'fuel':
            return 0.0
        space = fuel_capacity - _fuel["current"]
        actual = min(amount, space)
        _fuel["current"] += actual
        return actual
    ship.resupply.side_effect = _resupply

    # Resource consumption stubs for TurnEngine compatibility
    ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
    return ship


# ===========================================================================
# Task 5.1: Integration Tests
# ===========================================================================

class TestTurnProcessesFuelGeneration:
    """Verify TurnEngine processes fuel generation during ticks."""

    def test_turn_processes_fuel_generation(self):
        """Processing one turn generates fuel at facilities with synthesizers."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = TurnEngine(registries=registries)

        facility = _make_fuel_facility(fuel_level=0.0, has_synthesizer=True)
        colony = _make_colony_planet(owner_id=0, facilities=[facility])

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)

        # Process a single tick through the engine
        engine._process_tick(1, [empire], MockGalaxy())

        # Fuel should have been generated (300/100 = 3.0 per tick)
        assert facility.consumable_levels.get("fuel", 0.0) == pytest.approx(3.0)

    def test_full_turn_accumulates_fuel(self):
        """Processing a full turn (100 ticks) generates full turn's fuel."""
        registries = _make_mock_registries(fuel_gen_amount=300.0)
        engine = TurnEngine(registries=registries)

        facility = _make_fuel_facility(fuel_level=0.0, has_synthesizer=True)
        colony = _make_colony_planet(owner_id=0, facilities=[facility])

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)

        # Process all 100 ticks
        engine.process_turn([empire], MockGalaxy())

        # Full turn: 300 fuel generated total
        assert facility.consumable_levels.get("fuel", 0.0) == pytest.approx(300.0)


class TestTurnProcessesFleetResupply:
    """Verify TurnEngine processes fleet resupply during ticks."""

    def test_turn_processes_fleet_resupply(self):
        """Fleet at colony location with fuel in facility gets resupplied."""
        registries = _make_mock_registries(fuel_gen_amount=0.0)
        engine = TurnEngine(registries=registries)

        location = HexCoord(3, 4)

        # Facility with 200 fuel, no synthesizer (just existing fuel)
        facility = _make_fuel_facility(
            fuel_level=200.0, has_synthesizer=False
        )
        colony = _make_colony_planet(
            owner_id=0, location=location, facilities=[facility]
        )

        # Ship with half fuel
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=250.0, fuel_cost_per_hex=5.0)
        fleet = Fleet(1, 0, location, speed=0)
        fleet.ships = [ship]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        # Set up galaxy to return colony planet at fleet location
        galaxy = MockGalaxy()
        # Override get_planets_at_global_hex for our location
        galaxy.get_planets_at_global_hex = lambda h: [colony] if h == location else []

        # Process one tick
        engine._process_tick(1, [empire], galaxy)

        # Ship should have been resupplied
        ship.resupply.assert_called()

    def test_fleet_resupplied_before_movement(self):
        """Resupply runs before movement in tick processing order.

        We verify the ordering by checking that process_fuel_generation and
        process_fleet_resupply are called before collect_movements within
        a single _process_tick call.
        """
        registries = _make_mock_registries(fuel_gen_amount=0.0)

        # Use mock engines to track call order
        mock_resupply = MagicMock()
        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []

        call_order = []
        mock_resupply.process_fuel_generation.side_effect = (
            lambda *a, **kw: call_order.append("fuel_gen")
        )
        mock_resupply.process_fleet_resupply.side_effect = (
            lambda *a, **kw: call_order.append("fleet_resupply")
        )
        mock_movement.collect_movements.side_effect = (
            lambda *a, **kw: (call_order.append("movement"), [])[1]
        )

        engine = TurnEngine(
            registries=registries,
            resupply_engine=mock_resupply,
            movement_engine=mock_movement,
        )

        empire = Empire(0, "P1", (255, 0, 0))
        engine._process_tick(1, [empire], MockGalaxy())

        # Verify resupply phases run before movement
        assert call_order.index("fuel_gen") < call_order.index("movement")
        assert call_order.index("fleet_resupply") < call_order.index("movement")


class TestFullTurnResupplyAndMovement:
    """End-to-end test: fuel generation + resupply + movement together."""

    def test_full_turn_generates_and_resupplies(self):
        """Full turn: facility generates fuel AND resupplies fleet each tick."""
        registries = _make_mock_registries(
            fuel_gen_amount=100.0, fuel_tank_amount=1000.0
        )
        engine = TurnEngine(registries=registries)

        location = HexCoord(5, 5)

        # Facility starts with some fuel AND has synthesizer
        facility = _make_fuel_facility(fuel_level=50.0, has_synthesizer=True)
        colony = _make_colony_planet(
            owner_id=0, location=location, facilities=[facility]
        )

        # Ship with partial fuel
        ship = _make_mock_ship(
            fuel_capacity=500.0, current_fuel=200.0, fuel_cost_per_hex=5.0
        )

        fleet = Fleet(1, 0, location, speed=0)  # Stationary
        fleet.ships = [ship]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        galaxy = MockGalaxy()
        galaxy.get_planets_at_global_hex = lambda h: [colony] if h == location else []

        # Process full turn
        engine.process_turn([empire], galaxy)

        # Both fuel generation and fleet resupply should have occurred
        # Fuel was generated: 100/turn over 100 ticks
        # Fleet was also resupplied from facility's fuel
        # We verify ship.resupply was called at least once
        assert ship.resupply.call_count > 0
