"""End-to-end economy integration tests.

PROJ-75 Phase 6: Tests the full economy pipeline through TurnEngine,
using REAL HarvestingEngine, MaintenanceEngine, and ProductionEngine,
with other engines mocked out.

Tests cover:
- Full turn cycle: harvesting -> maintenance -> construction
- Resource depletion and build pausing
- Maintenance failure causing scuttling
- Storage cap enforcement
- Save/load round-trip of economy state
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.harvesting_engine import HarvestingEngine
from game.strategy.engine.maintenance_engine import MaintenanceEngine
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.interfaces.engines import IPopulationEngine


# ===========================================================================
# Inline mocks for non-economy engines
# ===========================================================================

class _NoOpPopulationEngine(IPopulationEngine):
    """No-op population engine for E2E economy tests."""
    def process_population_growth(self, empires):
        pass


def _make_mock_non_economy_engines():
    """Create mocks for all engines EXCEPT harvesting, maintenance, production."""
    movement = MagicMock()
    movement.collect_movements.return_value = []

    order_processor = MagicMock()
    order_processor.process_instant_orders.return_value = []

    return {
        'movement_engine': movement,
        'order_processor': order_processor,
        'conflict_engine': MagicMock(),
        'resource_engine': MagicMock(),
        'population_engine': _NoOpPopulationEngine(),
        'resupply_engine': MagicMock(),
    }


# ===========================================================================
# Factory helpers
# ===========================================================================

def _make_empire(resources=None, max_storage=None, empire_id=0):
    """Create an empire with optional starting resources and storage."""
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))
    if resources:
        empire.resource_pool = dict(resources)
    if max_storage:
        empire.max_storage = dict(max_storage)
    return empire


def _make_planet(
    name="Test World",
    resources=None,
    facilities=None,
    owner_id=0,
):
    """Create a minimal planet for economy testing."""
    planet = Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=2,
        mass=5.97e24,
        radius=6.37e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.8,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
    )
    planet.resources = resources or {}
    planet.facilities = facilities or []
    return planet


def _make_harvester_facility(
    resource_type="Metals",
    base_harvest_rate=100.0,
    resource_cost=None,
    instance_id="harv-001",
):
    """Create a facility with a ResourceHarvester component and optional build cost."""
    comp = {
        "id": f"{resource_type.lower()}_harvester",
        "abilities": {
            "ResourceHarvester": {
                "resource_type": resource_type,
                "base_harvest_rate": base_harvest_rate,
            }
        },
    }
    if resource_cost:
        comp["resource_cost"] = resource_cost
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id=f"{resource_type.lower()}_harvester_complex",
        name=f"{resource_type} Harvester",
        design_data={"layers": {"core": [comp]}},
    )


def _make_storage_facility(
    resource_type="Metals",
    capacity=10000.0,
    resource_cost=None,
    instance_id="store-001",
):
    """Create a facility with an EmpireStorage component."""
    comp = {
        "id": f"{resource_type.lower()}_vault",
        "abilities": {
            "EmpireStorage": {
                "resource_type": resource_type,
                "capacity": capacity,
            }
        },
    }
    if resource_cost:
        comp["resource_cost"] = resource_cost
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id=f"{resource_type.lower()}_vault",
        name=f"{resource_type} Vault",
        design_data={"layers": {"core": [comp]}},
    )


def _make_plain_facility(
    resource_cost,
    name="Test Facility",
    instance_id="fac-001",
):
    """Create a facility with only build cost (no abilities)."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="test_complex",
        name=name,
        design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": resource_cost}
                    ]
                }
            }
        },
        is_operational=True,
    )


def _make_ship_instance(name="Test Ship", design_data=None, owner_id=0):
    """Create a ShipInstance with given design data."""
    return ShipInstance(
        instance_id=f"ship-{name}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data=design_data or {"name": name, "layers": {}},
    )


def _make_fleet_with_ship(
    ship_resource_cost,
    fleet_id=10000,
    owner_id=0,
    ship_name="Test Ship",
):
    """Create a fleet with one ship that has a build cost."""
    ship = _make_ship_instance(
        name=ship_name,
        design_data={
            "name": ship_name,
            "layers": {
                "HULL": [
                    {"id": "hull_comp", "resource_cost": ship_resource_cost}
                ]
            },
        },
        owner_id=owner_id,
    )
    fleet = Fleet(fleet_id, owner_id, HexCoord(0, 0))
    fleet.ships.append(ship)
    return fleet


def _make_economy_turn_engine():
    """Create TurnEngine with real economy engines, all others mocked."""
    mocks = _make_mock_non_economy_engines()
    return TurnEngine(
        **mocks,
        harvesting_engine=HarvestingEngine(),
        maintenance_engine=MaintenanceEngine(),
        production_engine=ProductionEngine(),
    )


class MockGalaxy:
    """Minimal galaxy mock for turn engine."""
    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        return []

    def get_system_of_planet(self, planet):
        return None


# ===========================================================================
# E2E Tests
# ===========================================================================

class TestEconomyE2E:
    """End-to-end economy pipeline tests."""

    def test_full_turn_cycle_harvest_then_maintenance(self):
        """Harvest fills pool, then maintenance deducts costs."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        # Harvester: 100 rate * 1.0 quality = 100 Metals per turn
        # Build cost: 200 Metals -> maintenance: 200 * 0.05 = 10 Metals
        harvester = _make_harvester_facility(
            "Metals", base_harvest_rate=100.0,
            resource_cost={"Metals": 200},
        )
        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(
            resources={"Metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )

        empire = _make_empire()
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 100, Maintenance: 10 -> Net: 90
        assert empire.resource_pool["Metals"] == pytest.approx(90.0)
        # Planet depleted by 100
        assert planet.resources["Metals"]["quantity"] == pytest.approx(4900.0)

    def test_empire_starts_with_resources_harvests_more(self):
        """Pre-existing empire resources combine with harvested amounts."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        harvester = _make_harvester_facility(
            "Metals", base_harvest_rate=50.0,
            resource_cost={"Metals": 100},  # maintenance: 5
        )
        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(
            resources={"Metals": {"quantity": 3000, "quality": 0.8}},
            facilities=[storage, harvester],
        )

        empire = _make_empire(resources={"Metals": 500.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 50 * 0.8 = 40, Maintenance: 5
        # Final: 500 + 40 - 5 = 535
        assert empire.resource_pool["Metals"] == pytest.approx(535.0)

    def test_construction_consumes_resources_per_tick(self):
        """Queue items with cost_per_tick consume from empire pool each tick."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(
            facilities=[storage],
        )
        # Queue item: 3-turn build, 150 Metals total -> 0.5 per tick
        # After 1 turn: tick system decrements to 2, process_production decrements to 1
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 3,
            "total_cost": {"Metals": 150.0},
            "cost_per_tick": {"Metals": 0.5},
            "resources_consumed": {"Metals": 0.0},
            "ticks_in_current_turn": 0,
        }]

        empire = _make_empire(resources={"Metals": 1000.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # 100 ticks * 0.5 = 50 Metals consumed by construction
        # turns_remaining: 3 -> 2 (tick system at tick 100) -> 1 (process_production)
        assert empire.resource_pool["Metals"] == pytest.approx(950.0)
        assert planet.construction_queue[0]["turns_remaining"] == 1

    def test_resource_depletion_pauses_construction(self):
        """When empire runs out of resources, construction pauses (tick system)."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(facilities=[storage])

        # Queue item: 1 Metal per tick, but only 30 Metals available
        # Tick system pauses at tick 30; process_production still decrements once
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 3,
            "total_cost": {"Metals": 300.0},
            "cost_per_tick": {"Metals": 1.0},
            "resources_consumed": {"Metals": 0.0},
            "ticks_in_current_turn": 0,
        }]

        empire = _make_empire(resources={"Metals": 30.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Only 30 ticks proceed (resource depletion), then pause
        assert empire.resource_pool["Metals"] == pytest.approx(0.0)
        assert planet.construction_queue[0]["ticks_in_current_turn"] == 30
        # turns_remaining: 3 (tick system never hit 100) -> 2 (process_production)
        assert planet.construction_queue[0]["turns_remaining"] == 2

    def test_maintenance_failure_causes_facility_scuttle(self):
        """Facility is scuttled when empire can't pay maintenance."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        # Facility costs 1000 Metals -> maintenance: 50 Metals
        facility = _make_plain_facility(
            resource_cost={"Metals": 1000},
            name="Expensive Complex",
        )
        colony = _make_planet(facilities=[facility])

        # Empire has 20 Metals - not enough for 50 maintenance
        empire = _make_empire(resources={"Metals": 20.0})
        empire.add_colony(colony)

        engine.process_turn([empire], galaxy)

        # Facility should be scuttled
        assert len(colony.facilities) == 0
        # Resources untouched (failed payment means no deduction)
        assert empire.resource_pool["Metals"] == pytest.approx(20.0)

    def test_maintenance_failure_causes_ship_scuttle(self):
        """Ship is scuttled when empire can't pay maintenance."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        # Ship costs 500 Metals -> maintenance: 25 Metals
        fleet = _make_fleet_with_ship(
            ship_resource_cost={"Metals": 500},
            ship_name="Destroyer",
        )

        empire = _make_empire(resources={"Metals": 10.0})
        empire.add_fleet(fleet)
        # No colonies needed - just testing ship maintenance
        empire.colonies = []

        engine.process_turn([empire], galaxy)

        # Ship should be scuttled, fleet removed (empty + had scuttles)
        assert len(empire.fleets) == 0

    def test_harvesting_respects_storage_cap(self):
        """Harvested resources are capped at empire storage limit."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        harvester = _make_harvester_facility("Metals", base_harvest_rate=200.0)
        storage = _make_storage_facility("Metals", capacity=1000.0)
        planet = _make_planet(
            resources={"Metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )

        empire = _make_empire(resources={"Metals": 900.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 200, but cap at 1000 (only 100 fits)
        # After cap: 1000, maintenance on harvester: 0 (no resource_cost)
        assert empire.resource_pool["Metals"] == pytest.approx(1000.0)

    def test_save_load_preserves_economy_state(self):
        """Empire resource pool and storage survive serialization round-trip."""
        empire = _make_empire(
            resources={"Metals": 500.0, "Organics": 200.0},
            max_storage={"Metals": 10000.0, "Organics": 5000.0},
        )

        # Serialize
        data = empire.to_dict()

        # Deserialize
        restored = Empire.from_dict(data, galaxy=None)

        assert restored.resource_pool["Metals"] == pytest.approx(500.0)
        assert restored.resource_pool["Organics"] == pytest.approx(200.0)
        assert restored.max_storage["Metals"] == pytest.approx(10000.0)
        assert restored.max_storage["Organics"] == pytest.approx(5000.0)

    def test_multi_resource_construction(self):
        """Construction that costs multiple resources consumes all correctly."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        storage_m = _make_storage_facility("Metals", 10000.0, instance_id="store-m")
        storage_o = _make_storage_facility("Organics", 10000.0, instance_id="store-o")
        planet = _make_planet(facilities=[storage_m, storage_o])

        # Ship costs Metals + Organics, 0.5 and 0.3 per tick
        planet.construction_queue = [{
            "design_id": "multi_res_ship",
            "type": "complex",
            "turns_remaining": 2,
            "total_cost": {"Metals": 100.0, "Organics": 60.0},
            "cost_per_tick": {"Metals": 0.5, "Organics": 0.3},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0},
            "ticks_in_current_turn": 0,
        }]

        empire = _make_empire(resources={"Metals": 1000.0, "Organics": 500.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # 100 ticks: 50 Metals, 30 Organics consumed
        assert empire.resource_pool["Metals"] == pytest.approx(950.0)
        assert empire.resource_pool["Organics"] == pytest.approx(470.0)

    def test_multi_resource_pauses_if_one_depletes(self):
        """Construction pauses when ANY resource is insufficient."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        storage_m = _make_storage_facility("Metals", 10000.0, instance_id="store-m")
        storage_o = _make_storage_facility("Organics", 10000.0, instance_id="store-o")
        planet = _make_planet(facilities=[storage_m, storage_o])

        # Costs 1.0 Metals and 1.0 Organics per tick
        planet.construction_queue = [{
            "design_id": "expensive_thing",
            "type": "complex",
            "turns_remaining": 2,
            "total_cost": {"Metals": 200.0, "Organics": 200.0},
            "cost_per_tick": {"Metals": 1.0, "Organics": 1.0},
            "resources_consumed": {"Metals": 0.0, "Organics": 0.0},
            "ticks_in_current_turn": 0,
        }]

        # Plenty of Metals but only 20 Organics -> pauses at tick 20
        empire = _make_empire(resources={"Metals": 1000.0, "Organics": 20.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Only 20 ticks processed before Organics runs out
        assert empire.resource_pool["Metals"] == pytest.approx(980.0)
        assert empire.resource_pool["Organics"] == pytest.approx(0.0)
        assert planet.construction_queue[0]["ticks_in_current_turn"] == 20

    def test_harvesting_before_maintenance_order(self):
        """Harvesting runs first, making resources available for maintenance."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        # Harvester gives 100 Metals, and also costs 200 to build (maintenance: 10)
        harvester = _make_harvester_facility(
            "Metals", base_harvest_rate=100.0,
            resource_cost={"Metals": 200},
        )
        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(
            resources={"Metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )

        # Empire starts with 0 - but harvesting will give 100 before maintenance needs 10
        empire = _make_empire(resources={"Metals": 0.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 100, Maintenance: 10 -> Net: 90
        # Facility should NOT be scuttled because harvesting ran first
        assert len(planet.facilities) == 2  # storage + harvester
        assert empire.resource_pool["Metals"] == pytest.approx(90.0)

    def test_maintenance_paid_before_construction_tick(self):
        """Maintenance costs reduce pool before construction ticks."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        # Facility with 1000 Metal build cost -> maintenance: 50
        expensive = _make_plain_facility(
            resource_cost={"Metals": 1000},
            name="Expensive Facility",
        )
        storage = _make_storage_facility("Metals", capacity=10000.0, instance_id="store-1")
        planet = _make_planet(facilities=[storage, expensive])

        # Queue consumes 0.5 per tick = 50 per turn
        planet.construction_queue = [{
            "design_id": "new_complex",
            "type": "complex",
            "turns_remaining": 2,
            "total_cost": {"Metals": 100.0},
            "cost_per_tick": {"Metals": 0.5},
            "resources_consumed": {"Metals": 0.0},
            "ticks_in_current_turn": 0,
        }]

        empire = _make_empire(resources={"Metals": 200.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Maintenance: 50, Construction: 50 (100 ticks * 0.5) -> 200 - 50 - 50 = 100
        assert empire.resource_pool["Metals"] == pytest.approx(100.0)

    def test_planet_save_load_preserves_resources(self):
        """Planet resources and facilities survive serialization."""
        harvester = _make_harvester_facility("Metals", base_harvest_rate=75.0)
        planet = _make_planet(
            name="Resource World",
            resources={"Metals": {"quantity": 3000, "quality": 0.9}},
            facilities=[harvester],
        )

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert restored.resources["Metals"]["quantity"] == 3000
        assert restored.resources["Metals"]["quality"] == pytest.approx(0.9)
        assert len(restored.facilities) == 1
        assert restored.facilities[0].name == "Metals Harvester"

    def test_non_operational_facilities_skip_harvest_and_maintenance(self):
        """Non-operational facilities don't harvest and don't pay maintenance."""
        engine = _make_economy_turn_engine()
        galaxy = MockGalaxy()

        harvester = _make_harvester_facility(
            "Metals", base_harvest_rate=100.0,
            resource_cost={"Metals": 200},  # would cost 10 maintenance
        )
        harvester.is_operational = False

        storage = _make_storage_facility("Metals", capacity=10000.0)
        planet = _make_planet(
            resources={"Metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )

        empire = _make_empire(resources={"Metals": 0.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # No harvesting (non-operational), no maintenance
        assert empire.resource_pool.get("Metals", 0.0) == pytest.approx(0.0)
        # Facility still exists (no scuttle - non-operational is free)
        assert len(planet.facilities) == 2

    def test_construction_queue_save_load(self):
        """Queue items with cost tracking survive planet serialization."""
        planet = _make_planet()
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 5,
            "total_cost": {"Metals": 500.0},
            "cost_per_tick": {"Metals": 1.0},
            "resources_consumed": {"Metals": 150.0},
            "ticks_in_current_turn": 50,
        }]

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        item = restored.construction_queue[0]
        assert item["turns_remaining"] == 5
        assert item["total_cost"]["Metals"] == pytest.approx(500.0)
        assert item["cost_per_tick"]["Metals"] == pytest.approx(1.0)
        assert item["resources_consumed"]["Metals"] == pytest.approx(150.0)
        assert item["ticks_in_current_turn"] == 50
