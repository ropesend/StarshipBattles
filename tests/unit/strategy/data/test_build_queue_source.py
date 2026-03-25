"""
Tests for BuildQueueSource dataclass and collect_build_queues_at_hex().

PROJ-69 Phase 1: Verifies queue discovery logic at hex locations.
PROJ-97 Phase 2: Updated for per-resource production rates (Dict[str, float]).
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_build_queues_at_hex,
    collect_all_build_queues_for_empire,
    get_default_production_rates,
    get_production_rate_for_queue,
    estimate_build_turns,
)
from game.strategy.data.planet import Planet, PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


# Expected production rates from data/production_rates.json
EXPECTED_PLANETARY_RATES = {
    "Metals": 2000, "Organics": 2000, "Radioactives": 2000,
    "Vapors": 2000, "Exotics": 2000
}
EXPECTED_SHIPYARD_RATES = {
    "Metals": 3000, "Organics": 3000, "Radioactives": 3000,
    "Vapors": 3000, "Exotics": 3000
}
EXPECTED_FLEET_RATES = {
    "Metals": 3000, "Organics": 3000, "Radioactives": 3000,
    "Vapors": 3000, "Exotics": 3000
}


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


def _make_shipyard_facility(
    instance_id="yard-001",
    operational=True,
    queue=None,
    production_rates=None,
    construction_speed_bonus=None
) -> PlanetaryFacility:
    """Create a shipyard facility.

    Args:
        instance_id: Unique ID for the facility.
        operational: Whether facility is operational.
        queue: Construction queue list.
        production_rates: Optional per-resource rates dict for SpaceShipyard ability.
        construction_speed_bonus: Optional speed bonus multiplier.
    """
    shipyard_ability_data = {}
    if production_rates is not None:
        shipyard_ability_data["production_rates"] = production_rates
    if construction_speed_bonus is not None:
        shipyard_ability_data["construction_speed_bonus"] = construction_speed_bonus

    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="orbital_shipyard",
        name="Orbital Shipyard",
        design_data={
            "layers": {
                "hull": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": shipyard_ability_data}}
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
# Tests: PlanetaryFacility.is_shipyard (via property, not wrapper function)
# ---------------------------------------------------------------------------

class TestFacilityIsShipyard:
    """Test PlanetaryFacility.is_shipyard property."""

    def test_shipyard_facility_detected(self):
        """Operational shipyard facility should be detected."""
        facility = _make_shipyard_facility()
        assert facility.is_shipyard is True

    def test_non_shipyard_facility_not_detected(self):
        """Non-shipyard facility should not be detected."""
        facility = _make_non_shipyard_facility()
        assert facility.is_shipyard is False

    def test_non_operational_shipyard_excluded(self):
        """Non-operational shipyard facility should not be detected."""
        facility = _make_shipyard_facility(operational=False)
        assert facility.is_shipyard is False

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
        assert facility.is_shipyard is True

    def test_empty_design_data_not_shipyard(self):
        """Facility with empty design data should not be a shipyard."""
        facility = PlanetaryFacility(
            instance_id="empty-001",
            design_id="empty",
            name="Empty",
            design_data={},
            is_operational=True,
        )
        assert facility.is_shipyard is False


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
        assert sources[0].display_name == "Alpha Prime - Planetary Yard"
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
        assert fleet_source.queue_id == "fleet_100_yard_1"
        assert "Shipyard" in fleet_source.display_name
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


# ---------------------------------------------------------------------------
# Tests: collect_all_build_queues_for_empire
# ---------------------------------------------------------------------------

class TestCollectAllBuildQueuesForEmpire:
    """Test collect_all_build_queues_for_empire() function."""

    def test_collect_all_build_queues_empty_empire(self):
        """Empty empire with no colonies or fleets returns empty list."""
        empire = _make_empire(empire_id=0, fleets=[])
        empire.colonies = []

        sources = collect_all_build_queues_for_empire(empire)

        assert sources == []

    def test_collect_all_build_queues_with_planet_base_queue(self):
        """Planet colony gets a base queue (complexes only)."""
        planet = _make_planet(name="Colony Alpha", planet_id=42, owner_id=0)
        empire = _make_empire(empire_id=0)
        empire.colonies = [planet]

        sources = collect_all_build_queues_for_empire(empire)

        assert len(sources) == 1
        assert sources[0].queue_id == "planet_42_base"
        assert sources[0].display_name == "Colony Alpha - Planetary Yard"
        assert sources[0].owner_entity is planet
        assert sources[0].construction_queue is planet.construction_queue
        assert sources[0].can_build_ships is False
        assert sources[0].can_build_complexes is True
        assert sources[0].context_type == "planet"

    def test_collect_all_build_queues_with_shipyard_facility(self):
        """Planet with shipyard facility returns base + shipyard sources."""
        planet = _make_planet(name="Forge World", planet_id=7, owner_id=0)
        yard = _make_shipyard_facility(instance_id="yard-100")
        planet.facilities.append(yard)
        empire = _make_empire(empire_id=0)
        empire.colonies = [planet]

        sources = collect_all_build_queues_for_empire(empire)

        assert len(sources) == 2
        # Base queue
        assert sources[0].queue_id == "planet_7_base"
        assert sources[0].can_build_ships is False
        # Shipyard queue
        assert sources[1].queue_id == "yard-100"
        assert sources[1].display_name == "Forge World - Shipyard 1"
        assert sources[1].can_build_ships is True
        assert sources[1].can_build_complexes is True
        assert sources[1].construction_queue is yard.construction_queue

    def test_collect_all_build_queues_with_fleet_space_yard(self):
        """Fleet with space yard returns a fleet source."""
        fleet = _make_fleet_with_yard(fleet_id=555, owner_id=0, location=HexCoord(3, 3))
        empire = _make_empire(empire_id=0, fleets=[fleet])
        empire.colonies = []

        sources = collect_all_build_queues_for_empire(empire)

        assert len(sources) == 1
        assert sources[0].queue_id == "fleet_555_yard_1"
        assert "Shipyard" in sources[0].display_name
        assert sources[0].owner_entity is fleet
        assert sources[0].construction_queue is fleet.construction_queue
        assert sources[0].can_build_ships is True
        assert sources[0].context_type == "fleet"

    def test_collect_all_build_queues_mixed_sources(self):
        """Multiple planets and fleets produce correct combined result."""
        planet1 = _make_planet(name="Alpha", planet_id=1, owner_id=0)
        planet2 = _make_planet(name="Beta", planet_id=2, owner_id=0)
        planet2.facilities.append(_make_shipyard_facility(instance_id="yard-a"))
        planet2.facilities.append(_make_shipyard_facility(instance_id="yard-b"))

        fleet1 = _make_fleet_with_yard(fleet_id=300, owner_id=0, location=HexCoord(1, 1))
        fleet2 = _make_fleet_without_yard(fleet_id=400, owner_id=0, location=HexCoord(2, 2))

        empire = _make_empire(empire_id=0, fleets=[fleet1, fleet2])
        empire.colonies = [planet1, planet2]

        sources = collect_all_build_queues_for_empire(empire)

        # planet1 base + planet2 base + 2 shipyards + 1 fleet = 5
        assert len(sources) == 5

        queue_ids = [s.queue_id for s in sources]
        assert "planet_1_base" in queue_ids
        assert "planet_2_base" in queue_ids
        assert "yard-a" in queue_ids
        assert "yard-b" in queue_ids
        assert "fleet_300_yard_1" in queue_ids
        # Fleet without yard should NOT appear
        assert "fleet_400" not in queue_ids

    def test_collect_all_build_queues_non_operational_shipyard_excluded(self):
        """Non-operational shipyard on colony is excluded."""
        planet = _make_planet(name="Damaged", planet_id=9, owner_id=0)
        planet.facilities.append(_make_shipyard_facility(instance_id="broken-yard", operational=False))
        empire = _make_empire(empire_id=0)
        empire.colonies = [planet]

        sources = collect_all_build_queues_for_empire(empire)

        assert len(sources) == 1  # Only base queue
        assert sources[0].queue_id == "planet_9_base"

    def test_collect_all_build_queues_fleet_without_yard_excluded(self):
        """Fleet without space yard is not included."""
        fleet = _make_fleet_without_yard(fleet_id=999, owner_id=0, location=HexCoord(0, 0))
        empire = _make_empire(empire_id=0, fleets=[fleet])
        empire.colonies = []

        sources = collect_all_build_queues_for_empire(empire)

        assert sources == []


# ---------------------------------------------------------------------------
# Tests: New fields - build_rate and planet_id (PROJ-79)
# ---------------------------------------------------------------------------

class TestBuildQueueSourceNewFields:
    """Test build_rate and planet_id fields added in PROJ-79."""

    def test_build_queue_source_has_build_rate_default(self):
        """BuildQueueSource defaults build_rate to empty dict."""
        source = BuildQueueSource(
            queue_id="test",
            display_name="Test",
            owner_entity=None,
            construction_queue=[],
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
        )
        assert source.build_rate == {}

    def test_build_queue_source_has_planet_id_default(self):
        """BuildQueueSource defaults planet_id to None."""
        source = BuildQueueSource(
            queue_id="test",
            display_name="Test",
            owner_entity=None,
            construction_queue=[],
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
        )
        assert source.planet_id is None

    def test_collect_queues_sets_base_build_rate(self):
        """Base (Planetary Yard) queue has per-resource build rates from JSON."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=99)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 1
        assert sources[0].build_rate == EXPECTED_PLANETARY_RATES

    def test_collect_queues_sets_shipyard_build_rate(self):
        """Shipyard facility queue has per-resource rates from JSON defaults."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=99)
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-001"))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        # Sources: base + shipyard
        assert len(sources) == 2
        shipyard_source = sources[1]
        assert shipyard_source.build_rate == EXPECTED_SHIPYARD_RATES

    def test_collect_queues_sets_shipyard_build_rate_with_bonus(self):
        """Shipyard with construction_speed_bonus applies multiplier to all resources."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=99)
        # Create facility with construction_speed_bonus = 1.5
        facility = _make_shipyard_facility(
            instance_id="yard-boosted",
            construction_speed_bonus=1.5
        )
        planet.facilities.append(facility)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        shipyard_source = sources[1]
        # All resources should be 3000 * 1.5 = 4500
        expected_boosted = {res: rate * 1.5 for res, rate in EXPECTED_SHIPYARD_RATES.items()}
        assert shipyard_source.build_rate == expected_boosted

    def test_collect_queues_sets_fleet_build_rate(self):
        """Fleet shipyard queue has per-resource rates from JSON."""
        hex_coord = HexCoord(5, 5)
        fleet = _make_fleet_with_yard(location=hex_coord)
        galaxy = _make_galaxy({hex_coord: []})
        empire = _make_empire(empire_id=0, fleets=[fleet])

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert len(sources) == 1
        assert sources[0].build_rate == EXPECTED_FLEET_RATES

    def test_collect_queues_sets_planet_id_for_planet_sources(self):
        """Planet-based sources have planet_id set to planet.id."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=42)
        planet.facilities.append(_make_shipyard_facility(instance_id="yard-001"))
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        # Base queue
        assert sources[0].planet_id == 42
        # Shipyard queue
        assert sources[1].planet_id == 42

    def test_collect_queues_sets_planet_id_none_for_fleet(self):
        """Fleet-based sources have planet_id = None."""
        hex_coord = HexCoord(5, 5)
        fleet = _make_fleet_with_yard(location=hex_coord)
        galaxy = _make_galaxy({hex_coord: []})
        empire = _make_empire(empire_id=0, fleets=[fleet])

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        assert sources[0].planet_id is None

    def test_collect_queues_uses_explicit_production_rates(self):
        """Shipyard with explicit production_rates in design uses those rates."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=99)
        # Create facility with custom production rates
        custom_rates = {"Metals": 5000, "Organics": 4000, "Exotics": 1000}
        facility = _make_shipyard_facility(
            instance_id="yard-custom",
            production_rates=custom_rates
        )
        planet.facilities.append(facility)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        shipyard_source = sources[1]
        assert shipyard_source.build_rate == custom_rates

    def test_collect_queues_explicit_rates_with_bonus(self):
        """Explicit production_rates combined with construction_speed_bonus."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord, planet_id=99)
        # Custom rates with 2x bonus
        custom_rates = {"Metals": 1000, "Organics": 500}
        facility = _make_shipyard_facility(
            instance_id="yard-custom-boosted",
            production_rates=custom_rates,
            construction_speed_bonus=2.0
        )
        planet.facilities.append(facility)
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)

        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)

        shipyard_source = sources[1]
        expected = {"Metals": 2000, "Organics": 1000}  # 1000*2, 500*2
        assert shipyard_source.build_rate == expected


# ---------------------------------------------------------------------------
# Tests: get_default_production_rates (PROJ-97)
# ---------------------------------------------------------------------------

class TestGetDefaultProductionRates:
    """Test get_default_production_rates() function."""

    def test_planetary_yard_rates(self):
        """planetary_yard returns 2000 for all resources."""
        rates = get_default_production_rates("planetary_yard")
        assert rates == EXPECTED_PLANETARY_RATES

    def test_space_shipyard_rates(self):
        """space_shipyard returns 3000 for all resources."""
        rates = get_default_production_rates("space_shipyard")
        assert rates == EXPECTED_SHIPYARD_RATES

    def test_fleet_space_yard_rates(self):
        """fleet_space_yard returns 3000 for all resources."""
        rates = get_default_production_rates("fleet_space_yard")
        assert rates == EXPECTED_FLEET_RATES

    def test_unknown_yard_type_returns_empty(self):
        """Unknown yard type returns empty dict."""
        rates = get_default_production_rates("unknown_yard")
        assert rates == {}

    def test_returns_copy_not_reference(self):
        """get_default_production_rates returns a copy, not original dict."""
        rates1 = get_default_production_rates("planetary_yard")
        rates2 = get_default_production_rates("planetary_yard")
        rates1["Metals"] = 9999
        # Original should be unchanged
        assert rates2["Metals"] == 2000


# ---------------------------------------------------------------------------
# Tests: estimate_build_turns (BUG-96 refactor)
# ---------------------------------------------------------------------------

class TestEstimateBuildTurns:
    """Test estimate_build_turns() — single source of truth for turn estimation."""

    def test_limiting_resource_determines_turns(self):
        """Picks the slowest (limiting) resource."""
        # Metals: 8000/2000 = 4 turns, Electronics: 500/1000 = 0.5 turns → 4.0
        result = estimate_build_turns(
            {"metals": 8000.0, "electronics": 500.0},
            {"metals": 2000.0, "electronics": 1000.0}
        )
        assert result == 4.0

    def test_single_resource(self):
        """Works with a single resource."""
        result = estimate_build_turns(
            {"metals": 3000.0},
            {"metals": 1000.0}
        )
        assert result == 3.0

    def test_fallback_on_empty_cost(self):
        """Returns 1.0 if total_cost is empty."""
        result = estimate_build_turns({}, {"metals": 1000.0})
        assert result == 1.0

    def test_fallback_on_empty_rate(self):
        """Returns 1.0 if production_rate is empty."""
        result = estimate_build_turns({"metals": 1000.0}, {})
        assert result == 1.0

    def test_fallback_on_zero_rate(self):
        """Returns 1.0 if any required resource has zero production rate."""
        result = estimate_build_turns(
            {"metals": 1000.0}, {"metals": 0.0}
        )
        assert result == 1.0

    def test_fallback_on_missing_rate(self):
        """Returns 1.0 if a required resource has no matching rate entry."""
        result = estimate_build_turns(
            {"metals": 1000.0}, {"organics": 2000.0}
        )
        assert result == 1.0

    def test_zero_cost_resources_ignored(self):
        """Resources with zero cost are skipped."""
        result = estimate_build_turns(
            {"metals": 2000.0, "organics": 0.0},
            {"metals": 1000.0, "organics": 1000.0}
        )
        assert result == 2.0

    def test_minimum_return_value(self):
        """Never returns less than 0.01."""
        result = estimate_build_turns(
            {"metals": 1.0},
            {"metals": 1000000.0}
        )
        assert result >= 0.01


# ---------------------------------------------------------------------------
# Tests: get_production_rate_for_queue (BUG-96 refactor)
# ---------------------------------------------------------------------------

class TestGetProductionRateForQueue:
    """Test get_production_rate_for_queue() — unified rate resolution."""

    def test_planet_base_queue_returns_planetary_yard_rate(self):
        """Planet with no queue_id returns planetary yard rate."""
        planet = _make_planet()
        rate = get_production_rate_for_queue(planet, None)
        assert rate == EXPECTED_PLANETARY_RATES

    def test_planet_base_queue_with_explicit_id(self):
        """Planet base queue identified by planet_N_base pattern returns planetary rate."""
        planet = _make_planet(planet_id=5)
        rate = get_production_rate_for_queue(planet, "planet_5_base")
        # No facility matches this id, falls through to default
        assert rate == EXPECTED_PLANETARY_RATES

    def test_planet_shipyard_facility_queue(self):
        """Planet facility queue returns that facility's production rate."""
        planet = _make_planet()
        facility = _make_shipyard_facility(instance_id="yard-001")
        planet.facilities.append(facility)
        rate = get_production_rate_for_queue(planet, "yard-001")
        assert rate == EXPECTED_SHIPYARD_RATES

    def test_planet_shipyard_with_bonus(self):
        """Facility with construction_speed_bonus applies multiplier."""
        planet = _make_planet()
        facility = _make_shipyard_facility(
            instance_id="yard-fast", construction_speed_bonus=2.0
        )
        planet.facilities.append(facility)
        rate = get_production_rate_for_queue(planet, "yard-fast")
        expected = {res: val * 2.0 for res, val in EXPECTED_SHIPYARD_RATES.items()}
        assert rate == expected

    def test_fleet_returns_fleet_yard_rate(self):
        """Fleet returns fleet_space_yard rate."""
        fleet = _make_fleet_with_yard()
        rate = get_production_rate_for_queue(fleet, None)
        assert rate == EXPECTED_FLEET_RATES

    def test_fleet_multi_yard_multiplies_rate(self):
        """Fleet with multiple yards multiplies rate by yard count."""
        fleet = MagicMock()
        fleet.capabilities.space_shipyard_count = 2
        from game.strategy.data.fleet import Fleet
        # Make isinstance check pass
        fleet.__class__ = Fleet

        rate = get_production_rate_for_queue(fleet, None)
        expected = {res: val * 2 for res, val in EXPECTED_FLEET_RATES.items()}
        assert rate == expected

    def test_matches_collect_planet_sources_rate(self):
        """Rate for a facility queue matches what _collect_planet_sources produces."""
        hex_coord = HexCoord(5, 5)
        planet = _make_planet(hex_coord=hex_coord)
        facility = _make_shipyard_facility(
            instance_id="yard-verify", construction_speed_bonus=1.5
        )
        planet.facilities.append(facility)

        # Get rate via the new utility
        direct_rate = get_production_rate_for_queue(planet, "yard-verify")

        # Get rate via collect path
        galaxy = _make_galaxy({hex_coord: [planet]})
        empire = _make_empire(empire_id=0)
        sources = collect_build_queues_at_hex(hex_coord, galaxy, empire)
        shipyard_source = [s for s in sources if s.queue_id == "yard-verify"][0]

        assert direct_rate == shipyard_source.build_rate
