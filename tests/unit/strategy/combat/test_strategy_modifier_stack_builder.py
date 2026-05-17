"""PROJ-426 Phase 2 — tests for `StrategyModifierStackBuilder`.

The builder owns the modifier-stack helpers that used to live in
`spec_compiler.py`:

- `build(...)` — was `_build_modifier_stack`.
- `entries_from_sector_effects(...)` — was `_entries_from_sector_effects`.
- `entries_from_fleet_combat_modifiers(...)` — was
  `_entries_from_fleet_combat_modifiers`.

These tests pin the seam contract — the deeper modifier-translation rules
are still covered by the existing `test_spec_compiler.py` suite.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.simulation.combat.modifier_stack import ModifierStack
from game.strategy.combat.strategy_modifier_stack_builder import (
    StrategyModifierStackBuilder,
)


def test_build_with_no_modifiers_returns_empty_stack():
    """No env effects + no per-team modifiers -> empty `ModifierStack`."""
    builder = StrategyModifierStackBuilder()
    stack = builder.build(team_count=2)
    assert isinstance(stack, ModifierStack)
    assert stack.global_ == ()
    assert stack.per_team == {}


def test_build_routes_fleet_combat_modifiers_per_team():
    """`team_modifiers={tid: ...}` -> entries land in `per_team[tid]`."""
    builder = StrategyModifierStackBuilder()
    team_modifiers = {
        0: SimpleNamespace(shield_mult=1.5, damage_mult=1.0, flat_shield_bonus=0.0),
    }
    stack = builder.build(team_count=2, team_modifiers=team_modifiers)
    assert 0 in stack.per_team
    assert 1 not in stack.per_team
    assert any(
        getattr(getattr(e, "effect", None), "stat_key", None)
        == "shield_capacity_mult"
        for e in stack.per_team[0]
    )


def test_entries_from_fleet_combat_modifiers_emits_zero_when_neutral():
    """Default modifiers (no shield/damage/flat) -> empty list."""
    builder = StrategyModifierStackBuilder()
    neutral = SimpleNamespace(shield_mult=1.0, damage_mult=1.0, flat_shield_bonus=0.0)
    entries = builder.entries_from_fleet_combat_modifiers(neutral, team_id=0)
    assert entries == []


def test_entries_from_sector_effects_ownerless_goes_global():
    """Ownerless storm-style effects route to the global bucket."""
    builder = StrategyModifierStackBuilder()
    sector_effects = [
        {
            "ability_name": "ShieldModifier",
            "providers": [
                {
                    "is_active": True,
                    "ability_data": {"multiplier": 0.5},
                    "source_kind": "ion_storm",
                    "source_id": "ion-1",
                    "source_label": "Ion Storm",
                    "owner_id": None,
                },
            ],
        },
    ]
    global_entries, per_team = builder.entries_from_sector_effects(
        sector_effects, empire_to_team_id={10: 0}, team_count=2,
    )
    assert len(global_entries) >= 1
    assert per_team == {}
