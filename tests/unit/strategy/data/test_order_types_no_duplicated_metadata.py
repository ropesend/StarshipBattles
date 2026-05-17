"""Final-guard tests for PROJ-424 Phase 5.

After convergence, ``game/strategy/data/order_types.py`` keeps only
``OrderType`` + ``Order`` + serialization helpers. The four duplicated
metadata frozensets (``MOVEMENT_ORDER_TYPES``, ``ACTION_ORDER_TYPES``,
``PLANET_ACTION_ORDER_TYPES``, ``PLANET_FMS_ACTION_ORDER_TYPES``) are
gone, as are the two re-exports in ``game/strategy/data/fleet.py``.

Re-adding any of those names to either module is a deliberate
regression of the convergence and will fail these tests. There are NO
compatibility aliases — the end state is explicit imports from
``game.strategy.engine.commands.order_metadata_view``.
"""
from __future__ import annotations

import pytest

from game.strategy.data import fleet, order_types


_FORBIDDEN_NAMES = (
    "MOVEMENT_ORDER_TYPES",
    "ACTION_ORDER_TYPES",
    "PLANET_ACTION_ORDER_TYPES",
    "PLANET_FMS_ACTION_ORDER_TYPES",
)


@pytest.mark.parametrize("name", _FORBIDDEN_NAMES)
def test_order_types_module_no_longer_exports_metadata_constants(name: str) -> None:
    """``order_types.py`` exports only ``OrderType``, ``Order``, and
    serialization helpers. PROJ-424 Phase 5 deleted the duplicated
    frozensets. Re-introducing them is a regression — read through
    ``order_metadata`` instead.
    """
    assert not hasattr(order_types, name), (
        f"{name!r} is back on game.strategy.data.order_types. "
        f"This is a PROJ-424 regression. Read through "
        f"game.strategy.engine.commands.order_metadata_view.order_metadata "
        f"instead of restoring the duplicated frozenset."
    )


@pytest.mark.parametrize("name", ("MOVEMENT_ORDER_TYPES", "ACTION_ORDER_TYPES"))
def test_fleet_module_no_longer_re_exports_metadata_constants(name: str) -> None:
    """``fleet.py`` re-exported two of the duplicated frozensets for
    convenience. PROJ-424 Phase 5 deleted those re-exports — consumers
    must read through ``order_metadata`` explicitly.
    """
    assert not hasattr(fleet, name), (
        f"{name!r} is back on game.strategy.data.fleet. "
        f"This is a PROJ-424 regression. Read through "
        f"game.strategy.engine.commands.order_metadata_view.order_metadata "
        f"instead of restoring the re-export."
    )
