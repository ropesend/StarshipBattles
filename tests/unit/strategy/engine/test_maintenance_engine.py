"""Tests for MaintenanceEngine - maintenance cost deduction and scuttling.

PROJ-75 Phase 5: Maintenance System.

MaintenanceEngine deducts 5% of build cost per turn for each facility and ship.
If the empire cannot afford maintenance, the entity is scuttled immediately.
Processing is one-pass to prevent cascading scuttles.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.empire import Empire
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.hex_math import HexCoord


# --- Helpers ---

def _make_empire(resources: dict = None, empire_id: int = 0) -> Empire:
    """Create a real Empire with optional starting resources."""
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))
    if resources:
        for res, amount in resources.items():
            empire.resource_pool[res] = amount
    return empire


def _make_colony(facilities=None, name="Test Colony", planet_id=1):
    """Create a mock colony with facilities."""
    colony = MagicMock()
    colony.name = name
    colony.id = planet_id
    colony.facilities = list(facilities) if facilities else []
    return colony


def _make_facility(
    design_data: dict = None,
    name: str = "Test Facility",
    is_operational: bool = True,
    instance_id: str = "fac_1",
    design_id: str = "test_complex",
) -> PlanetaryFacility:
    """Create a PlanetaryFacility with given design_data."""
    if design_data is None:
        design_data = {
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "metals_harvester", "resource_cost": {"Metals": 1000, "Radioactives": 200}}
                    ]
                }
            }
        }
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id=design_id,
        name=name,
        design_data=design_data,
        is_operational=is_operational,
    )


def _make_fleet(ships=None, fleet_id=100, owner_id=0, location=None) -> Fleet:
    """Create a Fleet with optional ships."""
    loc = location or HexCoord(0, 0)
    fleet = Fleet(fleet_id=fleet_id, owner_id=owner_id, location=loc)
    if ships:
        for ship in ships:
            fleet.ships.append(ship)
    return fleet


def _make_ship_instance(
    design_data: dict = None,
    name: str = "Test Ship",
    design_id: str = "scout",
    instance_id: str = "ship_1",
    owner_id: int = 0,
) -> ShipInstance:
    """Create a ShipInstance with given design_data."""
    if design_data is None:
        design_data = {
            "layers": {
                "HULL": {
                    "components": [
                        {"id": "light_hull", "resource_cost": {"Metals": 500, "Organics": 100}}
                    ]
                }
            }
        }
    return ShipInstance(
        instance_id=instance_id,
        design_id=design_id,
        name=name,
        owner_id=owner_id,
        design_data=design_data,
    )


# --- Facility Maintenance Tests ---

class TestMaintenanceEngine:
    """Tests for MaintenanceEngine."""

    def _get_engine(self):
        from game.strategy.engine.maintenance_engine import MaintenanceEngine
        return MaintenanceEngine()

    # --- Cost calculation ---

    def test_maintenance_cost_is_5_percent_of_build_cost(self):
        """Maintenance cost should be 5% of total design build cost."""
        engine = self._get_engine()
        facility = _make_facility(design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": {"Metals": 1000}},
                        {"id": "comp_b", "resource_cost": {"Organics": 200}},
                    ]
                }
            }
        })
        cost = engine._calculate_maintenance_cost(facility.design_data)
        # 5% of Metals=1000 -> 50, 5% of Organics=200 -> 10
        assert cost == {"Metals": pytest.approx(50.0), "Organics": pytest.approx(10.0)}

    def test_maintenance_cost_multiple_layers(self):
        """Maintenance cost sums resource_cost across all layers."""
        engine = self._get_engine()
        facility = _make_facility(design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": {"Metals": 400}}
                    ]
                },
                "OUTER": {
                    "components": [
                        {"id": "comp_b", "resource_cost": {"Metals": 600, "Vapors": 100}}
                    ]
                }
            }
        })
        cost = engine._calculate_maintenance_cost(facility.design_data)
        # 5% of Metals=1000 -> 50, 5% of Vapors=100 -> 5
        assert cost == {"Metals": pytest.approx(50.0), "Vapors": pytest.approx(5.0)}

    def test_maintenance_cost_zero_for_empty_design(self):
        """Design with no components has zero maintenance cost."""
        engine = self._get_engine()
        cost = engine._calculate_maintenance_cost({"layers": {}})
        assert cost == {}

    def test_maintenance_cost_components_without_resource_cost(self):
        """Components without resource_cost field are ignored."""
        engine = self._get_engine()
        cost = engine._calculate_maintenance_cost({
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "sensor_array"},  # No resource_cost
                        {"id": "metals_harvester", "resource_cost": {"Metals": 200}},
                    ]
                }
            }
        })
        assert cost == {"Metals": pytest.approx(10.0)}

    # --- Successful facility payment ---

    def test_facility_maintenance_deducts_from_empire(self):
        """Successful maintenance payment deducts resources from empire pool."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 1000.0})
        facility = _make_facility(design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": {"Metals": 1000}}
                    ]
                }
            }
        })
        colony = _make_colony(facilities=[facility])
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        # 5% of 1000 = 50 Metals deducted
        assert empire.resource_pool["Metals"] == pytest.approx(950.0)
        assert len(events) == 0

    def test_multiple_facilities_all_checked(self):
        """All facilities on all colonies are processed in one pass."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 1000.0})
        fac1 = _make_facility(
            instance_id="fac_1",
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 200}}]}}},
        )
        fac2 = _make_facility(
            instance_id="fac_2",
            design_data={"layers": {"CORE": {"components": [{"id": "b", "resource_cost": {"Metals": 400}}]}}},
        )
        colony = _make_colony(facilities=[fac1, fac2])
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        # fac1: 5% of 200 = 10, fac2: 5% of 400 = 20
        assert empire.resource_pool["Metals"] == pytest.approx(970.0)
        assert len(events) == 0

    # --- Facility scuttling ---

    def test_facility_scuttled_when_payment_fails(self):
        """Facility is removed from planet when empire can't afford maintenance."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 0.0})
        facility = _make_facility(design_data={
            "layers": {
                "CORE": {
                    "components": [
                        {"id": "comp_a", "resource_cost": {"Metals": 1000}}
                    ]
                }
            }
        })
        colony = _make_colony(facilities=[facility])
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        assert len(colony.facilities) == 0
        assert len(events) == 1
        assert events[0].entity_type == "facility"
        assert events[0].entity_name == "Test Facility"

    def test_scuttle_event_has_correct_fields(self):
        """ScuttleEvent has all expected fields."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 0.0})
        facility = _make_facility(
            name="Metals Harvester",
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 100}}]}}},
        )
        colony = _make_colony(facilities=[facility], name="Alpha Prime", planet_id=42)
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        assert len(events) == 1
        event = events[0]
        assert event.empire_id == 0
        assert event.entity_type == "facility"
        assert event.entity_name == "Metals Harvester"
        assert "Alpha Prime" in event.location

    # --- Non-operational facilities ---

    def test_non_operational_facility_no_maintenance(self):
        """Non-operational facilities have zero maintenance cost."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 0.0})  # No resources at all
        facility = _make_facility(
            is_operational=False,
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 1000}}]}}},
        )
        colony = _make_colony(facilities=[facility])
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        # Not scuttled despite no resources - non-operational is free
        assert len(colony.facilities) == 1
        assert len(events) == 0

    # --- Scuttle cascade prevention ---

    def test_scuttle_cascade_prevention(self):
        """One-pass processing prevents cascading scuttles.

        If facility A is paid for and facility B fails, the resources
        from A's maintenance should NOT retroactively save B.
        Each facility is evaluated independently in order.
        """
        engine = self._get_engine()
        # Enough for one facility but not two
        empire = _make_empire({"Metals": 15.0})
        fac1 = _make_facility(
            instance_id="fac_1", name="Cheap Facility",
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 200}}]}}},
        )  # cost: 10 Metals
        fac2 = _make_facility(
            instance_id="fac_2", name="Expensive Facility",
            design_data={"layers": {"CORE": {"components": [{"id": "b", "resource_cost": {"Metals": 400}}]}}},
        )  # cost: 20 Metals
        colony = _make_colony(facilities=[fac1, fac2])
        empire.colonies = [colony]

        events = engine.process_maintenance([empire])

        # fac1 paid (10), fac2 can't pay (need 20 but only 5 left) -> scuttled
        assert len(colony.facilities) == 1
        assert colony.facilities[0].instance_id == "fac_1"
        assert len(events) == 1
        assert events[0].entity_name == "Expensive Facility"
        assert empire.resource_pool["Metals"] == pytest.approx(5.0)

    # --- Ship maintenance ---

    def test_ship_maintenance_deducts_from_empire(self):
        """Ship maintenance deducts 5% of build cost from empire pool."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 1000.0, "Organics": 500.0})
        ship = _make_ship_instance(design_data={
            "layers": {
                "HULL": {
                    "components": [
                        {"id": "hull", "resource_cost": {"Metals": 500, "Organics": 100}}
                    ]
                }
            }
        })
        fleet = _make_fleet(ships=[ship])
        empire.fleets = [fleet]

        events = engine.process_maintenance([empire])

        # 5% of 500=25 Metals, 5% of 100=5 Organics
        assert empire.resource_pool["Metals"] == pytest.approx(975.0)
        assert empire.resource_pool["Organics"] == pytest.approx(495.0)
        assert len(events) == 0

    def test_ship_scuttled_when_payment_fails(self):
        """Ship is removed from fleet when empire can't afford maintenance."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 0.0})
        ship = _make_ship_instance(
            name="Doomed Scout",
            design_data={"layers": {"HULL": {"components": [{"id": "h", "resource_cost": {"Metals": 200}}]}}},
        )
        fleet = _make_fleet(ships=[ship])
        empire.fleets = [fleet]

        events = engine.process_maintenance([empire])

        assert len(fleet.ships) == 0
        assert len(events) == 1
        assert events[0].entity_type == "ship"
        assert events[0].entity_name == "Doomed Scout"

    def test_multiple_ships_in_fleet(self):
        """Multiple ships in a fleet are processed independently."""
        engine = self._get_engine()
        # Enough for ship1 (25 Metals) but not ship2 (50 Metals)
        empire = _make_empire({"Metals": 40.0})
        ship1 = _make_ship_instance(
            instance_id="s1", name="Cheap Ship",
            design_data={"layers": {"HULL": {"components": [{"id": "h", "resource_cost": {"Metals": 500}}]}}},
        )  # cost: 25 Metals
        ship2 = _make_ship_instance(
            instance_id="s2", name="Expensive Ship",
            design_data={"layers": {"HULL": {"components": [{"id": "h", "resource_cost": {"Metals": 1000}}]}}},
        )  # cost: 50 Metals
        fleet = _make_fleet(ships=[ship1, ship2])
        empire.fleets = [fleet]

        events = engine.process_maintenance([empire])

        assert len(fleet.ships) == 1
        assert fleet.ships[0].name == "Cheap Ship"
        assert len(events) == 1
        assert events[0].entity_name == "Expensive Ship"
        assert empire.resource_pool["Metals"] == pytest.approx(15.0)

    def test_empty_fleet_removed_after_scuttle(self):
        """Fleets with no ships remaining are cleaned up after scuttles."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 0.0})
        ship = _make_ship_instance(
            design_data={"layers": {"HULL": {"components": [{"id": "h", "resource_cost": {"Metals": 200}}]}}},
        )
        fleet = _make_fleet(ships=[ship])
        empire.fleets = [fleet]

        events = engine.process_maintenance([empire])

        # Fleet should be removed from empire
        assert len(empire.fleets) == 0
        assert len(events) == 1

    def test_empty_empire_no_crash(self):
        """Empire with no colonies and no fleets processes without error."""
        engine = self._get_engine()
        empire = _make_empire({})
        empire.colonies = []
        empire.fleets = []

        events = engine.process_maintenance([empire])

        assert len(events) == 0

    def test_multiple_empires_processed(self):
        """Multiple empires are all processed."""
        engine = self._get_engine()
        empire1 = _make_empire({"Metals": 1000.0}, empire_id=0)
        empire2 = _make_empire({"Metals": 1000.0}, empire_id=1)
        fac1 = _make_facility(
            instance_id="f1",
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 200}}]}}},
        )
        fac2 = _make_facility(
            instance_id="f2",
            design_data={"layers": {"CORE": {"components": [{"id": "b", "resource_cost": {"Metals": 400}}]}}},
        )
        empire1.colonies = [_make_colony(facilities=[fac1])]
        empire2.colonies = [_make_colony(facilities=[fac2])]

        events = engine.process_maintenance([empire1, empire2])

        assert empire1.resource_pool["Metals"] == pytest.approx(990.0)  # 5% of 200 = 10
        assert empire2.resource_pool["Metals"] == pytest.approx(980.0)  # 5% of 400 = 20
        assert len(events) == 0

    def test_facilities_and_ships_both_processed(self):
        """Both facilities and ships are charged maintenance in the same pass."""
        engine = self._get_engine()
        empire = _make_empire({"Metals": 1000.0})
        facility = _make_facility(
            design_data={"layers": {"CORE": {"components": [{"id": "a", "resource_cost": {"Metals": 200}}]}}},
        )
        ship = _make_ship_instance(
            design_data={"layers": {"HULL": {"components": [{"id": "h", "resource_cost": {"Metals": 400}}]}}},
        )
        colony = _make_colony(facilities=[facility])
        fleet = _make_fleet(ships=[ship])
        empire.colonies = [colony]
        empire.fleets = [fleet]

        events = engine.process_maintenance([empire])

        # fac: 5% of 200 = 10, ship: 5% of 400 = 20 => total 30
        assert empire.resource_pool["Metals"] == pytest.approx(970.0)
        assert len(events) == 0
