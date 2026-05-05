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
    """A ship/component pair providing a scoped ability bonus.

    PROJ-357: provider identity is bound to (`component`, `ability`)
    not just `(ship, ability_class_name)`. The `value` field is the
    snapshot at registration time — UI surfaces (`get_active_bonuses`)
    read it for display, but `_recalculate` always re-reads the live
    `ability.value` so a provider's contribution tracks the live
    component / ability instance.

    A provider is considered live when:
      1. `ship.is_alive` (and not derelict where relevant), AND
      2. `component.is_operational`, AND
      3. `ability` is still present in `component.ability_instances`.

    Providers whose identity no longer resolves are dropped from the
    `_providers` list during `_recalculate`.
    """
    ship: Any
    component: Any
    ability: Any
    ability_name: str
    value: float
    stack_group: Optional[str]
    scope: str  # "fleet", "system", "empire"
    source_name: str  # For UI display


@dataclass
class ExternalModifier:
    """A battle condition modifier not tied to a ship (permanent for the battle).

    PROJ-271 Phase 7: `stack_group` drives two-phase aggregation —
    entries sharing a stack_group compose MAX; distinct stack_groups
    compose SUM. `None` means "unique group" (each entry contributes
    independently via SUM). Mirrors the ship-provider aura semantics.
    """
    ability_name: str
    value: float
    source_name: str
    team_id: Optional[int]  # None = global (all teams)
    stack_group: Optional[str] = None


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

    def initialize(
        self,
        ships: List[Any],
        *,
        modifier_stack: Any = None,
    ) -> None:
        """Scan ships for fleet-scope abilities and load external modifiers.

        PROJ-270 Phase 6.4a: removed the legacy `config` kwarg. Pre-PROJ-269
        the manager read `config.team_modifiers` / `config.global_modifiers`
        from a `BattleConfig`; those fields were deleted by PROJ-269
        Phase 6 and the branch is dead in production. External modifiers
        now flow through `modifier_stack` only.

        PROJ-269 Phase 5.5: `modifier_stack` translates each `ModifierEntry`
        in `stack.per_team` / `stack.global_` into an `ExternalModifier`
        (using the entry's `effect.stat_key` as the `ability_name`).
        Placeholder entries (stat_key == "placeholder") are silently
        ignored — a warning is logged once per source for visibility.
        """
        self._providers.clear()
        self._external.clear()
        self._team_bonuses.clear()

        # Scan ships for fleet/system/empire-scoped abilities
        for ship in ships:
            if not ship.is_alive:
                continue
            self._scan_ship(ship)

        # PROJ-269 Phase 5.5: translate ModifierStack (if provided) into
        # ExternalModifier entries. `stat_key == "placeholder"` is the
        # compiler marker for "we recorded this toggle's presence but
        # have no real effect mapping yet" — skip those.
        if modifier_stack is not None:
            per_team = getattr(modifier_stack, 'per_team', {}) or {}
            for team_id, entries in per_team.items():
                for entry in entries or ():
                    self._append_external_from_entry(entry, team_id=int(team_id))
            for entry in getattr(modifier_stack, 'global_', ()) or ():
                self._append_external_from_entry(entry, team_id=None)

        self._initialized = True
        self._recalculate(ships)
        self._last_fingerprint = self._get_provider_fingerprint(ships)
        self._providers_dirty = False

    def _append_external_from_entry(
        self, entry: Any, *, team_id: Optional[int]
    ) -> None:
        """Translate a single `ModifierEntry` into an `ExternalModifier`.

        Skips entries whose effect has `stat_key == "placeholder"` —
        those are compiler stubs with no real effect mapping yet.
        PROJ-270 Phase 6.4: placeholder skips are now logged (once per
        source) so compiler authors get immediate feedback when they
        add a new modifier source without a stat_key mapping.
        """
        effect = getattr(entry, 'effect', None)
        if effect is None:
            return
        stat_key = getattr(effect, 'stat_key', '') or ''
        source = str(
            getattr(entry, 'source', None)
            or getattr(effect, 'source_modifier_name', '')
            or 'Unknown'
        )
        if not stat_key or stat_key == 'placeholder':
            self._log_placeholder_once(source)
            return
        # PROJ-273 Phase 5: warn once per (stat_key, source) when the key
        # isn't in `KNOWN_EXTERNAL_STAT_KEYS`. Catches silent-drop bugs
        # where a compiler emits an entry no reader consumes. Late import
        # avoids adding a hard circular dep at module load time.
        from game.simulation.combat.ability_stat_registry import KNOWN_EXTERNAL_STAT_KEYS
        if stat_key not in KNOWN_EXTERNAL_STAT_KEYS:
            self._log_unknown_stat_key_once(stat_key, source)
            # Still record the entry — the engine already aggregates by
            # stat_key, so unknown keys are harmless (just unused). The
            # warning is advisory, not a hard filter.
        value = float(getattr(effect, 'value', 0.0) or 0.0)
        # PROJ-271 Phase 7: copy stack_group from the entry so the
        # recalculate path can apply two-phase MAX/SUM aggregation.
        stack_group = getattr(entry, 'stack_group', None)
        self._external.append(ExternalModifier(
            ability_name=stat_key,
            value=value,
            source_name=source,
            team_id=team_id,
            stack_group=stack_group,
        ))

    def _log_placeholder_once(self, source: str) -> None:
        """Emit one WARNING per unique placeholder source to avoid log spam.

        The set of already-warned sources lives on the manager instance so
        re-initialization (new battle) emits a fresh warning — useful for
        per-battle visibility.
        """
        if not hasattr(self, '_placeholder_warned_sources'):
            self._placeholder_warned_sources: set = set()
        if source in self._placeholder_warned_sources:
            return
        self._placeholder_warned_sources.add(source)
        logger.warning(
            "FleetAuraManager: ModifierEntry source=%r has no stat_key "
            "mapping (placeholder). Effect will NOT be applied to battle "
            "math. Compiler author should map this to a real StatKey.",
            source,
        )

    def _log_unknown_stat_key_once(self, stat_key: str, source: str) -> None:
        """Emit one WARNING per unique (stat_key, source) pair.

        PROJ-273 Phase 5: flags stat_keys that aren't in
        `KNOWN_EXTERNAL_STAT_KEYS`. Advisory only — the entry is still
        recorded, since the engine aggregates by stat_key and an unknown
        key is harmless. The warning tells contributors either:
        (a) they added a stat_key without wiring a reader, or
        (b) they wired a reader without updating `KNOWN_EXTERNAL_STAT_KEYS`.
        """
        if not hasattr(self, '_unknown_stat_key_warned'):
            self._unknown_stat_key_warned: set = set()
        key = (stat_key, source)
        if key in self._unknown_stat_key_warned:
            return
        self._unknown_stat_key_warned.add(key)
        logger.warning(
            "FleetAuraManager: ModifierEntry source=%r emits unknown stat_key=%r "
            "(not in KNOWN_EXTERNAL_STAT_KEYS). No downstream reader will "
            "consume this. Add the key to KNOWN_EXTERNAL_STAT_KEYS in "
            "game/simulation/combat/ability_stat_registry.py, or check the "
            "compiler emission.",
            source, stat_key,
        )

    def _scan_ship(self, ship: Any) -> None:
        """Find all non-SELF scoped abilities on a ship.

        PROJ-357: registers one `AuraProvider` per (component, ability)
        pair so that disabling one of two same-class providers on the
        same ship removes only the disabled component's contribution.
        """
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
                        component=comp,
                        ability=ab,
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

        # PROJ-357: identity-precise liveness check — the specific
        # `component` and `ability` instance the provider was registered
        # with must currently be operational/attached. Skip (do not
        # drop) providers whose component is non-operational — a
        # repaired component should resume contributing without
        # requiring a re-scan. Drop only when the underlying ability
        # instance has been replaced (true identity loss).
        retained_providers: List[AuraProvider] = []
        for provider in self._providers:
            ship = provider.ship

            # Real identity loss: the ability instance is no longer
            # attached to the component (component swap, ability
            # re-materialization). Drop the provider.
            ab = provider.ability
            comp = provider.component
            ability_instances = getattr(comp, 'ability_instances', ())
            if ab not in ability_instances:
                continue

            retained_providers.append(provider)

            if not ship.is_alive:
                continue
            if not getattr(comp, 'is_operational', False):
                continue

            # PROJ-357: read the LIVE value from the live ability
            # instance, not the cached `provider.value` snapshot. This
            # also future-proofs against formula re-resolution that
            # mutates `ability.value` mid-battle.
            live_value = getattr(ab, 'value', 0.0)
            if live_value == 0.0:
                # Zero live value contributes nothing; matches
                # `_scan_ship`'s zero filter at registration time.
                continue

            team_id = ship.team_id
            ability_name = provider.ability_name
            group = provider.stack_group or f"_default_{id(provider)}"

            if ability_name not in team_ability_groups[team_id]:
                team_ability_groups[team_id][ability_name] = {}
            groups = team_ability_groups[team_id][ability_name]
            if group not in groups:
                groups[group] = []
            groups[group].append(live_value)

        # Compact `_providers` only when an entry actually went away —
        # avoids list churn on the typical no-change path.
        if len(retained_providers) != len(self._providers):
            self._providers = retained_providers

        # PROJ-271 Phase 7: external ModifierEntry values now route
        # through the same team_ability_groups structure BEFORE
        # aggregation, so they participate in the two-phase MAX/SUM
        # alongside ship-provider auras. Same-stack_group entries MAX;
        # different stack_groups SUM; None stack_group becomes a
        # unique group (preserves pre-Phase-7 additive behavior for
        # un-grouped ToHitAttack/Defense entries).
        for idx, ext in enumerate(self._external):
            group = ext.stack_group or f"_default_ext_{idx}"
            target_teams = team_ids if ext.team_id is None else (
                {ext.team_id} if ext.team_id in team_ability_groups else set()
            )
            for team_id in target_teams:
                if ext.ability_name not in team_ability_groups[team_id]:
                    team_ability_groups[team_id][ext.ability_name] = {}
                groups = team_ability_groups[team_id][ext.ability_name]
                if group not in groups:
                    groups[group] = []
                groups[group].append(ext.value)

        # PROJ-253: Delegate two-phase aggregation to shared function.
        # PROJ-272 Phase 8: narrowed `if v` truthy filter → `if v is not None`
        # so legitimate 0.0 values (e.g., `damage_mult=0.0` = "deal zero
        # damage" suppressor) are preserved. 0.0 and "no modifier" are
        # semantically different game states and must not be conflated.
        for team_id, ability_groups in team_ability_groups.items():
            totals = _aggregate_ability_groups(ability_groups)
            self._team_bonuses[team_id] = {
                k: v for k, v in totals.items() if v is not None
            }

        self._apply_bonuses(ships)

    def _apply_bonuses(self, ships: List[Any]) -> None:
        """Apply cached team bonuses to ship attributes.

        PROJ-270 Phase 9: writes ALL team-bonus stat_keys onto
        `ship.external_stats` so the ability pipeline
        (`Ability.get_effective_stat`) can consume them. Previously this
        method read only the hardcoded `ToHitAttackModifier` /
        `ToHitDefenseModifier` keys and silently discarded every other
        stat_key in `_team_bonuses`, which meant `shield_capacity_mult`
        / `damage_mult` / `shield_mult` compiled by the strategy spec
        compiler never reached ship stats — the Track A battle-math
        regression from PROJ-269 Phase 5.5 that PROJ-270 Phase 6 falsely
        claimed to have restored.
        """
        for ship in ships:
            new_external_stats = {}
            if ship.is_alive:
                team = self._team_bonuses.get(ship.team_id, {})
                # Direct-attribute setters for fleet_attack_bonus /
                # fleet_defense_bonus — consumed by name in collision.py:115-120.
                ship.fleet_attack_bonus = team.get('ToHitAttackModifier', 0.0)
                ship.fleet_defense_bonus = team.get('ToHitDefenseModifier', 0.0)
                # Expose the FULL team-bonus dict via ship.external_stats
                # so ability-level stat lookup picks it up.
                new_external_stats = dict(team)
            else:
                ship.fleet_attack_bonus = 0.0
                ship.fleet_defense_bonus = 0.0

            # PROJ-270 Phase 9: cached derived values (e.g. ShieldProjection.capacity)
            # only re-compute on recalculate_stats(). Trigger it only when
            # external_stats actually changed — not every tick — to avoid
            # needless full recalculation of every ship's stat pipeline.
            prev = getattr(ship, 'external_stats', None)
            ship.external_stats = new_external_stats
            if prev != new_external_stats and ship.is_alive:
                # Guard for test-shim ships (SimpleNamespace, bare Mocks)
                # that don't implement recalculate_stats. Real `Ship`
                # always has it.
                recalc = getattr(ship, 'recalculate_stats', None)
                if callable(recalc):
                    recalc()

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
