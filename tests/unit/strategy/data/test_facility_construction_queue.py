"""
Tests for PlanetaryFacility construction_queue field.

PROJ-69 Phase 1: Verifies that facilities can have their own build queues
and that serialization round-trips correctly.
"""
import pytest
from game.strategy.data.planet import Planet, PlanetaryFacility
from game.core.hex_math import HexCoord


def _make_planet(**overrides) -> Planet:
    """Create a minimal planet for testing."""
    defaults = dict(
        name="Test Planet",
        location=HexCoord(0, 0),
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
        owner_id=0,
    )
    defaults.update(overrides)
    return Planet(**defaults)


def _make_shipyard_facility(instance_id: str = "yard-001", queue=None) -> PlanetaryFacility:
    """Create a shipyard facility with optional queue items."""
    facility = PlanetaryFacility(
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
        is_operational=True,
        construction_queue=queue if queue is not None else [],
    )
    return facility


class TestPlanetaryFacilityConstructionQueue:
    """Test PlanetaryFacility.construction_queue field."""

    def test_facility_defaults_to_empty_queue(self):
        """PlanetaryFacility should default to empty construction_queue."""
        facility = PlanetaryFacility(
            instance_id="test-001",
            design_id="power_plant",
            name="Power Plant",
            design_data={"layers": {}},
        )
        assert facility.construction_queue == []

    def test_facility_accepts_queue_items(self):
        """PlanetaryFacility should accept construction_queue items."""
        queue = [
            {"design_id": "frigate", "type": "ship", "turns_remaining": 3},
            {"design_id": "destroyer", "type": "ship", "turns_remaining": 5},
        ]
        facility = _make_shipyard_facility(queue=queue)
        assert len(facility.construction_queue) == 2
        assert facility.construction_queue[0]["design_id"] == "frigate"
        assert facility.construction_queue[1]["turns_remaining"] == 5


class TestFacilityQueueSerialization:
    """Test Planet.to_dict()/from_dict() with facility construction_queue."""

    def test_facility_queue_serializes_in_to_dict(self):
        """Planet.to_dict() should include facility construction_queue."""
        planet = _make_planet()
        queue = [{"design_id": "frigate", "type": "ship", "turns_remaining": 3}]
        facility = _make_shipyard_facility(queue=queue)
        planet.facilities.append(facility)

        data = planet.to_dict()
        facility_data = data["facilities"][0]
        assert "construction_queue" in facility_data
        assert len(facility_data["construction_queue"]) == 1
        assert facility_data["construction_queue"][0]["design_id"] == "frigate"

    def test_facility_queue_roundtrips_via_from_dict(self):
        """Planet.from_dict() should restore facility construction_queue."""
        planet = _make_planet()
        queue = [
            {"design_id": "frigate", "type": "ship", "turns_remaining": 3},
            {"design_id": "carrier", "type": "ship", "turns_remaining": 8},
        ]
        facility = _make_shipyard_facility(queue=queue)
        planet.facilities.append(facility)

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert len(restored.facilities) == 1
        restored_queue = restored.facilities[0].construction_queue
        assert len(restored_queue) == 2
        assert restored_queue[0]["design_id"] == "frigate"
        assert restored_queue[1]["design_id"] == "carrier"
        assert restored_queue[0]["turns_remaining"] == 3

    def test_facility_without_queue_in_save_defaults_to_empty(self):
        """from_dict() with old save data (no construction_queue) defaults to empty list."""
        planet = _make_planet()
        data = planet.to_dict()
        # Simulate old save format without construction_queue in facility
        data["facilities"] = [
            {
                "instance_id": "old-001",
                "design_id": "power_plant",
                "name": "Power Plant",
                "design_data": {"layers": {}},
                "is_operational": True,
                # No construction_queue key
            }
        ]
        restored = Planet.from_dict(data)
        assert restored.facilities[0].construction_queue == []

    def test_empty_facility_queue_serializes(self):
        """Empty construction_queue should serialize as empty list."""
        planet = _make_planet()
        facility = _make_shipyard_facility(queue=[])
        planet.facilities.append(facility)

        data = planet.to_dict()
        assert data["facilities"][0]["construction_queue"] == []

    def test_serialized_queue_is_independent_copy(self):
        """Serialized queue should be a copy, not a reference."""
        planet = _make_planet()
        queue = [{"design_id": "frigate", "type": "ship", "turns_remaining": 3}]
        facility = _make_shipyard_facility(queue=queue)
        planet.facilities.append(facility)

        data = planet.to_dict()
        # Mutate original
        facility.construction_queue.append({"design_id": "extra", "type": "ship", "turns_remaining": 1})
        # Serialized data should not be affected
        assert len(data["facilities"][0]["construction_queue"]) == 1


class TestFacilityConstructionQueuePaused:
    """FEAT-17 — PlanetaryFacility.construction_queue_paused round-trips."""

    def test_facility_defaults_paused_to_false(self):
        facility = _make_shipyard_facility()
        assert facility.construction_queue_paused is False

    def test_facility_paused_round_trips_via_planet_dict(self):
        planet = _make_planet()
        facility = _make_shipyard_facility()
        facility.construction_queue_paused = True
        planet.facilities.append(facility)

        data = planet.to_dict()
        assert data["facilities"][0]["construction_queue_paused"] is True

        restored = Planet.from_dict(data)
        assert restored.facilities[0].construction_queue_paused is True

    def test_facility_unpaused_round_trips_via_planet_dict(self):
        planet = _make_planet()
        facility = _make_shipyard_facility()
        facility.construction_queue_paused = False
        planet.facilities.append(facility)

        data = planet.to_dict()
        restored = Planet.from_dict(data)
        assert restored.facilities[0].construction_queue_paused is False

    def test_legacy_save_without_paused_key_defaults_to_false(self):
        """Save written before FEAT-17 must load with paused=False."""
        planet = _make_planet()
        data = planet.to_dict()
        data["facilities"] = [
            {
                "instance_id": "old-001",
                "design_id": "power_plant",
                "name": "Power Plant",
                "design_data": {"layers": {}},
                "is_operational": True,
                # No construction_queue_paused key
            }
        ]
        restored = Planet.from_dict(data)
        assert restored.facilities[0].construction_queue_paused is False
