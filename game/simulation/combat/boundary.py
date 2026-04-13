"""BoundaryRegion types — first-class arena boundary for BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.2.

`BattleSpec.boundary: Optional[BoundaryRegion]` carries the arena shape into
the engine:
  - Strategy reads a default from `game_settings.combat_boundary_default`.
  - Battle Setup exposes it to the user (UI dropdown).
  - Combat Lab scenarios specify it per test (often `UnboundedRegion`).

`None` or `UnboundedRegion` both mean "unbounded combat". Engine enforcement
(per-tick `contains()` check with `_apply_exit_policy()`) lands in Phase 3.
Phase 1 ships only the type shape so `BattleSpec` is well-typed.

Each boundary carries an `ExitPolicy`:
  - DESTROY — ship removed, status=DESTROYED (warp-out-to-void)
  - RETREAT — ship removed, status=RETREATED
  - BOUNCE — ship reflected back elastically
  - NONE — ship may exit freely (unrestricted Combat Lab scenarios)

All three concrete types are frozen dataclasses so they're hashable /
comparable and safe to stuff into a BattleSpec.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from game.core.math import Vector2


class ExitPolicy(Enum):
    """What happens when a ship crosses the boundary."""

    DESTROY = "destroy"
    RETREAT = "retreat"
    BOUNCE = "bounce"
    NONE = "none"


@runtime_checkable
class BoundaryRegion(Protocol):
    """Protocol for arena boundary shapes.

    Per `docs/02_PATTERNS.md` — runtime-checkable protocol. Callers that
    need a narrow type check should use duck-typing (`hasattr`) rather
    than `isinstance(obj, BoundaryRegion)` for mock compatibility.
    """

    exit_policy: ExitPolicy

    def contains(self, pos: Vector2) -> bool:
        """Return True if `pos` lies inside (or on) the boundary."""
        ...

    def closest_inside_point(self, pos: Vector2) -> Vector2:
        """Return the closest point inside the boundary to `pos`.

        Used by `BOUNCE` exit policy to reflect ships back in-bounds.
        For points already inside, returns `pos` unchanged.
        """
        ...

    def closest_edge_point(self, pos: Vector2) -> Vector2:
        """Return the closest point ON the boundary (perimeter) to `pos`.

        Used by `RetreatManager.find_nearest_edge` to navigate a
        retreating ship toward the arena edge. Unbounded regions have
        no edge — `UnboundedRegion.closest_edge_point` raises
        `NotImplementedError`.
        """
        ...

    def distance_to_edge(self, pos: Vector2) -> float:
        """Return the distance from `pos` to the nearest boundary edge.

        Used by `RetreatManager.at_map_edge` with a threshold check.
        For points inside the boundary, returns the positive gap to
        the perimeter. `UnboundedRegion.distance_to_edge` returns
        `math.inf` so edge-threshold checks naturally return False.
        """
        ...


@dataclass(frozen=True)
class RectBoundary:
    """Axis-aligned rectangular boundary centered on the origin.

    `width` and `height` are the full extents — half-extents `width/2`
    and `height/2` lie on each side of (0, 0). Boundary points count as
    inside.
    """

    width: float
    height: float
    exit_policy: ExitPolicy

    def contains(self, pos: Vector2) -> bool:
        half_w = self.width / 2.0
        half_h = self.height / 2.0
        return (-half_w <= pos.x <= half_w) and (-half_h <= pos.y <= half_h)

    def closest_inside_point(self, pos: Vector2) -> Vector2:
        half_w = self.width / 2.0
        half_h = self.height / 2.0
        clamped_x = max(-half_w, min(half_w, pos.x))
        clamped_y = max(-half_h, min(half_h, pos.y))
        return Vector2(clamped_x, clamped_y)

    def closest_edge_point(self, pos: Vector2) -> Vector2:
        half_w = self.width / 2.0
        half_h = self.height / 2.0
        dist_left = pos.x - (-half_w)
        dist_right = half_w - pos.x
        dist_top = pos.y - (-half_h)
        dist_bottom = half_h - pos.y
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
        if min_dist == dist_left:
            return Vector2(-half_w, pos.y)
        if min_dist == dist_right:
            return Vector2(half_w, pos.y)
        if min_dist == dist_top:
            return Vector2(pos.x, -half_h)
        return Vector2(pos.x, half_h)

    def distance_to_edge(self, pos: Vector2) -> float:
        half_w = self.width / 2.0
        half_h = self.height / 2.0
        dist_left = pos.x - (-half_w)
        dist_right = half_w - pos.x
        dist_top = pos.y - (-half_h)
        dist_bottom = half_h - pos.y
        return min(dist_left, dist_right, dist_top, dist_bottom)


@dataclass(frozen=True)
class CircleBoundary:
    """Circular boundary centered on the origin with the given radius."""

    radius: float
    exit_policy: ExitPolicy

    def contains(self, pos: Vector2) -> bool:
        # Compare squared distance to avoid sqrt.
        return (pos.x * pos.x + pos.y * pos.y) <= (self.radius * self.radius)

    def closest_inside_point(self, pos: Vector2) -> Vector2:
        dist_sq = pos.x * pos.x + pos.y * pos.y
        if dist_sq <= self.radius * self.radius:
            return pos
        # Project onto the circle boundary.
        dist = dist_sq ** 0.5
        scale = self.radius / dist
        return Vector2(pos.x * scale, pos.y * scale)

    def closest_edge_point(self, pos: Vector2) -> Vector2:
        dist_sq = pos.x * pos.x + pos.y * pos.y
        if dist_sq == 0.0:
            # Ambiguous — pick +x direction by convention.
            return Vector2(self.radius, 0.0)
        dist = dist_sq ** 0.5
        scale = self.radius / dist
        return Vector2(pos.x * scale, pos.y * scale)

    def distance_to_edge(self, pos: Vector2) -> float:
        dist = (pos.x * pos.x + pos.y * pos.y) ** 0.5
        return abs(self.radius - dist)


@dataclass(frozen=True)
class UnboundedRegion:
    """Always contains every point — marks an unbounded arena.

    `exit_policy` is fixed at `ExitPolicy.NONE` — ships never exit
    because they can never leave.
    """

    exit_policy: ExitPolicy = ExitPolicy.NONE

    def contains(self, pos: Vector2) -> bool:
        return True

    def closest_inside_point(self, pos: Vector2) -> Vector2:
        return pos

    def closest_edge_point(self, pos: Vector2) -> Vector2:
        raise NotImplementedError(
            "UnboundedRegion has no edge — callers must check "
            "`distance_to_edge() != math.inf` or type-check before "
            "invoking closest_edge_point."
        )

    def distance_to_edge(self, pos: Vector2) -> float:
        return math.inf


__all__ = [
    "BoundaryRegion",
    "CircleBoundary",
    "ExitPolicy",
    "RectBoundary",
    "UnboundedRegion",
]
