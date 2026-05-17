"""CombatModifierCollector — Collect strategic combat modifiers for a fleet.

Scans planetary facilities in the battle location's system/sector for
ShieldModifier, DamageModifier, and scoped ShieldProjection abilities,
then aggregates them into per-fleet combat modifiers applied pre-battle.

The collector handles the perspective of a single fleet:
- Allied/player-scoped boosters from the fleet owner's facilities → benefit
- Enemy-scoped suppressors from opponent facilities → penalty
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.strategy.services.ability_metadata import (
    StrategicKind,
    abilities_with_kind_tag,
)
from game.strategy.services.strategic_ability_scanner import (
    find_abilities_in_scope,
    aggregate_multipliers,
)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


@dataclass
class FleetCombatModifiers:
    """Per-fleet combat modifiers from strategic abilities."""
    shield_mult: float = 1.0        # Multiplicative to max_shields
    damage_mult: float = 1.0        # Multiplicative to weapon damage output
    flat_shield_bonus: float = 0.0   # Additive shield points from ShieldProjection


def collect_combat_modifiers(
    fleet: 'Fleet',
    opponent_fleet: 'Fleet',
    galaxy: 'Galaxy',
    empires: List['Empire'],
    registries,
) -> FleetCombatModifiers:
    """Collect all strategic combat modifiers affecting a fleet.

    Args:
        fleet: The fleet receiving the modifiers.
        opponent_fleet: The opposing fleet (for enemy-scope resolution).
        galaxy: Galaxy for spatial queries.
        empires: All empires in the game.
        registries: GameRegistries for component lookup.

    Returns:
        FleetCombatModifiers with aggregated shield/damage multipliers and flat bonuses.
    """
    result = FleetCombatModifiers()

    # Find a reference planet at the battle location for scope resolution
    ref_planet = _find_reference_planet(fleet.location, galaxy, empires)
    if ref_planet is None:
        return result

    fleet_empire = _find_empire(fleet.owner_id, empires)
    opponent_empire = _find_empire(opponent_fleet.owner_id, empires)

    # Collect allied boosters (from fleet owner's facilities).
    # Scan fleet owner's planets at system and sector scope, then filter
    # to abilities with allied/player scope to avoid double-counting.
    # Map scan level -> which ability scopes to include at that level
    _FRIENDLY_SCOPE_MAP = {
        'system': {'allied_system', 'player_system', 'system'},
        'sector': {'allied_sector', 'player_sector', 'sector', 'fleet'},
    }
    shield_entries = []
    damage_entries = []
    shield_projection_values = []

    # PROJ-272 Phase 1: resolve class default when JSON omits `scope`.
    # Previously `entry.get('scope', 'self')` silently dropped abilities
    # whose author forgot to specify scope — runtime falls back to
    # ALLIED_SYSTEM for ShieldModifier/DamageModifier, compiler/collector
    # fell back to 'self'. Disagreement caused silent no-ops.
    from game.simulation.components.abilities import get_ability_default_scope

    def _entry_scope(ability_key: str, entry: Dict[str, Any]) -> str:
        """Resolve effective scope for an ability data dict, matching runtime."""
        scope = entry.get('scope')
        if scope is not None:
            return scope
        return get_ability_default_scope(ability_key)

    if fleet_empire is not None:
        for scan_scope, valid_scopes in _FRIENDLY_SCOPE_MAP.items():
            for ability_key, entries_list in [
                ("ShieldModifier", shield_entries),
                ("DamageModifier", damage_entries),
            ]:
                found = find_abilities_in_scope(
                    ability_key, ref_planet, galaxy, fleet_empire, scan_scope, registries,
                    require_active=True,
                )
                for entry in found:
                    if _entry_scope(ability_key, entry) in valid_scopes:
                        entries_list.append(entry)

            # Flat-bonus combat abilities (COMBAT_FLAT_BONUS) — currently
            # only ``ShieldProjection``. PROJ-429 / TD-07 Phase 5: read
            # the name set live from the unified registry rather than
            # hardcoding ``"ShieldProjection"`` here and in
            # ``strategy_modifier_stack_builder``.
            for flat_bonus_name in abilities_with_kind_tag(
                StrategicKind.COMBAT_FLAT_BONUS
            ):
                sp_entries = find_abilities_in_scope(
                    flat_bonus_name, ref_planet, galaxy, fleet_empire, scan_scope, registries,
                    require_active=True,
                )
                for entry in sp_entries:
                    if _entry_scope(flat_bonus_name, entry) in valid_scopes:
                        value = entry.get('value', 0)
                        if isinstance(value, dict):
                            value = value.get('value', 0)
                        if value > 0:
                            shield_projection_values.append(float(value))

    # Collect enemy suppressors (from opponent's facilities that target enemies).
    # Scan opponent's own planets for abilities with enemy_* scope.
    # The scanner's "system"/"sector" scope returns planets owned by the empire,
    # which is what we want — the opponent's own facilities.
    if opponent_empire is not None:
        for scan_scope in ("system", "sector"):
            for ability_key, entries_list in [
                ("ShieldModifier", shield_entries),
                ("DamageModifier", damage_entries),
            ]:
                found = find_abilities_in_scope(
                    ability_key, ref_planet, galaxy, opponent_empire, scan_scope, registries,
                    require_active=True,
                )
                # Only include abilities with enemy_* scope
                for entry in found:
                    entry_scope = _entry_scope(ability_key, entry)
                    if entry_scope.startswith('enemy'):
                        entries_list.append(entry)

    # Aggregate
    result.shield_mult = aggregate_multipliers(shield_entries)
    result.damage_mult = aggregate_multipliers(damage_entries)
    result.flat_shield_bonus = sum(shield_projection_values)

    if result.shield_mult != 1.0 or result.damage_mult != 1.0 or result.flat_shield_bonus > 0:
        logger.info(
            f"Fleet {fleet.id}: strategic combat modifiers - "
            f"shield={result.shield_mult:.2f}x, damage={result.damage_mult:.2f}x, "
            f"flat_shield=+{result.flat_shield_bonus:.0f}"
        )

    return result


def _find_reference_planet(location, galaxy, empires) -> Optional[Any]:
    """Find any colonized planet at the battle location for scope resolution."""
    if galaxy is None:
        return None

    # Try to find a planet at the battle hex
    get_planets = getattr(galaxy, 'get_planets_at_global_hex', None)
    if get_planets is not None:
        planets = get_planets(location)
        if planets:
            return planets[0]

    # Try system lookup
    get_system = getattr(galaxy, 'get_system_at_hex', None)
    if get_system is not None:
        system = get_system(location)
        if system is not None:
            planets = getattr(system, 'planets', [])
            if planets:
                return planets[0]

    return None


def _find_empire(empire_id, empires) -> Optional[Any]:
    """Find an empire by ID."""
    for emp in empires:
        if getattr(emp, 'id', None) == empire_id:
            return emp
    return None
