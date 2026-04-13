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


# ---------------------------------------------------------------------------
# PROJ-271 Phase 7: stack_group respect on external entries
# ---------------------------------------------------------------------------


def _grouped_mult_entry(source: str, stat_key: str, value: float, stack_group: str):
    return ModifierEntry(
        source=source,
        stack_group=stack_group,
        effect=ModifierEffect(
            stat_key=stat_key,
            value=value,
            operation="multiply",
            target_ability=None,
            source_modifier_id="mod",
            source_modifier_name="Mod",
            formula_str="",
            param_value=value,
        ),
    )


def test_same_stack_group_entries_compose_max_not_sum():
    """PROJ-271 Phase 7: two external entries in the SAME stack_group
    compose MAX, not SUM. Matches ship-provider aura semantics."""
    ship = _ship(0)
    stack = ModifierStack(
        per_team={
            0: (
                _grouped_mult_entry("a", "shield_capacity_mult", 1.5, "shield_boost"),
                _grouped_mult_entry("b", "shield_capacity_mult", 1.25, "shield_boost"),
            ),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    # MAX(1.5, 1.25) = 1.5 — NOT 1.5 + 1.25 = 2.75
    assert ship.external_stats.get("shield_capacity_mult") == pytest.approx(1.5)


def test_different_stack_groups_compose_sum():
    """Entries with different stack_groups compose additively.

    Note: for `_mult` stat keys, "additive composition across groups"
    means the VALUES are summed (matches ship-provider aura — e.g.,
    two different types of shield boosters each 0.2 stack to 0.4).
    The engine then interprets the composed value per stat_key semantics
    (`_mult` uses the composed value directly)."""
    ship = _ship(0)
    stack = ModifierStack(
        per_team={
            0: (
                _grouped_mult_entry("a", "shield_capacity_mult", 1.2, "boost_type_a"),
                _grouped_mult_entry("b", "shield_capacity_mult", 1.3, "boost_type_b"),
            ),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    # Different groups: SUM = 1.2 + 1.3 = 2.5
    assert ship.external_stats.get("shield_capacity_mult") == pytest.approx(2.5)


def test_apply_bonuses_invokes_ship_recalculate_stats():
    """PROJ-271 Phase 11.5: confirm `FleetAuraManager._apply_bonuses`
    calls `ship.recalculate_stats()` when external_stats change, so
    the ship's `max_shields` (and other aggregate stats) reflect the
    new modifiers. Previously only integration tests proved this
    wiring; a direct unit test makes regression diagnosis fast."""
    from unittest.mock import MagicMock
    from types import SimpleNamespace
    ship = SimpleNamespace(
        team_id=0,
        is_alive=True,
        is_derelict=False,
        fleet_attack_bonus=0.0,
        fleet_defense_bonus=0.0,
        external_stats={},
        get_all_components=lambda: [],
        recalculate_stats=MagicMock(),
    )
    stack = ModifierStack(
        per_team={0: (_add_entry("planet", "shield_bonus_add", 50.0),)},
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    ship.recalculate_stats.assert_called()


def test_none_stack_group_entries_each_contribute_independently():
    """Entries with stack_group=None each form a unique group, so they
    all contribute via SUM (preserves pre-Phase-7 behavior for
    un-grouped entries)."""
    ship = _ship(0)
    stack = ModifierStack(
        per_team={
            0: (
                _entry("a", "ToHitAttackModifier", 0.1),
                _entry("b", "ToHitAttackModifier", 0.2),
                _entry("c", "ToHitAttackModifier", 0.3),
            ),
        },
        global_=(),
    )
    mgr = FleetAuraManager()
    mgr.initialize([ship], modifier_stack=stack)
    # All three have stack_group=None (from _entry helper); each is
    # a unique group → SUM = 0.6
    assert ship.fleet_attack_bonus == pytest.approx(0.6)


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
