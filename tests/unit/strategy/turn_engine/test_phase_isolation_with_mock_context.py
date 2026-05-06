"""
PROJ-369 Phase 5 — per-phase descriptor isolation tests.

Demonstrates the descriptor pattern's testability win: each phase
descriptor's ``callable_target`` and ``args_resolver`` can be exercised
against a minimal mock engine exposing only the engines the descriptor
reads. No full ``TurnEngine`` construction needed; no real production
engines instantiated.

This is a regression-strength contract. If a future descriptor edit
adds a hidden dependency on another engine, these tests will fail
because the mock engine won't expose that engine.

Five descriptors are exercised below — chosen to span the breadth of
arg shapes:
- ``harvesting`` — single-list arg, single-engine read.
- ``combat`` — set-kwarg (``moved_fleet_ids``) + multi-arg.
- ``organics_consumption`` — end-of-turn, single-list arg.
- ``quality_improvement`` — end-of-turn, terraforming engine.
- ``population_growth`` — end-of-turn, depends on `last_food_ratio`
  written by an earlier phase (verified upstream by the order test).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.engine.turn_phase_registry import (
    DEFAULT_END_OF_TURN_PHASE_LIST,
    DEFAULT_TICK_PHASE_LIST,
    TickContext,
)


def _find_phase(descriptor_list, phase_key):
    for descriptor in descriptor_list:
        if descriptor.phase_key == phase_key:
            return descriptor
    pytest.fail(f"Phase descriptor {phase_key!r} not found")


def _build_min_ctx(**overrides):
    """Build a minimal TickContext for descriptor invocation."""
    defaults = {
        "tick": 1,
        "empires": [MagicMock(name="empire", fleets=[])],
        "galaxy": MagicMock(name="galaxy"),
        "component_registry": MagicMock(name="component_registry"),
    }
    defaults.update(overrides)
    return TickContext(**defaults)


class TestDescriptorIsolation:
    """Each descriptor invokable with a minimal mock engine."""

    def test_harvesting_descriptor_invokes_with_minimal_engine(self):
        descriptor = _find_phase(DEFAULT_TICK_PHASE_LIST, "harvesting")
        mock_engine = MagicMock()
        mock_engine.harvesting_engine.process_harvesting_tick.return_value = []

        ctx = _build_min_ctx()
        target = descriptor.callable_target(mock_engine)
        args, kwargs = descriptor.args_resolver(ctx)
        target(*args, **kwargs)

        mock_engine.harvesting_engine.process_harvesting_tick.assert_called_once_with(
            ctx.tick, ctx.empires, ctx.galaxy
        )

    def test_combat_descriptor_invokes_with_moved_fleet_ids_kwarg(self):
        descriptor = _find_phase(DEFAULT_TICK_PHASE_LIST, "combat")
        mock_engine = MagicMock()
        mock_engine.conflict_engine.resolve_all_conflicts.return_value = None

        moved = {42, 100}
        ctx = _build_min_ctx(moved_fleet_ids=moved)
        target = descriptor.callable_target(mock_engine)
        args, kwargs = descriptor.args_resolver(ctx)
        target(*args, **kwargs)

        # moved_fleet_ids is a kwarg per PROJ-320 contract.
        mock_engine.conflict_engine.resolve_all_conflicts.assert_called_once()
        call = mock_engine.conflict_engine.resolve_all_conflicts.call_args
        assert call.kwargs["moved_fleet_ids"] is moved
        assert call.kwargs["tick"] == ctx.tick
        assert call.kwargs["galaxy"] is ctx.galaxy

    def test_organics_consumption_descriptor_invokes_with_minimal_engine(self):
        descriptor = _find_phase(
            DEFAULT_END_OF_TURN_PHASE_LIST, "organics_consumption",
        )
        mock_engine = MagicMock()
        # End-of-turn phases run with tick=0 sentinel.
        ctx = _build_min_ctx(tick=0)
        target = descriptor.callable_target(mock_engine)
        args, kwargs = descriptor.args_resolver(ctx)
        target(*args, **kwargs)

        mock_engine.organics_consumption_engine.process_consumption.assert_called_once_with(
            ctx.empires
        )

    def test_quality_improvement_descriptor_invokes_through_injected_engine(self):
        """PROJ-369 Phase 2: quality_engine is now injectable via
        ``TurnEngineConfig`` and resolved through the lazy property.
        Pre-Phase-2 this descriptor used a per-call resolver helper
        that did ``QualityEngine(registries=engine._registries)``;
        Phase 2 swapped that for ``lambda e: e.quality_engine.<m>``.
        """
        descriptor = _find_phase(
            DEFAULT_END_OF_TURN_PHASE_LIST, "quality_improvement",
        )
        mock_engine = MagicMock()
        ctx = _build_min_ctx(tick=0)
        target = descriptor.callable_target(mock_engine)
        args, kwargs = descriptor.args_resolver(ctx)
        target(*args, **kwargs)

        mock_engine.quality_engine.process_quality_improvement.assert_called_once_with(
            ctx.empires
        )

    def test_population_growth_descriptor_invokes_with_minimal_engine(self):
        descriptor = _find_phase(
            DEFAULT_END_OF_TURN_PHASE_LIST, "population_growth",
        )
        mock_engine = MagicMock()
        ctx = _build_min_ctx(tick=0)
        target = descriptor.callable_target(mock_engine)
        args, kwargs = descriptor.args_resolver(ctx)
        target(*args, **kwargs)

        mock_engine.population_engine.process_population_growth.assert_called_once_with(
            ctx.empires
        )
