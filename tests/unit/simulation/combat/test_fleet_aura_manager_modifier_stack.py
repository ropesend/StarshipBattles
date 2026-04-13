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
        external_stats={},
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


# ---------------------------------------------------------------------------
# PROJ-271 Phase 1 Task 1.3: shield_bonus_add end-to-end
# ---------------------------------------------------------------------------


def _add_entry(source: str, stat_key: str, value: float) -> ModifierEntry:
    """Build an ADD-operation ModifierEntry (distinct from the default
    multiply `_entry` above — shield_bonus_add is additive)."""
    return ModifierEntry(
        source=source,
        stack_group=None,
        effect=ModifierEffect(
            stat_key=stat_key,
            value=value,
            operation="add",
            target_ability=None,
            source_modifier_id="mod",
            source_modifier_name="Mod",
            formula_str="param",
            param_value=value,
        ),
    )


def test_shield_bonus_add_reaches_external_stats_per_team():
    """A per_team `shield_bonus_add` entry populates only the target
    team's ships via `ship.external_stats['shield_bonus_add']`."""
    team0_ship = _ship(0)
    team1_ship = _ship(1)
    stack = ModifierStack(
        per_team={
            0: (_add_entry("planet:flat_shield", "shield_bonus_add", 50.0),),
        },
        global_=(),
    )

    mgr = FleetAuraManager()
    mgr.initialize([team0_ship, team1_ship], modifier_stack=stack)

    assert team0_ship.external_stats.get("shield_bonus_add") == pytest.approx(50.0)
    # Team 1 must NOT see the bonus.
    assert team1_ship.external_stats.get("shield_bonus_add", 0.0) == 0.0


def test_shield_bonus_add_multiple_entries_sum():
    """Multiple `shield_bonus_add` entries on the same team compose
    additively (+30 + +20 → +50)."""
    ship = _ship(0)
    stack = ModifierStack(
        per_team={
            0: (
                _add_entry("planet:a", "shield_bonus_add", 30.0),
                _add_entry("planet:b", "shield_bonus_add", 20.0),
            ),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    assert ship.external_stats.get("shield_bonus_add") == pytest.approx(50.0)


def test_shield_bonus_add_global_entry_applies_to_every_team():
    """Global `shield_bonus_add` entries reach every team's ships."""
    ships = [_ship(0), _ship(1)]
    stack = ModifierStack(
        per_team={},
        global_=(_add_entry("system:buff", "shield_bonus_add", 75.0),),
    )
    mgr = FleetAuraManager()
    mgr.initialize(ships, modifier_stack=stack)
    for s in ships:
        assert s.external_stats.get("shield_bonus_add") == pytest.approx(75.0)


def test_shield_bonus_add_per_team_does_not_bleed_to_other_teams():
    """PROJ-271 Phase 3.3: additive stat_keys (`shield_bonus_add`) route
    per-team just like multiplicative stat_keys. A per_team[0] entry
    does NOT reach team 1's external_stats."""
    team0 = _ship(0)
    team1 = _ship(1)
    stack = ModifierStack(
        per_team={0: (_add_entry("planet:flat", "shield_bonus_add", 100.0),)},
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([team0, team1], modifier_stack=stack)
    assert team0.external_stats.get("shield_bonus_add") == pytest.approx(100.0)
    # The key must not appear at all on team 1's external_stats.
    assert "shield_bonus_add" not in team1.external_stats or team1.external_stats["shield_bonus_add"] == 0.0


def test_mixed_add_and_mult_per_team_isolation():
    """PROJ-271 Phase 3.3: multiplicative AND additive entries keyed to
    different teams both stay isolated. A per_team[0] additive + a
    per_team[1] multiplicative never cross-pollinate."""
    team0 = _ship(0)
    team1 = _ship(1)
    stack = ModifierStack(
        per_team={
            0: (_add_entry("planet:flat", "shield_bonus_add", 50.0),),
            1: (_entry("planet:booster", "shield_capacity_mult", 2.0),),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([team0, team1], modifier_stack=stack)
    # Team 0: only shield_bonus_add
    assert team0.external_stats.get("shield_bonus_add") == pytest.approx(50.0)
    assert team0.external_stats.get("shield_capacity_mult", 1.0) in (1.0, None, 0.0)
    # Team 1: only shield_capacity_mult
    assert team1.external_stats.get("shield_capacity_mult") == pytest.approx(2.0)
    assert team1.external_stats.get("shield_bonus_add", 0.0) == 0.0


def test_shield_bonus_add_does_not_log_placeholder_warning(caplog):
    """The new stat_key must NOT trigger the `_log_placeholder_once`
    warning — it's a real mapping now."""
    import logging
    ship = _ship(0)
    stack = ModifierStack(
        per_team={0: (_add_entry("planet:flat_shield", "shield_bonus_add", 50.0),)},
        global_=(),
    )
    mgr = FleetAuraManager()
    with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
        mgr.initialize([ship], modifier_stack=stack)
    # No warnings from the aura manager.
    placeholder_warnings = [
        rec for rec in caplog.records
        if rec.levelname == "WARNING" and "placeholder" in rec.getMessage().lower()
    ]
    assert not placeholder_warnings, (
        "shield_bonus_add should be a real stat_key, not placeholder. "
        f"Got placeholder warnings: {[r.getMessage() for r in placeholder_warnings]}"
    )
