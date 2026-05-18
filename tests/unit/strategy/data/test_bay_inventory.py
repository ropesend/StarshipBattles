"""PROJ-431 Phase 1 — typed BayInventory substrate.

RED → GREEN test for the new ``BayInventory`` dataclass that replaces
``ShipInstance.carried_items: List[Dict[str, Any]]`` mixed-shape list.
The bay is a homogeneous ``list[CarriedVehicle]``; the pods slot is a
homogeneous ``list[DropPod]``. There is no runtime discriminator.
"""
from __future__ import annotations

import pytest

from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle


def _make_carried_vehicle(mass: float = 10.0) -> CarriedVehicle:
    return CarriedVehicle(
        design_id="qs_fighter",
        design_data={"name": "qs_fighter"},
        vehicle_type="fighter",
        mass=mass,
        current_hp=50,
    )


def _make_drop_pod(mass: float = 5.0) -> DropPod:
    return DropPod(
        design_id="colony_pod",
        design_data={"name": "colony_pod"},
        mass=mass,
    )


class TestBayInventoryConstruction:
    def test_default_empty(self) -> None:
        bi = BayInventory()
        assert bi.bay == []
        assert bi.pods == []

    def test_with_initial_contents(self) -> None:
        cv = _make_carried_vehicle()
        pod = _make_drop_pod()
        bi = BayInventory(bay=[cv], pods=[pod])
        assert bi.bay == [cv]
        assert bi.pods == [pod]


class TestBayInventoryTypeEnforcement:
    def test_rejects_pod_in_bay(self) -> None:
        bi = BayInventory()
        pod = _make_drop_pod()
        with pytest.raises(TypeError):
            bi.add_vehicle(pod)  # type: ignore[arg-type]

    def test_rejects_vehicle_in_pods(self) -> None:
        bi = BayInventory()
        cv = _make_carried_vehicle()
        with pytest.raises(TypeError):
            bi.add_pod(cv)  # type: ignore[arg-type]


class TestBayInventoryMassAccounting:
    def test_total_pod_mass(self) -> None:
        bi = BayInventory(pods=[_make_drop_pod(5.0), _make_drop_pod(7.0)])
        assert bi.total_pod_mass() == 12.0

    def test_total_bay_mass(self) -> None:
        bi = BayInventory(bay=[
            _make_carried_vehicle(10.0),
            _make_carried_vehicle(20.0),
        ])
        assert bi.total_bay_mass() == 30.0


class TestBayInventoryRemoveGuards:
    def test_remove_resource_rejects_negative_amount(self) -> None:
        bi = BayInventory()
        with pytest.raises(ValueError):
            bi.remove_resource("metals", -3.0)

    def test_remove_population_rejects_negative_count(self) -> None:
        bi = BayInventory()
        with pytest.raises(ValueError):
            bi.remove_population("human", -2)


class TestBayInventoryRoundTrip:
    def test_to_dict_from_dict(self) -> None:
        cv = _make_carried_vehicle(15.0)
        pod = _make_drop_pod(3.5)
        bi = BayInventory(bay=[cv], pods=[pod])
        data = bi.to_dict()
        bi2 = BayInventory.from_dict(data)
        assert len(bi2.bay) == 1
        assert bi2.bay[0].design_id == "qs_fighter"
        assert bi2.bay[0].mass == 15.0
        assert len(bi2.pods) == 1
        assert bi2.pods[0].design_id == "colony_pod"
        assert bi2.pods[0].mass == 3.5

    def test_empty_round_trip(self) -> None:
        bi = BayInventory()
        bi2 = BayInventory.from_dict(bi.to_dict())
        assert bi2.bay == []
        assert bi2.pods == []
