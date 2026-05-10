"""
PROJ-369 Phase 1 — Golden phase-list characterization tests for the
end-of-turn descriptor block in ``TurnEngine.process_turn``.

These tests pin the order of the 6 end-of-turn phases (organics →
happiness → population_growth → quality_improvement → atmosphere →
water_modification). The PROJ-284 ordering invariant
(organics_consumption writes ``last_food_ratio`` → happiness reads it →
population_growth reads happiness) must remain stable; any divergence
would cause a silent gameplay regression.

This file mirrors ``test_default_tick_phase_list.py`` for the per-tick
descriptor list. PROJ-369 Phase 1 introduces
``DEFAULT_END_OF_TURN_PHASE_LIST`` so the imperative end-of-turn block
in ``process_turn`` becomes one descriptor iteration.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.engine.turn_phase_registry import (
    DEFAULT_END_OF_TURN_PHASE_LIST,
    TickPhase,
)


GOLDEN_END_OF_TURN_ORDER = (
    'organics_consumption',
    'happiness',
    'population_growth',
    'quality_improvement',
    'atmosphere',
    'water_modification',
)


class TestDefaultEndOfTurnPhaseList:
    """Pin the 6-phase end-of-turn descriptor list ordering and shape."""

    def test_end_of_turn_phase_list_pinned_order(self):
        """The descriptor tuple must match the PROJ-284-pinned order."""
        actual = tuple(p.phase_key for p in DEFAULT_END_OF_TURN_PHASE_LIST)
        assert actual == GOLDEN_END_OF_TURN_ORDER

    def test_end_of_turn_phase_list_length_6(self):
        """Exactly 6 end-of-turn phases — no more, no less."""
        assert len(DEFAULT_END_OF_TURN_PHASE_LIST) == 6

    def test_end_of_turn_phase_keys_match_phase_times_buckets(
        self, fresh_registries
    ):
        """Every phase_key (or timing_bucket) must be a valid bucket key
        in TurnEngine._phase_times so timing accumulation works."""
        engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock(),
        )
        for descriptor in DEFAULT_END_OF_TURN_PHASE_LIST:
            bucket = descriptor.timing_bucket or descriptor.phase_key
            assert bucket in engine._phase_times, (
                f"end-of-turn descriptor {descriptor.phase_key!r} bucket "
                f"{bucket!r} is missing from _phase_times"
            )

    def test_each_descriptor_is_frozen_TickPhase(self):
        """Each entry must be a frozen ``TickPhase`` (no runtime mutation)."""
        for descriptor in DEFAULT_END_OF_TURN_PHASE_LIST:
            assert isinstance(descriptor, TickPhase)
            with pytest.raises((AttributeError, Exception)):
                # Frozen dataclass: assignment must raise dataclasses.FrozenInstanceError
                # which is a subclass of AttributeError.
                descriptor.phase_key = 'mutated'  # type: ignore[misc]
