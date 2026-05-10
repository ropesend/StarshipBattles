"""End-to-end economy integration tests.

PROJ-75 Phase 6: Tests the full economy pipeline through TurnEngine,
using REAL HarvestingEngine and ProductionEngine,
with other engines mocked out.

Tests cover:
- Full turn cycle: harvesting -> construction
- Resource depletion and build pausing
- Storage cap enforcement
- Save/load round-trip of economy state
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.harvesting_engine import HarvestingEngine
from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
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
    """Create an empire with optional starting resources and storage.

    Resources go to _fleet_resource_pool since colonies haven't been added yet.
    empire.resource_pool is a computed aggregate of colony stockpiles + fleet pool.
    """
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))
    if resources:
        empire._fleet_resource_pool = dict(resources)
    if max_storage:
        empire.max_storage = dict(max_storage)
    return empire


def _make_planetary_yard():
    """Create a PlanetaryYard facility for base construction queue processing."""
    return PlanetaryFacility(
        instance_id="yard_starter",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {
                "CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]
            }
        },
        is_operational=True,
    )


def _make_planet(
    name="Test World",
    resources=None,
    facilities=None,
    owner_id=0,
):
    """Create a minimal planet for economy testing.

    Always includes a PlanetaryYard facility so the base construction
    queue is processed by ProductionEngine.
    """
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
    planet.deposits = resources or {}
    # Always include PlanetaryYard; append any additional facilities
    planet.facilities = [_make_planetary_yard()] + (facilities or [])
    return planet


def _make_harvester_facility(
    resource_type="metals",
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
        name=f"{resource_type.capitalize()} Harvester",
        design_data={"layers": {"core": [comp]}},
    )


def _make_storage_facility(
    resource_type="metals",
    capacity=10000.0,
    resource_cost=None,
    instance_id="store-001",
):
    """Create a facility with an LocalStorage component."""
    comp = {
        "id": f"{resource_type.lower()}_vault",
        "abilities": {
            "LocalStorage": {
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
        name=f"{resource_type.capitalize()} Vault",
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


def _make_economy_turn_engine(registries):
    """Create TurnEngine with real economy engines, all others mocked."""
    mocks = _make_mock_non_economy_engines()
    return TurnEngine(
        registries=registries,
        **mocks,
        harvesting_engine=HarvestingEngine(registries=registries),
        production_engine=ProductionEngine(registries=registries),
    )


class MockGalaxy:
    """Minimal galaxy mock for turn engine."""
    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        return []

    def get_system_of_planet(self, planet):
        return None

    def get_zones_at_global_hex(self, global_hex):
        """Return empty list - no storms in this mock."""
        return []


# ===========================================================================
# E2E Tests
# ===========================================================================

class TestEconomyE2E:
    """End-to-end economy pipeline tests."""

    def test_empire_starts_with_resources_harvests_more(self, fresh_registries):
        """Harvested resources go to colony stockpile, empire pool unchanged by harvest."""
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        harvester = _make_harvester_facility(
            "metals", base_harvest_rate=50.0,
        )
        storage = _make_storage_facility("metals", capacity=10000.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 3000, "quality": 0.8}},
            facilities=[storage, harvester],
        )

        empire = _make_empire(resources={"metals": 500.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 50 * 0.8 = 40, deposited into colony stockpile
        assert planet.stockpile.get("metals", 0.0) == pytest.approx(40.0)
        # Fleet resource pool unchanged by harvesting (harvest goes to colony stockpile)
        assert empire._fleet_resource_pool.get("metals", 0.0) == pytest.approx(500.0)
        # Aggregate resource_pool = fleet pool (500) + colony stockpile (40) = 540
        assert empire.resource_pool["metals"] == pytest.approx(540.0)

    def test_construction_consumes_resources_per_tick(self, fresh_registries):
        """Construction uses tick-based dynamic consumption from planet stockpile.

        Dynamic system uses production_rates.json: planetary_yard = 2000/turn = 20/tick.
        Item with total_cost=150 at 20/tick completes in 7.5 ticks, consuming all 150.
        """
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        storage = _make_storage_facility("metals", capacity=10000.0)
        planet = _make_planet(
            facilities=[storage],
        )
        # Give planet stockpile for construction to draw from
        planet.stockpile = {"metals": 1000.0}
        # Queue item: 150 Metals total. At 20/tick rate, completes in 7.5 ticks.
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 3,
            "total_cost": {"metals": 150.0},
            "resources_consumed": {"metals": 0.0},
        }]

        empire = _make_empire(resources={})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Item completes mid-turn (tick 8), consuming all 150 Metals from stockpile
        # Queue should be empty after completion
        assert planet.stockpile["metals"] == pytest.approx(850.0)
        assert len(planet.construction_queue) == 0  # Item completed

    def test_resource_depletion_pauses_construction(self, fresh_registries):
        """When planet stockpile runs out, construction pauses.

        Dynamic system rate = 20/tick. Stockpile has 30 Metals.
        Tick 1: consumes 20 (10 left). Tick 2: can't afford 20, pauses.
        System pauses when stockpile can't afford a full tick's consumption.
        Track progress via resources_consumed, not ticks_in_current_turn (dead field).
        """
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        storage = _make_storage_facility("metals", capacity=10000.0)
        planet = _make_planet(facilities=[storage])

        # Item needs 300 Metals. At 20/tick, needs 15 ticks if resources available.
        # Stockpile has 30 Metals. Tick 1: 20 consumed (10 left). Tick 2: can't afford 20, pauses.
        planet.stockpile = {"metals": 30.0}
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 3,
            "total_cost": {"metals": 300.0},
            "resources_consumed": {"metals": 0.0},
        }]

        empire = _make_empire(resources={})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # After tick 1: 20 consumed from stockpile, 10 remaining. Tick 2 pauses (can't afford 20).
        assert planet.stockpile["metals"] == pytest.approx(10.0)
        # Progress tracked via resources_consumed
        assert planet.construction_queue[0]["resources_consumed"]["metals"] == pytest.approx(20.0)
        # Item still in queue (not complete)
        assert len(planet.construction_queue) == 1

    def test_harvesting_respects_storage_cap(self, fresh_registries):
        """Harvested resources are capped at colony stockpile limit."""
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        harvester = _make_harvester_facility("metals", base_harvest_rate=200.0)
        storage = _make_storage_facility("metals", capacity=1000.0)
        planet = _make_planet(
            resources={"metals": {"quantity": 5000, "quality": 1.0}},
            facilities=[storage, harvester],
        )
        planet.stockpile = {"metals": 900.0}

        empire = _make_empire(resources={"metals": 900.0})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Harvest: 200, but colony stockpile cap at 1000 (only 100 fits)
        assert planet.stockpile["metals"] == pytest.approx(1000.0)

    def test_save_load_preserves_economy_state(self):
        """Empire resource pool and storage survive serialization round-trip."""
        empire = _make_empire(
            resources={"metals": 500.0, "organics": 200.0},
            max_storage={"metals": 10000.0, "organics": 5000.0},
        )

        # Serialize
        data = empire.to_dict()

        # Deserialize
        restored = Empire.from_dict(data, galaxy=None)

        assert restored.resource_pool["metals"] == pytest.approx(500.0)
        assert restored.resource_pool["organics"] == pytest.approx(200.0)
        assert restored.max_storage["metals"] == pytest.approx(10000.0)
        assert restored.max_storage["organics"] == pytest.approx(5000.0)

    def test_multi_resource_construction(self, fresh_registries):
        """Construction that costs multiple resources completes correctly.

        Dynamic system: planetary_yard rate = 20/tick per resource.
        Limiting resource logic: resource with highest (remaining / rate) sets pace.
        - Metals: 100 / 20 = 5 ticks
        - Organics: 60 / 20 = 3 ticks
        Metals is limiting (5 ticks). All resources consumed in 5 ticks.
        """
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        storage_m = _make_storage_facility("metals", 10000.0, instance_id="store-m")
        storage_o = _make_storage_facility("organics", 10000.0, instance_id="store-o")
        planet = _make_planet(facilities=[storage_m, storage_o])

        # Give planet stockpile for construction
        planet.stockpile = {"metals": 1000.0, "organics": 500.0}

        # Costs 100 Metals + 60 Organics. Completes in 5 ticks at 20/tick rate.
        planet.construction_queue = [{
            "design_id": "multi_res_ship",
            "type": "complex",
            "turns_remaining": 2,
            "total_cost": {"metals": 100.0, "organics": 60.0},
            "resources_consumed": {"metals": 0.0, "organics": 0.0},
        }]

        empire = _make_empire(resources={})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # Item completes at tick 5, consuming all resources from stockpile
        assert planet.stockpile["metals"] == pytest.approx(900.0)  # 1000 - 100
        assert planet.stockpile["organics"] == pytest.approx(440.0)  # 500 - 60
        assert len(planet.construction_queue) == 0  # Item completed

    def test_multi_resource_pauses_if_one_depletes(self, fresh_registries):
        """Construction pauses when ANY resource is insufficient in stockpile.

        Dynamic system rate = 20/tick per resource. Both 200/200 cost.
        Stockpile has 1000 Metals but only 20 Organics.
        After tick 1: 20 of each consumed. Organics exhausted, pauses.
        Track progress via resources_consumed, not ticks_in_current_turn.
        """
        engine = _make_economy_turn_engine(fresh_registries)
        galaxy = MockGalaxy()

        storage_m = _make_storage_facility("metals", 10000.0, instance_id="store-m")
        storage_o = _make_storage_facility("organics", 10000.0, instance_id="store-o")
        planet = _make_planet(facilities=[storage_m, storage_o])

        # Give planet stockpile: plenty of Metals but only 20 Organics
        planet.stockpile = {"metals": 1000.0, "organics": 20.0}

        # Costs 200 Metals + 200 Organics. At 20/tick each, needs 10 ticks.
        planet.construction_queue = [{
            "design_id": "expensive_thing",
            "type": "complex",
            "turns_remaining": 2,
            "total_cost": {"metals": 200.0, "organics": 200.0},
            "resources_consumed": {"metals": 0.0, "organics": 0.0},
        }]

        empire = _make_empire(resources={})
        empire.add_colony(planet)

        engine.process_turn([empire], galaxy)

        # After 1 tick: 20 Metals, 20 Organics consumed from stockpile. Then Organics exhausted.
        assert planet.stockpile["metals"] == pytest.approx(980.0)
        assert planet.stockpile["organics"] == pytest.approx(0.0)
        # Track progress via resources_consumed
        assert planet.construction_queue[0]["resources_consumed"]["metals"] == pytest.approx(20.0)
        assert planet.construction_queue[0]["resources_consumed"]["organics"] == pytest.approx(20.0)

    def test_planet_save_load_preserves_resources(self):
        """Planet resources and facilities survive serialization."""
        harvester = _make_harvester_facility("metals", base_harvest_rate=75.0)
        planet = _make_planet(
            name="Resource World",
            resources={"metals": {"quantity": 3000, "quality": 0.9}},
            facilities=[harvester],
        )

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert restored.deposits["metals"]["quantity"] == 3000
        assert restored.deposits["metals"]["quality"] == pytest.approx(0.9)
        # Starter PlanetaryYard + harvester = 2 facilities
        assert len(restored.facilities) == 2
        harvester_names = [f.name for f in restored.facilities]
        assert "Metals Harvester" in harvester_names

    def test_construction_queue_save_load(self):
        """Queue items with cost tracking survive planet serialization.

        Dynamic system uses total_cost and resources_consumed for progress.
        cost_per_tick and ticks_in_current_turn are dead fields (not used).
        """
        planet = _make_planet()
        planet.construction_queue = [{
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 5,
            "total_cost": {"metals": 500.0},
            "resources_consumed": {"metals": 150.0},
        }]

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        item = restored.construction_queue[0]
        assert item["turns_remaining"] == 5
        assert item["total_cost"]["metals"] == pytest.approx(500.0)
        assert item["resources_consumed"]["metals"] == pytest.approx(150.0)
