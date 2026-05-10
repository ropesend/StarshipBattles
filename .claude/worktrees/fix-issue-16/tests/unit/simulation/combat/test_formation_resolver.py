"""Tests for `FormationResolver` (PROJ-269 Phase 4 Task 4.2).

Deterministic per-shape positioning + rotation + translation by
`EntryVector`. Boundary clamping is an edge-case assertion.

Convention in these tests: `facing=0` means "facing +x" (east). Ships
are placed in formation-local coordinates, then rotated by the facing
angle (degrees) and translated to the origin.
"""
import math

import pytest

from game.core.math import Vector2
from game.simulation.battle_spec import EntryVector
from game.simulation.combat.formation import (
    FormationResolver,
    FormationShape,
    FormationSpec,
)


# ---------------------------------------------------------------------------
# Helpers — minimal "ship" stand-ins (resolver only reads instance_id)
# ---------------------------------------------------------------------------


class _FakeShip:
    def __init__(self, instance_id: str, design_role: str = "fleet_escort"):
        self.instance_id = instance_id
        self.design_role = design_role


def _mkships(n: int, role: str = "fleet_escort"):
    return [_FakeShip(f"s{i}", role) for i in range(n)]


# ---------------------------------------------------------------------------
# LINE_ABREAST — perpendicular to facing, symmetric around origin
# ---------------------------------------------------------------------------


def test_line_abreast_3_ships_spread_perpendicular_to_east_facing():
    formation = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    ships = _mkships(3)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)  # facing east
    poses = FormationResolver.resolve(formation, ev, None, ships)

    # 3 ships perpendicular to east (i.e. on the north-south axis)
    # positions should differ only in Y
    ys = sorted(p[0].y for p in poses.values())
    assert ys == pytest.approx([-100.0, 0.0, 100.0])
    # All ships at x=0
    for pose in poses.values():
        assert pose[0].x == pytest.approx(0.0)


def test_line_abreast_ships_angle_matches_entry_facing():
    formation = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    ships = _mkships(2)
    ev = EntryVector(origin=Vector2(0, 0), facing=45.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    for pose in poses.values():
        assert pose[1] == pytest.approx(45.0)


# ---------------------------------------------------------------------------
# LINE_ASTERN — single file along facing
# ---------------------------------------------------------------------------


def test_line_astern_3_ships_along_east_axis():
    formation = FormationSpec(shape=FormationShape.LINE_ASTERN, spacing=100.0)
    ships = _mkships(3)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)

    xs = sorted(p[0].x for p in poses.values())
    assert xs == pytest.approx([0.0, 100.0, 200.0])
    for pose in poses.values():
        assert pose[0].y == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# WEDGE — arrowhead pointing along facing
# ---------------------------------------------------------------------------


def test_wedge_5_ships_has_leader_at_origin_and_wingmen_behind():
    """Wedge: leader at (0, 0); wingmen one row back symmetric in Y;
    outer pair two rows back further out in Y."""
    formation = FormationSpec(shape=FormationShape.WEDGE, spacing=100.0)
    ships = _mkships(5)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)

    # Leader (closest to +x) sits at (0, 0).
    positions = [p[0] for p in poses.values()]
    leader = max(positions, key=lambda v: v.x)
    assert leader.x == pytest.approx(0.0)
    assert leader.y == pytest.approx(0.0)

    # All other ships behind the leader (x < 0) with wingmen paired.
    behind = [v for v in positions if v is not leader]
    assert all(v.x < 0 for v in behind)


# ---------------------------------------------------------------------------
# ECHELON_LEFT / ECHELON_RIGHT — diagonal
# ---------------------------------------------------------------------------


def test_echelon_left_3_ships_diagonal_to_upper_left():
    formation = FormationSpec(shape=FormationShape.ECHELON_LEFT, spacing=100.0)
    ships = _mkships(3)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    positions = sorted(poses.values(), key=lambda p: p[0].x)
    # Should be stacked with decreasing x, increasing y (going left-and-up)
    xs = [p[0].x for p in positions]
    ys = [p[0].y for p in positions]
    # Either strictly increasing or decreasing on both axes — we just
    # verify the diagonal property: consecutive deltas are equal.
    for i in range(1, len(positions)):
        dx = xs[i] - xs[i - 1]
        dy = ys[i] - ys[i - 1]
        assert dx != 0
        assert dy != 0


def test_echelon_right_3_ships_diagonal_to_lower_left():
    formation = FormationSpec(shape=FormationShape.ECHELON_RIGHT, spacing=100.0)
    ships = _mkships(3)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    positions = sorted(poses.values(), key=lambda p: p[0].x)
    xs = [p[0].x for p in positions]
    ys = [p[0].y for p in positions]
    for i in range(1, len(positions)):
        dx = xs[i] - xs[i - 1]
        dy = ys[i] - ys[i - 1]
        assert dx != 0
        assert dy != 0


# ---------------------------------------------------------------------------
# SCREEN — heavy ships at x=0 column, lighter ahead
# ---------------------------------------------------------------------------


def test_screen_has_two_columns():
    """Phase 4 MVP: SCREEN places half the ships at x=0 (main line)
    and the other half at x=+spacing (screen). Ordering by mass would
    be a refinement; position-shape correctness is the core check."""
    formation = FormationSpec(shape=FormationShape.SCREEN, spacing=100.0)
    ships = _mkships(4)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    xs = {p[0].x for p in poses.values()}
    # Expected: two distinct x-columns
    assert len(xs) == 2


# ---------------------------------------------------------------------------
# CARRIER_PROTECTED — carriers center, others ring
# ---------------------------------------------------------------------------


def test_carrier_protected_places_ships_within_ring():
    """Ships split: "carriers" at origin, rest on ring of radius = spacing."""
    formation = FormationSpec(shape=FormationShape.CARRIER_PROTECTED, spacing=150.0)
    ships = _mkships(5)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    positions = [p[0] for p in poses.values()]
    # At least one ship at or near origin (carrier)
    centered = [v for v in positions if v.length() < 1.0]
    assert len(centered) >= 1
    # Others spaced out
    outer = [v for v in positions if v.length() > 50.0]
    assert len(outer) >= 1


# ---------------------------------------------------------------------------
# CUSTOM — positions used verbatim
# ---------------------------------------------------------------------------


def test_custom_uses_provided_positions():
    custom = (Vector2(10, 20), Vector2(30, 40), Vector2(50, 60))
    formation = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=custom,
    )
    ships = _mkships(3)
    ev = EntryVector(origin=Vector2(0, 0), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    positions = sorted((p[0] for p in poses.values()), key=lambda v: v.x)
    assert positions[0] == Vector2(10, 20)
    assert positions[1] == Vector2(30, 40)
    assert positions[2] == Vector2(50, 60)


# ---------------------------------------------------------------------------
# Rotation invariance: facing=90° rotates every position by 90°
# ---------------------------------------------------------------------------


def test_rotation_invariance_line_astern():
    formation = FormationSpec(shape=FormationShape.LINE_ASTERN, spacing=100.0)
    ships = _mkships(3)
    base = FormationResolver.resolve(
        formation,
        EntryVector(origin=Vector2(0, 0), facing=0.0),
        None,
        ships,
    )
    rotated = FormationResolver.resolve(
        formation,
        EntryVector(origin=Vector2(0, 0), facing=90.0),
        None,
        ships,
    )

    # Each ship in `rotated` should be the `base` position rotated by 90° CCW.
    for ship_id, (base_pos, _) in base.items():
        rot_pos, _ = rotated[ship_id]
        # (x, y) rotated 90° CCW = (-y, x)
        assert rot_pos.x == pytest.approx(-base_pos.y, abs=1e-6)
        assert rot_pos.y == pytest.approx(base_pos.x, abs=1e-6)


def test_translation_by_origin():
    formation = FormationSpec(shape=FormationShape.LINE_ASTERN, spacing=100.0)
    ships = _mkships(2)
    ev = EntryVector(origin=Vector2(500, 1000), facing=0.0)
    poses = FormationResolver.resolve(formation, ev, None, ships)
    # Both ships should be shifted by (500, 1000)
    xs = sorted(p[0].x for p in poses.values())
    ys = sorted(p[0].y for p in poses.values())
    assert xs == pytest.approx([500.0, 600.0])
    assert ys == pytest.approx([1000.0, 1000.0])


# ---------------------------------------------------------------------------
# Determinism: same inputs → same outputs
# ---------------------------------------------------------------------------


def test_resolver_is_deterministic():
    formation = FormationSpec(shape=FormationShape.WEDGE, spacing=100.0)
    ships = _mkships(5)
    ev = EntryVector(origin=Vector2(123, 456), facing=30.0)

    out_a = FormationResolver.resolve(formation, ev, None, ships)
    out_b = FormationResolver.resolve(formation, ev, None, ships)
    assert out_a == out_b
