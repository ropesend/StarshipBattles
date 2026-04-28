"""PROJ-312 Phase 1 — ErraticBehavior seeded determinism.

Verifies that ``ErraticBehavior`` consumes its RNG via dependency injection
(no module-level ``random.*`` calls). Two instances built with the same
seed must produce identical sequences of direction-change decisions and
interval choices; instances built with different seeds must diverge.

This is the unit-level proof that PROJ-312 Phase 1's RNG plumbing is
correct. The integration-level proof lives in
``tests/integration/fleet_combat/test_battle_determinism.py``.
"""
from __future__ import annotations

import random
from typing import List, Tuple
from unittest.mock import Mock

import pytest

from game.ai.behaviors import ErraticBehavior
from game.core.config import AIConfig
from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Mock ship that satisfies ErraticBehavior's call surface."""
    ship = Mock()
    ship.get_position.return_value = Vector2(100, 100)
    ship.get_rotation.return_value = 0.0
    ship.thrust_forward = Mock()
    ship.rotate = Mock()
    return ship


@pytest.fixture
def mock_controller(mock_ship):
    """Mock controller wrapping the mock ship."""
    controller = Mock()
    controller.ship = mock_ship
    return controller


def _record_sequence(behavior: ErraticBehavior, *, ticks: int) -> List[Tuple[int, float]]:
    """Drive the behavior through `ticks` updates and record its decisions.

    Returns a list of (current_direction, next_change_interval) tuples sampled
    at every tick.
    """
    behavior.enter()
    samples: List[Tuple[int, float]] = [
        (behavior.current_direction, behavior.next_change_interval)
    ]
    # Force quick direction changes so the seed actually drives multiple
    # decisions within the captured window.
    behavior.next_change_interval = 0.001
    for _ in range(ticks):
        behavior.update(target=None, strategy={})
        samples.append((behavior.current_direction, behavior.next_change_interval))
    return samples


class TestErraticBehaviorSeededDeterminism:
    """PROJ-312 Phase 1 — Task 1.5."""

    def test_same_seed_produces_identical_sequence(self, mock_controller):
        """Two ErraticBehaviors with the same seed must agree tick-by-tick."""
        a = ErraticBehavior(mock_controller, rng=random.Random(42))
        b = ErraticBehavior(mock_controller, rng=random.Random(42))
        seq_a = _record_sequence(a, ticks=100)
        seq_b = _record_sequence(b, ticks=100)
        assert seq_a == seq_b, (
            "Two ErraticBehaviors built with seed=42 produced divergent "
            "decision sequences. RNG plumbing is broken or a non-seeded "
            "random.* call is leaking into the hot path."
        )

    def test_different_seeds_diverge(self, mock_controller):
        """Different seeds must drive different decisions (sanity check)."""
        a = ErraticBehavior(mock_controller, rng=random.Random(42))
        b = ErraticBehavior(mock_controller, rng=random.Random(43))
        seq_a = _record_sequence(a, ticks=100)
        seq_b = _record_sequence(b, ticks=100)
        assert seq_a != seq_b, (
            "Seeds 42 and 43 produced identical sequences — the RNG isn't "
            "actually steering ErraticBehavior decisions."
        )

    def test_enter_uses_injected_rng(self, mock_controller):
        """`enter()` must consume the injected RNG, not module-level random."""
        # Burn the injected RNG to a known state, then consume the next two
        # values directly. Build a fresh behavior with an RNG primed to the
        # same state and assert enter() picks the same direction + interval.
        rng_probe = random.Random(99)
        expected_direction = rng_probe.choice([-1, 1])
        expected_interval = rng_probe.uniform(
            AIConfig.ERRATIC_TURN_INTERVAL_MIN,
            AIConfig.ERRATIC_TURN_INTERVAL_MAX,
        )

        rng = random.Random(99)
        behavior = ErraticBehavior(mock_controller, rng=rng)
        behavior.enter()

        assert behavior.current_direction == expected_direction
        assert behavior.next_change_interval == expected_interval

    def test_rng_kwarg_is_required(self, mock_controller):
        """No silent fallback: ErraticBehavior must demand an explicit rng."""
        with pytest.raises(TypeError):
            ErraticBehavior(mock_controller)  # type: ignore[call-arg]
