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
import os
import random
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from game.core.math import Vector2
from game.core.paths import Paths

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

from game.simulation.entities.projectile import Projectile
from game.simulation.entities.ship import Ship
from game.simulation.combat.damage_calculator import DamageCalculator
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    # PROJ-132: Only import protocols from simulation layer, not concrete AI types
    from game.simulation.interfaces.ai_controller import IAIController, IAIControllerFactory
    from game.simulation.systems.tick_phase import TickPhaseRegistry

class BattleLogger:
    """Toggleable logger that writes battle events to file."""

    def __init__(self, filename: str = None, enabled: bool = True):
        if filename is None:
            filename = os.path.join(Paths.LOGS_DIR, "battle_log.txt")
        self.enabled = enabled
        self.filename = filename
        self.file = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed."""
        self.close()
        return False
    
    def __del__(self):
        """Destructor - ensures file is closed on garbage collection."""
        self.close()
        
    def start_session(self):
        """Start a new logging session.

        ERR-010: Uses try/except/finally for proper cleanup on failure.
        """
        if self.enabled:
            self.close()  # Ensure existing file is closed before opening new one
            new_file = None
            try:
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                new_file = open(self.filename, 'w', encoding='utf-8')
                new_file.write("=== BATTLE LOG STARTED ===\n")
                self.file = new_file  # Only assign on success
            except IOError as e:
                logger.warning(f"Could not open battle log '{self.filename}': {e}")
                self.enabled = False
                if new_file:
                    try:
                        new_file.close()
                    except IOError:
                        pass  # Already in error state, ignore close failure
    
    def log(self, message: str):
        """Log a message if logging is enabled."""
        if self.enabled and self.file:
            try:
                self.file.write(f"{message}\n")

            except IOError as e:
                logger.warning(f"BattleLogger: Failed to write to '{self.filename}': {e}")
    
    def close(self):
        """Close the log file."""
        if self.file:
            try:
                self.log("=== BATTLE LOG ENDED ===")
                self.file.close()
            except IOError as e:
                logger.warning(f"BattleLogger: Failed to close '{self.filename}': {e}")
            finally:
                self.file = None

class BattleEngine:
    """
    Core combat simulation engine.

    Manages real-time space combat between two teams of ships, handling:
    - Ship and AI controller lifecycle
    - Spatial indexing for efficient collision queries
    - Projectile and beam weapon processing
    - Fighter launches and reinforcements
    - Battle end conditions

    Attributes:
        ships: All ships currently in battle
        ai_controllers: AI controllers for each ship
        projectile_manager: Tracks and updates projectiles
        collision_system: Handles hit detection
        recent_beams: Beam attack data for current tick (for rendering)
        grid: Spatial hash grid for efficient neighbor queries
        tick_counter: Number of simulation ticks elapsed
        winner: Winning team ID after battle ends (0, 1, or None)
        end_condition: Configurable battle end condition
        logger: Battle event logger (disabled by default)
    """

    def __init__(
        self,
        logger: Optional[BattleLogger] = None,
        ai_factory: Optional['IAIControllerFactory'] = None,
        tick_phases: Optional['TickPhaseRegistry'] = None,
    ):
        """
        Create a BattleEngine instance.

        Args:
            logger: Optional battle logger for event recording
            ai_factory: AI controller factory for creating controllers.
            tick_phases: Optional TickPhaseRegistry for custom tick phases.
                        If None, uses create_default_phases() (PROJ-259).
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

    @property
    def projectiles(self) -> List[Any]:
        return self.projectile_manager.projectiles

    def start(
        self,
        team0_ships: List['Ship'],
        team1_ships: List['Ship'],
        seed: Optional[int] = None,
        end_condition: Optional[IEndCondition] = None,
        absolute_max_ticks: Optional[int] = None,
        ai_controllers: Optional[List['IAIController']] = None
    ) -> None:
        """
        Initialize battle state with configurable end condition.

        Args:
            team0_ships: List of ships for team 0
            team1_ships: List of ships for team 1
            seed: Random seed for deterministic battles
            end_condition: Battle end condition (default: TeamEliminatedCondition)
            absolute_max_ticks: Safety ceiling (default: SimulationConstants.ABSOLUTE_MAX_TICKS)
            ai_controllers: Pre-created AI controllers (optional).
                If provided, uses these instead of creating controllers via factory.
        """
        # PROJ-252: Per-battle RNG — never seed the global random module
        self.rng = random.Random(seed)
        # Propagate RNG to subsystems
        self.collision_system.rng = self.rng
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        ShipCombatEngine._damage_calculator = DamageCalculator(rng=self.rng)

        self.ships = []
        self.ai_controllers = []
        self.projectile_manager.clear()
        self.recent_beams = []
        self.tick_counter = 0
        self.winner = None

        # Set end condition
        self.end_condition = end_condition if end_condition is not None else TeamEliminatedCondition()
        if absolute_max_ticks is not None:
            self._absolute_max_ticks = absolute_max_ticks

        # Handle single ship args (though type hint implies lists)
        if not isinstance(team0_ships, list): team0_ships = [team0_ships]
        if not isinstance(team1_ships, list): team1_ships = [team1_ships]

        # Add ships to teams (common to all paths)
        for s in team0_ships:
            s.team_id = 0
            self.ships.append(s)
        for s in team1_ships:
            s.team_id = 1
            self.ships.append(s)

        if ai_controllers is not None:
            # Use pre-created controllers if provided
            self.ai_controllers = list(ai_controllers)
        elif self._ai_factory is not None:
            # PROJ-43: Use injected factory to create AI controllers
            team0_controllers = self._ai_factory.create_for_ships(team0_ships, enemy_team_id=1)
            team1_controllers = self._ai_factory.create_for_ships(team1_ships, enemy_team_id=0)
            self.ai_controllers = team0_controllers + team1_controllers
        else:
            raise ValidationException(
                "BattleEngine requires AI configuration",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"missing": "ai_controllers and ai_factory", "operation": "start"}
            )

        # Per-ship initialization: event bus, components, stats, derelict check
        for s in self.ships:
            self._initialize_ship(s)

        # Initialize fleet aura manager (scoped ability bonuses)
        self.aura_manager.initialize(self.ships)

        # Logging
        self.logger.start_session()
        self.logger.log(f"Battle started: {len(team0_ships)} vs {len(team1_ships)} ships")

        self._log_initial_status()

    def _log_initial_status(self) -> None:
        for s in self.ships:
            fuel = s.resources.get_value("fuel")
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f}"
            self.logger.log(status_msg)
            logger.info(status_msg)
            # Removed Derelict Warning
            if s.total_thrust <= 0:
                self.logger.log(f"WARNING: {s.name} has NO THRUST!")
            if s.turn_speed <= 0.01:
                self.logger.log(f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})!")

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
        """Collect and clear attacks emitted by ships this tick."""
        new_attacks = []
        for ship in alive_ships:
            if ship.just_fired_projectiles:
                new_attacks.extend(ship.just_fired_projectiles)
                ship.just_fired_projectiles = []
        return new_attacks

    def _process_attacks(self, attacks: List[Any]) -> None:
        """Process projectile, beam, and launch attacks."""
        for attack in attacks:
            is_dict = isinstance(attack, dict)
            attack_type = attack.get('type') if is_dict else attack.type

            if attack_type in (AttackType.PROJECTILE, AttackType.MISSILE):
                self._process_projectile_attack(attack, attack_type, is_dict)
            elif attack_type == AttackType.BEAM:
                self.collision_system.process_beam_attack(attack, self.recent_beams)
            elif attack_type == AttackType.LAUNCH:
                self._process_launch_attack(attack)

    def _process_projectile_attack(self, attack: Any, attack_type: AttackType, is_dict: bool) -> None:
        """Register a projectile or missile attack with logging."""
        if is_dict:
            return

        self.projectile_manager.add_projectile(attack)
        if attack_type == AttackType.PROJECTILE:
            self.logger.log(f"Projectile fired at {attack.position}")
        else:
            target_name = attack.target.name if attack.target else 'unknown'
            self.logger.log(f"Missile fired at {target_name}")

    def _process_launch_attack(self, attack: Dict[str, Any]) -> None:
        """Spawn a launched fighter and add it to the battle."""
        source_ship = attack.get('source')
        fighter_class = attack.get('fighter_class', 'Fighter (Small)')
        origin = attack.get('origin', Vector2(0, 0))

        count = len([ship for ship in self.ships if ship.team_id == source_ship.team_id])
        new_name = f"{source_ship.name} Wing {count+1}"

        offset = Vector2(self.rng.uniform(-10, 10), self.rng.uniform(-10, 10))
        spawn_pos = origin + offset

        new_ship = Ship(
            name=new_name,
            x=spawn_pos.x,
            y=spawn_pos.y,
            color=source_ship.color,
            team_id=source_ship.team_id,
            ship_class=fighter_class,
            theme_id=source_ship.theme_id,
            registries=source_ship.registries,
        )

        new_ship.velocity = Vector2(source_ship.velocity)
        launch_dir = Vector2(1, 0).rotate(source_ship.angle)
        new_ship.velocity += launch_dir * BattleTuning.FIGHTER_LAUNCH_SPEED
        new_ship.angle = source_ship.angle

        self.add_ship_mid_battle(new_ship, new_ship.team_id)
        self.logger.log(f"LAUNCH: {new_name} launched from {source_ship.name}")

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
        """
        Determine battle winner based on surviving ships.

        Note: This method always returns an int, never None. The return type
        is explicitly `int` (not `Optional[int]`). Layers above (BattleService,
        BattleController) may return None to indicate "no active battle".

        Returns:
            0: Team 0 wins (team 1 has no alive ships)
            1: Team 1 wins (team 0 has no alive ships)
            -1: Draw (both teams have alive ships, or both eliminated)
        """
        team0_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team1_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        if team0_alive > 0 and team1_alive == 0:
            return 0
        elif team1_alive > 0 and team0_alive == 0:
            return 1
        return -1
    
    def shutdown(self) -> None:
        """Close resources and cleanup. Must be called when battle ends."""
        self.logger.close()
