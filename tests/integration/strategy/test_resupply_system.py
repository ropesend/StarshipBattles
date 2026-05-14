"""End-to-end integration tests for the resupply system.

PROJ-74 Phase 6: Tests verify the complete fuel synthesis and resupply workflow
including fuel generation at facilities, fleet resupply with range equalization,
and multi-turn accumulation.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.engine.resupply_engine import ResupplyEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord


# ===========================================================================
# Helpers
# ===========================================================================

def _make_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0):
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


def _make_facility(
    instance_id="fuel-001",
    fuel_level=0.0,
    has_synthesizer=True,
    is_operational=True,
    fuel_tank_id="fuel_tank",
):
    """Create a fuel facility with optional synthesizer and fuel tank."""
    components = []
    if has_synthesizer:
        components.append({"id": "fuel_synthesizer"})
    components.append({"id": fuel_tank_id})

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


def _make_colony(name="Colony Alpha", location=HexCoord(0, 0),
                 owner_id=0, facilities=None):
    """Create a minimal Planet colony."""
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


class MockGalaxy:
    """Minimal galaxy mock for spatial lookup."""

    def __init__(self, planet_map=None):
        """
        Args:
            planet_map: Dict[HexCoord, List[Planet]] for spatial queries.
        """
        self._planet_map = planet_map or {}
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        return self._planet_map.get(global_hex, [])

    def get_zones_at_global_hex(self, global_hex):
        """Return empty list - no storms in this mock."""
        return []


def _make_mock_ship(
    fuel_capacity=500.0,
    current_fuel=500.0,
    fuel_cost_per_hex=5.0,
    combat_capable=True,
):
    """Create a mock ship with stateful fuel tracking."""
    ship = MagicMock()
    ship.is_combat_capable.return_value = combat_capable
    ship.get_resource_capacity.return_value = fuel_capacity
    ship.get_all_resource_costs_per_hex.return_value = {"fuel": fuel_cost_per_hex}

    _fuel = {"current": current_fuel}

    def _get_current_resource(resource_name):
        if resource_name == "fuel":
            return _fuel["current"]
        return 0.0
    ship.get_current_resource.side_effect = _get_current_resource

    def _resupply(resource_name, amount):
        if resource_name != "fuel":
            return 0.0
        space = fuel_capacity - _fuel["current"]
        actual = min(amount, space)
        _fuel["current"] += actual
        return actual
    ship.resupply.side_effect = _resupply

    ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
    return ship


# ===========================================================================
# Task 6.1: Complete Resupply Flow
# ===========================================================================

class TestCompleteResupplyFlow:
    """End-to-end test of fuel synthesis → storage → fleet resupply."""

    def test_complete_resupply_flow(self):
        """Full cycle: synthesizer generates fuel, facility stores it, fleet receives it."""
        # Setup: 300 fuel/turn synthesizer, 500 capacity tank
        registries = _make_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = build_test_turn_engine(registries)

        location = HexCoord(2, 3)

        # Facility starts empty, has synthesizer + tank
        facility = _make_facility(fuel_level=0.0, has_synthesizer=True)
        colony = _make_colony(owner_id=0, location=location, facilities=[facility])

        # Fleet with ship at 50% fuel (250/500)
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=250.0, fuel_cost_per_hex=5.0)
        fleet = Fleet(1, 0, location, speed=0)
        fleet.ships = [ship]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        galaxy = MockGalaxy(planet_map={location: [colony]})

        # Process a full turn (100 ticks)
        engine.process_turn([empire], galaxy)

        # Verify: ship was resupplied (resupply called at least once)
        assert ship.resupply.call_count > 0
        # Ship should have received fuel (more than starting 250)
        assert ship.get_current_resource('fuel') > 250.0

    def test_multi_turn_fuel_accumulation(self):
        """Fuel accumulates across multiple turns when no fleet is present."""
        registries = _make_registries(fuel_tank_amount=1000.0, fuel_gen_amount=200.0)
        engine = build_test_turn_engine(registries)

        facility = _make_facility(fuel_level=0.0, has_synthesizer=True)
        colony = _make_colony(owner_id=0, facilities=[facility])

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        # No fleet - fuel just accumulates

        galaxy = MockGalaxy()

        # Process 3 turns
        for _ in range(3):
            engine.process_turn([empire], galaxy)

        # 3 turns × 200 fuel/turn = 600 fuel accumulated
        assert facility.consumable_levels.get("fuel", 0) == pytest.approx(600.0)

    def test_fuel_capped_at_storage_capacity(self):
        """Fuel does not exceed facility storage capacity."""
        # Tank capacity 500, generation 300/turn
        registries = _make_registries(fuel_tank_amount=500.0, fuel_gen_amount=300.0)
        engine = build_test_turn_engine(registries)

        facility = _make_facility(fuel_level=0.0, has_synthesizer=True)
        colony = _make_colony(owner_id=0, facilities=[facility])

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)

        galaxy = MockGalaxy()

        # Process 3 turns (would be 900 fuel without cap, but tank is only 500)
        for _ in range(3):
            engine.process_turn([empire], galaxy)

        # Fuel should be capped at 500 (tank max)
        assert facility.consumable_levels.get("fuel", 0) == pytest.approx(500.0)

    def test_non_operational_facility_no_generation(self):
        """Non-operational facilities produce no fuel."""
        registries = _make_registries(fuel_gen_amount=300.0)
        engine = build_test_turn_engine(registries)

        facility = _make_facility(fuel_level=0.0, has_synthesizer=True, is_operational=False)
        colony = _make_colony(owner_id=0, facilities=[facility])

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)

        galaxy = MockGalaxy()
        engine.process_turn([empire], galaxy)

        assert facility.consumable_levels.get("fuel", 0) == pytest.approx(0.0)


# ===========================================================================
# Task 6.1: Range Equalization
# ===========================================================================

class TestRangeEqualization:
    """Verify range-equalization fuel distribution across fleet ships."""

    def test_range_equalization_two_ship_types(self):
        """Ships with different fuel costs get fuel to equalize range.

        Setup:
        - Ship A: capacity=500, current=100, cost_per_hex=10 (range=10 hexes)
        - Ship B: capacity=200, current=100, cost_per_hex=2  (range=50 hexes)
        - Facility: 400 fuel available

        After equalization:
        - Total fuel pool: 100 + 100 + 400 = 600
        - Total cost per hex: 10 + 2 = 12
        - Max equal range: 600 / 12 = 50 hexes
        - Ship A target: 50 * 10 = 500 (at capacity)
        - Ship B target: 50 * 2 = 100 (already has 100)
        - Ship A gets 400, Ship B gets 0
        """
        registries = _make_registries(fuel_gen_amount=0.0, fuel_tank_amount=1000.0)
        resupply_engine = ResupplyEngine(registries=registries)

        location = HexCoord(5, 5)

        facility = _make_facility(fuel_level=400.0, has_synthesizer=False)
        colony = _make_colony(owner_id=0, location=location, facilities=[facility])

        ship_a = _make_mock_ship(fuel_capacity=500.0, current_fuel=100.0, fuel_cost_per_hex=10.0)
        ship_b = _make_mock_ship(fuel_capacity=200.0, current_fuel=100.0, fuel_cost_per_hex=2.0)

        fleet = Fleet(1, 0, location, speed=0)
        fleet.ships = [ship_a, ship_b]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        galaxy = MockGalaxy(planet_map={location: [colony]})

        # Run resupply (one tick is enough to demonstrate distribution)
        resupply_engine.process_fleet_resupply(1, [empire], galaxy)

        # Ship A should get fuel (was at 100/500, needs more)
        assert ship_a.get_current_resource('fuel') == pytest.approx(500.0)
        # Ship B should stay at 100 (target is 100, already there)
        assert ship_b.get_current_resource('fuel') == pytest.approx(100.0)
        # Facility should have 0 fuel left (400 transferred to Ship A)
        assert facility.get_fuel_storage() == pytest.approx(0.0)

    def test_range_equalization_limited_fuel(self):
        """When fuel is limited, ships get proportional amounts for equal range.

        Setup:
        - Ship A: capacity=500, current=0, cost_per_hex=10
        - Ship B: capacity=500, current=0, cost_per_hex=5
        - Facility: 150 fuel

        After equalization:
        - Total pool: 0 + 0 + 150 = 150
        - Total cost/hex: 10 + 5 = 15
        - Max range: 150 / 15 = 10 hexes
        - Ship A target: 10 * 10 = 100
        - Ship B target: 10 * 5 = 50
        """
        registries = _make_registries(fuel_gen_amount=0.0, fuel_tank_amount=1000.0)
        resupply_engine = ResupplyEngine(registries=registries)

        location = HexCoord(5, 5)

        facility = _make_facility(fuel_level=150.0, has_synthesizer=False)
        colony = _make_colony(owner_id=0, location=location, facilities=[facility])

        ship_a = _make_mock_ship(fuel_capacity=500.0, current_fuel=0.0, fuel_cost_per_hex=10.0)
        ship_b = _make_mock_ship(fuel_capacity=500.0, current_fuel=0.0, fuel_cost_per_hex=5.0)

        fleet = Fleet(1, 0, location, speed=0)
        fleet.ships = [ship_a, ship_b]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        galaxy = MockGalaxy(planet_map={location: [colony]})

        resupply_engine.process_fleet_resupply(1, [empire], galaxy)

        # Ship A: 100 fuel (10 hexes × 10 cost/hex)
        assert ship_a.get_current_resource('fuel') == pytest.approx(100.0)
        # Ship B: 50 fuel (10 hexes × 5 cost/hex)
        assert ship_b.get_current_resource('fuel') == pytest.approx(50.0)
        # Facility depleted
        assert facility.get_fuel_storage() == pytest.approx(0.0)

    def test_enemy_fleet_not_resupplied(self):
        """Fleets belonging to a different owner than the planet get nothing."""
        registries = _make_registries(fuel_gen_amount=0.0, fuel_tank_amount=1000.0)
        resupply_engine = ResupplyEngine(registries=registries)

        location = HexCoord(5, 5)

        # Planet owned by player 0
        facility = _make_facility(fuel_level=500.0, has_synthesizer=False)
        colony = _make_colony(owner_id=0, location=location, facilities=[facility])

        # Fleet owned by player 1
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=100.0, fuel_cost_per_hex=5.0)
        fleet = Fleet(1, 1, location, speed=0)  # owner_id=1
        fleet.ships = [ship]

        empire_0 = Empire(0, "P1", (255, 0, 0))
        empire_0.add_colony(colony)

        empire_1 = Empire(1, "P2", (0, 0, 255))
        empire_1.add_fleet(fleet)

        galaxy = MockGalaxy(planet_map={location: [colony]})

        resupply_engine.process_fleet_resupply(1, [empire_0, empire_1], galaxy)

        # Ship should NOT have been resupplied
        ship.resupply.assert_not_called()
        # Fuel should remain in facility
        assert facility.get_fuel_storage() == pytest.approx(500.0)

    def test_fleet_already_full_no_transfer(self):
        """Fleet at full fuel receives no additional fuel."""
        registries = _make_registries(fuel_gen_amount=0.0, fuel_tank_amount=1000.0)
        resupply_engine = ResupplyEngine(registries=registries)

        location = HexCoord(5, 5)

        facility = _make_facility(fuel_level=500.0, has_synthesizer=False)
        colony = _make_colony(owner_id=0, location=location, facilities=[facility])

        # Ship at full fuel
        ship = _make_mock_ship(fuel_capacity=500.0, current_fuel=500.0, fuel_cost_per_hex=5.0)
        fleet = Fleet(1, 0, location, speed=0)
        fleet.ships = [ship]

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_colony(colony)
        empire.add_fleet(fleet)

        galaxy = MockGalaxy(planet_map={location: [colony]})

        resupply_engine.process_fleet_resupply(1, [empire], galaxy)

        # Fuel in facility should not change (no deficit to fill)
        assert facility.get_fuel_storage() == pytest.approx(500.0)
