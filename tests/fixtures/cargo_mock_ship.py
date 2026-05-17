"""Shared factory for cargo-bearing mock ships in tests.

PROJ-322 Task 6.3 (DUP-003): consolidates the closure-based cargo mock
helpers from `tests/unit/strategy/data/test_fleet_cargo_resources.py`
(``_make_ship``) and the cargo half of
`tests/unit/strategy/engine/test_resupply_engine.py` (``_make_mock_ship``)
into a single ``make_cargo_mock_ship`` factory.

The factory returns a ``MagicMock`` whose cargo-related methods
(`get_cargo_capacity`, `get_current_cargo`, `load_cargo`, `unload_cargo`)
behave like a real Ship: capacity is read-only, cargo_contents is mutable
and the load/unload methods enforce the capacity constraint.

Usage
-----

::

    from tests.fixtures.cargo_mock_ship import make_cargo_mock_ship

    ship = make_cargo_mock_ship(
        cargo_capacity={"metals": 1000, "fuel": 500},
        cargo_contents={"metals": 250},
    )
    assert ship.get_cargo_capacity("metals") == 1000
    assert ship.load_cargo("metals", 100) == 100
    assert ship.cargo_contents["metals"] == 350
"""

from __future__ import annotations

from typing import Any, Mapping
from unittest.mock import MagicMock


def make_cargo_mock_ship(
    cargo_capacity: Mapping[str, float] | None = None,
    cargo_contents: Mapping[str, float] | None = None,
    *,
    is_combat_capable: bool = True,
) -> Any:
    """Build a mock ship with realistic cargo behaviour.

    Arguments
    ---------
    cargo_capacity
        Mapping of cargo type -> max capacity. Anything queried for a
        type not in this mapping reports capacity 0.
    cargo_contents
        Mapping of cargo type -> initial amount loaded. Defaults to
        empty. The returned mock keeps a mutable copy in
        ``ship.cargo_contents``.
    is_combat_capable
        Whether the ship reports as combat-capable. Most cargo tests
        treat freighters as combat-capable; pass ``False`` for an
        unarmed freighter scenario.

    Returns
    -------
    A ``MagicMock`` instance with the cargo API wired:

    * ``get_cargo_capacity(cargo_type) -> float``
    * ``get_current_cargo(cargo_type) -> float``
    * ``load_cargo(cargo_type, amount) -> float`` (returns actual loaded)
    * ``unload_cargo(cargo_type, amount) -> float`` (returns actual unloaded)
    * ``cargo_contents`` — mutable dict mirroring loaded amounts
    * ``is_combat_capable`` — bool attribute
    """

    ship = MagicMock()
    ship.cargo_contents = dict(cargo_contents or {})
    _cap = dict(cargo_capacity or {})

    def get_cargo_capacity(cargo_type):
        return _cap.get(cargo_type, 0)

    def get_current_cargo(cargo_type):
        return ship.cargo_contents.get(cargo_type, 0)

    def load_cargo(cargo_type, amount):
        space = _cap.get(cargo_type, 0) - ship.cargo_contents.get(cargo_type, 0)
        actual = min(amount, max(0, space))
        if actual > 0:
            ship.cargo_contents[cargo_type] = (
                ship.cargo_contents.get(cargo_type, 0) + actual
            )
        return actual

    def unload_cargo(cargo_type, amount):
        current = ship.cargo_contents.get(cargo_type, 0)
        actual = min(amount, current)
        if actual > 0:
            ship.cargo_contents[cargo_type] = current - actual
        return actual

    ship.get_cargo_capacity = get_cargo_capacity
    ship.get_current_cargo = get_current_cargo
    ship.load_cargo = load_cargo
    ship.unload_cargo = unload_cargo
    ship.is_combat_capable = is_combat_capable

    # PROJ-425 Phase 6: production callers now route through
    # ``ship._cargo_mgr`` (the cargo manager), so expose the same four
    # cargo methods on a mock manager too. The mock is shared with the
    # closures so reads/writes stay in sync with ``ship.cargo_contents``.
    cargo_mgr = MagicMock()
    cargo_mgr.get_cargo_capacity = get_cargo_capacity
    cargo_mgr.get_current_cargo = get_current_cargo
    cargo_mgr.load_cargo = load_cargo
    cargo_mgr.unload_cargo = unload_cargo
    ship._cargo_mgr = cargo_mgr

    return ship


__all__ = ["make_cargo_mock_ship"]
