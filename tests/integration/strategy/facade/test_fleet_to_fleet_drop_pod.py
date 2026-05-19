"""PROJ-450 Phase 1 — fleet-to-fleet drop pod regression.

Integration coverage for the PROJ-445 Phase 2 fleet-to-fleet pod path
after PROJ-450 Phase 1's engine cleanup. The Phase 1 edits move three
helpers from ``transfer_branches.py`` into ``planet.py`` and drop the
``cv.to_dict()`` / payload-flatten boundary calls. The fleet-to-fleet
drop-pod path never went through the planet staging yard — pods route
through ``ShipInstance.bay_inventory.pods`` (typed slot) on both source
and destination. This test pins that the path still moves the typed
``DropPod`` end-to-end after the helpers' relocation.

PROJ-445 Phase 2 fixed a silent no-op where ``drop_pod`` cargo_type
routed through the generic-cargo resource aggregator and returned 0.
The contract here is that the pod arrives at the destination ship's
typed pod slot with all source fields preserved.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.transfer import TransferHandler


def _ok_validation():
    v = MagicMock()
    v.is_valid = True
    return v


def _bay_ship(*, name: str, pods=None):
    """Ship with a typed ``BayInventory`` and a write-through
    ``set_bay_inventory`` mirror — same shape used by the unit tests
    for the dispatch branches.
    """
    ship = MagicMock()
    ship.name = name
    ship.bay_inventory = BayInventory(bay=[], pods=list(pods or []))

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi

    ship.set_bay_inventory = _set_bay_inventory
    return ship


def _fleet(fleet_id: int) -> MagicMock:
    f = MagicMock(spec=Fleet)
    f.id = fleet_id
    f.location = HexCoord(0, 0)
    f.ships = []
    f.orders = []
    f.pop_order = MagicMock()
    return f


def _empire():
    e = MagicMock()
    e.id = 0
    e.fleets = []
    e.race_config = MagicMock(race_id="humans")
    return e


def test_fleet_to_fleet_drop_pod_preserves_typed_payload_after_phase_1_cleanup():
    """Fleet A's ship holds a ``DropPod``; Fleet B's ship has bay
    capacity; the pod ends up on Fleet B's ship with its full identity
    (design_id, mass, payload) preserved.

    The fleet-to-fleet path NEVER walks the planet staging yard, so it
    is the natural smoke for Phase 1: if the helpers' relocation broke
    the typed-pod flow, this test surfaces the regression even though
    the cleanup edits target the planet branches.
    """
    handler = TransferHandler()

    # Source pod with a rich payload — exercise round-trip preservation.
    source_pod = DropPod(
        design_id="drop_pod_colony",
        design_data={"name": "drop_pod_colony", "tier": 2},
        mass=120.0,
        payload={
            "name": "Hephaestus",
            "colonists": 1500,
            "supplies": {"metals": 50, "organics": 40},
        },
    )

    src_ship = _bay_ship(name="Carrier-Src", pods=[source_pod])
    src_ship._cargo_mgr = MagicMock()
    src_ship._cargo_mgr.can_carry_pod = MagicMock(return_value=False)

    dst_ship = _bay_ship(name="Carrier-Dst")
    dst_ship._cargo_mgr = MagicMock()
    dst_ship._cargo_mgr.can_carry_pod = MagicMock(return_value=True)

    source_fleet = _fleet(fleet_id=1)
    source_fleet.ships = [src_ship]
    target_fleet = _fleet(fleet_id=2)
    target_fleet.ships = [dst_ship]

    empire = _empire()
    empire.fleets = [source_fleet, target_fleet]
    galaxy = MagicMock(spec=[])

    source_fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "drop_pod",
            "amount": 1,
            "target_fleet_id": 2,
        },
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(source_fleet, empire, galaxy)

    # The pod moved end-to-end.
    assert result.success is True
    assert result.amount_transferred == 1

    # Source ship drained; destination ship received the pod.
    assert src_ship.bay_inventory.pods == []
    assert len(dst_ship.bay_inventory.pods) == 1

    delivered = dst_ship.bay_inventory.pods[0]
    assert isinstance(delivered, DropPod)
    assert delivered.design_id == "drop_pod_colony"
    assert delivered.mass == 120.0
    # Payload preserved verbatim — fleet-to-fleet does NOT flatten
    # payload into the dict substrate (the staging-yard boundary did,
    # and that boundary lives inside Planet now post-PROJ-450).
    assert delivered.payload == source_pod.payload
