"""PROJ-477 Phase 2 Task 2.5 — narrow scene write handle (`order_writes`).

The Category B mutator WRITE seams (set-active-empire, set-fleet-path,
pop-fleet-order) route through a tiny composition-root write handle on
``StrategyScreen`` instead of reopening the ``session`` getter. The handle is
backed by ``screen._session.active_empire`` / ``screen._session.fleet_mutator``.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.ui.screens.strategy_world_writes import StrategyOrderWrites


def test_set_active_empire_writes_session_active_empire() -> None:
    session = MagicMock()
    handle = StrategyOrderWrites(lambda: session)
    empire = MagicMock(id=3)

    handle.set_active_empire(empire)

    assert session.active_empire is empire


def test_set_fleet_path_routes_through_fleet_mutator() -> None:
    session = MagicMock()
    handle = StrategyOrderWrites(lambda: session)
    fleet = MagicMock()

    handle.set_fleet_path(fleet, [])

    session.fleet_mutator.set_path.assert_called_once_with(fleet, [])


def test_pop_fleet_order_routes_through_fleet_mutator() -> None:
    session = MagicMock()
    handle = StrategyOrderWrites(lambda: session)
    fleet = MagicMock()

    handle.pop_fleet_order(fleet, index=2)

    session.fleet_mutator.pop_order.assert_called_once_with(fleet, index=2)


def test_handle_reads_session_lazily_through_provider() -> None:
    """The handle resolves the session through a provider callable so a
    test-swapped session (``screen.session = mock``) is honoured at call time,
    not bound at construction."""
    first = MagicMock()
    second = MagicMock()
    box = {"session": first}
    handle = StrategyOrderWrites(lambda: box["session"])

    emp = MagicMock()
    handle.set_active_empire(emp)
    assert first.active_empire is emp

    box["session"] = second
    emp2 = MagicMock()
    handle.set_active_empire(emp2)
    assert second.active_empire is emp2
