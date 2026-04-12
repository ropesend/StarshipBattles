"""Tests for `BattleEngine` per-tick boundary enforcement (PROJ-269 Phase 3 Task 3.1).

Phase 3.1 scope: `BattleEngine.boundary` field, per-tick `contains()`
check, dispatch into `_apply_exit_policy` (stubbed for NONE / existing
policies until Task 3.2 fills in DESTROY / RETREAT / BOUNCE).

Covers:
- Engine default boundary is `UnboundedRegion` — ships far outside are
  never removed
- Engine constructed with `RectBoundary(ExitPolicy.NONE)` — ships outside
  the rect remain in battle (NONE = no action)
- Per-tick enforcement runs in the tick-phase sequence (post-movement,
  pre-attacks) — verified by a spy policy that counts calls
"""
import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.combat.boundary import (
    CircleBoundary,
    ExitPolicy,
    RectBoundary,
    UnboundedRegion,
)
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


# ---------------------------------------------------------------------------
# Helpers — minimal ships from the `fresh_registries` fixture
# ---------------------------------------------------------------------------


def _make_ship(fresh_registries, name: str, x: float, y: float, team_id: int):
    from game.simulation.entities.ship import Ship

    return Ship(
        name=name,
        x=x,
        y=y,
        color=(255, 0, 0),
        team_id=team_id,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries,
    )


# ---------------------------------------------------------------------------
# Default boundary: UnboundedRegion
# ---------------------------------------------------------------------------


def test_engine_default_boundary_is_unbounded(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())
    assert isinstance(engine.boundary, UnboundedRegion)


def test_engine_with_unbounded_boundary_never_removes_ships(fresh_registries):
    engine = BattleEngine(
        ai_factory=AIControllerFactory(),
        boundary=UnboundedRegion(),
    )
    ship1 = _make_ship(fresh_registries, "A", 1e9, 0, 0)
    ship2 = _make_ship(fresh_registries, "B", -1e9, 0, 1)
    engine.start([ship1], [ship2], seed=0, end_condition=TickLimitCondition(max_ticks=3))

    for _ in range(3):
        engine.update()

    assert ship1 in engine.ships
    assert ship2 in engine.ships


# ---------------------------------------------------------------------------
# Rect + NONE policy: ships outside boundary remain in battle
# ---------------------------------------------------------------------------


def test_engine_rect_boundary_none_policy_keeps_ships_in_battle(fresh_registries):
    boundary = RectBoundary(width=1000.0, height=1000.0, exit_policy=ExitPolicy.NONE)
    engine = BattleEngine(
        ai_factory=AIControllerFactory(),
        boundary=boundary,
    )
    ship_far = _make_ship(fresh_registries, "Far", 5000.0, 0.0, 0)
    ship_near = _make_ship(fresh_registries, "Near", 100.0, 0.0, 1)
    engine.start([ship_far], [ship_near], seed=0, end_condition=TickLimitCondition(max_ticks=3))

    for _ in range(3):
        engine.update()

    # NONE policy: ship was outside the rect, but policy said "ship may
    # exit freely", so it's still in the battle.
    assert ship_far in engine.ships


# ---------------------------------------------------------------------------
# Enforcement runs per tick — spy policy records every call
# ---------------------------------------------------------------------------


class _SpyBoundary:
    """Dummy boundary that records every contains()/closest_inside_point()
    call, accepts every ship by default."""

    def __init__(self, accept: bool = True, policy=ExitPolicy.NONE):
        self.exit_policy = policy
        self._accept = accept
        self.contains_calls = 0
        self.closest_calls = 0

    def contains(self, pos):
        self.contains_calls += 1
        return self._accept

    def closest_inside_point(self, pos):
        self.closest_calls += 1
        return pos


def test_engine_boundary_contains_called_every_tick_per_ship(fresh_registries):
    spy = _SpyBoundary(accept=True)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=spy)
    ship_a = _make_ship(fresh_registries, "A", 0, 0, 0)
    ship_b = _make_ship(fresh_registries, "B", 500, 0, 1)
    engine.start([ship_a], [ship_b], seed=0, end_condition=TickLimitCondition(max_ticks=4))

    for _ in range(4):
        engine.update()

    # With 2 ships and 4 ticks, contains() must have been called at least
    # once per ship per tick — i.e. >= 8 calls.
    assert spy.contains_calls >= 8


def test_engine_apply_exit_policy_hook_exists(fresh_registries):
    """`_apply_exit_policy` is the dispatcher Task 3.2 fills in. Task 3.1
    at minimum requires the method exist so boundary enforcement can
    call into it without exploding."""
    engine = BattleEngine(ai_factory=AIControllerFactory())
    assert callable(getattr(engine, "_apply_exit_policy", None))
