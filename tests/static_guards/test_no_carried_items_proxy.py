"""PROJ-436 Phase 9 deletion guard.

Locks in the final-state contract for the legacy ``carried_items`` shim:

* :class:`game.strategy.data.ship_instance._CarriedItemsProxy` class is GONE.
* :attr:`game.strategy.data.ship_instance.ShipInstance.carried_items` property
  + setter are GONE.
* The companion legacy-shim helpers
  ``_items_to_bay_inventory`` / ``_bay_inventory_to_items`` are GONE.

Production code and test infrastructure write to
``ship.bay_inventory.bay`` / ``ship.bay_inventory.pods`` /
``ship.set_bay_inventory(...)`` directly. The PROJ-431 typed
:class:`BayInventory` substrate is the canonical surface; there is no
mixed-shape ``List[Dict[str, Any]]`` projection.

Model: ``tests/static_guards/test_no_legacy_storage_fields.py``
(PROJ-436 Phase 3f / 4f / 5 / 7 / 8 deletion guards).
"""
from __future__ import annotations

from pathlib import Path

import game.strategy.data.ship_instance as ship_instance_module
from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_module_has_no_carried_items_proxy_class() -> None:
    """``_CarriedItemsProxy`` class MUST be gone from ship_instance.py.

    PROJ-436 Phase 9 deletion guard. The write-through dict-list proxy
    is replaced by direct access to the typed ``BayInventory`` slots.
    """
    assert not hasattr(ship_instance_module, "_CarriedItemsProxy"), (
        "ship_instance still defines `_CarriedItemsProxy` "
        "(PROJ-436 Phase 9 deletion guard). The typed `BayInventory` "
        "substrate is the canonical write surface; the proxy is gone."
    )


def test_ship_instance_has_no_carried_items_property() -> None:
    """``ShipInstance.carried_items`` property + setter MUST be gone.

    PROJ-436 Phase 9 deletion guard. Tests that previously did
    ``ship.carried_items.append({...})`` / ``ship.carried_items = [...]``
    now write to ``ship.bay_inventory.bay`` / ``ship.bay_inventory.pods``
    / ``ship.set_bay_inventory(...)``.
    """
    assert "carried_items" not in vars(ShipInstance), (
        "ShipInstance still exposes a `carried_items` class attribute "
        "(PROJ-436 Phase 9 deletion guard). Production and test code "
        "must route through `bay_inventory` directly."
    )


def test_ship_instance_module_has_no_legacy_shim_helpers() -> None:
    """The ``_items_to_bay_inventory`` / ``_bay_inventory_to_items``
    legacy helpers MUST be gone.

    PROJ-436 Phase 9 deletion guard. These functions existed to bridge
    the legacy mixed-shape dict-list with the typed BayInventory; with
    the proxy and property deleted they have no callers.
    """
    for name in ("_items_to_bay_inventory", "_bay_inventory_to_items"):
        assert not hasattr(ship_instance_module, name), (
            f"ship_instance still defines `{name}` "
            f"(PROJ-436 Phase 9 deletion guard). The legacy mixed-shape "
            f"dict-list projection is gone; nothing should need this "
            f"helper."
        )


def test_ship_instance_source_has_no_carried_items_proxy_text() -> None:
    """``ship_instance.py`` source MUST NOT contain the proxy identifier.

    PROJ-436 Phase 9 deletion guard. Text-level pin in case a future
    refactor accidentally re-introduces ``_CarriedItemsProxy`` as a
    method name, comment fragment, or import — only the deletion
    comment + this test should mention it. This guard's own
    self-reference is filtered.
    """
    source = Path(ship_instance_module.__file__).read_text(encoding="utf-8")
    occurrences = source.count("_CarriedItemsProxy")
    # The deletion-comment markers in ship_instance.py legitimately
    # name the deleted symbol twice (one inline note near the old
    # property site, one in the module-level "what was deleted" block).
    # Any further occurrence is a regression.
    assert occurrences <= 2, (
        f"ship_instance.py contains {occurrences} mentions of "
        f"`_CarriedItemsProxy` (PROJ-436 Phase 9 deletion guard "
        f"allows at most 2 — the deletion-comment markers)."
    )
