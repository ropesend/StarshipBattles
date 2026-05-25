"""Shared fixtures for `tests/unit/strategy/engine/order_handlers/` (PROJ-368).

Lifted from the helper functions in `tests/unit/strategy/engine/
test_order_processor_instant.py` and `..._colonize.py` so that per-handler
tests can construct realistic Fleet/Empire/event-bus stand-ins without
duplicating the patterns.
"""
from __future__ import annotations

from typing import Any, List, Tuple
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet


def _real_fleet(fleet_id: int, ship_count: int = 1, location: HexCoord = HexCoord(0, 0)) -> Fleet:
    """Real Fleet so `isinstance(target, Fleet)` and other type checks pass."""
    f = Fleet(fleet_id=fleet_id, owner_id=0, location=location)
    f.ships = [MagicMock() for _ in range(ship_count)]
    return f


def _empire_with(fleets: List[Fleet]) -> Any:
    """Mock Empire whose `remove_fleet` actually mutates `empire.fleets`."""
    e = MagicMock()
    e.id = 0
    e.fleets = list(fleets)
    e.remove_fleet = MagicMock(side_effect=lambda fl, **kw: e.fleets.remove(fl))
    return e


def _captured() -> Tuple[Any, list]:
    """Tiny stand-in for `EventBus` that records every `log_event` call."""
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    return _Bus(), captured


@pytest.fixture
def make_real_fleet_fixture():
    """Factory fixture returning a real Fleet with N MagicMock ships.

    PROJ-492 Phase 2 (HLP-004): renamed from ``make_fleet`` so it no longer
    collides with the canonical ``tests.conftest._make_mock_fleet`` namespace.
    """
    return _real_fleet


@pytest.fixture
def make_empire():
    """Factory fixture returning a mock Empire whose fleets list mutates."""
    return _empire_with


@pytest.fixture
def event_bus_capture():
    """Fixture yielding `(bus, captured_events_list)`."""
    return _captured
