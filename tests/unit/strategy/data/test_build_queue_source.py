"""
Tests for BuildQueueSource dataclass and collect_build_queues_at_hex().

PROJ-69 Phase 1: Verifies queue discovery logic at hex locations.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_build_queues_at_hex,
    _facility_is_shipyard,
)
from game.strategy.data.planet import Planet, PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.data.hex_math import HexCoord


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_planet(name="Alpha Prime", hex_coord=HexCoord(5, 5), owner_id=0, planet_id=1) -> Planet:
    """Create a minimal planet for testing."""
    planet = Planet(
        name=name,
        location=hex_coord,
        orbit_distance=3,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        owner_id=owner_id,
        id=planet_id,
    )
    return planet


def _make_shipyard_facility(instance_id="yard-001", operational=True, queue=None) -> PlanetaryFacility:
    """Create a shipyard facility."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="orbital_shipyard",
        name="Orbital Shipyard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": {}}}
                ]
            }
        },
        is_operational=operational,
        construction_queue=queue if queue is not None else [],
    )


def _make_non_shipyard_facility(instance_id="fac-001") -> PlanetaryFacility:
    """Create a non-shipyard facility (e.g., power plant)."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="power_plant",
        name="Power Plant",
        design_data={"layers": {"hull": [{"id": "power_core"}]}},
        is_operational=True,
    )


def _make_fleet_with_yard(fleet_id=100, owner_id=0, location=HexCoord(5, 5)) -> Fleet:
    """Create a fleet with a space yard ship."""
    fleet = Fleet(fleet_id=fleet_id, owner_id=owner_id, location=location, speed=5.0)
    # Add a mock ship with fleet_space_yard component
    ship = MagicMock()
    ship.name = "Yard Ship"
    ship.is_combat_capable.return_value = True
    ship.design_data = {
        "layers": {
            "hull": [
                {"id": "fleet_space_yard", "abilities": {"SpaceShipyard": {}}}
            ]
        }
    }
    ship.mass = 100
    fleet.ships.append(ship)
    # Set speed directly to avoid triggering FleetSpeedCalculator
    fleet.speed = 5.0
    return fleet


def _make_fleet_without_yard(fleet_id=200, owner_id=0, location=HexCoord(5, 5)) -> Fleet:
    """Create a fleet without a space yard."""
    fleet = Fleet(fleet_id=fleet_id, owner_id=owner_id, location=location, speed=5.0)
    ship = MagicMock()
    ship.name = "Combat Ship"
    ship.is_combat_capable.return_value = True
    ship.design_data = {"layers": {"hull": [{"id": "laser_cannon"}]}}
    ship.mass = 50
    fleet.ships.append(ship)
    fleet.speed = 5.0
    return fleet


def _make_empire(empire_id=0, fleets=None) -> Empire:
    """Create an empire with given fleets."""
    empire = Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))
    if fleets:
        empire.fleets = fleets
    return empire


def _make_galaxy(planets_at_hex=None):
    """Create a mock galaxy with planet hex lookup."""
    galaxy = MagicMock()
    hex_planets = planets_at_hex or {}
    galaxy.get_planets_at_global_hex.side_effect = lambda h: hex_planets.get(h, [])
    return galaxy


# ---------------------------------------------------------------------------
# Tests: _facility_is_shipyard
# ---------------------------------------------------------------------------

class TestFacilityIsShipyard:
    """Test _facility_is_shipyard helper."""

    def test_shipyard_facility_detected(self):
        """Operational shipyard facility should be detected."""
        facility = _make_shipyard_facility()
        assert _facility_is_shipyard(facility) is True

    def test_non_shipyard_facility_not_detected(self):
        """Non-shipyard facility should not be detected."""
        facility = _make_non_shipyard_facility()
        assert _facility_is_shipyard(facility) is False

    def test_non_operational_shipyard_excluded(self):
        """Non-operational shipyard facility should not be detected."""
        facility = _make_shipyard_facility(operational=False)
        assert _facility_is_shipyard(facility) is False

    def test_shipyard_by_ability_only(self):
        """Facility with SpaceShipyard ability but different id is detected."""
        facility = PlanetaryFacility(
            instance_id="yard-alt",
            design_id="custom_yard",
            name="Custom Yard",
            design_data={
                "layers": {
                    "hull": [
                        {"id": "custom_component", "abilities": {"SpaceShipyard": {"level": 2}}}
                    ]
                }
            },
            is_operational=True,
        )
        assert _facility_is_shipyard(facility) is True

    def test_empty_design_data_not_shipyard(self):
        """Facility with empty design data should not be a shipyard."""
        facility = PlanetaryFacility(
            instance_id="empty-001",
            design_id="empty",
            name="Empty",
            design_data={},
            is_operational=True,
        )
        assert _facility_is_shipyard(facility) is False


# ---------------------------------------------------------------------------
# Tests: collect_build_queues_at_hex
# ---------------------------------------------------------------------------

class TestCollectBuildQueuesAtHex:
    """Test collect_build_queues_at_hex() function."""

    def test_planet_no_shipyards_returns_base_only(self):
        """Planet with 0 shipyards returns 1 source (base queue)."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 1
        assert sources[0].queue_id == "planet_1_base"
        assert sources[0].display_name == "Alpha Prime - Base"
        assert sources[0].can_build_ships is False
        assert sources[0].can_build_complexes is True
        assert sources[0].context_type == "planet"
        assert sources[0].construction_queue is planet.construction_queue

    def test_planet_with_two_shipyards_returns_three_sources(self):
        """Planet with 2 shipyards returns 3 sources (base + 2 shipyard)."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-001"))
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-002"))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 3
        # Base queue
        assert sources[0].queue_id == "planet_1_base"
        assert sources[0].can_build_ships is False
        # Shipyard 1
        assert sources[1].queue_id == "yard-001"
        assert sources[1].display_name == "Alpha Prime - Shipyard 1"
        assert sources[1].can_build_ships is True
        assert sources[1].can_build_complexes is True
        # Shipyard 2
        assert sources[2].queue_id == "yard-002"
        assert sources[2].display_name == "Alpha Prime - Shipyard 2"

    def test_fleet_with_space_yard_included(self):
        """Fleet with space yard at same hex included in results."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        fleet = _make_fleet_with_yard(location=hex_coord)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0, fleets=[fleet])

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 2  # base + fleet
        fleet_source = sources[1]
        assert fleet_source.queue_id == "fleet_100"
        assert "Space Yard" in fleet_source.display_name
        assert fleet_source.can_build_ships is True
        assert fleet_source.context_type == "fleet"

    def test_different_empire_planet_excluded(self):
        """Planet owned by different empire excluded from results."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, owner_id=1)  # Enemy planet
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)  # Player empire

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 0

    def test_non_operational_shipyard_excluded(self):
        """Non-operational shipyard facility excluded from results."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-broken", operational=False))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 1  # Only base queue, no shipyard
        assert sources[0].queue_id == "planet_1_base"

    def test_fleet_without_yard_excluded(self):
        """Fleet without space yard not included in results."""
        hex_coord = HexCoord(5, 5)
        fleet = _make_fleet_without_yard(location=hex_coord)
        galaxy = _make_galaxy({hex_coord: []})
        empire = _make_empire(empire_id=0, fleets=[fleet])

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 0

    def test_fleet_at_different_hex_excluded(self):
        """Fleet at different hex not included in results."""
        hex_coord = HexCoord(5, 5)
        other_hex = HexCoord(10, 10)
        fleet = _make_fleet_with_yard(location=other_hex)
        galaxy = _make_galaxy({hex_coord: []})
        empire = _make_empire(empire_id=0, fleets=[fleet])

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 0

    def test_empty_hex_returns_empty_list(self):
        """Hex with no planets or fleets returns empty list."""
        hex_coord = HexCoord(5, 5)
        galaxy = _make_galaxy({})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert sources == []

    def test_queue_references_are_shared(self):
        """BuildQueueSource construction_queue should reference the actual list."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-001"))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        # Base queue references planet.construction_queue
        assert sources[0].construction_queue is planet.construction_queue
        # Shipyard queue references facility.construction_queue
        assert sources[1].construction_queue is planet.facilities[0].construction_queue

    def test_mixed_facilities_only_shipyards_get_queues(self):
        """Only shipyard facilities get queue sources, not other facility types."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        planet.facilities.append(_make_non_shipyard_facility(instance_id="fac-001"))
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-001"))
        planet.facilities.append(_make_non_shipyard_facility(instance_id="fac-002"))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 2  # base + 1 shipyard
        assert sources[0].queue_id == "planet_1_base"
        assert sources[1].queue_id == "yard-001"
