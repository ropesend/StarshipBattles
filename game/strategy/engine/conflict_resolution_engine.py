"""
ConflictResolutionEngine - Combat Resolution for Strategy Layer

PROJ-36: Extracted from TurnEngine to handle combat detection and resolution.

Responsibilities:
- Detect multi-empire conflicts at contested hexes
- Orchestrate battle resolution via IBattleResolver
- Apply combat results to fleet rosters
"""

import random
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING

from game.core.logger import log_debug, log_info, log_event
from game.strategy.events.event_types import EventType, EventCategory

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries


@dataclass
class ConflictResult:
    """Result of conflict resolution for a turn."""
    combats_resolved: int
    fleets_destroyed: List[int]  # Fleet IDs


class ConflictResolutionEngine:
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
        battle_resolver: Optional['IBattleResolver'] = None,
        *,
        registries: Optional['GameRegistries'] = None
    ):
        """
        Initialize the conflict resolution engine.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
            registries: Optional GameRegistries for DI. Required for strict DI
                       compliance in PROJ-50.
        """
        # Battle seed counter for deterministic battles
        self._battle_seed_counter = 0

        # PROJ-50: Store registries for passing to battle resolver
        self._registries = registries

        # PROJ-11: Inject battle resolver for clean layer separation
        if battle_resolver is None:
            from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
            self._battle_resolver = SimulationBattleResolver()
        else:
            self._battle_resolver = battle_resolver

    def _generate_battle_seed(self) -> int:
        """Generate a deterministic seed for battles."""
        self._battle_seed_counter += 1
        return self._battle_seed_counter

    def resolve_all_conflicts(self, empires) -> ConflictResult:
        """
        Resolve all conflicts between empires.

        Public API method that wraps _resolve_conflicts and returns
        a structured result.

        Args:
            empires: List of Empire objects to check for conflicts

        Returns:
            ConflictResult with combat statistics
        """
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
            id1, id2 = random.sample(emp_ids, 2)
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
            loser_empire.remove_fleet(loser)

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
        log_debug("Using RNG combat resolution (empty fleet)")
        if random.random() > 0.5:
            winner, loser = f1, f2
        else:
            winner, loser = f2, f1

        log_event(
            EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            empire_id=winner.owner_id,
            message=f"Battle: Fleet {winner.id} defeated Fleet {loser.id}",
            winner_fleet_id=winner.id,
            loser_fleet_id=loser.id,
        )
        return winner

    def _resolve_combat_simulated(self, f1: 'Fleet', f2: 'Fleet') -> 'Fleet':
        """
        Resolve combat using the injected battle resolver.

        PROJ-11 Phase 4: Uses IBattleResolver interface for clean
        separation between strategy and simulation layers.

        Args:
            f1: First fleet (team 0)
            f2: Second fleet (team 1)

        Returns:
            The winning fleet
        """
        # Use the injected battle resolver
        # PROJ-50: Pass registries for strict DI compliance
        seed = self._generate_battle_seed()
        result = self._battle_resolver.resolve_battle(
            f1, f2, seed=seed, registries=self._registries
        )

        # Apply results to fleets
        f1.update_from_battle_results(result.team0_survivors)
        f2.update_from_battle_results(result.team1_survivors)

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

        log_event(
            EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            empire_id=winner.owner_id,
            message=f"Battle: Fleet {winner.id} defeated Fleet {loser.id}",
            winner_fleet_id=winner.id,
            loser_fleet_id=loser.id,
        )
        return winner
