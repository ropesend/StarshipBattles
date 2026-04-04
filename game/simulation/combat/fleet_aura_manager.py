"""
Fleet Aura Manager — Manages fleet/system/empire-scoped ability bonuses.

Collects abilities with non-SELF scope from ships in battle and applies
their bonuses to all friendly ships. Recalculates every tick so bonuses
are removed immediately when a provider is destroyed or incapacitated.

Also manages external battle conditions (per-team and global modifiers)
injected via BattleConfig.

Stacking follows the same two-phase pattern as component abilities:
- Same stack_group: take MAX (redundancy)
- Different stack_groups: SUM
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from game.simulation.components.abilities.base import AbilityScope

logger = logging.getLogger(__name__)


@dataclass
class AuraProvider:
    """A ship providing a scoped ability bonus."""
    ship: Any
    ability_name: str
    value: float
    stack_group: Optional[str]
    scope: str  # "fleet", "system", "empire"
    source_name: str  # For UI display


@dataclass
class ExternalModifier:
    """A battle condition modifier not tied to a ship (permanent for the battle)."""
    ability_name: str
    value: float
    source_name: str
    team_id: Optional[int]  # None = global (all teams)


class FleetAuraManager:
    """Manages fleet-scoped ability bonuses during combat.

    Lifecycle:
        1. initialize(ships, config) — called at battle start
        2. update(ships) — called every tick
        3. get_attack_bonus(ship) — queried by combat calculations
        4. get_active_bonuses(team_id) — queried by UI
    """

    def __init__(self):
        self._providers: List[AuraProvider] = []
        self._external: List[ExternalModifier] = []
        self._team_bonuses: Dict[int, Dict[str, float]] = {}  # team -> ability -> total
        self._initialized = False

    def initialize(self, ships: List[Any], config: Any = None) -> None:
        """Scan ships for fleet-scope abilities and load config modifiers."""
        self._providers.clear()
        self._external.clear()
        self._team_bonuses.clear()

        # Scan ships for fleet/system/empire-scoped abilities
        for ship in ships:
            if not ship.is_alive:
                continue
            self._scan_ship(ship)

        # Load external modifiers from config
        if config:
            for team_id, mods in getattr(config, 'team_modifiers', {}).items():
                for mod in mods:
                    self._external.append(ExternalModifier(
                        ability_name=mod.get('ability', ''),
                        value=mod.get('value', 0.0),
                        source_name=mod.get('source', 'Unknown'),
                        team_id=int(team_id),
                    ))
            for mod in getattr(config, 'global_modifiers', []):
                self._external.append(ExternalModifier(
                    ability_name=mod.get('ability', ''),
                    value=mod.get('value', 0.0),
                    source_name=mod.get('source', 'Unknown'),
                    team_id=None,
                ))

        self._initialized = True
        self._recalculate(ships)

    def _scan_ship(self, ship: Any) -> None:
        """Find all non-SELF scoped abilities on a ship."""
        for comp in ship.get_all_components():
            if not comp.is_operational:
                continue
            for ab in getattr(comp, 'ability_instances', []):
                scope = getattr(ab, 'scope', AbilityScope.SELF)
                if scope != AbilityScope.SELF:
                    value = getattr(ab, 'value', 0.0)
                    if value == 0.0:
                        continue
                    ability_name = type(ab).__name__
                    stack_group = getattr(ab, 'stack_group', None)
                    self._providers.append(AuraProvider(
                        ship=ship,
                        ability_name=ability_name,
                        value=value,
                        stack_group=stack_group,
                        scope=scope.value,
                        source_name=f"{comp.name} ({ship.name})",
                    ))

    def update(self, ships: List[Any]) -> None:
        """Recalculate bonuses based on alive/operational providers."""
        if not self._initialized:
            return
        self._recalculate(ships)

    def _recalculate(self, ships: List[Any]) -> None:
        """Recalculate per-team bonuses from alive providers + externals."""
        # Collect team IDs
        team_ids = {s.team_id for s in ships}
        self._team_bonuses = {tid: {} for tid in team_ids}

        # Group active provider values by team, ability, stack_group
        # Structure: team -> ability -> stack_group -> [values]
        team_ability_groups: Dict[int, Dict[str, Dict[str, List[float]]]] = {
            tid: {} for tid in team_ids
        }

        for provider in self._providers:
            ship = provider.ship
            # Provider must be alive (derelict ships can still provide aura bonuses
            # as long as the providing component is operational)
            if not ship.is_alive:
                continue

            # Check if the specific component is still operational
            comp_still_operational = False
            for comp in ship.get_all_components():
                if not comp.is_operational:
                    continue
                for ab in getattr(comp, 'ability_instances', []):
                    if (type(ab).__name__ == provider.ability_name
                            and getattr(ab, 'scope', AbilityScope.SELF) != AbilityScope.SELF):
                        comp_still_operational = True
                        break
                if comp_still_operational:
                    break

            if not comp_still_operational:
                continue

            # Apply to the provider's team
            team_id = ship.team_id
            ability = provider.ability_name
            group = provider.stack_group or f"_default_{id(provider)}"

            if ability not in team_ability_groups[team_id]:
                team_ability_groups[team_id][ability] = {}
            groups = team_ability_groups[team_id][ability]
            if group not in groups:
                groups[group] = []
            groups[group].append(provider.value)

        # Two-phase aggregation: intra-group MAX, inter-group SUM
        for team_id, abilities in team_ability_groups.items():
            for ability_name, groups in abilities.items():
                group_maxes = [max(vals) for vals in groups.values() if vals]
                total = sum(group_maxes)
                if total != 0:
                    self._team_bonuses[team_id][ability_name] = total

        # Add external modifiers (always active, no stacking groups)
        for ext in self._external:
            if ext.team_id is None:
                # Global — apply to all teams
                for team_id in team_ids:
                    current = self._team_bonuses[team_id].get(ext.ability_name, 0.0)
                    self._team_bonuses[team_id][ext.ability_name] = current + ext.value
            else:
                team_id = ext.team_id
                if team_id in self._team_bonuses:
                    current = self._team_bonuses[team_id].get(ext.ability_name, 0.0)
                    self._team_bonuses[team_id][ext.ability_name] = current + ext.value

        # Apply fleet bonuses to each ship for combat calculations
        for ship in ships:
            if ship.is_alive:
                team = self._team_bonuses.get(ship.team_id, {})
                ship.fleet_attack_bonus = team.get('ToHitAttackModifier', 0.0)
                ship.fleet_defense_bonus = team.get('ToHitDefenseModifier', 0.0)
            else:
                ship.fleet_attack_bonus = 0.0
                ship.fleet_defense_bonus = 0.0

    def get_attack_bonus(self, ship: Any) -> float:
        """Get the fleet to-hit attack bonus for a ship."""
        return self._team_bonuses.get(ship.team_id, {}).get('ToHitAttackModifier', 0.0)

    def get_defense_bonus(self, ship: Any) -> float:
        """Get the fleet to-hit defense bonus for a ship."""
        return self._team_bonuses.get(ship.team_id, {}).get('ToHitDefenseModifier', 0.0)

    def get_active_bonuses(self, team_id: int) -> List[Dict[str, Any]]:
        """Get active bonuses and their sources for UI display."""
        result = []

        # From ship providers
        for provider in self._providers:
            if provider.ship.team_id != team_id:
                continue
            if not provider.ship.is_alive or provider.ship.is_derelict:
                continue
            result.append({
                'ability': provider.ability_name,
                'value': provider.value,
                'source': provider.source_name,
                'scope': provider.scope,
                'active': True,
            })

        # From external modifiers
        for ext in self._external:
            if ext.team_id is None or ext.team_id == team_id:
                result.append({
                    'ability': ext.ability_name,
                    'value': ext.value,
                    'source': ext.source_name,
                    'scope': 'external',
                    'active': True,
                })

        return result
