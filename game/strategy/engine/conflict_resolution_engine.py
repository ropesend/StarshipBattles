"""
ConflictResolutionEngine - Combat Resolution for Strategy Layer

PROJ-36: Extracted from TurnEngine to handle combat detection and
resolution.

Responsibilities:
- Detect multi-empire conflicts at contested hexes
- Orchestrate battle resolution via IBattleResolver
- Report which fleets were wiped (zero ships) post-combat

BUG-126: the strategy layer no longer assigns a winner. Surviving
ships from BOTH sides remain in their fleets after the battle, and the
fleet stays on the strategy map. Empty fleets (every ship destroyed)
are pruned by `PostBattleHook._prune_empty_fleets` — the strategy
engine just reports their ids in `ConflictResult.fleets_destroyed`.

If two co-located fleets both retain ships, combat re-engages on the
next strategy tick (the tick loop rebuilds the hex_map from scratch
each call — see `_resolve_conflicts`).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.interfaces.engines import IConflictEngine

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
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
            event_bus: Optional EventBus for structured event logging.

        PROJ-300 Phase 7: AreaEffectManager removed; environmental effects
        are read by `_lookup_environmental_effects` directly via the unified
        `system_effects_collector`.
        """
        # Battle seed counter for deterministic battles
        self._battle_seed_counter = 0

        # PROJ-50: Store registries for passing to battle resolver
        self._registries = registries

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
        fleets: List['Fleet'],
        surviving_fleet_ids: List[int],
        destroyed_fleet_ids: List[int],
        location,
        environmental_effects=None,
    ) -> None:
        """Log a single combat_resolved event for an N-team battle.

        BUG-126: replaced the legacy winner/loser pairing with a
        participant-based payload. Every battle emits exactly one
        event; consumers read `participating_fleet_ids` /
        `surviving_fleet_ids` / `destroyed_fleet_ids` instead of
        `winner_fleet_id` / `loser_fleet_id`.

        Args:
            fleets: All participating fleets, in team_id order.
            surviving_fleet_ids: Fleet ids that retained ≥1 ship.
            destroyed_fleet_ids: Fleet ids whose ships list was wiped
                to empty by the resolver / `PostBattleHook`.
            location: Hex location of the combat.
            environmental_effects: Optional sector-effects list from
                `collect_sector_effects` (PROJ-300).
        """
        # Look up system name for granular event log columns.
        system_name = ""
        if self._galaxy and hasattr(self._galaxy, 'get_system_at_location'):
            sys = self._galaxy.get_system_at_location(location)
            if sys:
                system_name = sys.name

        # PROJ-300 Phase 7: derive storm names from sector-effects providers.
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

        if not self._event_bus:
            return

        participating_fleet_ids = [f.id for f in fleets]
        # `empire_id` is the lowest participating empire id — the
        # strategy layer no longer designates a 'winning' empire
        # (BUG-126), but the event-log filter still needs a single
        # owner column.
        owner_ids = [f.owner_id for f in fleets if f.owner_id is not None]
        empire_id = min(owner_ids) if owner_ids else 0

        if destroyed_fleet_ids:
            destroyed_str = ", ".join(str(fid) for fid in destroyed_fleet_ids)
            message = (
                f"Battle: {len(fleets)} fleets engaged; destroyed "
                f"Fleet {destroyed_str}"
            )
        else:
            message = (
                f"Battle: {len(fleets)} fleets engaged; no fleet destroyed"
            )

        self._event_bus.log_event(
            EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            empire_id=empire_id,
            message=message,
            participating_fleet_ids=participating_fleet_ids,
            surviving_fleet_ids=surviving_fleet_ids,
            destroyed_fleet_ids=destroyed_fleet_ids,
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

        PROJ-275 Phase 7: single `IBattleResolver.resolve_battle(fleets)`
        call resolving all participating fleets at once.

        BUG-126: the strategy layer no longer assigns a winner. The
        resolver's `PostBattleHook` mutates each `Fleet.ships` list to
        reflect what survived — this engine then reports any fleet
        whose ships list ended up empty as "destroyed" in
        `ConflictResult.fleets_destroyed`. Fleets that retain ships
        stay in their empires, and combat re-engages on subsequent
        ticks until one side is wiped or the fleets separate.

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

        # BUG-126: every-fleet-empty case is not a real combat. The
        # legacy `_rng_resolve_empty_fleets` only existed to keep
        # empire bookkeeping consistent when picking a "winner" — and
        # the strategy layer no longer assigns winners. Skip silently.
        if not any(f.ships for f in fleets):
            logger.info(
                f"Skipping combat at {location}: no participating fleet "
                f"has any ships (fleets=[{', '.join(f'Fleet {f.id}' for f in fleets)}])"
            )
            return

        logger.info(
            f"Combat at {location}: "
            + " vs ".join(
                f"empire {eid}/Fleet {fleets_by_empire[eid].id}"
                f"({len(fleets_by_empire[eid].ships)} ships)"
                for eid in empire_order
            )
        )

        environmental_effects = self._lookup_environmental_effects(location)
        modifiers = self._collect_team_modifiers(fleets)
        seed = self._generate_battle_seed()
        empires_by_team_id: Dict[int, Any] = {
            tid: empire_by_id[empire_order[tid]]
            for tid in range(len(fleets))
        }
        # PROJ-269 Phase 6: fleet updates (component HP, ship pruning)
        # happen via the compiler's `PostBattleHook` inside `run_battle`.
        # `empires` flows through to the hook so empty fleets are
        # removed from their empires post-battle.
        self._battle_resolver.resolve_battle(
            fleets,
            modifiers=modifiers,
            seed=seed,
            registries=self._registries,
            environmental_effects=environmental_effects,
            empires=empires_by_team_id,
        )

        # Report which fleets ended the battle with zero ships. Pruning
        # is the hook's job; the strategy engine just observes the
        # outcome for the audit log + `ConflictResult` payload.
        destroyed_fleet_ids = [f.id for f in fleets if not f.ships]
        surviving_fleet_ids = [f.id for f in fleets if f.ships]

        self._combats_resolved += 1
        self._fleets_destroyed.extend(destroyed_fleet_ids)

        logger.info(
            f"Combat at {location} resolved: "
            f"surviving={surviving_fleet_ids}, destroyed={destroyed_fleet_ids}"
        )

        self._log_combat_result(
            fleets,
            surviving_fleet_ids=surviving_fleet_ids,
            destroyed_fleet_ids=destroyed_fleet_ids,
            location=location,
            environmental_effects=environmental_effects,
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

