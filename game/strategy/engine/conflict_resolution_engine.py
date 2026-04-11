"""
ConflictResolutionEngine - Combat Resolution for Strategy Layer

PROJ-36: Extracted from TurnEngine to handle combat detection and resolution.

Responsibilities:
- Detect multi-empire conflicts at contested hexes
- Orchestrate battle resolution via IBattleResolver
- Apply combat results to fleet rosters
"""

import logging
import random
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING

from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.interfaces.engines import IConflictEngine

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
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

        # Get storm names from environmental effects or area effect manager
        storm_names = []
        if environmental_effects is not None and environmental_effects.in_storm:
            storm_names = environmental_effects.storm_names
        elif self._area_effect_manager is not None and self._galaxy is not None:
            effects = self._area_effect_manager.get_effects_at_global_hex(
                self._galaxy, location
            )
            if effects.in_storm:
                storm_names = effects.storm_names

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

    def _resolve_conflicts(self, empires):
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

    def _resolve_combat_at_hex(self, occupants):
        """Simple RNG resolution. Last standing empire wins."""
        # occupants: List[(Empire, Fleet)]

        # Group by Empire
        fleets_by_emp = {}
        for emp, f in occupants:
            if emp.id not in fleets_by_emp:
                fleets_by_emp[emp.id] = []
            fleets_by_emp[emp.id].append(f)

        # While > 1 empire has ships
        while len(fleets_by_emp) > 1:
            emp_ids = list(fleets_by_emp.keys())

            # Pick two random opposing fleets
            id1, id2 = self._rng.sample(emp_ids, 2)
            f1 = fleets_by_emp[id1][0]
            f2 = fleets_by_emp[id2][0]

            # Roll
            survivor = self._resolve_combat(f1, f2)

            loser = f2 if survivor == f1 else f1
            loser_owner_id = loser.owner_id

            # Track combat stats
            self._combats_resolved += 1
            self._fleets_destroyed.append(loser.id)

            # Remove loser
            # 1. From list
            fleets_by_emp[loser_owner_id].remove(loser)
            if not fleets_by_emp[loser_owner_id]:
                del fleets_by_emp[loser_owner_id]

            # 2. From Empire (Global State)
            # We need reference to Empire object.
            # occupants has (Empire, Fleet). Find empire for loser.
            start_tuple = next(t for t in occupants if t[1] == loser)
            loser_empire = start_tuple[0]
            loser_empire.remove_fleet(loser, event_bus=self._event_bus)

    def _resolve_combat(self, f1: 'Fleet', f2: 'Fleet') -> 'Fleet':
        """
        Return the winner of single encounter.

        Uses the full battle simulation via BattleController.
        Falls back to RNG only if a fleet is empty.
        """
        # Check if both fleets have ships for simulation
        if f1.ships and f2.ships:
            return self._resolve_combat_simulated(f1, f2)

        # Fallback to simple RNG for empty fleets
        logger.debug("Using RNG combat resolution (empty fleet)")
        if self._rng.random() > 0.5:
            winner, loser = f1, f2
        else:
            winner, loser = f2, f1

        self._log_combat_result(winner, loser, f1.location)
        return winner

    def _resolve_combat_simulated(self, f1: 'Fleet', f2: 'Fleet') -> 'Fleet':
        """
        Resolve combat using the injected battle resolver.

        PROJ-11 Phase 4: Uses IBattleResolver interface for clean
        separation between strategy and simulation layers.

        PROJ-189: Queries environmental effects at combat location and passes
        them to the battle resolver for shield interference in storms.

        Args:
            f1: First fleet (team 0)
            f2: Second fleet (team 1)

        Returns:
            The winning fleet
        """
        # PROJ-189: Query environmental effects at combat location
        environmental_effects = None
        if self._area_effect_manager is not None and self._galaxy is not None:
            # Use f1's location (should be same as f2's since they're in conflict)
            environmental_effects = self._area_effect_manager.get_effects_at_global_hex(
                self._galaxy, f1.location
            )

        # Collect strategic combat modifiers for both fleets
        team0_mods = None
        team1_mods = None
        if self._galaxy is not None:
            try:
                from game.strategy.services.combat_modifier_collector import collect_combat_modifiers
                all_empires = getattr(self, '_empires', [])
                team0_mods = collect_combat_modifiers(
                    f1, f2, self._galaxy, all_empires, self._registries
                )
                team1_mods = collect_combat_modifiers(
                    f2, f1, self._galaxy, all_empires, self._registries
                )
            except Exception as e:
                logger.warning(f"Failed to collect combat modifiers: {e}")

        # Use the injected battle resolver
        # PROJ-50: Pass registries for strict DI compliance
        # PROJ-189: Pass environmental effects for storm shield interference
        seed = self._generate_battle_seed()
        # Build kwargs — only include modifiers if non-default to stay compatible
        # with resolvers that don't accept the new parameters
        resolve_kwargs = dict(
            seed=seed, registries=self._registries,
            environmental_effects=environmental_effects,
        )
        if team0_mods is not None:
            resolve_kwargs['team0_modifiers'] = team0_mods
        if team1_mods is not None:
            resolve_kwargs['team1_modifiers'] = team1_mods

        try:
            result = self._battle_resolver.resolve_battle(f1, f2, **resolve_kwargs)
        except TypeError:
            # Fallback: resolver doesn't accept modifier params (e.g., test mocks)
            result = self._battle_resolver.resolve_battle(
                f1, f2, seed=seed, registries=self._registries,
                environmental_effects=environmental_effects,
            )

        # Apply results to fleets (PROJ-210: use battle adapter property)
        f1.battle.update_from_battle_results(result.team0_survivors)
        f2.battle.update_from_battle_results(result.team1_survivors)

        # Determine winner
        if result.winner == 0:
            winner, loser = f1, f2
        elif result.winner == 1:
            winner, loser = f2, f1
        else:
            # Draw - return fleet with more survivors
            if len(result.team0_survivors) >= len(result.team1_survivors):
                winner, loser = f1, f2
            else:
                winner, loser = f2, f1

        self._log_combat_result(winner, loser, f1.location, environmental_effects)
        return winner
