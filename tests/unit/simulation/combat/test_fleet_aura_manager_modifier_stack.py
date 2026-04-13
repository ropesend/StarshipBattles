"""Tests for `FleetAuraManager` consuming `ModifierStack` (PROJ-269 Phase 5.5 Task 5.5.2).

Covers:
- `aura_manager.initialize(ships, modifier_stack=stack)` converts each
  `ModifierEntry` into an external modifier applied to the right team(s)
- Real effects (non-placeholder `stat_key`) produce the expected
  `fleet_attack_bonus` / `fleet_defense_bonus` on ships
- Global entries apply to every team
- Placeholder effects (stat_key="placeholder") are silently ignored —
  no crash, no phantom bonus
"""
from types import SimpleNamespace

import pytest

from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.components.modifier_effects import ModifierEffect


def _ship(team_id: int):
    """Minimal ship stand-in exposing the fields FleetAuraManager touches."""
    return SimpleNamespace(
        team_id=team_id,
        is_alive=True,
        is_derelict=False,
        fleet_attack_bonus=0.0,
        fleet_defense_bonus=0.0,
        get_all_components=lambda: [],
    )


def _effect(stat_key: str, value: float) -> ModifierEffect:
    return ModifierEffect(
        stat_key=stat_key,
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="mod",
        source_modifier_name="Mod",
        formula_str="param",
        param_value=value,
    )


def _entry(source: str, stat_key: str, value: float) -> ModifierEntry:
    return ModifierEntry(
        source=source,
        stack_group=None,
        effect=_effect(stat_key, value),
    )


# ---------------------------------------------------------------------------
# per-team ToHitAttackModifier lands on the right team's ships
# ---------------------------------------------------------------------------


def test_per_team_attack_modifier_applies_only_to_target_team():
    team0_ship = _ship(0)
    team1_ship = _ship(1)
    stack = ModifierStack(
        per_team={0: (_entry("empire:buff", "ToHitAttackModifier", 0.5),)},
        global_=(),
    )

    mgr = FleetAuraManager()
    mgr.initialize([team0_ship, team1_ship], modifier_stack=stack)

    assert team0_ship.fleet_attack_bonus == pytest.approx(0.5)
    assert team1_ship.fleet_attack_bonus == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# global entries apply to every team
# ---------------------------------------------------------------------------


def test_global_modifier_applies_to_every_team():
    ships = [_ship(0), _ship(1), _ship(2)]
    stack = ModifierStack(
        per_team={},
        global_=(_entry("system:nebula", "ToHitDefenseModifier", 0.3),),
    )
    mgr = FleetAuraManager()
    mgr.initialize(ships, modifier_stack=stack)

    for s in ships:
        assert s.fleet_defense_bonus == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# placeholder effects are ignored
# ---------------------------------------------------------------------------


def test_placeholder_effects_are_silently_ignored():
    ship = _ship(0)
    stack = ModifierStack(
        per_team={0: (_entry("complex:stub", "placeholder", 0.0),)},
        global_=(_entry("sector:stub", "placeholder", 99.0),),
    )
    mgr = FleetAuraManager()
    # Should NOT raise.
    mgr.initialize([ship], modifier_stack=stack)
    # No bonuses accumulated.
    assert ship.fleet_attack_bonus == 0.0
    assert ship.fleet_defense_bonus == 0.0


# ---------------------------------------------------------------------------
# ModifierStack + legacy BattleConfig.team_modifiers both work
# ---------------------------------------------------------------------------


def test_multiple_stack_entries_compose():
    """PROJ-270 Phase 6.4a: legacy `config=` branch is gone; multiple
    `ModifierEntry` entries on the stack (per_team + global_) compose
    additively into the aura totals.

    (Pre-PROJ-270, this test exercised both a legacy BattleConfig-style
    config AND a ModifierStack coexisting. The legacy branch was dead
    in production after PROJ-269 Phase 6 and was deleted by PROJ-270.)
    """
    ship = _ship(0)
    stack = ModifierStack(
        per_team={
            0: (
                _entry("legacy:buff", "ToHitAttackModifier", 0.1),
                _entry("empire:buff", "ToHitAttackModifier", 0.2),
            ),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    # 0.1 + 0.2 = 0.3 — entries compose additively in external aura.
    assert ship.fleet_attack_bonus == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# Empty stack is a no-op
# ---------------------------------------------------------------------------


def test_empty_stack_is_noop():
    ship = _ship(0)
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=ModifierStack.empty())
    assert ship.fleet_attack_bonus == 0.0
    assert ship.fleet_defense_bonus == 0.0


# ---------------------------------------------------------------------------
# None modifier_stack is a no-op (backward compat)
# ---------------------------------------------------------------------------


def test_none_modifier_stack_is_noop():
    ship = _ship(0)
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=None)
    assert ship.fleet_attack_bonus == 0.0
    assert ship.fleet_defense_bonus == 0.0
