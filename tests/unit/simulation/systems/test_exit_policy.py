"""Tests for `ExitPolicy` application (PROJ-269 Phase 3 Task 3.2).

Covers:
- DESTROY: ship outside boundary is killed via the damage pipeline
- RETREAT: ship outside boundary is removed from engine.ships, tracked
  on engine.retreated_ships
- BOUNCE: ship's position clamped to closest_inside_point; velocity
  reflected (RectBoundary: flip component, CircleBoundary: radial reflect)
- NONE: no-op (verified in Task 3.1 tests)
"""
from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.combat.boundary import (
    CircleBoundary,
    ExitPolicy,
    RectBoundary,
)
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _make_ship(fresh_registries, name: str, x: float, y: float, team_id: int):
    from game.simulation.entities.ship import Ship

    return Ship(
        name=name,
        x=x,
        y=y,
        color=(200, 200, 200),
        team_id=team_id,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries,
    )


# ---------------------------------------------------------------------------
# DESTROY
# ---------------------------------------------------------------------------


def test_destroy_policy_kills_ship_outside_boundary(fresh_registries):
    boundary = RectBoundary(width=1000.0, height=1000.0, exit_policy=ExitPolicy.DESTROY)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)

    ship_outside = _make_ship(fresh_registries, "Outside", 5000.0, 0, 0)
    ship_inside = _make_ship(fresh_registries, "Inside", 100.0, 0, 1)
    engine.start([ship_outside], [ship_inside], seed=0, end_condition=TickLimitCondition(max_ticks=2))

    # Tick once — the BoundaryEnforcementPhase should trigger DESTROY.
    engine.update()

    assert not ship_outside.is_alive, "Ship outside DESTROY boundary must be dead"
    assert ship_inside.is_alive, "Ship inside DESTROY boundary must remain alive"


# ---------------------------------------------------------------------------
# RETREAT
# ---------------------------------------------------------------------------


def test_retreat_policy_removes_ship_from_engine(fresh_registries):
    boundary = RectBoundary(width=1000.0, height=1000.0, exit_policy=ExitPolicy.RETREAT)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)

    fleeing = _make_ship(fresh_registries, "Fleeing", 5000.0, 0, 0)
    remaining = _make_ship(fresh_registries, "Remaining", 100.0, 0, 1)
    engine.start([fleeing], [remaining], seed=0, end_condition=TickLimitCondition(max_ticks=2))

    engine.update()

    assert fleeing not in engine.ships
    assert fleeing in engine.retreated_ships
    assert remaining in engine.ships
    # Fleeing ship is not destroyed — just removed.
    assert fleeing.is_alive is True


# ---------------------------------------------------------------------------
# BOUNCE
# ---------------------------------------------------------------------------


def test_bounce_policy_clamps_position_to_rect_boundary(fresh_registries):
    """Integration: a ship outside the rect gets its position clamped
    to the nearest in-bounds point via `_apply_exit_policy(BOUNCE)`.

    Velocity reflection is unit-tested on `_bounce_ship` directly
    (below) — in the integration tick the physics drag dominates, so
    the velocity magnitude by the time bounce runs is non-deterministic.
    """
    boundary = RectBoundary(width=200.0, height=200.0, exit_policy=ExitPolicy.BOUNCE)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)

    # Place ship outside +X extent (half-width = 100)
    ship = _make_ship(fresh_registries, "Bouncer", 500.0, 0, 0)
    other = _make_ship(fresh_registries, "Other", -5000.0, 0, 1)
    engine.start([ship], [other], seed=0, end_condition=TickLimitCondition(max_ticks=1))

    engine.update()

    # Clamped to +X extent: half-width = 100
    assert ship.x == 100.0


def test_bounce_unit_rect_flips_x_velocity(fresh_registries):
    """Unit test for `_bounce_ship` with a RectBoundary."""
    boundary = RectBoundary(width=200.0, height=200.0, exit_policy=ExitPolicy.BOUNCE)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)
    ship = _make_ship(fresh_registries, "B", 500.0, 0, 0)
    ship.velocity = Vector2(50.0, 0.0)

    # Clamp + flip
    engine._bounce_ship(ship, Vector2(100.0, 0.0))

    assert ship.x == 100.0
    assert ship.velocity.x == -50.0


def test_bounce_unit_rect_flips_y_velocity(fresh_registries):
    boundary = RectBoundary(width=200.0, height=200.0, exit_policy=ExitPolicy.BOUNCE)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)
    ship = _make_ship(fresh_registries, "B", 0, 500.0, 0)
    ship.velocity = Vector2(0.0, 50.0)

    engine._bounce_ship(ship, Vector2(0.0, 100.0))
    assert ship.y == 100.0
    assert ship.velocity.y == -50.0


def test_bounce_unit_circle_reflects_radial(fresh_registries):
    """Unit test for `_bounce_ship` with a CircleBoundary — velocity
    reflected about the radial normal at the clamp point."""
    boundary = CircleBoundary(radius=100.0, exit_policy=ExitPolicy.BOUNCE)
    engine = BattleEngine(ai_factory=AIControllerFactory(), boundary=boundary)
    ship = _make_ship(fresh_registries, "B", 300.0, 0, 0)
    ship.velocity = Vector2(10.0, 0.0)  # pointing outward

    engine._bounce_ship(ship, Vector2(100.0, 0.0))

    assert ship.x == 100.0
    # Radial normal at (100, 0) is (1, 0); 10*1 = 10, reflect: v.x -= 2*10*1 = -10.
    assert ship.velocity.x == -10.0
