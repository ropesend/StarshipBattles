"""PROJ-449 Phase 4 deletion guard.

Pins the absence of the PROJ-436 Phase 3f legacy-kwarg constructor
wrapper and the matching ``@setter`` shims on
:class:`game.strategy.data.ship_instance.ShipInstance`.

Companion / mirror to ``test_no_planet_legacy_kwarg_wrapper.py`` (the
Phase 3 guard for Planet). After PROJ-449 Phase 4:

* ``_ship_instance_init_with_legacy_kwargs`` is gone (the wrapper that
  translated public kwargs ``consumable_levels=`` / ``cargo_contents=``
  to their underscore-prefixed dataclass spellings).
* The ``consumable_levels`` / ``cargo_contents`` ``@setter`` shims that
  allowed ``ship.consumable_levels = {...}`` / ``ship.cargo_contents =
  {...}`` rebinding are gone.
* The matching ``@property`` GETTERS survive as read-only attribute
  views over the private ``_consumable_levels`` / ``_cargo_contents``
  fields. Writes must route through the manager APIs
  (``_resource_mgr.set_level`` / ``replace_levels`` / ``deplete`` and
  ``_cargo_mgr.set_cargo`` / ``add_to_cargo`` / ``remove_from_cargo``).

See PROJ-449 decisions.md row 2026-05-18 "Phase 3+4 scope adjustment".
"""
from __future__ import annotations

import game.strategy.data.ship_instance as ship_instance_module
from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_module_has_no_legacy_kwargs_wrapper() -> None:
    """``ship_instance`` module MUST NOT define ``_ship_instance_init_with_legacy_kwargs``.

    PROJ-449 Phase 4 deletion guard. The PROJ-436 Phase 3f wrapper that
    translated public kwarg names is gone; ``ShipInstance.__init__`` is
    the unmodified dataclass-generated ``__init__`` accepting only
    private (underscore-prefixed) field names.
    """
    assert not hasattr(ship_instance_module, "_ship_instance_init_with_legacy_kwargs"), (
        "ship_instance module still defines "
        "`_ship_instance_init_with_legacy_kwargs` (PROJ-449 Phase 4 "
        "deletion guard). The wrapper was retired; all callers must "
        "pass `_consumable_levels=` / `_cargo_contents=` directly."
    )


def _property_has_setter(cls: type, name: str) -> bool:
    """Return True iff ``cls.<name>`` is a descriptor with an ``fset``.

    Plain attributes and dataclass fields return False. Read-only
    ``@property`` accessors (no ``@setter``) return False.
    """
    descriptor = getattr(cls, name, None)
    if not isinstance(descriptor, property):
        return False
    return descriptor.fset is not None


def test_ship_instance_consumable_levels_has_no_setter() -> None:
    """``ShipInstance.consumable_levels`` MUST be read-only (no ``@setter``).

    PROJ-449 Phase 4 deletion guard. The setter shim that allowed
    ``ship.consumable_levels = {...}`` rebinding is gone. Writes route
    through ``_resource_mgr.set_level`` / ``replace_levels`` /
    ``deplete``.
    """
    assert not _property_has_setter(ShipInstance, "consumable_levels"), (
        "ShipInstance.consumable_levels still has an @setter "
        "(PROJ-449 Phase 4 deletion guard). The setter shim allowing "
        "`ship.consumable_levels = {...}` rebinding was retired."
    )


def test_ship_instance_cargo_contents_has_no_setter() -> None:
    """``ShipInstance.cargo_contents`` MUST be read-only (no ``@setter``).

    PROJ-449 Phase 4 deletion guard. The setter shim that allowed
    ``ship.cargo_contents = {...}`` rebinding is gone. Writes route
    through ``_cargo_mgr.set_cargo`` / ``add_to_cargo`` /
    ``remove_from_cargo``.
    """
    assert not _property_has_setter(ShipInstance, "cargo_contents"), (
        "ShipInstance.cargo_contents still has an @setter "
        "(PROJ-449 Phase 4 deletion guard). The setter shim allowing "
        "`ship.cargo_contents = {...}` rebinding was retired."
    )
