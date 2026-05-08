"""
Battle Engine - Core Combat Simulation System

This module provides the BattleEngine class, which runs real-time space combat
simulations between two teams of ships.

Battle Lifecycle:
    1. INIT: Create BattleEngine instance
       engine = BattleEngine()

    2. START: Initialize battle with ships
       engine.start(team0_ships, team1_ships, seed=42)
       - Assigns team IDs (0 and 1)
       - Creates AI controller for each ship via injected factory
       - Initializes spatial grid and projectile manager
       - Starts logging session

    3. TICK: Run simulation loop
       while not engine.is_battle_over():
           engine.update()
       - Updates spatial grid with alive ships/projectiles
       - Runs AI controllers for target selection and behavior
       - Processes ship updates (movement, weapons, abilities)
       - Handles new attacks (projectiles, beams, fighter launches)
       - Processes collisions (ramming)
       - Updates projectiles

    4. END: Check winner and cleanup
       winner = engine.get_winner()  # 0, 1, or -1 (draw)
       engine.shutdown()  # Close logger

End Condition Modes (BattleEndMode):
    - HP_BASED: Battle ends when all ships on one team are dead (default)
    - TIME_BASED: Battle ends after max_ticks reached
    - CAPABILITY_BASED: Battle ends when a team can't fight or move
    - MANUAL: Battle never ends automatically

BattleLogger:
    Writes timestamped battle events to a file for debugging and replay.
    Supports context manager usage and toggleable enabled/disabled state.
    Log format: Plain text, one event per line.

Example:
    engine = BattleEngine()
    engine.start([ship1, ship2], [enemy1], seed=12345)

    while not engine.is_battle_over():
        engine.update()

    winner = engine.get_winner()
    engine.shutdown()
"""
import logging
import random
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from game.core.math import Vector2

logger = logging.getLogger(__name__)
from game.engine.spatial import SpatialGrid
from game.core.constants import AttackType, SimulationConstants
from game.core.config import PhysicsConfig, BattleTuning
from game.simulation.projectile_manager import ProjectileManager
from game.engine.collision import CollisionSystem
from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    TeamEliminatedCondition,
)
# PROJ-382 Phase 5: BattleLogger + boundary helpers extracted into sibling
# modules to bring this file under the 500 LOC ceiling.
from game.simulation.systems.battle_logger import BattleLogger
from game.simulation.systems import boundary_enforcement as _boundary
from game.simulation.systems import attack_processor as _attacks
from game.simulation.systems import battle_setup as _setup

from game.simulation.entities.projectile import Projectile
from game.simulation.entities.ship import Ship
from game.simulation.combat.damage_calculator import DamageCalculator
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    # PROJ-132: Only import protocols from simulation layer, not concrete AI types
    from game.simulation.interfaces.ai_controller import IAIController, IAIControllerFactory
    from game.simulation.systems.tick_phase import TickPhaseRegistry


class BattleEngine:
    """Core combat simulation engine — see module docstring for the
    battle lifecycle and ``BattleEndMode`` semantics.

    Manages ship + AI controller lifecycle, spatial indexing, projectile
    and beam processing, fighter launches/reinforcements, and end
    conditions.  PROJ-382 Phase 5: heavy lifting (battle_logger, attack
    processing, boundary enforcement, battle setup) lives in sibling
    modules; this class is the engine façade.
    """

    def __init__(
        self,
        logger: Optional[BattleLogger] = None,
        ai_factory: Optional['IAIControllerFactory'] = None,
        tick_phases: Optional['TickPhaseRegistry'] = None,
        boundary: Optional[Any] = None,
        modifier_stack: Optional[Any] = None,
    ):
        """
        Create a BattleEngine instance.

        Args:
            logger: Optional battle logger for event recording
            ai_factory: AI controller factory for creating controllers.
            tick_phases: Optional TickPhaseRegistry for custom tick phases.
                        If None, uses create_default_phases() (PROJ-259).
            boundary: Optional `BoundaryRegion` — per-tick `contains()`
                        enforcement with `ExitPolicy` applied when a ship
                        crosses. Default `UnboundedRegion()` (no-op).
                        Introduced by PROJ-269 Phase 3 Task 3.1.
        """
        # PROJ-259: Tick phase registry (pluggable tick phases)
        if tick_phases is None:
            from game.simulation.systems.tick_phase import create_default_phases
            self._tick_phases = create_default_phases()
        else:
            self._tick_phases = tick_phases

        self.ships: List['Ship'] = []
        self.ai_controllers: List['IAIController'] = []

        # PROJ-252: Default unseeded RNG; overridden with seeded instance in start()
        self.rng: random.Random = random.Random()

        self.projectile_manager = ProjectileManager()
        self.collision_system = CollisionSystem(rng=self.rng)

        self.recent_beams: List[Dict[str, Any]] = []
        self.grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)
        self.tick_counter: int = 0
        self.winner: Optional[int] = None

        # Battle end condition (default: team eliminated)
        self.end_condition: IEndCondition = TeamEliminatedCondition()
        self._absolute_max_ticks: int = SimulationConstants.ABSOLUTE_MAX_TICKS

        # Combat event bus (one per battle)
        from game.simulation.combat.combat_events import CombatEventBus
        self.combat_events = CombatEventBus()

        # Fleet aura manager (scoped ability bonuses)
        from game.simulation.combat.fleet_aura_manager import FleetAuraManager
        self.aura_manager = FleetAuraManager()

        # PROJ-259: Cache for alive ships (set by RebuildGridPhase, read by AttackProcessingPhase)
        self._alive_ships_cache: List['Ship'] = []

        # Use provided logger or create a default one (disabled by default to avoid side effects unless requested)
        self.logger = logger if logger else BattleLogger(enabled=False)

        # PROJ-43/PROJ-126: AI factory for decoupled AI controller creation
        # Factory is injected, then we call set_grid() so it can create controllers
        self._ai_factory = ai_factory
        if self._ai_factory is not None:
            self._ai_factory.set_grid(self.grid)
            # PROJ-312: forward the engine's pre-seed RNG to the factory so
            # tests that pre-create controllers before start_teams() get a
            # working factory. start_teams() will overwrite this with the
            # seeded `random.Random(seed)` instance once the seed is known.
            self._ai_factory.set_rng(self.rng)

        # PROJ-269 Phase 3: boundary region (per-tick enforcement).
        # Defaults to UnboundedRegion when not passed — matches pre-Phase-3 behavior.
        if boundary is None:
            from game.simulation.combat.boundary import UnboundedRegion
            boundary = UnboundedRegion()
        self.boundary = boundary
        # Retreated ships — removed from self.ships but tracked here so
        # extract_outcome can mark ShipOutcome.status=RETREATED.
        self.retreated_ships: List['Ship'] = []

        # PROJ-269 Phase 5.5: modifier stack applied at engine start via
        # the FleetAuraManager pipeline. None = no external modifiers.
        self.modifier_stack = modifier_stack

    @property
    def projectiles(self) -> List[Any]:
        return self.projectile_manager.projectiles

    # ------------------------------------------------------------------
    # PROJ-269 Phase 3: N-team accessors
    # ------------------------------------------------------------------

    @property
    def teams(self) -> Dict[int, List['Ship']]:
        """Ships grouped by `team_id`.

        Derived from `self.ships` — always in sync with mid-battle
        additions/removals. Keys are the distinct team_ids currently
        present; empty groups don't appear.
        """
        teams: Dict[int, List['Ship']] = {}
        for ship in self.ships:
            teams.setdefault(ship.team_id, []).append(ship)
        return teams

    def get_ships_by_team(self, team_id: int) -> List['Ship']:
        """Return all ships on the given team (alive or dead)."""
        return [s for s in self.ships if s.team_id == team_id]

    def get_enemies_of(self, ship: 'Ship') -> List['Ship']:
        """Return every ship whose team_id differs from `ship.team_id`.

        N-team rule: no alliances. Every non-self team is equally
        hostile. Future projects may introduce a non-aggression layer
        on top of this predicate.
        """
        return [s for s in self.ships if s.team_id != ship.team_id]

    def start_teams(
        self,
        teams: Dict[int, List['Ship']],
        *,
        seed: Optional[int] = None,
        end_condition: Optional[IEndCondition] = None,
        absolute_max_ticks: Optional[int] = None,
        ai_controllers: Optional[List['IAIController']] = None,
    ) -> None:
        """N-team version of ``start()``.  Delegates to ``battle_setup``
        helper (PROJ-382 Phase 5 extraction)."""
        _setup.start_teams(
            self, teams,
            seed=seed,
            end_condition=end_condition,
            absolute_max_ticks=absolute_max_ticks,
            ai_controllers=ai_controllers,
        )

    def _initialize_start_state(
        self,
        seed: Optional[int],
        end_condition: Optional[IEndCondition],
        absolute_max_ticks: Optional[int],
    ) -> None:
        """Delegate to ``battle_setup.initialize_start_state`` (PROJ-382)."""
        _setup.initialize_start_state(self, seed, end_condition, absolute_max_ticks)

    def start(
        self,
        team0_ships: List['Ship'],
        team1_ships: List['Ship'],
        seed: Optional[int] = None,
        end_condition: Optional[IEndCondition] = None,
        absolute_max_ticks: Optional[int] = None,
        ai_controllers: Optional[List['IAIController']] = None
    ) -> None:
        """2-team backward-compat wrapper around `start_teams` (PROJ-269 Phase 3).

        Delegates to `start_teams({0: team0_ships, 1: team1_ships}, ...)`
        so existing callers keep working unchanged while new callers
        can use `start_teams` directly for N-team battles.
        """
        if not isinstance(team0_ships, list):
            team0_ships = [team0_ships]
        if not isinstance(team1_ships, list):
            team1_ships = [team1_ships]
        self.start_teams(
            {0: team0_ships, 1: team1_ships},
            seed=seed,
            end_condition=end_condition,
            absolute_max_ticks=absolute_max_ticks,
            ai_controllers=ai_controllers,
        )

    def _log_initial_status(self) -> None:
        """Delegate to ``battle_setup.log_initial_status`` (PROJ-382)."""
        _setup.log_initial_status(self)

    def _initialize_ship(self, ship: 'Ship') -> None:
        """Run per-ship initialization: event bus, components, stats, derelict check.

        Called from start() for initial ships and add_ship_mid_battle() for
        reinforcements. Extracted to ensure parity between both paths.
        """
        ship.set_event_bus(self.combat_events)
        for comp in ship.get_all_components():
            if comp.is_active:
                comp.update()
        ship.recalculate_stats()
        ship.update_derelict_status()

    def add_ship_mid_battle(
        self,
        ship: 'Ship',
        team_id: int,
        ai_controller: Optional['IAIController'] = None
    ) -> None:
        """
        Add a ship to the battle mid-combat (for reinforcements).

        Args:
            ship: Ship to add
            team_id: Team identifier (0 or 1)
            ai_controller: Pre-created AI controller (optional).
                If provided, uses this instead of creating one via factory.
        """
        ship.team_id = team_id
        self.ships.append(ship)

        if ai_controller is not None:
            # Use pre-created controller if provided
            self.ai_controllers.append(ai_controller)
        elif self._ai_factory is not None:
            # PROJ-43: Use injected factory to create AI controller
            enemy_team = 1 if team_id == 0 else 0
            ai = self._ai_factory.create_for_ship(ship, enemy_team)
            self.ai_controllers.append(ai)
        else:
            raise ValidationException(
                "BattleEngine requires AI configuration",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"missing": "ai_controller and ai_factory", "operation": "add_ship_mid_battle"}
            )

        # Initialize ship (event bus, components, stats, derelict check)
        self._initialize_ship(ship)
        # Register with aura manager (scan abilities, recalculate bonuses)
        self.aura_manager.register_ship(ship, self.ships)

        self.logger.log(f"Reinforcement arrived: {ship.name} (Team {team_id})")
        logger.info(f"Reinforcement arrived: {ship.name} (Team {team_id})")

    def remove_ship(self, ship: 'Ship') -> bool:
        """
        Remove a ship from the battle (for retreat/escape).

        Args:
            ship: Ship to remove

        Returns:
            True if ship was found and removed
        """
        if ship in self.ships:
            self.ships.remove(ship)

            # Unregister from aura manager (remove fleet-scope bonuses)
            self.aura_manager.unregister_ship(ship, self.ships)

            # Remove associated AI controller.
            # Adapter unwrap: ai.ship is a ShipControllableAdapter (the facade
            # that AIController interacts with), and ai.ship.ship is the underlying
            # Ship entity. We compare the unwrapped Ship to find the matching controller.
            # O(n) scan is fine — fleet sizes are small. Safe to remove-during-iterate
            # because we break immediately after the removal.
            for ai in self.ai_controllers:
                if ai.ship.ship == ship:
                    self.ai_controllers.remove(ai)
                    break

            self.logger.log(f"Ship removed: {ship.name}")
            return True
        return False

    def get_ship_by_name(self, name: str) -> Optional['Ship']:
        """Find a ship by name."""
        for s in self.ships:
            if s.name == name:
                return s
        return None

    def update(self) -> None:
        """
        Run one simulation tick.

        Tick sequence:
            1. Rebuild spatial grid with alive ships/projectiles
            2. Update AI controllers (target selection, behavior)
            3. Update ships (movement, weapons, abilities)
            4. Process new attacks:
               - PROJECTILE/MISSILE: Add to projectile manager
               - BEAM: Raycast hit detection via collision system
               - LAUNCH: Spawn fighter ship with initial velocity
            5. Process ramming collisions (kamikaze ships)
            6. Update projectiles (movement, hit detection, expiration)

        Returns immediately if battle is already over.
        """
        if self.is_battle_over():
            return

        self.tick_counter += 1
        self.recent_beams = []  # Clear previous beams

        # PROJ-259: Delegate to registered tick phases (default: 5 phases)
        self._tick_phases.execute_all(self)

    def _rebuild_grid(self) -> List['Ship']:
        """Rebuild the spatial grid and return ships alive at tick start."""
        self.grid.clear()
        alive_ships = [s for s in self.ships if s.is_alive]
        for ship in alive_ships:
            self.grid.insert(ship)

        for projectile in self.projectiles:
            if projectile.is_alive:
                self.grid.insert(projectile)

        return alive_ships

    def _update_ai_and_ships(self) -> None:
        """Run controller, ship, and aura updates for the current tick."""
        combat_context = {
            'projectiles': self.projectiles,
            'grid': self.grid
        }

        for ai in self.ai_controllers:
            ai.update()
        for ship in self.ships:
            ship.update(context=combat_context)

        self.aura_manager.update(self.ships)

    def _collect_new_attacks(self, alive_ships: List['Ship']) -> List[Any]:
        """Delegate to ``attack_processor.collect_new_attacks`` (PROJ-382)."""
        return _attacks.collect_new_attacks(self, alive_ships)

    def _process_attacks(self, attacks: List[Any]) -> None:
        """Delegate to ``attack_processor.process_attacks`` (PROJ-382)."""
        _attacks.process_attacks(self, attacks)

    def _process_projectile_attack(self, attack: Any, attack_type: AttackType, is_dict: bool) -> None:
        """Delegate to ``attack_processor.process_projectile_attack`` (PROJ-382)."""
        _attacks.process_projectile_attack(self, attack, attack_type, is_dict)

    def _process_launch_attack(self, attack: Dict[str, Any]) -> None:
        """Delegate to ``attack_processor.process_launch_attack`` (PROJ-382)."""
        _attacks.process_launch_attack(self, attack)

    # ------------------------------------------------------------------
    # PROJ-269 Phase 3: boundary enforcement
    # ------------------------------------------------------------------

    def enforce_boundary(self) -> None:
        """Per-tick boundary check — delegates to the boundary_enforcement
        helper module (PROJ-382 Phase 5 extraction).

        Wrapper preserved so the BoundaryEnforcementPhase can call
        ``engine.enforce_boundary()`` without knowing about the helper
        module.
        """
        _boundary.enforce_boundary(self)

    def _apply_exit_policy(self, ship: 'Ship', policy) -> None:
        """Delegate to ``boundary_enforcement.apply_exit_policy`` (PROJ-382)."""
        _boundary.apply_exit_policy(self, ship, policy)

    def _bounce_ship(self, ship: 'Ship', new_pos: Vector2) -> None:
        """Delegate to ``boundary_enforcement.bounce_ship`` (PROJ-382)."""
        _boundary.bounce_ship(self, ship, new_pos)

    def is_battle_over(self) -> bool:
        """
        Check if battle should end based on configured end condition.

        The safety ceiling (absolute_max_ticks) is checked first, then
        the composable end condition is evaluated.

        Returns:
            True if battle should end, False otherwise
        """
        # Safety ceiling always checked first
        if self.tick_counter >= self._absolute_max_ticks:
            return True
        return self.end_condition.is_met(self.ships, self.tick_counter)

    def get_winner(self) -> int:
        """Determine battle winner based on surviving ships (N-team).

        PROJ-269 Phase 3: generalized from fixed-2-team to N teams.

        Returns:
            team_id: The sole team_id whose ships are still alive.
            -1: Draw (0 teams alive, 2+ teams alive, or no ships present).
        """
        alive_team_ids = {
            s.team_id for s in self.ships if s.is_alive
        }
        if len(alive_team_ids) == 1:
            return next(iter(alive_team_ids))
        return -1
    
    def shutdown(self) -> None:
        """Close resources and cleanup. Must be called when battle ends."""
        self.logger.close()
