"""
Tests for OrderProcessor staging yard pod load/unload operations.

PROJ-264 Phase 2: Coverage for _load_pod_from_staging_yard() and
_unload_pod_to_staging_yard() which had zero test coverage.
"""

import pytest
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.order_types import OrderType
from unittest.mock import MagicMock

from game.strategy.engine.order_handlers.transfer import TransferHandler


@pytest.fixture
def processor():
    # PROJ-368 Phase 4: staging yard ops live on TransferHandler.
    return TransferHandler()


def _make_pod(name="Continental Drop Pod", mass=500):
    return {"name": name, "mass": mass, "vehicle_type": "drop_pod", "design_id": "pod_1"}


def _pod_dict_to_typed(d) -> DropPod:
    return DropPod(
        design_id=str(d.get("design_id", "")),
        design_data=dict(d.get("design_data", {})),
        mass=float(d.get("mass", 0.0)),
        payload={
            k: v for k, v in d.items()
            if k not in {"design_id", "design_data", "mass"}
        },
    )


def _make_ship(can_carry=True, carried_items=None):
    """PROJ-436 Phase 9: wire the typed ``bay_inventory.pods`` slot
    from a list of legacy pod dicts. The legacy ``carried_items``
    mirror is gone — production code reads the typed slot directly.
    """
    ship = MagicMock()
    ship.name = "Colony Ship"
    seed = list(carried_items or [])
    ship.bay_inventory = BayInventory(
        bay=[], pods=[_pod_dict_to_typed(p) for p in seed]
    )
    ship.get_pod_storage_capacity = MagicMock(return_value=1000 if can_carry else 0)
    ship.get_pod_storage_used = MagicMock(return_value=0)
    ship.can_carry_pod = MagicMock(return_value=can_carry)
    # PROJ-425 Phase 6: production reads via ``ship._cargo_mgr``.
    ship._cargo_mgr.get_pod_storage_capacity = MagicMock(return_value=1000 if can_carry else 0)
    ship._cargo_mgr.get_pod_storage_used = MagicMock(return_value=0)
    ship._cargo_mgr.can_carry_pod = MagicMock(return_value=can_carry)

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi

    ship.set_bay_inventory = _set_bay_inventory
    return ship


def _make_planet_with_yard(pods=None):
    planet = MagicMock()
    planet.name = "Colony"
    planet.staging_yard = list(pods) if pods else []
    planet.remove_from_staging_yard = MagicMock(
        side_effect=lambda i: planet.staging_yard.pop(i) if 0 <= i < len(planet.staging_yard) else None
    )

    # PROJ-450 Phase 1: ``_dispatch_drop_pod_load`` pops via the typed
    # API. Mirror the Planet behaviour: pop the raw dict and promote.
    def _pop_typed(i):
        if not (0 <= i < len(planet.staging_yard)):
            return None
        return _pod_dict_to_typed(planet.staging_yard.pop(i))
    planet.pop_staging_yard_typed = MagicMock(side_effect=_pop_typed)

    planet.add_to_staging_yard = MagicMock(return_value=True)
    return planet


def _make_fleet(ships=None):
    fleet = MagicMock()
    fleet.ships = ships or []
    return fleet


# =============================================================================
# _load_pod_from_staging_yard Tests
# =============================================================================


class TestLoadPodFromStagingYard:
    """Tests for OrderProcessor._load_pod_from_staging_yard()."""

    def test_loads_pod_to_ship(self, processor):
        """Pod moves from staging yard to ship carried_items."""
        pod = _make_pod()
        ship = _make_ship(can_carry=True, carried_items=[])
        planet = _make_planet_with_yard(pods=[pod])
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_load(fleet, planet)

        assert result == 1
        assert len(ship.bay_inventory.pods) == 1
        # PROJ-431 Phase 1d: pods round-trip through DropPod.to_dict on
        # the typed write-through path, so identity is not preserved.
        # Assert on the payload-equality view instead.
        assert ship.bay_inventory.pods[0].payload["name"] == pod["name"]
        assert ship.bay_inventory.pods[0].design_id == pod["design_id"]

    def test_filters_by_pod_name(self, processor):
        """Only loads pods matching pod_name."""
        wrong_pod = _make_pod(name="Wrong Pod")
        right_pod = _make_pod(name="Target Pod")
        ship = _make_ship(can_carry=True, carried_items=[])
        planet = _make_planet_with_yard(pods=[wrong_pod, right_pod])
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_load(fleet, planet, pod_name="Target Pod")

        assert result == 1
        assert ship.bay_inventory.pods[0].payload["name"] == "Target Pod"
        # Wrong pod still in staging yard
        assert len(planet.staging_yard) == 1
        assert planet.staging_yard[0]["name"] == "Wrong Pod"

    def test_caps_by_amount(self, processor):
        """Respects amount parameter."""
        pods = [_make_pod(name=f"Pod {i}") for i in range(5)]
        ship = _make_ship(can_carry=True, carried_items=[])
        planet = _make_planet_with_yard(pods=pods)
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_load(fleet, planet, amount=2)

        assert result == 2
        assert len(ship.bay_inventory.pods) == 2
        assert len(planet.staging_yard) == 3

    def test_amount_zero_loads_all(self, processor):
        """amount=0 loads all pods that fit."""
        pods = [_make_pod(name=f"Pod {i}") for i in range(3)]
        ship = _make_ship(can_carry=True, carried_items=[])
        planet = _make_planet_with_yard(pods=pods)
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_load(fleet, planet, amount=0)

        assert result == 3
        assert len(ship.bay_inventory.pods) == 3

    def test_no_capacity_stays_in_yard(self, processor):
        """Pod stays in yard when no ship can carry it."""
        pod = _make_pod()
        ship = _make_ship(can_carry=False, carried_items=[])
        planet = _make_planet_with_yard(pods=[pod])
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_load(fleet, planet)

        assert result == 0
        assert len(planet.staging_yard) == 1  # Pod still there

    def test_multiple_ships_fills_first(self, processor):
        """Distributes to first ship with capacity."""
        pod = _make_pod()
        ship1 = _make_ship(can_carry=False, carried_items=[])  # No capacity
        ship2 = _make_ship(can_carry=True, carried_items=[])   # Has capacity
        planet = _make_planet_with_yard(pods=[pod])
        fleet = _make_fleet(ships=[ship1, ship2])

        result = processor._dispatch_drop_pod_load(fleet, planet)

        assert result == 1
        assert len(ship1.bay_inventory.pods) == 0
        assert len(ship2.bay_inventory.pods) == 1


# =============================================================================
# _unload_pod_to_staging_yard Tests
# =============================================================================


class TestUnloadPodToStagingYard:
    """Tests for OrderProcessor._unload_pod_to_staging_yard()."""

    def test_unloads_pod_from_ship(self, processor):
        """Pod moves from ship to staging yard."""
        pod = _make_pod()
        ship = _make_ship(carried_items=[pod])
        planet = _make_planet_with_yard()
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_unload(fleet, planet)

        assert result == 1
        # PROJ-450 Phase 1: handler hands the typed ``DropPod`` to the
        # planet directly; the dict ↔ typed normalisation lives inside
        # ``Planet.add_to_staging_yard``. Surface the pod identity via
        # the typed fields.
        assert planet.add_to_staging_yard.call_count == 1
        delivered = planet.add_to_staging_yard.call_args.args[0]
        assert isinstance(delivered, DropPod)
        assert delivered.design_id == pod["design_id"]
        assert delivered.payload["name"] == pod["name"]
        assert len(ship.bay_inventory.pods) == 0

    def test_filters_by_pod_name(self, processor):
        """Only unloads pods matching pod_name."""
        wrong_pod = _make_pod(name="Wrong Pod")
        right_pod = _make_pod(name="Target Pod")
        ship = _make_ship(carried_items=[wrong_pod, right_pod])
        planet = _make_planet_with_yard()
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_unload(fleet, planet, pod_name="Target Pod")

        assert result == 1
        # Wrong pod still on ship
        assert len(ship.bay_inventory.pods) == 1
        assert ship.bay_inventory.pods[0].payload["name"] == "Wrong Pod"

    def test_amount_zero_unloads_all(self, processor):
        """amount=0 unloads all pods."""
        pods = [_make_pod(name=f"Pod {i}") for i in range(3)]
        ship = _make_ship(carried_items=pods)
        planet = _make_planet_with_yard()
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_unload(fleet, planet, amount=0)

        assert result == 3
        assert len(ship.bay_inventory.pods) == 0

    def test_caps_by_amount(self, processor):
        """Respects amount parameter."""
        pods = [_make_pod(name=f"Pod {i}") for i in range(5)]
        ship = _make_ship(carried_items=pods)
        planet = _make_planet_with_yard()
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_unload(fleet, planet, amount=2)

        assert result == 2
        assert len(ship.bay_inventory.pods) == 3

    def test_iterates_all_ships(self, processor):
        """Checks all ships in fleet."""
        pod1 = _make_pod(name="Pod 1")
        pod2 = _make_pod(name="Pod 2")
        ship1 = _make_ship(carried_items=[pod1])
        ship2 = _make_ship(carried_items=[pod2])
        planet = _make_planet_with_yard()
        fleet = _make_fleet(ships=[ship1, ship2])

        result = processor._dispatch_drop_pod_unload(fleet, planet, amount=0)

        assert result == 2
        assert len(ship1.bay_inventory.pods) == 0
        assert len(ship2.bay_inventory.pods) == 0

    def test_add_fails_stays_on_ship(self, processor):
        """Pod stays on ship when staging yard refuses it."""
        pod = _make_pod()
        ship = _make_ship(carried_items=[pod])
        planet = _make_planet_with_yard()
        planet.add_to_staging_yard.return_value = False  # Yard refuses
        fleet = _make_fleet(ships=[ship])

        result = processor._dispatch_drop_pod_unload(fleet, planet)

        assert result == 0
        assert len(ship.bay_inventory.pods) == 1  # Pod still on ship
