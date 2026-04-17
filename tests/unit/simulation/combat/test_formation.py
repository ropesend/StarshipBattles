"""Tests for FormationSpec / FormationShape (PROJ-269 Phase 1 Task 1.4).

Phase 1 only ships the type shape. The `FormationResolver` that converts
(formation, entry_vector, boundary, ships) → per-ship (position, angle)
lands in Phase 4.

Covers:
- `FormationShape` enum with all 8 documented members
- `FormationSpec` frozen dataclass with shape / spacing / custom_positions
- `custom_positions` defaults to empty tuple
"""
import dataclasses
from enum import Enum

import pytest

from game.core.math import Vector2
from game.simulation.combat.formation import FormationShape, FormationSpec


# ---------------------------------------------------------------------------
# FormationShape enum
# ---------------------------------------------------------------------------


def test_formation_shape_is_enum():
    assert issubclass(FormationShape, Enum)


def test_formation_shape_has_all_documented_members():
    names = {m.name for m in FormationShape}
    required = {
        "LINE_ABREAST",
        "LINE_ASTERN",
        "WEDGE",
        "ECHELON_LEFT",
        "ECHELON_RIGHT",
        "SCREEN",
        "CARRIER_PROTECTED",
        "CUSTOM",
    }
    missing = required - names
    assert not missing, f"FormationShape missing members: {missing}"


# ---------------------------------------------------------------------------
# FormationSpec dataclass
# ---------------------------------------------------------------------------


def test_formation_spec_is_frozen_dataclass():
    assert dataclasses.is_dataclass(FormationSpec)
    params = getattr(FormationSpec, "__dataclass_params__", None)
    assert params is not None and params.frozen


def test_formation_spec_required_fields():
    fs = FormationSpec(shape=FormationShape.WEDGE, spacing=150.0)
    assert fs.shape == FormationShape.WEDGE
    assert fs.spacing == pytest.approx(150.0)
    # custom_positions defaults to empty tuple
    assert fs.custom_positions == ()


def test_formation_spec_custom_positions_field():
    custom = (Vector2(0, 0), Vector2(100, 0), Vector2(-100, 0))
    fs = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=custom,
    )
    assert fs.custom_positions == custom
    assert isinstance(fs.custom_positions, tuple)


def test_formation_spec_is_immutable():
    fs = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=200.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        fs.spacing = 300.0  # type: ignore[misc]


def test_formation_spec_equality_semantics():
    a = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    b = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=100.0)
    c = FormationSpec(shape=FormationShape.LINE_ABREAST, spacing=200.0)
    assert a == b
    assert a != c


# ---------------------------------------------------------------------------
# resolve_team_entry_vectors (PROJ-275 Phase 2)
# ---------------------------------------------------------------------------


class TestResolveTeamEntryVectors:
    """Pure-function helper that assigns `EntryVector` per team_id.

    Convention:
    - 2 teams: team 0 at (-arena_radius, 0) facing east (0°); team 1 at
      (+arena_radius, 0) facing west (180°). Preserves the existing
      Battle Setup `_SIDE_ENTRY_VECTORS` layout EXACTLY.
    - N≥3 teams: team i at angle `180 + i*(360/N)` degrees, on a circle
      of radius `arena_radius`. All face inward (angle + 180° mod 360°).
    - team_count < 2 or > 8 raises ValueError.
    """

    def test_two_teams_preserves_legacy_west_east_layout(self):
        from game.simulation.combat.formation import resolve_team_entry_vectors

        vecs = resolve_team_entry_vectors(team_count=2, arena_radius=500.0)
        assert set(vecs.keys()) == {0, 1}
        # Team 0: west, facing east.
        assert vecs[0].origin.x == pytest.approx(-500.0)
        assert vecs[0].origin.y == pytest.approx(0.0, abs=1e-9)
        assert vecs[0].facing == pytest.approx(0.0, abs=1e-6)
        # Team 1: east, facing west (180°).
        assert vecs[1].origin.x == pytest.approx(500.0)
        assert vecs[1].origin.y == pytest.approx(0.0, abs=1e-9)
        assert vecs[1].facing == pytest.approx(180.0)

    def test_three_teams_equally_spaced_on_ring(self):
        import math

        from game.simulation.combat.formation import resolve_team_entry_vectors

        vecs = resolve_team_entry_vectors(team_count=3, arena_radius=600.0)
        assert set(vecs.keys()) == {0, 1, 2}
        # Each origin should sit on the ring of radius 600.
        for tid, ev in vecs.items():
            dist = math.hypot(ev.origin.x, ev.origin.y)
            assert dist == pytest.approx(600.0, abs=1e-6), (
                f"team {tid} origin {ev.origin} not on radius-600 ring"
            )
        # Team 0 at angle 180° → (-600, 0), facing 0°.
        assert vecs[0].origin.x == pytest.approx(-600.0)
        assert vecs[0].origin.y == pytest.approx(0.0, abs=1e-6)
        # 120° spacing between successive teams.
        for a, b in [(0, 1), (1, 2)]:
            ang_a = math.degrees(math.atan2(vecs[a].origin.y, vecs[a].origin.x))
            ang_b = math.degrees(math.atan2(vecs[b].origin.y, vecs[b].origin.x))
            delta = (ang_b - ang_a) % 360
            assert delta == pytest.approx(120.0, abs=1e-6)

    def test_four_teams_at_cardinal_directions(self):
        from game.simulation.combat.formation import resolve_team_entry_vectors

        vecs = resolve_team_entry_vectors(team_count=4, arena_radius=500.0)
        assert set(vecs.keys()) == {0, 1, 2, 3}
        # Team 0 at west (-500, 0).
        assert vecs[0].origin.x == pytest.approx(-500.0)
        assert vecs[0].origin.y == pytest.approx(0.0, abs=1e-6)
        # Team 1 at angle 270° → (0, -500).
        assert vecs[1].origin.x == pytest.approx(0.0, abs=1e-6)
        assert vecs[1].origin.y == pytest.approx(-500.0)
        # Team 2 at east (500, 0).
        assert vecs[2].origin.x == pytest.approx(500.0)
        assert vecs[2].origin.y == pytest.approx(0.0, abs=1e-6)
        # Team 3 at north (0, 500).
        assert vecs[3].origin.x == pytest.approx(0.0, abs=1e-6)
        assert vecs[3].origin.y == pytest.approx(500.0)

    def test_facings_point_inward_toward_origin(self):
        import math

        from game.simulation.combat.formation import resolve_team_entry_vectors

        for n in (2, 3, 4, 5, 6, 7, 8):
            vecs = resolve_team_entry_vectors(team_count=n, arena_radius=500.0)
            for tid, ev in vecs.items():
                # facing direction as unit vector
                f_rad = math.radians(ev.facing)
                fx, fy = math.cos(f_rad), math.sin(f_rad)
                # from origin towards (0,0): normalize -origin
                dist = math.hypot(ev.origin.x, ev.origin.y)
                if dist == 0:
                    continue
                tx, ty = -ev.origin.x / dist, -ev.origin.y / dist
                dot = fx * tx + fy * ty
                assert dot == pytest.approx(1.0, abs=1e-6), (
                    f"n={n} team {tid}: facing {ev.facing}° does not point inward "
                    f"(origin={ev.origin}, dot={dot})"
                )

    def test_raises_value_error_on_team_count_one(self):
        from game.simulation.combat.formation import resolve_team_entry_vectors

        with pytest.raises(ValueError):
            resolve_team_entry_vectors(team_count=1, arena_radius=500.0)

    def test_raises_value_error_on_team_count_zero(self):
        from game.simulation.combat.formation import resolve_team_entry_vectors

        with pytest.raises(ValueError):
            resolve_team_entry_vectors(team_count=0, arena_radius=500.0)

    def test_raises_value_error_on_team_count_nine(self):
        from game.simulation.combat.formation import resolve_team_entry_vectors

        with pytest.raises(ValueError):
            resolve_team_entry_vectors(team_count=9, arena_radius=500.0)

    def test_default_arena_radius(self):
        """When arena_radius is omitted, uses a sensible default.

        Exact value is a design decision — we assert only that it's a
        reasonable positive number.
        """
        from game.simulation.combat.formation import resolve_team_entry_vectors

        vecs = resolve_team_entry_vectors(team_count=2)
        # Some positive radius; must be non-zero.
        dist = (vecs[0].origin.x ** 2 + vecs[0].origin.y ** 2) ** 0.5
        assert dist > 0
        # Symmetric (2-team legacy layout).
        assert vecs[0].origin.x == -vecs[1].origin.x
        assert vecs[0].origin.y == vecs[1].origin.y == 0
