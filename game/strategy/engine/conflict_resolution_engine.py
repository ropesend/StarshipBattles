"""
ConflictResolutionEngine - Combat Resolution for Strategy Layer

PROJ-36: Extracted from TurnEngine to handle combat detection and resolution.

Responsibilities:
- Detect multi-empire conflicts at contested hexes
- Orchestrate battle resolution via IBattleResolver
- Apply combat results to fleet rosters
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.interfaces.engines import IConflictEngine

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import BattleResult, IBattleResolver
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
    from game.strategy.services.area_effect_manager import AreaEffectManager
    from game.strategy.data.galaxy import Galaxy


@dataclass
class ConflictResult:
    """Result of conflict resolution for a turn."""
    combats_resolved: int
    fleets_destroyed: List[int]  # Fleet IDs


class ConflictResolutionEngine(IConflictEngine):
    """
    Engine for resolving combat conflicts between empires.

    PROJ-36: Extracted from TurnEngine to decompose the god class.

    Handles:
    - Detection of multi-empire conflicts at hexes
    - Battle resolution via IBattleResolver interface
    - Tracking combat results
    """

    def __init__(
        self,
        battle_resolver: 'IBattleResolver',
        *,
        registries: Optional['GameRegistries'] = None,
        area_effect_manager: Optional['AreaEffectManager'] = None,
        event_bus=None,
    ):
        """
        Initialize the conflict resolution engine.

        Args:
            battle_resolver: Battle resolver implementation (required).
                           PROJ-239: Made required to eliminate default
                           SimulationBattleResolver creation (which needed AI import).
            registries: Optional GameRegistries for DI. Required for strict DI
                       compliance in PROJ-50.
            area_effect_manager: Optional AreaEffectManager for environmental
                                effects (PROJ-189). When provided, storm effects
                                are applied to ships during combat.
            event_bus: Optional EventBus for structured event logging.
        """
        # Battle seed counter for deterministic battles
        self._battle_seed_counter = 0
        # PROJ-252: Per-engine RNG for strategy-layer randomness
        self._rng = random.Random()

        # PROJ-50: Store registries for passing to battle resolver
        self._registries = registries

        # PROJ-189: Store area effect manager for storm integration
        self._area_effect_manager: Optional['AreaEffectManager'] = area_effect_manager
        self._galaxy: Optional['Galaxy'] = None  # Set during resolve_all_conflicts

        # PROJ-252: Session-scoped EventBus for structured event logging
        self._event_bus = event_bus

        self._battle_resolver = battle_resolver

        # Per-resolution stats — reset at the top of `resolve_all_conflicts`,
        # but pre-initialized here so `_resolve_combat_at_hex` can be safely
        # invoked outside the public API (tests, direct calls).
        self._combats_resolved: int = 0
        self._fleets_destroyed: List[int] = []
        self._empires: List[Any] = []

    def _generate_battle_seed(self) -> int:
        """Generate a deterministic seed for battles."""
        self._battle_seed_counter += 1
        return self._battle_seed_counter

    def _log_combat_result(
        self,
        winner: 'Fleet',
        loser: 'Fleet',
        location,
        environmental_effects=None
    ) -> None:
        """Log a combat resolved event with system and storm context.

        Centralizes the combat event logging that was previously duplicated
        in _resolve_combat (RNG path) and _resolve_combat_simulated.

        Args:
            winner: The winning fleet.
            loser: The losing fleet.
            location: Hex location of the combat.
            environmental_effects: Optional environmental effects at combat location.
        """
        # Look up system name for granular event log columns
        system_name = ""
        if self._galaxy and hasattr(self._galaxy, 'get_system_at_location'):
            sys = self._galaxy.get_system_at_location(location)
            if sys:
                system_name = sys.name

        # PROJ-300: derive storm names from sector-effects providers.
        # `environmental_effects` may be the new sector-effects list shape
        # OR the legacy EnvironmentalEffects object. Handle both during
        # the migration window.
        storm_names: List[str] = []
        if isinstance(environmental_effects, list):
            seen = set()
            for effect in environmental_effects:
                for provider in effect.get('providers', []):
                    if provider.get('source_kind') == 'storm':
                        label = provider.get('source_label')
                        if label and label not in seen:
                            seen.add(label)
                            storm_names.append(label)
        elif environmental_effects is not None and getattr(environmental_effects, 'in_storm', False):
            storm_names = list(getattr(environmental_effects, 'storm_names', []))

        if self._event_bus:
            self._event_bus.log_event(
                EventType.COMBAT_RESOLVED,
                category=EventCategory.COMBAT,
                empire_id=winner.owner_id,
                message=f"Battle: Fleet {winner.id} defeated Fleet {loser.id}",
                winner_fleet_id=winner.id,
                loser_fleet_id=loser.id,
                location_hex=[location.q, location.r],
                system_name=system_name,
                storm_names=storm_names,
            )

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before conflict resolution.

        Raises:
            ValidationException: If any fleet has invalid location or owner.
        """
        from game.core.exceptions import ValidationException
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    raise ValidationException(
                        f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                        context={"empire_id": empire.id, "fleet_id": fleet.id}
                    )

    def resolve_all_conflicts(
        self,
        empires,
        galaxy: Optional['Galaxy'] = None
    ) -> ConflictResult:
        """
        Resolve all conflicts between empires.

        Public API method that wraps _resolve_conflicts and returns
        a structured result.

        Args:
            empires: List of Empire objects to check for conflicts
            galaxy: Optional Galaxy for environmental effect lookup (PROJ-189).
                   Required when area_effect_manager is set.

        Returns:
            ConflictResult with combat statistics
        """
        self._validate_tick_inputs(empires)
        # PROJ-189: Store galaxy reference for effect lookup in combat resolution
        self._galaxy = galaxy
        # Store empires for combat modifier collection
        self._empires = empires

        # Track stats during resolution
        self._combats_resolved = 0
        self._fleets_destroyed: List[int] = []

        self._resolve_conflicts(empires)

        return ConflictResult(
            combats_resolved=self._combats_resolved,
            fleets_destroyed=self._fleets_destroyed
        )

    def _resolve_conflicts(self, empires) -> None:
        """Check for collisions and resolve battles."""
        # Map: Hex -> List[(Empire, Fleet)]
        hex_map = {}

        for emp in empires:
            for f in emp.fleets:
                if f.location not in hex_map:
                    hex_map[f.location] = []
                hex_map[f.location].append((emp, f))

        # Check collisions
        for loc, occupants in hex_map.items():
            if len(occupants) < 2:
                continue

            # Check if multiple EMPIRES present
            occupied_empires = set(emp.id for emp, f in occupants)
            if len(occupied_empires) > 1:
                # CONFLICT!
                self._resolve_combat_at_hex(occupants)

    def _resolve_combat_at_hex(self, occupants) -> None:
        """Resolve a multi-empire conflict at one hex as a single N-team battle.

        PROJ-275 Phase 7: replaced the legacy sequential 2-fleet
        decomposition (the user explicitly called out as "a mistake")
        with a single call into `IBattleResolver.resolve_battle(fleets)`
        that resolves all participating fleets at once. Losing empires
        each lose their participating fleet; the winner keeps theirs.

        Args:
            occupants: `List[(Empire, Fleet)]` for the contested hex.
                Order is the empire-iteration order from
                `_resolve_conflicts`; converted to per-team
                `fleets[i]` placement for the resolver.
        """
        if len(occupants) < 2:
            return

        # One fleet per empire, in deterministic empire-id order. (Empires
        # with multiple fleets at the hex contribute their first; later
        # work could merge intra-empire fleets before the call.)
        fleets_by_empire: Dict[int, 'Fleet'] = {}
        empire_by_id: Dict[int, Any] = {}
        for empire, fleet in occupants:
            if empire.id not in fleets_by_empire:
                fleets_by_empire[empire.id] = fleet
                empire_by_id[empire.id] = empire

        if len(fleets_by_empire) < 2:
            return  # Only one empire actually present after dedup.

        empire_order: List[int] = sorted(fleets_by_empire.keys())
        fleets: List['Fleet'] = [fleets_by_empire[eid] for eid in empire_order]
        location = fleets[0].location

        environmental_effects = self._lookup_environmental_effects(location)
        # Empty-fleet edge case: no participating fleet has ships. Skip the
        # resolver entirely (no real combat possible) and pick a winner via
        # the engine's RNG so the empire/fleet bookkeeping still happens.
        if not any(f.ships for f in fleets):
            result = self._rng_resolve_empty_fleets(fleets)
        else:
            modifiers = self._collect_team_modifiers(fleets)
            seed = self._generate_battle_seed()
            result = self._battle_resolver.resolve_battle(
                fleets,
                modifiers=modifiers,
                seed=seed,
                registries=self._registries,
                environmental_effects=environmental_effects,
            )

        # PROJ-269 Phase 6: fleet updates (component HP, ship pruning)
        # happen via the compiler's `PostBattleHook` inside `run_battle`.
        # All we do here is empire-level fleet bookkeeping based on the
        # team-level survivor data.
        winner_team_id = self._resolve_winner_team(result, fleets)

        self._combats_resolved += 1
        for team_id, fleet in enumerate(fleets):
            if team_id == winner_team_id:
                continue
            empire = empire_by_id[empire_order[team_id]]
            self._fleets_destroyed.append(fleet.id)
            empire.remove_fleet(fleet, event_bus=self._event_bus)

        # Event logging — pair winner against each loser for the audit log.
        if winner_team_id is not None:
            winner_fleet = fleets[winner_team_id]
            for team_id, fleet in enumerate(fleets):
                if team_id == winner_team_id:
                    continue
                self._log_combat_result(
                    winner_fleet, fleet, location, environmental_effects
                )

    def _rng_resolve_empty_fleets(self, fleets: List['Fleet']) -> 'BattleResult':
        """Edge-case resolver for empty-fleet "combat" — no ships exist
        so the simulation isn't applicable; the engine's RNG just picks
        one team to win so empire bookkeeping still happens.
        """
        from game.strategy.interfaces.battle_resolver import BattleResult

        winner_team_id = self._rng.randrange(len(fleets))
        return BattleResult(
            winner=winner_team_id,
            tick_count=0,
            team_survivors={i: [] for i in range(len(fleets))},
        )

    def _lookup_environmental_effects(self, location) -> Optional[Any]:
        """PROJ-189: Query environmental effects at the combat location.

        PROJ-300: returns the new sector-effects list shape from the unified
        collector. The spec compiler accepts either the legacy
        EnvironmentalEffects object (effective during AreaEffectManager
        deprecation) or this new list. Phase 7 deletes the legacy path.
        """
        if self._galaxy is None:
            return None
        get_system = getattr(self._galaxy, 'get_system_at_location', None)
        if get_system is None:
            return None
        system = get_system(location)
        if system is None:
            return None
        from game.strategy.services.system_effects_collector import collect_sector_effects
        return collect_sector_effects(
            system, location, empire_id=None, registries=self._registries,
        )

    def _collect_team_modifiers(
        self, fleets: List['Fleet']
    ) -> Optional[Dict[int, Any]]:
        """Collect strategic combat modifiers for each team.

        For N teams, each fleet's modifiers are computed against the
        union of opposing fleets (one representative is enough — only
        the opponent's empire id matters for facility scope queries).
        """
        if self._galaxy is None:
            return None
        all_empires = getattr(self, '_empires', [])
        modifiers: Dict[int, Any] = {}
        try:
            from game.strategy.services.combat_modifier_collector import (
                collect_combat_modifiers,
            )
            for team_id, fleet in enumerate(fleets):
                opponents = [f for tid, f in enumerate(fleets) if tid != team_id]
                if not opponents:
                    continue
                modifiers[team_id] = collect_combat_modifiers(
                    fleet, opponents[0], self._galaxy, all_empires,
                    self._registries,
                )
        except Exception as e:
            logger.warning(f"Failed to collect combat modifiers: {e}")
            return None
        return modifiers or None

    def _resolve_winner_team(
        self, result, fleets: List['Fleet']
    ) -> Optional[int]:
        """Map a `BattleResult` to a winning team_id.

        Honors `result.winner` directly when present. On a draw,
        breaks the tie by survivor count (most survivors wins) — and
        ultimately falls back to team 0 when even that is ambiguous so
        the empire bookkeeping stays deterministic.
        """
        if result.winner is not None:
            return result.winner
        # Draw — pick the team with the most survivors.
        survivors = result.team_survivors or {}
        if not survivors:
            return None
        # Most survivors wins; ties broken by lowest team_id.
        return max(
            range(len(fleets)),
            key=lambda tid: (len(survivors.get(tid, [])), -tid),
        )
