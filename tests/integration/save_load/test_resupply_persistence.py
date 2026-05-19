"""Tests for resupply-related data persistence across save/load cycles.

PROJ-74 Phase 6: Verify that facility fuel levels and partial ship fuel
levels survive serialization round-trips (to_dict/from_dict and full
save/load service).
"""
import pytest
from unittest.mock import patch

from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.ship_instance import ShipInstance
from game.core.hex_math import HexCoord
from game.strategy.systems.save_game_service import SaveGameService
from game.core import paths as paths_module


# ===========================================================================
# Unit-level serialization round-trips
# ===========================================================================

class TestFacilityFuelPersistence:
    """Verify PlanetaryFacility fuel levels survive serialization."""

    def test_facility_fuel_persists_via_planet_round_trip(self):
        """Facility fuel levels survive Planet to_dict → from_dict cycle."""
        facility = PlanetaryFacility(
            instance_id="fuel-001",
            design_id="fuel_depot",
            name="Fuel Depot",
            design_data={"layers": {"hull": [{"id": "fuel_synthesizer"}, {"id": "fuel_tank"}]}},
            is_operational=True,
        )
        facility.consumable_levels = {"fuel": 347.5}

        planet = Planet(
            name="TestWorld",
            location=HexCoord(3, 4),
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
            owner_id=0,
        )
        planet.id = 42
        planet.facilities = [facility]

        # Round trip
        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert len(restored.facilities) == 1
        assert restored.facilities[0].consumable_levels.get("fuel") == pytest.approx(347.5)
        assert restored.facilities[0].instance_id == "fuel-001"
        assert restored.facilities[0].is_operational is True

    def test_facility_empty_fuel_persists(self):
        """Facility with zero fuel (empty dict) survives round-trip."""
        facility = PlanetaryFacility(
            instance_id="fuel-002",
            design_id="fuel_depot",
            name="Empty Depot",
            design_data={"layers": {"hull": [{"id": "fuel_tank"}]}},
        )
        # consumable_levels defaults to {} (no fuel key)

        planet = Planet(
            name="EmptyWorld",
            location=HexCoord(1, 1),
            orbit_distance=2,
            mass=1e24,
            radius=3e6,
            surface_area=1e14,
            density=4000.0,
            surface_gravity=5.0,
            surface_pressure=50000.0,
            surface_temperature=250.0,
            surface_water=0.2,
            tectonic_activity=0.1,
            magnetic_field=0.5,
            planet_type=PlanetType.BARREN,
            owner_id=0,
        )
        planet.id = 43
        planet.facilities = [facility]

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert len(restored.facilities) == 1
        assert restored.facilities[0].consumable_levels == {}
        assert restored.facilities[0].get_fuel_storage() == 0.0

    def test_facility_design_data_persists(self):
        """Facility design_data (component layout) persists for fuel calculations."""
        design = {
            "layers": {
                "hull": [
                    {"id": "fuel_synthesizer"},
                    {"id": "fuel_tank"},
                ]
            }
        }
        facility = PlanetaryFacility(
            instance_id="fuel-003",
            design_id="fuel_depot",
            name="Design Test",
            design_data=design,
            consumable_levels={"fuel": 100.0},
        )

        planet = Planet(
            name="DesignWorld",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=1e24,
            radius=3e6,
            surface_area=1e14,
            density=4000.0,
            surface_gravity=5.0,
            surface_pressure=50000.0,
            surface_temperature=250.0,
            surface_water=0.0,
            tectonic_activity=0.0,
            magnetic_field=0.0,
            planet_type=PlanetType.BARREN,
            owner_id=0,
        )
        planet.id = 44
        planet.facilities = [facility]

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        restored_facility = restored.facilities[0]
        # Design data must be preserved so ResupplyEngine can calculate rates
        assert "fuel_synthesizer" in str(restored_facility.design_data)
        assert "fuel_tank" in str(restored_facility.design_data)
        hull_layer = restored_facility.design_data["layers"]["hull"]
        comp_ids = [c["id"] for c in hull_layer]
        assert "fuel_synthesizer" in comp_ids
        assert "fuel_tank" in comp_ids


class TestShipFuelPersistence:
    """Verify partial ship fuel levels survive serialization."""

    def test_partial_fuel_persists_via_ship_round_trip(self):
        """ShipInstance with partial fuel survives to_dict → from_dict cycle."""
        ship = ShipInstance(
            instance_id="ship-001",
            design_id="destroyer",
            name="ISS Falcon",
            owner_id=0,
            design_data={"name": "Destroyer", "layers": {}},
        )
        ship._consumable_levels = {"fuel": 250.0}

        data = ship.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.consumable_levels.get("fuel") == pytest.approx(250.0)
        assert restored.instance_id == "ship-001"

    def test_full_fuel_ship_persists_empty_resources(self):
        """Ship at full fuel (no consumable_levels entry) round-trips correctly."""
        ship = ShipInstance(
            instance_id="ship-002",
            design_id="scout",
            name="ISS Swift",
            owner_id=0,
            design_data={"name": "Scout", "layers": {}},
        )
        # No consumable_levels entry = full fuel

        data = ship.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.consumable_levels == {}

    def test_multiple_resources_persist(self):
        """Ship with multiple partial resources all persist."""
        ship = ShipInstance(
            instance_id="ship-003",
            design_id="cruiser",
            name="ISS Titan",
            owner_id=0,
            design_data={"name": "Cruiser", "layers": {}},
        )
        ship._consumable_levels = {"fuel": 100.0, "energy": 75.5}

        data = ship.to_dict()
        restored = ShipInstance.from_dict(data)

        assert restored.consumable_levels.get("fuel") == pytest.approx(100.0)
        assert restored.consumable_levels.get("energy") == pytest.approx(75.5)


# ===========================================================================
# Full save/load service tests
# ===========================================================================

class TestResupplyStateSaveLoad:
    """Verify resupply state survives a full save/load cycle via SaveGameService."""

    def test_facility_fuel_persists_across_save_load(
        self, game_session_with_state, temp_save_folder
    ):
        """Facility fuel levels survive a full game save → load cycle."""
        session = game_session_with_state

        # F-A-029: deterministic — the `game_session_with_state` fixture
        # uses default players=2 over `system_count=2`, so every empire
        # gets a home colony. Assert that invariant rather than skip.
        target_planet = None
        for empire in session.empires:
            if empire.colonies:
                target_planet = empire.colonies[0]
                break
        assert target_planet is not None, (
            "Fixture invariant: at least one empire must have a home colony."
        )

        # Add a fuel facility with specific fuel level
        facility = PlanetaryFacility(
            instance_id="save-test-fuel-001",
            design_id="fuel_depot",
            name="Save Test Fuel Depot",
            design_data={"layers": {"hull": [{"id": "fuel_synthesizer"}, {"id": "fuel_tank"}]}},
            consumable_levels={"fuel": 273.5},
        )
        target_planet.facilities.append(facility)

        # Save
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(session, save_name="resupply_test")
            assert success, f"Save failed: {message}"

            # Load
            loaded_session, load_msg = SaveGameService.load_game(save_path)

        assert loaded_session is not None, f"Load failed: {load_msg}"

        # Find the facility in the loaded session
        found = False
        for empire in loaded_session.empires:
            for colony in empire.colonies:
                for fac in colony.facilities:
                    if fac.instance_id == "save-test-fuel-001":
                        assert fac.consumable_levels.get("fuel") == pytest.approx(273.5)
                        assert fac.name == "Save Test Fuel Depot"
                        found = True
                        break

        assert found, "Facility not found in loaded session"

    def test_partial_fuel_ships_persist_across_save_load(
        self, game_session_with_state, temp_save_folder
    ):
        """Partial ship fuel levels survive a full game save → load cycle."""
        session = game_session_with_state

        # F-A-029: deterministic — `game_session_with_state` explicitly
        # adds two fleets (fleet1 + fleet2) each with one mock ship; the
        # invariant is guaranteed by the fixture, not by RNG.
        target_fleet = None
        for empire in session.empires:
            if empire.fleets:
                target_fleet = empire.fleets[0]
                break
        assert target_fleet is not None, (
            "Fixture invariant: at least one empire must have a fleet."
        )
        assert target_fleet.ships, (
            "Fixture invariant: the seeded fleet must contain at least one ship."
        )

        # Set partial fuel on the first ship
        target_ship = target_fleet.ships[0]
        target_ship.consumable_levels["fuel"] = 123.4
        ship_id = target_ship.instance_id

        # Save
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(session, save_name="fuel_test")
            assert success, f"Save failed: {message}"

            # Load
            loaded_session, load_msg = SaveGameService.load_game(save_path)

        assert loaded_session is not None, f"Load failed: {load_msg}"

        # Find the ship in the loaded session
        found = False
        for empire in loaded_session.empires:
            for fleet in empire.fleets:
                for ship in fleet.ships:
                    if ship.instance_id == ship_id:
                        assert ship.consumable_levels.get("fuel") == pytest.approx(123.4)
                        found = True
                        break

        assert found, "Ship not found in loaded session"
