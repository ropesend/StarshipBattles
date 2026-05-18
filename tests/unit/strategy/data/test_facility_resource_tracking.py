"""
Tests for PlanetaryFacility resource tracking.

PROJ-74 Phase 2: Verifies that facilities can track fuel storage levels,
serialize/deserialize consumable_levels, and use helper methods for
fuel operations.
"""
import pytest
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet
from game.strategy.data.planetary_facility import PlanetaryFacility
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


def _make_fuel_facility(
    instance_id: str = "fuel-001",
    fuel_storage_amount: float = 500.0,
    has_synthesizer: bool = True,
    consumable_levels: dict = None,
) -> PlanetaryFacility:
    """Create a facility with fuel tank and optional fuel synthesizer."""
    components = []
    if has_synthesizer:
        components.append({
            "id": "fuel_synthesizer",
            "abilities": {"ResourceGeneration": [{"resource": "fuel", "amount": 300}]},
        })
    components.append({
        "id": "fuel_tank",
        "abilities": {"ResourceStorage": [{"resource": "fuel", "amount": fuel_storage_amount}]},
    })
    facility = PlanetaryFacility(
        instance_id=instance_id,
        design_id="fuel_depot",
        name="Fuel Depot",
        design_data={"layers": {"hull": components}},
        is_operational=True,
    )
    if consumable_levels is not None:
        facility.consumable_levels = consumable_levels.copy()
    return facility


def _make_mock_registries(fuel_tank_amount: float = 500.0):
    """Create mock registries with a fuel_tank component that has ResourceStorage."""
    registries = MagicMock()

    # Create component definitions
    fuel_tank_comp = MagicMock()
    fuel_tank_comp.abilities = {
        "ResourceStorage": [{"resource": "fuel", "amount": fuel_tank_amount}],
    }

    fuel_synth_comp = MagicMock()
    fuel_synth_comp.abilities = {
        "ResourceGeneration": [{"resource": "fuel", "amount": 300}],
    }

    def get_component(comp_id):
        if comp_id == "fuel_tank":
            return fuel_tank_comp
        if comp_id == "fuel_synthesizer":
            return fuel_synth_comp
        return None

    registries.components.get = get_component
    return registries


# ===========================================================================
# Task 2.1: consumable_levels field
# ===========================================================================

class TestFacilityResourceLevelsField:
    """Test PlanetaryFacility.consumable_levels field."""

    def test_facility_defaults_to_empty_consumable_levels(self):
        """PlanetaryFacility should default to empty consumable_levels dict."""
        facility = PlanetaryFacility(
            instance_id="test-001",
            design_id="power_plant",
            name="Power Plant",
            design_data={"layers": {}},
        )
        assert facility.consumable_levels == {}

    def test_facility_accepts_consumable_levels(self):
        """PlanetaryFacility should accept consumable_levels values."""
        facility = _make_fuel_facility(consumable_levels={"fuel": 250.0})
        assert facility.consumable_levels == {"fuel": 250.0}

    def test_consumable_levels_are_independent_per_instance(self):
        """Each facility should have independent consumable_levels."""
        f1 = _make_fuel_facility(instance_id="f1")
        f2 = _make_fuel_facility(instance_id="f2")
        f1.consumable_levels["fuel"] = 100.0
        assert f2.consumable_levels == {}


# ===========================================================================
# Task 2.2: Serialization
# ===========================================================================

class TestFacilityResourceSerialization:
    """Test Planet.to_dict()/from_dict() with facility consumable_levels."""

    def test_consumable_levels_serializes_in_to_dict(self):
        """Planet.to_dict() should include facility consumable_levels."""
        planet = _make_planet()
        facility = _make_fuel_facility(consumable_levels={"fuel": 200.0})
        planet.facilities.append(facility)

        data = planet.to_dict()
        facility_data = data["facilities"][0]
        assert "consumable_levels" in facility_data
        assert facility_data["consumable_levels"] == {"fuel": 200.0}

    def test_consumable_levels_roundtrips_via_from_dict(self):
        """Planet.from_dict() should restore facility consumable_levels."""
        planet = _make_planet()
        facility = _make_fuel_facility(consumable_levels={"fuel": 350.5})
        planet.facilities.append(facility)

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert len(restored.facilities) == 1
        assert restored.facilities[0].consumable_levels == {"fuel": 350.5}

    def test_old_save_without_consumable_levels_defaults_empty(self):
        """from_dict() with old save data (no consumable_levels) defaults to empty dict."""
        planet = _make_planet()
        data = planet.to_dict()
        # Simulate old save format without consumable_levels
        data["facilities"] = [
            {
                "instance_id": "old-001",
                "design_id": "power_plant",
                "name": "Power Plant",
                "design_data": {"layers": {}},
                "is_operational": True,
                "construction_queue": [],
                # No consumable_levels key
            }
        ]
        restored = Planet.from_dict(data)
        assert restored.facilities[0].consumable_levels == {}

    def test_empty_consumable_levels_serializes(self):
        """Empty consumable_levels should serialize as empty dict."""
        planet = _make_planet()
        facility = _make_fuel_facility()
        planet.facilities.append(facility)

        data = planet.to_dict()
        assert data["facilities"][0]["consumable_levels"] == {}

    def test_serialized_consumable_levels_is_independent_copy(self):
        """Serialized consumable_levels should be a copy, not a reference."""
        planet = _make_planet()
        facility = _make_fuel_facility(consumable_levels={"fuel": 100.0})
        planet.facilities.append(facility)

        data = planet.to_dict()
        # Mutate original
        facility.consumable_levels["fuel"] = 999.0
        # Serialized data should not be affected
        assert data["facilities"][0]["consumable_levels"]["fuel"] == 100.0

    def test_multiple_resource_types_roundtrip(self):
        """Multiple resource types should serialize and restore correctly."""
        planet = _make_planet()
        facility = _make_fuel_facility(consumable_levels={"fuel": 200.0, "energy": 50.0})
        planet.facilities.append(facility)

        data = planet.to_dict()
        restored = Planet.from_dict(data)
        assert restored.facilities[0].consumable_levels == {"fuel": 200.0, "energy": 50.0}


# ===========================================================================
# Task 2.3: Helper methods
# ===========================================================================

class TestGenericConsumableAPI:
    """F-A-012: generic add/withdraw/get_consumable_* API."""

    def _make_storage_facility(self, resource_id: str, capacity: float = 500.0):
        facility = PlanetaryFacility(
            instance_id=f"{resource_id}-depot",
            design_id="depot",
            name=f"{resource_id.title()} Depot",
            design_data={
                "layers": {"hull": [{"id": f"{resource_id}_tank"}]}
            },
            is_operational=True,
        )
        registries = MagicMock()
        tank_comp = MagicMock()
        tank_comp.abilities = {
            "ResourceStorage": [{"resource": resource_id, "amount": capacity}],
        }
        registries.components.get = lambda cid: (
            tank_comp if cid == f"{resource_id}_tank" else None
        )
        return facility, registries

    def test_add_consumable_organics_increases_level(self):
        facility, registries = self._make_storage_facility("organics", capacity=400.0)
        overflow = facility.add_consumable("organics", 150.0, registries)
        assert overflow == 0.0
        assert facility.get_consumable_storage("organics") == 150.0

    def test_withdraw_consumable_radioactives_decreases_level(self):
        facility, _ = self._make_storage_facility("radioactives", capacity=100.0)
        facility.consumable_levels["radioactives"] = 80.0
        withdrawn = facility.withdraw_consumable("radioactives", 30.0)
        assert withdrawn == 30.0
        assert facility.get_consumable_storage("radioactives") == 50.0

    def test_get_consumable_storage_returns_zero_for_unstored_resource(self):
        """A resource never stored in this facility reads as 0.0."""
        facility, _ = self._make_storage_facility("organics")
        assert facility.get_consumable_storage("fuel") == 0.0

    def test_get_max_consumable_storage_raises_on_unknown_resource_id(self):
        """Unknown-to-catalog resource IDs fail fast."""
        facility, registries = self._make_storage_facility("organics")
        with pytest.raises(ValueError):
            facility.get_max_consumable_storage("not_a_real_resource", registries)

    def test_add_consumable_returns_overflow_when_capacity_exceeded(self):
        facility, registries = self._make_storage_facility("organics", capacity=100.0)
        overflow = facility.add_consumable("organics", 150.0, registries)
        assert overflow == 50.0
        assert facility.get_consumable_storage("organics") == 100.0

    def test_fuel_wrappers_delegate_to_generic_consumable_api(self):
        """add_fuel/get_fuel_storage are now thin wrappers over the generic API."""
        facility, registries = self._make_storage_facility("fuel", capacity=200.0)
        facility.add_fuel(75.0, registries)
        # Same value visible through both APIs.
        assert facility.get_fuel_storage() == 75.0
        assert facility.get_consumable_storage("fuel") == 75.0


class TestGetFuelStorage:
    """Test PlanetaryFacility.get_fuel_storage()."""

    def test_returns_zero_when_no_fuel(self):
        """get_fuel_storage() returns 0.0 when no fuel stored."""
        facility = _make_fuel_facility()
        assert facility.get_fuel_storage() == 0.0

    def test_returns_current_fuel_level(self):
        """get_fuel_storage() returns the current fuel level."""
        facility = _make_fuel_facility(consumable_levels={"fuel": 250.0})
        assert facility.get_fuel_storage() == 250.0

    def test_ignores_other_resource_types(self):
        """get_fuel_storage() only returns fuel, not other resources."""
        facility = _make_fuel_facility(consumable_levels={"energy": 100.0})
        assert facility.get_fuel_storage() == 0.0


class TestGetMaxFuelStorage:
    """Test PlanetaryFacility.get_max_fuel_storage()."""

    def test_returns_fuel_tank_capacity(self):
        """get_max_fuel_storage() returns total fuel tank capacity from components."""
        facility = _make_fuel_facility(fuel_storage_amount=500.0)
        registries = _make_mock_registries(fuel_tank_amount=500.0)
        assert facility.get_max_fuel_storage(registries) == 500.0

    def test_returns_zero_when_no_fuel_tanks(self):
        """get_max_fuel_storage() returns 0 when facility has no fuel tank components."""
        facility = PlanetaryFacility(
            instance_id="no-tank",
            design_id="basic",
            name="Basic",
            design_data={"layers": {"hull": [{"id": "hull_plate"}]}},
        )
        registries = MagicMock()
        # hull_plate has no abilities
        hull_comp = MagicMock()
        hull_comp.abilities = {}
        registries.components.get = lambda cid: hull_comp if cid == "hull_plate" else None
        assert facility.get_max_fuel_storage(registries) == 0.0

    def test_sums_multiple_fuel_tanks(self):
        """get_max_fuel_storage() sums multiple fuel tank components."""
        facility = PlanetaryFacility(
            instance_id="multi-tank",
            design_id="big_depot",
            name="Big Depot",
            design_data={
                "layers": {
                    "hull": [
                        {"id": "fuel_tank"},
                        {"id": "fuel_tank"},
                    ]
                }
            },
        )
        registries = _make_mock_registries(fuel_tank_amount=300.0)
        assert facility.get_max_fuel_storage(registries) == 600.0

    def test_ignores_non_fuel_storage(self):
        """get_max_fuel_storage() ignores non-fuel ResourceStorage abilities."""
        facility = PlanetaryFacility(
            instance_id="mixed",
            design_id="mixed",
            name="Mixed",
            design_data={"layers": {"hull": [{"id": "energy_tank"}]}},
        )
        registries = MagicMock()
        energy_comp = MagicMock()
        energy_comp.abilities = {
            "ResourceStorage": [{"resource": "energy", "amount": 1000}],
        }
        registries.components.get = lambda cid: energy_comp if cid == "energy_tank" else None
        assert facility.get_max_fuel_storage(registries) == 0.0


class TestAddFuel:
    """Test PlanetaryFacility.add_fuel()."""

    def test_adds_fuel_to_empty_facility(self):
        """add_fuel() should add fuel when facility is empty."""
        facility = _make_fuel_facility(fuel_storage_amount=500.0)
        registries = _make_mock_registries(fuel_tank_amount=500.0)
        overflow = facility.add_fuel(200.0, registries)
        assert facility.get_fuel_storage() == 200.0
        assert overflow == 0.0

    def test_caps_at_max_storage(self):
        """add_fuel() should cap fuel at max storage and return overflow."""
        facility = _make_fuel_facility(fuel_storage_amount=500.0)
        registries = _make_mock_registries(fuel_tank_amount=500.0)
        overflow = facility.add_fuel(700.0, registries)
        assert facility.get_fuel_storage() == 500.0
        assert overflow == 200.0

    def test_adds_to_existing_fuel(self):
        """add_fuel() should add to existing fuel level."""
        facility = _make_fuel_facility(
            fuel_storage_amount=500.0,
            consumable_levels={"fuel": 200.0},
        )
        registries = _make_mock_registries(fuel_tank_amount=500.0)
        overflow = facility.add_fuel(100.0, registries)
        assert facility.get_fuel_storage() == 300.0
        assert overflow == 0.0

    def test_partial_overflow_when_near_capacity(self):
        """add_fuel() returns overflow when adding more than remaining space."""
        facility = _make_fuel_facility(
            fuel_storage_amount=500.0,
            consumable_levels={"fuel": 450.0},
        )
        registries = _make_mock_registries(fuel_tank_amount=500.0)
        overflow = facility.add_fuel(100.0, registries)
        assert facility.get_fuel_storage() == 500.0
        assert overflow == 50.0

    def test_zero_capacity_returns_all_as_overflow(self):
        """add_fuel() with zero max storage returns all fuel as overflow."""
        facility = PlanetaryFacility(
            instance_id="no-tank",
            design_id="basic",
            name="Basic",
            design_data={"layers": {"hull": [{"id": "hull_plate"}]}},
        )
        registries = MagicMock()
        hull_comp = MagicMock()
        hull_comp.abilities = {}
        registries.components.get = lambda cid: hull_comp
        overflow = facility.add_fuel(100.0, registries)
        assert facility.get_fuel_storage() == 0.0
        assert overflow == 100.0


class TestWithdrawFuel:
    """Test PlanetaryFacility.withdraw_fuel()."""

    def test_withdraws_available_fuel(self):
        """withdraw_fuel() should return requested amount when available."""
        facility = _make_fuel_facility(consumable_levels={"fuel": 300.0})
        withdrawn = facility.withdraw_fuel(100.0)
        assert withdrawn == 100.0
        assert facility.get_fuel_storage() == 200.0

    def test_withdraws_all_when_requesting_more(self):
        """withdraw_fuel() should return actual amount when requesting more than available."""
        facility = _make_fuel_facility(consumable_levels={"fuel": 50.0})
        withdrawn = facility.withdraw_fuel(100.0)
        assert withdrawn == 50.0
        assert facility.get_fuel_storage() == 0.0

    def test_returns_zero_when_empty(self):
        """withdraw_fuel() returns 0.0 when facility has no fuel."""
        facility = _make_fuel_facility()
        withdrawn = facility.withdraw_fuel(100.0)
        assert withdrawn == 0.0
        assert facility.get_fuel_storage() == 0.0

    def test_exact_withdrawal(self):
        """withdraw_fuel() works correctly for exact amount available."""
        facility = _make_fuel_facility(consumable_levels={"fuel": 100.0})
        withdrawn = facility.withdraw_fuel(100.0)
        assert withdrawn == 100.0
        assert facility.get_fuel_storage() == 0.0
