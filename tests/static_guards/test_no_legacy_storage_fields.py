"""PROJ-436 Phase 3f deletion guard.

Locks in the final-state contract for Phase 3f:

* :class:`ShipInstance` MUST NOT carry ``cargo_contents`` as a dataclass
  field.
* :class:`ShipInstance` MUST NOT carry ``consumable_levels`` as a
  dataclass field.

Both legacy ``Dict[str, ...]`` fields are replaced by write-through
property views over private storage owned by the ship's cargo /
consumable managers (PROJ-436 sub-phases 3b-3e routed every production
caller through the manager API; the fields themselves are deleted in
3f). Backward-compatible property accessors of the same names are
permitted — they exist to keep test infrastructure that pokes
``ship.cargo_contents[k] = v`` / ``ship.consumable_levels[k] = v``
working without a per-test migration.

This test is the explicit ratchet preventing reintroduction of either
seam as a real dataclass field.

Model: ``tests/unit/strategy/data/test_phase_1f_deletion_guard.py``
(PROJ-431 Phase 1f deletion guard for ``carried_items``).
"""
from __future__ import annotations

from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_has_no_cargo_contents_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``cargo_contents`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._cargo_mgr.set_cargo`` / ``get_all_cargo`` / ``total_cargo_units``
    / ``has_cargo`` (the stable manager API landed in Phase 3b). A
    backward-compatible ``cargo_contents`` property over the cargo
    manager's storage is permitted as a test-fixture compatibility
    shim — the dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "cargo_contents" not in fields, (
        f"ShipInstance still has a `cargo_contents` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable cargo-manager "
        f"API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_ship_instance_has_no_consumable_levels_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``consumable_levels`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._resource_mgr.set_level`` / ``get_all_levels`` /
    ``get_current_resource`` / ``replace_levels`` (the stable manager
    API landed in Phase 3b). A backward-compatible
    ``consumable_levels`` property over the consumable manager's
    storage is permitted as a test-fixture compatibility shim — the
    dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "consumable_levels" not in fields, (
        f"ShipInstance still has a `consumable_levels` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable consumable-"
        f"manager API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )
