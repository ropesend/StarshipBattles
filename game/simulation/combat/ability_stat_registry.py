"""Shared registry mapping ability class names to stat_keys (PROJ-273).

This module is the single source of truth for how combat-modifier abilities
project into the `ModifierStack` that `FleetAuraManager` consumes. Both the
Battle Setup spec compiler (`game/ui/screens/battle_setup/spec_compiler.py`)
and the Strategy spec compiler (`game/strategy/combat/spec_compiler.py`)
emit `ModifierEntry` objects for the same three abilities
(`ShieldProjection`, `ShieldModifier`, `DamageModifier`). Before PROJ-273
each compiler hardcoded its own mapping; this module replaces those
duplicate hardcodings with one registry.

Adding a new combat-affecting ability is now a one-line registry edit.
The glob-driven test at
`tests/unit/simulation/combat/test_ability_stat_registry.py` iterates
every `qs_*_complex.json` and validates every mapped ability produces a
real (non-placeholder) entry.

N-team forward compat: `emit_entries_for_ability` already accepts
`num_teams` and fans `enemy_*` scopes out to all non-owner teams. Current
compilers pass `num_teams=2`; PROJ-275 will raise this to arbitrary N.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List, Literal, Optional, Tuple, Union

from game.simulation.combat.modifier_stack import ModifierEntry
from game.simulation.components.modifier_effects import ModifierEffect


@dataclass(frozen=True)
class AbilityStatMapping:
    """One entry in `ABILITY_STAT_REGISTRY`.

    Fields:
      - `ability_class_name`: the string key under components.json
        "abilities" (e.g., "ShieldProjection").
      - `stat_key`: the `ship.external_stats` key the emitted entry
        writes to (e.g., "shield_bonus_add").
      - `operation`: "add" or "multiply" — how the stat composes at
        `ShipStatsCalculator._apply_aggregated_stats` time.
      - `value_field`: the key in the ability's JSON dict to read the
        numeric value from ("multiplier" for ratio-based modifiers,
        "value" for capacity-points like ShieldProjection).
    """

    ability_class_name: str
    stat_key: str
    operation: Literal["add", "multiply"]
    value_field: str


# The canonical mapping. Adding a new combat-affecting ability is a
# one-line edit here plus (for content coverage) a design JSON referencing
# it; the glob-driven test will pick it up automatically.
ABILITY_STAT_REGISTRY: Dict[str, AbilityStatMapping] = {
    "ShieldProjection": AbilityStatMapping(
        ability_class_name="ShieldProjection",
        stat_key="shield_bonus_add",
        operation="add",
        value_field="value",
    ),
    "ShieldModifier": AbilityStatMapping(
        ability_class_name="ShieldModifier",
        stat_key="shield_capacity_mult",
        operation="multiply",
        value_field="multiplier",
    ),
    "DamageModifier": AbilityStatMapping(
        ability_class_name="DamageModifier",
        stat_key="damage_mult",
        operation="multiply",
        value_field="multiplier",
    ),
}


# Scopes whose entries route to the OPPONENT team rather than the owner.
# Shared by Battle Setup + Strategy compilers; callers that roll their
# own scope routing should import this.
OPPONENT_SCOPES: FrozenSet[str] = frozenset({"enemy_sector", "enemy_system"})


# Every `stat_key` that the engine actually consumes downstream of
# `ship.external_stats`. `FleetAuraManager._append_external_from_entry`
# warns once per (stat_key, source) if it sees a ModifierEntry with a
# stat_key NOT in this set — catching silent-drop bugs where a compiler
# emits an entry no reader picks up.
#
# Sources of truth:
#   - `ABILITY_STAT_REGISTRY` values (compiler-driven stat_keys).
#   - `game/simulation/entities/ship_stats.py::_apply_aggregated_stats`
#     reads `shield_bonus_add` and `shield_capacity_mult` directly.
#   - `game/simulation/components/abilities/base.py::get_effective_stat`
#     reads ANY `stat_key` attribute exposed by a `SimpleMultiplierAbility`
#     subclass. Those keys are enumerated below.
#
# Adding a new stat_key: add to BOTH this set AND `ABILITY_STAT_REGISTRY`
# (if compiler-emitted) or wire the reader in `ship_stats.py` (if ship-
# level direct-read). A test in `test_ability_stat_registry.py` asserts
# every registry value is contained here.
KNOWN_EXTERNAL_STAT_KEYS: FrozenSet[str] = frozenset({
    # Registry-emitted stat_keys (compiler-driven).
    "shield_bonus_add",
    "shield_capacity_mult",
    "damage_mult",
    # SimpleMultiplierAbility subclasses whose stat_key may be read via
    # `Ability.get_effective_stat` on external_stats.
    "thrust_mult",
    "turn_mult",
    "strategic_mult",
    "capacity_mult",
    "energy_gen_mult",
    "crew_capacity_mult",
    "life_support_capacity_mult",
})


def _extract_value(
    mapping: AbilityStatMapping,
    ability_data: Union[Dict[str, Any], float, int],
) -> float:
    """Read the numeric value from ability_data per the mapping.

    Dict path: reads `mapping.value_field` with a sensible default
    (1.0 for multiply operations, 0.0 for add).
    Primitive path: treats the numeric itself as the value (matches
    components.json convention for ShieldProjection-style abilities
    that sometimes ship as `"ShieldProjection": 500` without a dict).
    """
    if isinstance(ability_data, dict):
        default = 1.0 if mapping.operation == "multiply" else 0.0
        return float(ability_data.get(mapping.value_field, default))
    if isinstance(ability_data, (int, float)):
        return float(ability_data)
    return 0.0


def _route_team_ids(scope: str, owner_team: int, num_teams: int) -> List[int]:
    """Determine which team_ids a given scope's entry targets.

    - `enemy_*` scopes: all non-owner teams (fan-out for N teams).
    - Anything else (self, allied_*, etc.): `[owner_team]`.
    """
    if scope in OPPONENT_SCOPES:
        return [t for t in range(num_teams) if t != owner_team]
    return [owner_team]


def emit_entries_for_ability(
    ability_name: str,
    ability_data: Union[Dict[str, Any], float, int],
    *,
    scope: str,
    owner_team: int,
    num_teams: int,
    source: str,
    source_modifier_id: str,
    source_modifier_name: str,
    stack_group: Optional[str] = None,
) -> List[Tuple[int, ModifierEntry]]:
    """Translate one ability invocation into zero or more `ModifierEntry` objects.

    Args:
        ability_name: class name as it appears in components.json
            "abilities" (e.g. "ShieldProjection").
        ability_data: either the raw primitive the ability was declared
            with, or the dict form including an optional `value` /
            `multiplier` field depending on the ability.
        scope: the scope string (`self`, `allied_sector`, `enemy_system`,
            etc.). Determines team routing.
        owner_team: team_id of the ship/source emitting this ability.
        num_teams: total team count in the battle. Enables N-team fan-out
            for `enemy_*` scopes (returns one entry per non-owner team).
        source: human-readable source tag for the ModifierEntry (e.g.,
            `"sector:complex:qs_sector_shield_booster_complex:ShieldProjection"`).
        source_modifier_id: id used for ModifierEffect.source_modifier_id
            (typically the design_id).
        source_modifier_name: display name used for
            ModifierEffect.source_modifier_name.
        stack_group: optional grouping key used by the two-phase
            aggregator (`None` = unique group, participates in SUM only).

    Returns:
        A list of `(team_id, ModifierEntry)` tuples. Empty if the ability
        is not in `ABILITY_STAT_REGISTRY`, or if the extracted value is
        zero/falsy. For `enemy_*` scopes with `num_teams > 2`, returns
        one tuple per opponent team (N-team fan-out).
    """
    mapping = ABILITY_STAT_REGISTRY.get(ability_name)
    if mapping is None:
        return []

    value = _extract_value(mapping, ability_data)
    if not value:
        return []

    team_ids = _route_team_ids(scope, owner_team, num_teams)
    if not team_ids:
        return []

    out: List[Tuple[int, ModifierEntry]] = []
    for team_id in team_ids:
        effect = ModifierEffect(
            stat_key=mapping.stat_key,
            value=value,
            operation=mapping.operation,
            target_ability=None,
            source_modifier_id=source_modifier_id,
            source_modifier_name=source_modifier_name,
            formula_str="",
            param_value=value,
        )
        entry = ModifierEntry(
            source=source,
            stack_group=stack_group,
            effect=effect,
        )
        out.append((team_id, entry))
    return out


__all__ = [
    "ABILITY_STAT_REGISTRY",
    "AbilityStatMapping",
    "OPPONENT_SCOPES",
    "emit_entries_for_ability",
]
