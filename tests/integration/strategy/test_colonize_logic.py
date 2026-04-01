"""
Integration tests for colonize order logic.

Phase 2: Colony pods are cargo items. Ships are reusable after colonization.
"""
import pytest
from enum import Enum
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.core.hex_math import HexCoord


class MockPlanetType(Enum):
    """Mock planet types for testing."""
    ICE_DWARF = "ICE_DWARF"
    CONTINENTAL = "CONTINENTAL"


class MockSystem:
    def __init__(self, global_loc, planets):
        self.global_location = global_loc
        self.planets = planets
        self.name = "MockSystem"

class MockPlanet:
    _next_id = 1

    def __init__(self, name, relative_loc, owner_id=None):
        self.name = name
        self.location = relative_loc
        self.owner_id = owner_id
        self.construction_queue = []
        self.planet_type = MockPlanetType.ICE_DWARF
        self.populations = []
        self.facilities = []
        self.stockpile = {}
        self.id = MockPlanet._next_id
        MockPlanet._next_id += 1

    def add_to_stockpile(self, resource, amount):
        self.stockpile[resource] = self.stockpile.get(resource, 0.0) + amount

class MockGalaxy:
    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result

    def get_zones_at_global_hex(self, global_hex):
        return []

    def get_system_of_planet(self, planet):
        return None


def make_colony_ship(name: str, owner_id: int, pod_type: str = "ICE_DWARF") -> ShipInstance:
    """Create a ship with a drop pod in carried_items."""
    ship = ShipInstance(
        instance_id=f"colony-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=f"{pod_type}_colony_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # Load drop pod as carried item
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": f"{pod_type.lower()}_drop_pod",
        "name": f"Drop Pod ({pod_type})",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
    return ship

@pytest.fixture
def order_processor():
    return OrderProcessor()

@pytest.fixture
def component_registry():
    return {}

@pytest.fixture
def galaxy_setup():
    galaxy = MockGalaxy()

    pA = MockPlanet("Planet A", HexCoord(0,0))
    pB = MockPlanet("Planet B", HexCoord(1,0))

    system = MockSystem(HexCoord(10, 10), [pA, pB])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, system, pA, pB

def test_colonize_specific_success_at_exact_location(order_processor, galaxy_setup, component_registry):
    galaxy, system, pA, pB = galaxy_setup

    fleet = Fleet(1, 1, HexCoord(11, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pB))

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    result = order_processor.execute_action_order(
        fleet, empire, galaxy, component_registry=component_registry
    )

    assert result is True
    assert pB.owner_id == 1
    assert pB in empire.colonies
    # Phase 2: Fleet stays (ship is reusable)
    assert fleet in empire.fleets

def test_colonize_specific_fail_wrong_location(order_processor, galaxy_setup, component_registry):
    galaxy, system, pA, pB = galaxy_setup

    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pB))

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    result = order_processor.execute_action_order(
        fleet, empire, galaxy, component_registry=component_registry
    )

    assert result is False
    assert pB.owner_id is None
    assert len(fleet.orders) == 0
    assert len(empire.fleets) == 1

def test_colonize_any_success_at_location(order_processor, galaxy_setup, component_registry):
    galaxy, system, pA, pB = galaxy_setup

    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    result = order_processor.execute_action_order(
        fleet, empire, galaxy, component_registry=component_registry
    )

    assert result is True
    assert pA.owner_id == 1
    assert pA in empire.colonies

def test_colonize_any_fail_no_candidates(order_processor, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    fleet = Fleet(1, 1, HexCoord(50, 50))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

    empire = Empire(1, "Player 1", (255, 0, 0))

    result = order_processor.execute_action_order(fleet, empire, galaxy)

    assert result is False
    assert len(fleet.orders) == 0

def test_colonize_specific_fail_owned(order_processor, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    pA.owner_id = 2

    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pA))

    empire = Empire(1, "Player 1", (255, 0, 0))

    result = order_processor.execute_action_order(fleet, empire, galaxy)

    assert result is False
    assert len(fleet.orders) == 0
    assert pA.owner_id == 2


# =============================================================================
# Phase 2: Colony Pod Cargo Consumption Tests
# =============================================================================


@pytest.fixture
def galaxy_with_typed_planets():
    galaxy = MockGalaxy()

    ice_planet = MockPlanet("Ice World", HexCoord(0, 0))
    ice_planet.planet_type = MockPlanetType.ICE_DWARF

    continental_planet = MockPlanet("Earth-like", HexCoord(1, 0))
    continental_planet.planet_type = MockPlanetType.CONTINENTAL

    system = MockSystem(HexCoord(10, 10), [ice_planet, continental_planet])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, ice_planet, continental_planet


class TestColonizePodCargoConsumption:
    """Tests for Phase 2: Colony pod consumed from cargo, ship stays."""

    def test_colonize_consumes_pod_from_cargo_ship_stays(
        self, galaxy_with_typed_planets
    ):
        """Colonization consumes pod from cargo. Ship and fleet stay."""
        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        colony_ship = make_colony_ship("Colony Ship", 1, "ICE_DWARF")
        combat_ship = ShipInstance(
            instance_id="combat-1", design_id="combat", name="Combat Ship",
            owner_id=1, design_data={'name': 'Combat', 'vehicle_type': 'Ship',
            'stats': {'mass': 100}, 'layers': {'HULL': [{'id': 'laser_cannon'}]}}
        )

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Both ships stay in fleet
        assert colony_ship in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 2

        # Drop pod consumed from carried_items
        drop_pods = [i for i in colony_ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 0

        # Fleet still exists
        assert fleet in empire.fleets

    def test_colonize_single_ship_fleet_stays(
        self, galaxy_with_typed_planets
    ):
        """Single-ship fleet stays after colonization."""
        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        colony_ship = make_colony_ship("Lone Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Ship stays
        assert colony_ship in fleet.ships
        # Fleet stays
        assert fleet in empire.fleets

    def test_colonize_consumes_one_drop_pod(
        self, galaxy_with_typed_planets
    ):
        """Colonizing consumes exactly one drop pod from carried_items."""
        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        # Ship carrying two drop pods
        ship = ShipInstance(
            instance_id="multi-pod-1", design_id="multi_carrier", name="Multi Carrier",
            owner_id=1, design_data={'name': 'Multi', 'vehicle_type': 'Ship',
            'stats': {'mass': 100}, 'layers': {'HULL': [{'id': 'colony_pod_bay'}]}}
        )
        ship.carried_items.append({
            "vehicle_type": "drop_pod", "design_id": "pod_1",
            "name": "Pod 1", "design_data": {"layers": {"CORE": []}}, "mass": 500,
        })
        ship.carried_items.append({
            "vehicle_type": "drop_pod", "design_id": "pod_2",
            "name": "Pod 2", "design_data": {"layers": {"CORE": []}}, "mass": 500,
        })

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # One pod consumed, one remains
        drop_pods = [i for i in ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 1
