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
from game.simulation.entities.ability_aggregator import _aggregate_ability_groups

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
        # PROJ-253: Dirty flag and fingerprint for provider-state caching
        self._providers_dirty: bool = True
        self._last_fingerprint: Optional[tuple] = None

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
        self._last_fingerprint = self._get_provider_fingerprint(ships)
        self._providers_dirty = False

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

    def register_ship(self, ship: Any, all_ships: List[Any]) -> None:
        """Register a ship added mid-battle.

        Scans the new ship for fleet-scope abilities and recalculates
        all team bonuses so that:
        1. The new ship's abilities contribute to teammates
        2. The new ship receives existing fleet bonuses

        Args:
            ship: The newly added ship
            all_ships: All ships currently in battle (including the new one)
        """
        if ship.is_alive:
            self._scan_ship(ship)
        self._recalculate(all_ships)

    def unregister_ship(self, ship: Any, all_ships: List[Any]) -> None:
        """Unregister a ship removed from battle (retreat/escape).

        Removes the ship's AuraProvider entries and recalculates bonuses
        so teammates no longer receive bonuses from the removed ship.

        Args:
            ship: The ship being removed
            all_ships: All ships remaining in battle (excluding the removed one)
        """
        self._providers = [p for p in self._providers if p.ship is not ship]
        self._providers_dirty = True
        self._recalculate(all_ships)

    def invalidate_aura_cache(self) -> None:
        """Mark aura cache as dirty (PROJ-253). Forces recalculation on next update."""
        self._providers_dirty = True

    def update(self, ships: List[Any]) -> None:
        """Recalculate bonuses based on alive/operational providers."""
        if not self._initialized:
            return
        # PROJ-253: Build a provider fingerprint to detect changes
        fingerprint = self._get_provider_fingerprint(ships)
        if not self._providers_dirty and fingerprint == self._last_fingerprint:
            # Apply cached bonuses to ships (may have new ships)
            self._apply_bonuses(ships)
            return
        self._recalculate(ships)
        self._last_fingerprint = fingerprint
        self._providers_dirty = False

    def _get_provider_fingerprint(self, ships: List[Any]) -> tuple:
        """Build a fingerprint of provider state for cache invalidation (PROJ-253).

        Includes per-provider-ship operational component count so that component
        destruction (without ship death) triggers cache invalidation.
        """
        parts = []
        for provider in self._providers:
            s = provider.ship
            # Count operational components — changes when aura-providing component is destroyed
            op_count = sum(1 for c in s.get_all_components() if c.is_operational) if s.is_alive else 0
            parts.append((id(s), s.is_alive, s.is_derelict, op_count))
        for s in ships:
            parts.append((s.team_id, s.is_alive))
        return tuple(parts)

    def _recalculate(self, ships: List[Any]) -> None:
        """Recalculate per-team bonuses from alive providers + externals.

        PROJ-253: Uses shared _aggregate_ability_groups for two-phase aggregation.
        """
        # Collect team IDs
        team_ids = {s.team_id for s in ships}
        self._team_bonuses = {tid: {} for tid in team_ids}

        # Build ability groups per team using the shared aggregator's input shape
        # Structure: team -> ability -> stack_group -> [values]
        team_ability_groups: Dict[int, Dict[str, Dict[str, List[float]]]] = {
            tid: {} for tid in team_ids
        }

        for provider in self._providers:
            ship = provider.ship
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

            team_id = ship.team_id
            ability = provider.ability_name
            group = provider.stack_group or f"_default_{id(provider)}"

            if ability not in team_ability_groups[team_id]:
                team_ability_groups[team_id][ability] = {}
            groups = team_ability_groups[team_id][ability]
            if group not in groups:
                groups[group] = []
            groups[group].append(provider.value)

        # PROJ-253: Delegate two-phase aggregation to shared function
        for team_id, ability_groups in team_ability_groups.items():
            totals = _aggregate_ability_groups(ability_groups)
            self._team_bonuses[team_id] = {k: v for k, v in totals.items() if v}

        # Add external modifiers (always active, no stacking groups)
        for ext in self._external:
            if ext.team_id is None:
                for team_id in team_ids:
                    current = self._team_bonuses[team_id].get(ext.ability_name, 0.0)
                    self._team_bonuses[team_id][ext.ability_name] = current + ext.value
            else:
                team_id = ext.team_id
                if team_id in self._team_bonuses:
                    current = self._team_bonuses[team_id].get(ext.ability_name, 0.0)
                    self._team_bonuses[team_id][ext.ability_name] = current + ext.value

        self._apply_bonuses(ships)

    def _apply_bonuses(self, ships: List[Any]) -> None:
        """Apply cached team bonuses to ship attributes."""
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
