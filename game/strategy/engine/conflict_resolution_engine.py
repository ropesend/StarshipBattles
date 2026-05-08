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
are pruned by `EmpireWriteService.prune_empty_fleets` (PROJ-370) — the
strategy engine just reports their ids in `ConflictResult.fleets_destroyed`.

PROJ-320: combat dispatch is per-fleet on movement-opportunity ticks
(`tick % get_tick_interval(fleet.speed) == 0`) gated by whether the
fleet successfully left the hex on that tick. Pre-PROJ-320 the
`_resolve_conflicts` rebuilt a hex_map from scratch every tick and
fired combat unconditionally for every contested hex — producing ~100
battles per turn at any stalemated sector. The new model produces one
battle per fleet per opportunity (sum-of-speeds), typically 5-30 per
encounter. See [docs/systems/strategy_layer.md] § Turn Engine and
[docs/systems/combat_simulation.md] § 9 (PROJ-320 closure note) for
the design rationale.
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
        replay_id: Optional[str] = None,
        replay_unavailable_reason: Optional[str] = None,
    ) -> None:
        """Log a single combat_resolved event for an N-team battle.

        BUG-126: replaced the legacy winner/loser pairing with a
        participant-based payload. Every battle emits exactly one
        event; consumers read `participating_fleet_ids` /
        `surviving_fleet_ids` / `destroyed_fleet_ids` instead of
        `winner_fleet_id` / `loser_fleet_id`.

        FEAT-26: `replay_id` (when present) is the uuid of the captured
        replay sidecar. The kwarg flows into `Event.details["replay_id"]`
        via `EventBus.log_event(**kwargs)` so the Event Log UI can
        render a Replay button for this row. None = no captured replay
        (legacy event from before PROJ-312, sole-survivor shortcut, or
        capture sink unregistered).

        Issue #8: `replay_unavailable_reason` (when present) is a
        UI-friendly identifier — see `BattleResult` — that the Event
        Log button maps to an honest tooltip when `replay_id` is None.

        Args:
            fleets: All participating fleets, in team_id order.
            surviving_fleet_ids: Fleet ids that retained ≥1 ship.
            destroyed_fleet_ids: Fleet ids whose ships list was wiped
                to empty by the resolver / `PostBattleHook`.
            location: Hex location of the combat.
            environmental_effects: Optional sector-effects list from
                `collect_sector_effects` (PROJ-300).
            replay_id: Optional uuid of the captured replay sidecar.
            replay_unavailable_reason: Optional UI tooltip key (issue #8).
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
            replay_id=replay_id,
            replay_unavailable_reason=replay_unavailable_reason,
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
        galaxy: Optional['Galaxy'] = None,
        *,
        tick: Optional[int] = None,
        moved_fleet_ids: Optional[set] = None,
    ) -> ConflictResult:
        """
        Resolve all conflicts between empires for a single strategic sub-tick.

        Public API method that wraps _resolve_conflicts and returns
        a structured result.

        Args:
            empires: List of Empire objects to check for conflicts
            galaxy: Optional Galaxy for environmental effect lookup (PROJ-189).
                   Required when area_effect_manager is set.
            tick: PROJ-320 — current strategic sub-tick (1..TICKS_PER_TURN).
                When None, no combat fires (the trigger predicate cannot
                evaluate `tick % interval`). Production callers always
                supply this.
            moved_fleet_ids: PROJ-320 — set of fleet ids whose location
                changed in this tick's Phase 3. Combat is skipped for any
                fleet in this set (it exercised its movement opportunity
                by leaving the hex). Defaults to an empty set when omitted.

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

        if tick is None:
            # PROJ-320: no tick supplied → no combat. Caller must opt in.
            return ConflictResult(
                combats_resolved=0, fleets_destroyed=[],
            )

        self._resolve_conflicts(
            empires, tick=tick, moved_fleet_ids=moved_fleet_ids or set(),
        )

        return ConflictResult(
            combats_resolved=self._combats_resolved,
            fleets_destroyed=self._fleets_destroyed
        )

    def _should_trigger_combat_for_fleet(
        self,
        fleet: 'Fleet',
        tick: int,
        moved_fleet_ids,
    ) -> bool:
        """PROJ-320: per-fleet combat trigger predicate.

        Returns True iff `fleet` is on a movement-opportunity tick
        (`tick % get_tick_interval(fleet.speed) == 0`) AND did not leave
        the hex this tick (`fleet.id not in moved_fleet_ids`). Fully
        derived from per-tick state — no persistent fleet field is
        needed. The unifying rule is "did the fleet leave?", not "did
        the fleet have orders?" — idle, action-ordered, blocked, and
        path-failed fleets all satisfy "did not leave" and trigger combat.
        """
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        if fleet.speed <= 0:
            return False
        interval = get_tick_interval(fleet.speed)
        if tick % interval != 0:
            return False
        if fleet.id in moved_fleet_ids:
            return False
        return True

    def _resolve_conflicts(
        self,
        empires,
        *,
        tick: int,
        moved_fleet_ids,
    ) -> None:
        """PROJ-320: per-fleet movement-opportunity dispatch.

        Iterate every empire's every fleet in deterministic
        `(empire_id, fleet_id)` order. For each fleet at a contested hex
        whose `_should_trigger_combat_for_fleet` returns True, dispatch
        a battle. Multiple combat rounds may fire at the same hex on the
        same tick if multiple fleets' opportunity ticks coincide; each
        round re-derives its occupants list from current `Empire.fleets`
        (fresh after any preceding round's `apply_outcome_to_fleets`)
        rather than reusing a cached snapshot.

        Determinism: iteration order is `(empire_id, fleet_id)` so the
        deterministic `_battle_seed_counter` produces stable replays.
        """
        # Snapshot the (empire, fleet) pairs at the start of the tick in
        # deterministic `(empire_id, fleet_id)` order for replay stability.
        # The snapshot identifies which fleets HAD opportunities this tick;
        # liveness re-checks below catch fleets pruned by earlier rounds.
        sorted_fleet_refs: List[Any] = sorted(
            ((emp, f) for emp in empires for f in emp.fleets),
            key=lambda pair: (pair[0].id, pair[1].id),
        )

        for triggering_empire, fleet in sorted_fleet_refs:
            # Re-derive liveness — an earlier round in this tick may have
            # pruned this fleet via `apply_outcome_to_fleets`. The
            # post-battle hook removes destroyed/retreated ships via
            # `fleet.remove_ship(...)` and prunes empty fleets via
            # `Empire.fleets.remove(fleet)`.
            if fleet not in triggering_empire.fleets:
                continue
            if not self._should_trigger_combat_for_fleet(
                fleet, tick, moved_fleet_ids,
            ):
                continue
            # Build current occupants list at this fleet's hex from LIVE
            # empire.fleets state. Skip if no opposing empire is present.
            occupants = []
            for other_empire in empires:
                for other_fleet in other_empire.fleets:
                    if other_fleet.location == fleet.location:
                        occupants.append((other_empire, other_fleet))
            if len({emp.id for emp, _ in occupants}) < 2:
                continue
            self._resolve_combat_at_hex(occupants)

    def _resolve_combat_at_hex(self, occupants) -> None:
        """Resolve a multi-empire conflict at one hex as a single N-team battle.

        PROJ-275 Phase 7: single `IBattleResolver.resolve_battle(fleets)`
        call resolving all participating fleets at once.

        PROJ-320 Phase 3: every fleet of every empire at the contested
        hex now participates. Pre-PROJ-320 the engine kept only the FIRST
        fleet per empire (silently dropping the rest). Allies are grouped
        into a single team by the spec compiler (`build_strategy_battle_spec`
        groups by `owner_id`), so adding extra fleets per empire just
        bulks up that team's ship count — no extra teams.

        BUG-126: the strategy layer no longer assigns a winner. The
        resolver's `PostBattleHook` mutates each `Fleet.ships` list to
        reflect what survived — this engine then reports any fleet
        whose ships list ended up empty as "destroyed" in
        `ConflictResult.fleets_destroyed`.

        PROJ-320: subsequent rounds at the same hex (within the same
        tick or on later ticks) are gated by per-fleet movement-
        opportunity ticks (see `_should_trigger_combat_for_fleet`).
        Stalemated fleets re-engage on each side's opportunity tick
        rather than every sub-tick.

        Args:
            occupants: `List[(Empire, Fleet)]` for the contested hex.
                Order is the empire-iteration order from
                `_resolve_conflicts`; ALL fleets per empire are kept
                (PROJ-320) and forwarded to the resolver.
        """
        if len(occupants) < 2:
            return

        # PROJ-320 Phase 3: collect ALL fleets per empire (not just the first).
        fleets_by_empire: Dict[int, List['Fleet']] = {}
        empire_by_id: Dict[int, Any] = {}
        for empire, fleet in occupants:
            fleets_by_empire.setdefault(empire.id, []).append(fleet)
            empire_by_id[empire.id] = empire

        if len(fleets_by_empire) < 2:
            return  # Only one empire actually present.

        empire_order: List[int] = sorted(fleets_by_empire.keys())
        # Flat fleet list in deterministic (empire_id, fleet_id) order.
        # The spec compiler re-groups by `fleet.owner_id` to produce one
        # team per empire (PROJ-320 Phase 3), so iteration order here is
        # cosmetic for the engine and load-bearing for replay determinism.
        fleets: List['Fleet'] = []
        for eid in empire_order:
            for fleet in sorted(fleets_by_empire[eid], key=lambda f: f.id):
                fleets.append(fleet)
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
                f"empire {eid}/[" + ", ".join(
                    f"Fleet {f.id}({len(f.ships)} ships)"
                    for f in sorted(fleets_by_empire[eid], key=lambda f: f.id)
                ) + "]"
                for eid in empire_order
            )
        )

        environmental_effects = self._lookup_environmental_effects(location)
        modifiers = self._collect_team_modifiers(
            fleets_by_empire, empire_order, location=location,
        )
        seed = self._generate_battle_seed()
        # PROJ-320 Phase 3: one team per empire, so empires_by_team_id has
        # `len(empire_order)` entries (was `len(fleets)` pre-PROJ-320).
        empires_by_team_id: Dict[int, Any] = {
            tid: empire_by_id[empire_order[tid]]
            for tid in range(len(empire_order))
        }
        # PROJ-269 Phase 6: fleet updates (component HP, ship pruning)
        # happen via the compiler's `PostBattleHook` inside `run_battle`.
        # `empires` flows through to the hook so empty fleets are
        # removed from their empires post-battle.
        # PROJ-369 Phase 3: explicit raise replaces the deleted
        # ``_NullBattleResolver`` placeholder. Combat without a wired
        # resolver is a caller mistake — fail loudly at the actual
        # resolve site so non-combat ticks aren't penalised.
        if self._battle_resolver is None:
            raise ValueError(
                "ConflictResolutionEngine was constructed without a "
                "battle_resolver; combat cannot resolve. Provide "
                "ai_factory= to TurnEngineConfig.create_default(...) so "
                "a SimulationBattleResolver is wired."
            )
        result = self._battle_resolver.resolve_battle(
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

        # FEAT-26: thread the captured replay id (when present) into the
        # COMBAT_RESOLVED event so the Event Log can render a Replay
        # button for this battle. None = no captured replay (older
        # save, sole-survivor shortcut, or no capture sink registered).
        # Issue #8: also thread `replay_unavailable_reason` so the UI
        # can show an honest tooltip instead of the generic "older save"
        # wording when the absence is structural (sole_survivor / no_ships).
        self._log_combat_result(
            fleets,
            surviving_fleet_ids=surviving_fleet_ids,
            destroyed_fleet_ids=destroyed_fleet_ids,
            location=location,
            environmental_effects=environmental_effects,
            replay_id=getattr(result, "replay_id", None),
            replay_unavailable_reason=getattr(
                result, "replay_unavailable_reason", None
            ),
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
        self,
        fleets_by_empire: Dict[int, List['Fleet']],
        empire_order: List[int],
        *,
        location: Any = None,
    ) -> Optional[Dict[int, Any]]:
        """Collect strategic combat modifiers for each team.

        PROJ-320 Phase 3: rewritten to operate on per-empire fleet lists.
        With per-owner team grouping (spec compiler PROJ-320 Phase 3),
        team_id corresponds to a position in `empire_order`. Each team's
        modifier set is computed once using a representative fleet of
        that empire (the lowest-id one, deterministic) — only the
        opponent's empire id matters for facility scope queries, so a
        single representative per side suffices.
        """
        if self._galaxy is None:
            return None
        all_empires = getattr(self, '_empires', [])
        modifiers: Dict[int, Any] = {}
        # Pre-pick one representative fleet per empire for the modifier
        # collector — sorted by fleet.id for determinism.
        representatives: Dict[int, 'Fleet'] = {
            eid: sorted(fleets_by_empire[eid], key=lambda f: f.id)[0]
            for eid in empire_order
        }
        try:
            from game.strategy.services.combat_modifier_collector import (
                collect_combat_modifiers,
            )
            for team_id, eid in enumerate(empire_order):
                fleet = representatives[eid]
                opponent_empires = [other for other in empire_order if other != eid]
                if not opponent_empires:
                    continue
                opponent_fleet = representatives[opponent_empires[0]]
                modifiers[team_id] = collect_combat_modifiers(
                    fleet, opponent_fleet, self._galaxy, all_empires,
                    self._registries,
                )
        except Exception as e:  # Intentional broad catch: external collector may raise any type from non-engine empire/system extensions; ERROR-log and proceed with degraded modifier stack so battle still resolves. Hex + empire context included to allow log-side debugging.
            # PROJ-381 Phase 2 (B-7): demote-to-warning was hiding a real
            # information loss; promote to error and include hex/empire
            # context so the log line is actionable.
            logger.error(
                "Failed to collect combat modifiers at hex=%s empires=%s: %s",
                location, empire_order, e,
            )
            return None
        return modifiers or None

