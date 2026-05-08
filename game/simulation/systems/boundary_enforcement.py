"""Boundary-enforcement helpers for the battle engine.

PROJ-382 Phase 5: extracted from ``battle_engine.py`` to bring the parent
module under the 500 LOC ceiling.  These three free functions implement the
per-tick boundary check + ExitPolicy dispatch (NONE / DESTROY / RETREAT /
BOUNCE) that the ``BoundaryEnforcementPhase`` triggers on every tick.

The functions take an explicit ``engine`` parameter rather than ``self``
because they were extracted from ``BattleEngine`` methods; the engine
object provides the ``ships`` / ``boundary`` / ``logger`` /
``retreated_ships`` references the helpers need.  This keeps the module
free of a circular dependency on ``battle_engine``.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine


logger = logging.getLogger(__name__)


def enforce_boundary(engine: "BattleEngine") -> None:
    """Per-tick boundary check — called from the BoundaryEnforcementPhase.

    For each alive ship, if ``engine.boundary.contains(ship.position)``
    returns False, dispatch to ``apply_exit_policy(engine, ship, policy)``.
    NONE policy is the default safety net for engines constructed without an
    explicit boundary (UnboundedRegion always returns True).
    """
    boundary = engine.boundary
    if boundary is None:
        return
    policy = getattr(boundary, "exit_policy", None)
    # Snapshot the alive ships — apply_exit_policy may remove from
    # engine.ships mid-iteration.
    for ship in list(engine.ships):
        if not getattr(ship, "is_alive", True):
            continue
        if not boundary.contains(ship.position):
            apply_exit_policy(engine, ship, policy)


def apply_exit_policy(engine: "BattleEngine", ship: "Ship", policy: Any) -> None:
    """Apply the configured ``ExitPolicy`` to a ship that crossed the boundary."""
    from game.simulation.combat.boundary import ExitPolicy

    if policy is None or policy == ExitPolicy.NONE:
        return
    if policy == ExitPolicy.DESTROY:
        # Destroy the ship by applying lethal damage. Uses the normal
        # damage pipeline so SHIP_DESTROYED events fire correctly.
        remaining_hp = max(ship.hp, 1)
        ship.combat_engine.take_damage(remaining_hp)
        engine.logger.log(
            f"Boundary DESTROY: {ship.name} crossed boundary at "
            f"({ship.x:.0f}, {ship.y:.0f})"
        )
        return
    if policy == ExitPolicy.RETREAT:
        # Remove ship from active battle, track for outcome reporting.
        if ship in engine.ships:
            engine.retreated_ships.append(ship)
            engine.remove_ship(ship)
            engine.logger.log(
                f"Boundary RETREAT: {ship.name} exited battle at "
                f"({ship.x:.0f}, {ship.y:.0f})"
            )
        return
    if policy == ExitPolicy.BOUNCE:
        # Clamp to closest in-bounds point and reflect velocity.
        new_pos = engine.boundary.closest_inside_point(ship.position)
        bounce_ship(engine, ship, new_pos)
        return
    logger.warning(f"Unknown ExitPolicy: {policy!r}; treating as NONE.")


def bounce_ship(engine: "BattleEngine", ship: "Ship", new_pos: Vector2) -> None:
    """Clamp ``ship.position`` to ``new_pos`` and reflect velocity along
    the outward normal.

    For Rect boundaries we flip whichever velocity component was carrying
    the ship out; for Circle boundaries we reflect along the radial vector.
    """
    from game.simulation.combat.boundary import CircleBoundary, RectBoundary

    old_x, old_y = ship.x, ship.y
    ship.x = float(new_pos.x)
    ship.y = float(new_pos.y)
    vel = getattr(ship, "velocity", None)
    if vel is None:
        return

    boundary = engine.boundary
    if isinstance(boundary, RectBoundary):
        # Ship crossed either the X or Y extent; flip the component(s)
        # that exceed the boundary.
        half_w = boundary.width / 2.0
        half_h = boundary.height / 2.0
        if abs(old_x) > half_w:
            vel.x = -vel.x
        if abs(old_y) > half_h:
            vel.y = -vel.y
    elif isinstance(boundary, CircleBoundary):
        # Reflect velocity about the radial normal.
        r = (new_pos.x ** 2 + new_pos.y ** 2) ** 0.5
        if r > 0:
            nx = new_pos.x / r
            ny = new_pos.y / r
            dot = vel.x * nx + vel.y * ny
            vel.x -= 2 * dot * nx
            vel.y -= 2 * dot * ny
    else:
        # Fallback: flip both components.
        vel.x = -vel.x
        vel.y = -vel.y
