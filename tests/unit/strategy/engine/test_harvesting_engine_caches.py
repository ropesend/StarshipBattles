"""PROJ-412 Phase 5 — per-turn cache contract for HarvestingEngine."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.engine.harvesting_engine import HarvestingEngine


def _make_empire(empire_id: int = 0) -> Empire:
    emp = MagicMock(spec=Empire)
    emp.id = empire_id
    emp.colonies = []
    emp.max_storage = {}
    emp._storage_dirty = True
    emp._booster_dirty = True
    return emp


def _make_engine(fresh_registries) -> HarvestingEngine:
    return HarvestingEngine(registries=fresh_registries)


def test_storage_cache_hits_after_first_rebuild(fresh_registries) -> None:
    engine = _make_engine(fresh_registries)
    empire = _make_empire()
    engine.set_current_turn(1)

    # First tick of the turn → miss (turn-key miss).
    engine.process_harvesting_tick(1, [empire])
    counters = engine._cache_counters
    assert counters['storage_misses_turn'] == 1
    assert counters['storage_hits'] == 0

    # Ticks 2..100 of the same turn → hits.
    for tick in range(2, 101):
        engine.process_harvesting_tick(tick, [empire])
    assert counters['storage_misses_turn'] == 1
    assert counters['storage_hits'] == 99


def test_storage_cache_dirty_flag_forces_rebuild(fresh_registries) -> None:
    engine = _make_engine(fresh_registries)
    empire = _make_empire()
    engine.set_current_turn(1)

    engine.process_harvesting_tick(1, [empire])
    assert engine._cache_counters['storage_misses_turn'] == 1

    # Simulate a mutator flipping the dirty flag mid-turn.
    empire._storage_dirty = True
    engine.process_harvesting_tick(2, [empire])
    assert engine._cache_counters['storage_misses_dirty'] == 1


def test_turn_change_forces_rebuild(fresh_registries) -> None:
    engine = _make_engine(fresh_registries)
    empire = _make_empire()
    engine.set_current_turn(1)
    engine.process_harvesting_tick(1, [empire])

    engine.set_current_turn(2)
    engine.process_harvesting_tick(1, [empire])
    assert engine._cache_counters['storage_misses_turn'] == 2


def test_invalidate_turn_caches_clears_state(fresh_registries) -> None:
    engine = _make_engine(fresh_registries)
    empire = _make_empire()
    engine.set_current_turn(5)
    engine.process_harvesting_tick(1, [empire])
    assert engine._storage_cache_turn.get(empire.id) == 5

    engine.invalidate_turn_caches()
    assert engine._storage_cache_turn == {}
    assert engine._booster_cache == {}

    # Same turn number, but cache was cleared → another miss.
    engine.process_harvesting_tick(1, [empire])
    assert engine._cache_counters['storage_misses_turn'] == 2
