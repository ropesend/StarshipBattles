"""Tests for `resolve_default_for_task_force` (PROJ-269 Phase 4 Task 4.3).

Maps the dominant `design_role` of a task force's ships to a default
`FormationSpec` per decisions.md:
  - Carrier (dominant) → CARRIER_PROTECTED
  - Strike (dominant) → WEDGE
  - Defender (dominant) → LINE_ABREAST
  - Scout/Skirmisher (dominant) → LINE_ASTERN
  - Mixed (no dominant) → LINE_ABREAST
"""
from game.simulation.combat.formation import (
    FormationShape,
    FormationSpec,
    resolve_default_for_task_force,
)


class _FakeShip:
    def __init__(self, design_role: str):
        self.design_role = design_role


# ---------------------------------------------------------------------------
# Per-archetype defaults
# ---------------------------------------------------------------------------


def test_dominant_carrier_fleet_gets_carrier_protected():
    ships = [_FakeShip("carrier"), _FakeShip("carrier"), _FakeShip("fleet_escort")]
    spec = resolve_default_for_task_force(ships)
    assert spec.shape == FormationShape.CARRIER_PROTECTED


def test_dominant_strike_fleet_gets_wedge():
    ships = [
        _FakeShip("interceptor"),
        _FakeShip("interceptor"),
        _FakeShip("assault_ship"),
    ]
    spec = resolve_default_for_task_force(ships)
    assert spec.shape == FormationShape.WEDGE


def test_dominant_defender_fleet_gets_line_abreast():
    ships = [
        _FakeShip("line_combatant"),
        _FakeShip("line_combatant"),
        _FakeShip("fleet_escort"),
    ]
    spec = resolve_default_for_task_force(ships)
    assert spec.shape == FormationShape.LINE_ABREAST


def test_dominant_scout_fleet_gets_line_astern():
    ships = [_FakeShip("scout"), _FakeShip("scout"), _FakeShip("raider")]
    spec = resolve_default_for_task_force(ships)
    assert spec.shape == FormationShape.LINE_ASTERN


# ---------------------------------------------------------------------------
# Mixed / fallback
# ---------------------------------------------------------------------------


def test_no_ships_returns_line_abreast():
    spec = resolve_default_for_task_force([])
    assert spec.shape == FormationShape.LINE_ABREAST


def test_mixed_roles_returns_line_abreast():
    ships = [
        _FakeShip("carrier"),
        _FakeShip("line_combatant"),
        _FakeShip("scout"),
    ]
    spec = resolve_default_for_task_force(ships)
    # No dominant archetype (1 of each → tie). Fallback is LINE_ABREAST.
    assert spec.shape == FormationShape.LINE_ABREAST


def test_unknown_role_falls_back_to_line_abreast():
    ships = [_FakeShip("made_up_role"), _FakeShip("also_unknown")]
    spec = resolve_default_for_task_force(ships)
    assert spec.shape == FormationShape.LINE_ABREAST


# ---------------------------------------------------------------------------
# Default spacing
# ---------------------------------------------------------------------------


def test_default_formation_has_nonzero_spacing():
    ships = [_FakeShip("carrier")]
    spec = resolve_default_for_task_force(ships)
    assert spec.spacing > 0
