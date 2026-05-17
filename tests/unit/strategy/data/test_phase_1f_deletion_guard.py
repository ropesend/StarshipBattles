"""PROJ-431 Phase 1f deletion guard.

Locks in the final-state contract for Phase 1f:

* :class:`ShipInstance` MUST NOT carry ``carried_items`` as a dataclass
  field. (A backward-compatible property used only by test infrastructure
  is permitted.)
* :class:`CarriedVehicle` MUST NOT expose a ``from_any`` attribute — the
  legacy runtime dict/typed-entry discriminator was needed only to walk
  the old mixed-shape ``carried_items`` list. Post-Phase-1 the bay is
  homogeneous ``list[CarriedVehicle]`` and pods live in their own typed
  slot, so the discriminator has no remaining role.

This test is the explicit ratchet preventing reintroduction of either
seam.
"""
from __future__ import annotations

from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_has_no_carried_items_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``carried_items`` as a dataclass field.

    Phase 1f deletion guard. The typed ``bay_inventory`` substrate is the
    canonical storage; ``carried_items`` (if present at all) is a
    legacy-shim property used by test infrastructure only.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "carried_items" not in fields, (
        f"ShipInstance still has a `carried_items` dataclass field "
        f"(PROJ-431 Phase 1f deletion guard). The typed `bay_inventory` "
        f"substrate is the canonical storage. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_carried_vehicle_has_no_from_any_method() -> None:
    """``CarriedVehicle.from_any`` must NOT exist.

    Phase 1f deletion guard. The legacy runtime dict/typed-entry
    discriminator served only to walk the old mixed-shape
    ``carried_items`` list. Post-migration the bay is homogeneous
    ``list[CarriedVehicle]`` and pods live in a separate typed slot, so
    no discrimination is needed. Callers that received an untyped dict
    from an out-of-scope substrate (e.g. planet staging yard) must do an
    explicit shape check + ``CarriedVehicle.from_dict(...)`` instead.
    """
    assert not hasattr(CarriedVehicle, "from_any"), (
        "CarriedVehicle.from_any still exists (PROJ-431 Phase 1f "
        "deletion guard). Replace remaining callers with an explicit "
        "`vehicle_type in VALID_VEHICLE_TYPES` shape check + "
        "`CarriedVehicle.from_dict(...)`."
    )
