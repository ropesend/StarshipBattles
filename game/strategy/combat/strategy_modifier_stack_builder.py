"""PROJ-426 — `StrategyModifierStackBuilder`.

Owns the strategy-side translation of environmental sector effects
(PROJ-300) and per-team `FleetCombatModifiers` into a `ModifierStack` for
the simulation engine. Lifted from `spec_compiler.py`'s
`_build_modifier_stack` / `_entries_from_sector_effects` /
`_entries_from_fleet_combat_modifiers`.

Behavior is unchanged from the original helpers — this extraction is
structural only. See `decisions.md` "No rule changes belong in this
refactor."
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack


__all__ = ["StrategyModifierStackBuilder"]


class StrategyModifierStackBuilder:
    """Translate strategy-layer environmental + per-team modifiers to a stack."""

    def build(
        self,
        *,
        team_count: int,
        environmental_effects: Any = None,
        team_modifiers: Optional[Mapping[int, Any]] = None,
        empire_to_team_id: Optional[Mapping[Any, int]] = None,
    ) -> ModifierStack:
        """Assemble the final `ModifierStack` for a battle."""
        global_entries: List[ModifierEntry] = []
        sector_per_team: Dict[int, List[ModifierEntry]] = {}
        if environmental_effects is not None:
            from_sector_global, sector_per_team = self.entries_from_sector_effects(
                environmental_effects,
                empire_to_team_id=empire_to_team_id,
                team_count=team_count,
            )
            global_entries.extend(from_sector_global)

        per_team: Dict[int, Tuple[ModifierEntry, ...]] = {}
        for team_id in range(team_count):
            entries: List[ModifierEntry] = []
            if team_modifiers is not None and team_id in team_modifiers:
                entries.extend(
                    self.entries_from_fleet_combat_modifiers(
                        team_modifiers[team_id], team_id=team_id,
                    )
                )
            if team_id in sector_per_team:
                entries.extend(sector_per_team[team_id])
            if entries:
                per_team[team_id] = tuple(entries)

        return ModifierStack(per_team=per_team, global_=tuple(global_entries))

    def entries_from_sector_effects(
        self,
        sector_effects: Sequence[Dict[str, Any]],
        *,
        empire_to_team_id: Optional[Mapping[Any, int]] = None,
        team_count: int = 1,
    ) -> Tuple[List[ModifierEntry], Dict[int, List[ModifierEntry]]]:
        """Translate a PROJ-300 sector-effects list into `ModifierEntry` entries.

        For each combat-relevant ability emit one entry per ACTIVE provider
        (no shared stack_group between providers — overlapping storms
        multiply). PROJ-343 T1.3-combat: split ownerless vs. ownerful
        providers so facility-projected modifiers apply only to the owning
        team's stack.
        """
        combat_ability_names = {"ShieldModifier", "DamageModifier", "ThrustModifier"}
        global_entries: List[ModifierEntry] = []
        per_team_entries: Dict[int, List[ModifierEntry]] = {}

        for effect in sector_effects:
            ability_name = effect.get('ability_name')
            if ability_name not in combat_ability_names:
                continue
            for provider in effect.get('providers', []):
                if not provider.get('is_active', True):
                    continue
                ability_data = provider.get('ability_data') or {}
                mult = ability_data.get('multiplier', 1.0)
                if mult == 1.0:
                    continue
                source_kind = provider.get('source_kind', 'unknown')
                source_id = provider.get('source_id', 'unknown')
                source_label = provider.get('source_label', source_id)
                stack_group = ability_data.get('stack_group')
                owner_id = provider.get('owner_id')

                if owner_id is None or empire_to_team_id is None:
                    target_team: Optional[int] = None
                elif owner_id in empire_to_team_id:
                    target_team = empire_to_team_id[owner_id]
                else:
                    continue  # owner not in this battle

                if target_team is None:
                    emitted = emit_entries_for_ability(
                        ability_name,
                        mult,
                        scope="self",
                        owner_team=0,
                        num_teams=1,
                        source=f"sector:{source_kind}",
                        source_modifier_id=source_id,
                        source_modifier_name=source_label,
                        stack_group=stack_group,
                    )
                    global_entries.extend(entry for _, entry in emitted)
                else:
                    emitted = emit_entries_for_ability(
                        ability_name,
                        mult,
                        scope="self",
                        owner_team=target_team,
                        num_teams=team_count,
                        source=f"sector:{source_kind}",
                        source_modifier_id=source_id,
                        source_modifier_name=source_label,
                        stack_group=stack_group,
                    )
                    bucket = per_team_entries.setdefault(target_team, [])
                    bucket.extend(entry for _, entry in emitted)

        return global_entries, per_team_entries

    def entries_from_fleet_combat_modifiers(
        self,
        modifiers: Any,
        *,
        team_id: int,
    ) -> List[ModifierEntry]:
        """Translate a `FleetCombatModifiers` value into `ModifierEntry` entries.

        Emits real stat_keys:
          - `shield_mult` -> `shield_capacity_mult` (via ShieldModifier)
          - `damage_mult` -> `damage_mult` (via DamageModifier)
          - `flat_shield_bonus` -> `shield_bonus_add` (via ShieldProjection)
        """
        entries: List[ModifierEntry] = []
        shield_mult = getattr(modifiers, "shield_mult", 1.0)
        damage_mult = getattr(modifiers, "damage_mult", 1.0)
        flat_shield = getattr(modifiers, "flat_shield_bonus", 0.0)
        if shield_mult != 1.0:
            entries.extend(
                self._emit_team_scoped(
                    "ShieldModifier",
                    shield_mult,
                    team_id=team_id,
                    source=f"team{team_id}:shield_mult",
                    display_name=f"Shield x{shield_mult:.2f}",
                    design_id="team_shield_mult",
                    stack_group=f"team{team_id}_shield_mult",
                )
            )
        if damage_mult != 1.0:
            entries.extend(
                self._emit_team_scoped(
                    "DamageModifier",
                    damage_mult,
                    team_id=team_id,
                    source=f"team{team_id}:damage_mult",
                    display_name=f"Damage x{damage_mult:.2f}",
                    design_id="team_damage_mult",
                    stack_group=f"team{team_id}_damage_mult",
                )
            )
        if flat_shield:
            entries.extend(
                self._emit_team_scoped(
                    "ShieldProjection",
                    flat_shield,
                    team_id=team_id,
                    source=f"team{team_id}:flat_shield_bonus",
                    display_name=f"Shield +{flat_shield}",
                    design_id="team_flat_shield_bonus",
                    stack_group=f"team{team_id}_flat_shield",
                )
            )
        return entries

    @staticmethod
    def _emit_team_scoped(
        ability_name: str,
        value: float,
        *,
        team_id: int,
        source: str,
        display_name: str,
        design_id: str,
        stack_group: Optional[str] = None,
    ) -> List[ModifierEntry]:
        team_entries = emit_entries_for_ability(
            ability_name,
            value,
            scope="self",
            owner_team=team_id,
            num_teams=team_id + 1,
            source=source,
            source_modifier_id=design_id,
            source_modifier_name=display_name,
            stack_group=stack_group,
        )
        return [entry for _, entry in team_entries]
