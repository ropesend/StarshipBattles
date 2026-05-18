"""
PROJ-436 Phase 2: tests for the three-slice widening of `BayInventory`.

Phase 2 adds resource and population slots to the existing bay/pods
slots from PROJ-431. Existing `bay` / `pods` semantics are preserved
verbatim (test_bay_inventory.py still passes); the new slots add
resource and population storage with mass accounting unified across
all four.

Container-aware extras:
- `bay_inventory.add_resource()` / `get_resource()` / `remove_resource()`
- `bay_inventory.add_population()` / `get_population()` / `remove_population()`
- `total_resource_mass()` / `total_population_mass()` / `total_mass()`
"""
from __future__ import annotations

import pytest

from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle


def _carried(mass: float = 10.0) -> CarriedVehicle:
    return CarriedVehicle(
        design_id="qs_fighter",
        design_data={"name": "qs_fighter"},
        vehicle_type="fighter",
        mass=mass,
        current_hp=50,
    )


def _pod(mass: float = 5.0) -> DropPod:
    return DropPod(
        design_id="colony_pod",
        design_data={"name": "colony_pod"},
        mass=mass,
    )


# ---------------------------------------------------------------------------
# New slots exist
# ---------------------------------------------------------------------------


class TestResourceSlot:
    def test_resources_default_empty(self):
        bi = BayInventory()
        assert bi.resources == {}

    def test_add_resource(self):
        bi = BayInventory()
        bi.add_resource("metals", 100.0)
        assert bi.get_resource("metals") == pytest.approx(100.0)
        # 100 metals * 0.01 mass/unit = 1.0 ton
        assert bi.total_resource_mass() == pytest.approx(1.0)

    def test_add_resource_accumulates(self):
        bi = BayInventory()
        bi.add_resource("metals", 100.0)
        bi.add_resource("metals", 50.0)
        assert bi.get_resource("metals") == pytest.approx(150.0)

    def test_get_missing_resource_returns_zero(self):
        bi = BayInventory()
        assert bi.get_resource("metals") == 0.0

    def test_remove_resource(self):
        bi = BayInventory()
        bi.add_resource("metals", 100.0)
        ok = bi.remove_resource("metals", 30.0)
        assert ok is True
        assert bi.get_resource("metals") == pytest.approx(70.0)

    def test_remove_resource_not_enough(self):
        bi = BayInventory()
        bi.add_resource("metals", 10.0)
        ok = bi.remove_resource("metals", 30.0)
        assert ok is False
        assert bi.get_resource("metals") == pytest.approx(10.0)

    def test_remove_to_zero_clears_key(self):
        bi = BayInventory()
        bi.add_resource("fuel", 50.0)
        bi.remove_resource("fuel", 50.0)
        assert "fuel" not in bi.resources
        assert bi.get_resource("fuel") == 0.0

    def test_unknown_resource_raises_on_add(self):
        bi = BayInventory()
        with pytest.raises(KeyError):
            bi.add_resource("dilithium", 5.0)

    def test_negative_amount_rejected(self):
        bi = BayInventory()
        with pytest.raises(ValueError):
            bi.add_resource("metals", -1.0)


class TestPopulationSlot:
    def test_population_default_empty(self):
        bi = BayInventory()
        assert bi.population == {}

    def test_add_population(self):
        bi = BayInventory()
        bi.add_population("human", 100)
        assert bi.get_population("human") == 100
        # 100 humans * 0.1 ton/individual = 10 tons
        assert bi.total_population_mass() == pytest.approx(10.0)

    def test_add_population_accumulates(self):
        bi = BayInventory()
        bi.add_population("human", 100)
        bi.add_population("human", 50)
        assert bi.get_population("human") == 150

    def test_population_per_species(self):
        bi = BayInventory()
        bi.add_population("human", 100)
        bi.add_population("vulcan", 50)
        assert bi.get_population("human") == 100
        assert bi.get_population("vulcan") == 50
        # (100 + 50) * 0.1 = 15.0 tons total
        assert bi.total_population_mass() == pytest.approx(15.0)

    def test_get_missing_species_returns_zero(self):
        bi = BayInventory()
        assert bi.get_population("klingon") == 0

    def test_remove_population(self):
        bi = BayInventory()
        bi.add_population("human", 100)
        ok = bi.remove_population("human", 30)
        assert ok is True
        assert bi.get_population("human") == 70

    def test_remove_population_not_enough(self):
        bi = BayInventory()
        bi.add_population("human", 10)
        ok = bi.remove_population("human", 30)
        assert ok is False
        assert bi.get_population("human") == 10

    def test_remove_to_zero_clears_key(self):
        bi = BayInventory()
        bi.add_population("human", 50)
        bi.remove_population("human", 50)
        assert "human" not in bi.population

    def test_population_count_must_be_integer(self):
        bi = BayInventory()
        with pytest.raises(TypeError):
            bi.add_population("human", 5.5)  # type: ignore[arg-type]

    def test_negative_count_rejected(self):
        bi = BayInventory()
        with pytest.raises(ValueError):
            bi.add_population("human", -5)


# ---------------------------------------------------------------------------
# Total mass across all four slots
# ---------------------------------------------------------------------------


class TestTotalMass:
    def test_total_mass_zero_when_empty(self):
        bi = BayInventory()
        assert bi.total_mass() == 0.0

    def test_total_mass_sums_all_four_slots(self):
        bi = BayInventory()
        bi.add_vehicle(_carried(mass=10.0))          # 10.0 mass in bay
        bi.add_pod(_pod(mass=5.0))                   # 5.0 mass in pods
        bi.add_resource("metals", 1000.0)            # 1000 * 0.01 = 10.0 mass
        bi.add_population("human", 50)               # 50 * 0.1 = 5.0 mass
        assert bi.total_mass() == pytest.approx(30.0)

    def test_total_mass_matches_per_slot_sums(self):
        bi = BayInventory()
        bi.add_vehicle(_carried(mass=12.0))
        bi.add_pod(_pod(mass=3.0))
        bi.add_resource("fuel", 50_000.0)
        bi.add_population("human", 100)
        assert bi.total_mass() == pytest.approx(
            bi.total_bay_mass()
            + bi.total_pod_mass()
            + bi.total_resource_mass()
            + bi.total_population_mass()
        )


class TestIsEmpty:
    def test_empty_when_all_slots_empty(self):
        bi = BayInventory()
        assert bi.is_empty()

    def test_not_empty_with_bay(self):
        bi = BayInventory(bay=[_carried()])
        assert not bi.is_empty()

    def test_not_empty_with_pods(self):
        bi = BayInventory(pods=[_pod()])
        assert not bi.is_empty()

    def test_not_empty_with_resources(self):
        bi = BayInventory()
        bi.add_resource("metals", 1.0)
        assert not bi.is_empty()

    def test_not_empty_with_population(self):
        bi = BayInventory()
        bi.add_population("human", 1)
        assert not bi.is_empty()


# ---------------------------------------------------------------------------
# Round-trip carries all four slots
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_round_trip_with_all_four_slots(self):
        bi = BayInventory()
        bi.add_vehicle(_carried(mass=10.0))
        bi.add_pod(_pod(mass=5.0))
        bi.add_resource("metals", 200.0)
        bi.add_resource("fuel", 1000.0)
        bi.add_population("human", 25)
        bi.add_population("vulcan", 10)

        data = bi.to_dict()
        rebuilt = BayInventory.from_dict(data)

        assert len(rebuilt.bay) == 1
        assert rebuilt.bay[0].design_id == "qs_fighter"
        assert len(rebuilt.pods) == 1
        assert rebuilt.pods[0].design_id == "colony_pod"
        assert rebuilt.get_resource("metals") == pytest.approx(200.0)
        assert rebuilt.get_resource("fuel") == pytest.approx(1000.0)
        assert rebuilt.get_population("human") == 25
        assert rebuilt.get_population("vulcan") == 10
        assert rebuilt.total_mass() == pytest.approx(bi.total_mass())

    def test_legacy_round_trip_without_new_slots(self):
        """Old saves predating Phase 2 (bay+pods only) load correctly."""
        legacy_data = {
            "bay": [
                {
                    "design_id": "qs_fighter",
                    "design_data": {},
                    "vehicle_type": "fighter",
                    "mass": 12.5,
                    "current_hp": 50,
                    "component_states": None,
                },
            ],
            "pods": [
                {"design_id": "colony_pod", "design_data": {}, "mass": 4.0, "payload": {}},
            ],
        }
        bi = BayInventory.from_dict(legacy_data)
        assert len(bi.bay) == 1
        assert len(bi.pods) == 1
        assert bi.resources == {}
        assert bi.population == {}

    def test_empty_round_trip(self):
        bi = BayInventory()
        rebuilt = BayInventory.from_dict(bi.to_dict())
        assert rebuilt.is_empty()
