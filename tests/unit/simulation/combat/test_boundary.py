"""Tests for BoundaryRegion types (PROJ-269 Phase 1 Task 1.2).

Task 1.2 ships the *type shape* only: `BattleSpec.boundary` is well-typed,
and each concrete type has the right geometric contract. Per-tick
enforcement inside the engine lands in Phase 3 — no tests here exercise
the engine.

Covers:
- `ExitPolicy` enum (DESTROY / RETREAT / BOUNCE / NONE)
- `BoundaryRegion` protocol — runtime-checkable, carries `exit_policy`,
  `contains(pos)`, `closest_inside_point(pos)`
- `RectBoundary`, `CircleBoundary`, `UnboundedRegion` satisfy the protocol
- `UnboundedRegion.contains(any)` is always True
- Rect and Circle basic geometry
"""
from enum import Enum

import pytest

from game.core.math import Vector2
from game.simulation.combat.boundary import (
    BoundaryRegion,
    CircleBoundary,
    ExitPolicy,
    RectBoundary,
    UnboundedRegion,
)


# ---------------------------------------------------------------------------
# ExitPolicy enum
# ---------------------------------------------------------------------------


def test_exit_policy_is_enum_with_required_members():
    assert issubclass(ExitPolicy, Enum)
    names = {m.name for m in ExitPolicy}
    assert {"DESTROY", "RETREAT", "BOUNCE", "NONE"}.issubset(names)


# ---------------------------------------------------------------------------
# Protocol conformance — duck-typed: each class carries the expected methods
# + `exit_policy` attribute.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "region",
    [
        RectBoundary(width=1000.0, height=1000.0, exit_policy=ExitPolicy.DESTROY),
        CircleBoundary(radius=500.0, exit_policy=ExitPolicy.RETREAT),
        UnboundedRegion(),
    ],
)
def test_region_implements_protocol(region):
    # Protocol-level attribute/method presence — duck typing for test-mock
    # compatibility per docs/02_PATTERNS.md Protocol + TypeGuard.
    assert hasattr(region, "exit_policy")
    assert callable(getattr(region, "contains", None))
    assert callable(getattr(region, "closest_inside_point", None))
    assert isinstance(region, BoundaryRegion)


# ---------------------------------------------------------------------------
# UnboundedRegion — always contains every point; fixed NONE policy.
# ---------------------------------------------------------------------------


def test_unbounded_region_contains_any_point():
    region = UnboundedRegion()
    assert region.contains(Vector2(0, 0)) is True
    assert region.contains(Vector2(1e9, -1e9)) is True
    assert region.contains(Vector2(-1e12, 1e12)) is True


def test_unbounded_region_exit_policy_is_none():
    assert UnboundedRegion().exit_policy == ExitPolicy.NONE


def test_unbounded_region_closest_inside_returns_same_point():
    region = UnboundedRegion()
    pt = Vector2(123.0, -456.0)
    closest = region.closest_inside_point(pt)
    assert closest == pt


# ---------------------------------------------------------------------------
# RectBoundary — centered on (0, 0), width/height extent.
# ---------------------------------------------------------------------------


def test_rect_boundary_contains_inside_point():
    rect = RectBoundary(width=1000.0, height=600.0, exit_policy=ExitPolicy.DESTROY)
    assert rect.contains(Vector2(0, 0)) is True
    assert rect.contains(Vector2(499.0, 299.0)) is True
    assert rect.contains(Vector2(-499.0, -299.0)) is True


def test_rect_boundary_excludes_outside_point():
    rect = RectBoundary(width=1000.0, height=600.0, exit_policy=ExitPolicy.DESTROY)
    assert rect.contains(Vector2(501.0, 0)) is False
    assert rect.contains(Vector2(0, 301.0)) is False
    assert rect.contains(Vector2(-501.0, -301.0)) is False


def test_rect_boundary_contains_on_boundary_is_inclusive():
    # Boundary points count as inside. Half-extent = w/2, h/2.
    rect = RectBoundary(width=100.0, height=50.0, exit_policy=ExitPolicy.BOUNCE)
    assert rect.contains(Vector2(50.0, 25.0)) is True
    assert rect.contains(Vector2(-50.0, -25.0)) is True


def test_rect_boundary_closest_inside_clamps_to_extents():
    rect = RectBoundary(width=200.0, height=100.0, exit_policy=ExitPolicy.BOUNCE)
    closest = rect.closest_inside_point(Vector2(500.0, 500.0))
    assert closest == Vector2(100.0, 50.0)
    closest_neg = rect.closest_inside_point(Vector2(-500.0, -500.0))
    assert closest_neg == Vector2(-100.0, -50.0)


# ---------------------------------------------------------------------------
# CircleBoundary — centered on (0, 0), radius extent.
# ---------------------------------------------------------------------------


def test_circle_boundary_contains_inside_point():
    circle = CircleBoundary(radius=100.0, exit_policy=ExitPolicy.RETREAT)
    assert circle.contains(Vector2(0, 0)) is True
    assert circle.contains(Vector2(50.0, 50.0)) is True  # dist ~70.7
    assert circle.contains(Vector2(99.0, 0.0)) is True


def test_circle_boundary_excludes_outside_point():
    circle = CircleBoundary(radius=100.0, exit_policy=ExitPolicy.RETREAT)
    assert circle.contains(Vector2(101.0, 0.0)) is False
    assert circle.contains(Vector2(80.0, 80.0)) is False  # dist ~113


def test_circle_boundary_contains_on_boundary_is_inclusive():
    circle = CircleBoundary(radius=50.0, exit_policy=ExitPolicy.DESTROY)
    assert circle.contains(Vector2(50.0, 0)) is True
    assert circle.contains(Vector2(0, -50.0)) is True


def test_circle_boundary_closest_inside_projects_to_radius():
    circle = CircleBoundary(radius=100.0, exit_policy=ExitPolicy.BOUNCE)
    closest = circle.closest_inside_point(Vector2(300.0, 0.0))
    assert closest.x == pytest.approx(100.0)
    assert closest.y == pytest.approx(0.0)


def test_circle_boundary_closest_inside_returns_inside_points_unchanged():
    circle = CircleBoundary(radius=100.0, exit_policy=ExitPolicy.BOUNCE)
    pt = Vector2(10.0, 20.0)
    closest = circle.closest_inside_point(pt)
    assert closest == pt


# ---------------------------------------------------------------------------
# Frozen behavior — concrete boundaries are frozen dataclasses.
# ---------------------------------------------------------------------------


def test_rect_boundary_is_frozen():
    import dataclasses

    rect = RectBoundary(width=1.0, height=1.0, exit_policy=ExitPolicy.DESTROY)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rect.width = 2.0  # type: ignore[misc]


def test_circle_boundary_is_frozen():
    import dataclasses

    circle = CircleBoundary(radius=1.0, exit_policy=ExitPolicy.DESTROY)
    with pytest.raises(dataclasses.FrozenInstanceError):
        circle.radius = 2.0  # type: ignore[misc]
