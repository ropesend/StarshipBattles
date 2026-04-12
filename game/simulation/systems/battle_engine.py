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
        """N-team version of `start()`. Accepts any number of teams.

        Each key in `teams` is the `team_id` to assign; values are the
        ship lists. AI controllers default to the factory with
        `enemy_team_id=None` (the factory picks a default); Task 3.4
        refines the AI to read `engine.get_enemies_of` dynamically.

        The existing 2-team `start(team0, team1, ...)` signature is kept
        as a thin wrapper (see below) for backwards compatibility.
        """
        self._initialize_start_state(seed, end_condition, absolute_max_ticks)

        # Assign team_ids + append ships.
        ships_per_team: Dict[int, List['Ship']] = {}
        for team_id, team_ships in teams.items():
            if not isinstance(team_ships, list):
                team_ships = [team_ships]
            for s in team_ships:
                s.team_id = team_id
                self.ships.append(s)
            ships_per_team[team_id] = list(team_ships)

        if ai_controllers is not None:
            self.ai_controllers = list(ai_controllers)
        elif self._ai_factory is not None:
            # Phase 3 Task 3.3: AI factory's `enemy_team_id` is a 2-team
            # artifact. For N teams, we pass any non-self team id as a
            # hint — Task 3.4 refines the AI to scan all enemies.
            self.ai_controllers = []
            all_team_ids = list(ships_per_team.keys())
            for team_id, team_ships in ships_per_team.items():
                enemy_candidates = [tid for tid in all_team_ids if tid != team_id]
                enemy_hint = enemy_candidates[0] if enemy_candidates else team_id
                controllers = self._ai_factory.create_for_ships(
                    team_ships, enemy_team_id=enemy_hint
                )
                self.ai_controllers.extend(controllers)
        else:
            raise ValidationException(
                "BattleEngine requires AI configuration",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"missing": "ai_controllers and ai_factory", "operation": "start_teams"}
            )

        for s in self.ships:
            self._initialize_ship(s)
        # PROJ-269 Phase 5.5: thread the engine's modifier_stack (populated
        # by run_battle from spec) into the aura manager for effect application.
        self.aura_manager.initialize(self.ships, modifier_stack=self.modifier_stack)
        self.logger.start_session()
        self.logger.log(
            f"Battle started: {sum(len(t) for t in teams.values())} ships "
            f"across {len(teams)} teams"
        )
        self._log_initial_status()

    def _initialize_start_state(
        self,
        seed: Optional[int],
        end_condition: Optional[IEndCondition],
        absolute_max_ticks: Optional[int],
    ) -> None:
        """Shared setup for `start()` and `start_teams()`."""
        self.rng = random.Random(seed)
        self.collision_system.rng = self.rng
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        ShipCombatEngine._damage_calculator = DamageCalculator(rng=self.rng)

        self.ships = []
        self.ai_controllers = []
        self.projectile_manager.clear()
        self.recent_beams = []
        self.tick_counter = 0
        self.winner = None
        self.retreated_ships = []

        self.end_condition = end_condition if end_condition is not None else TeamEliminatedCondition()
        if absolute_max_ticks is not None:
            self._absolute_max_ticks = absolute_max_ticks

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

    # ------------------------------------------------------------------
    # PROJ-269 Phase 3: boundary enforcement
    # ------------------------------------------------------------------

    def enforce_boundary(self) -> None:
        """Per-tick boundary check — called from the BoundaryEnforcementPhase.

        For each alive ship, if `self.boundary.contains(ship.position)`
        returns False, dispatch to `_apply_exit_policy(ship, policy)`.
        NONE policy is the default safety net for engines constructed
        without an explicit boundary (UnboundedRegion always returns True).
        """
        boundary = self.boundary
        if boundary is None:
            return
        policy = getattr(boundary, "exit_policy", None)
        # Snapshot the alive ships — _apply_exit_policy may remove from
        # self.ships mid-iteration.
        for ship in list(self.ships):
            if not getattr(ship, "is_alive", True):
                continue
            if not boundary.contains(ship.position):
                self._apply_exit_policy(ship, policy)

    def _apply_exit_policy(self, ship: 'Ship', policy) -> None:
        """Apply the configured `ExitPolicy` to a ship that crossed the boundary.

        Phase 3 Task 3.1 stub: only handles NONE (no-op). DESTROY /
        RETREAT / BOUNCE are implemented in Task 3.2.
        """
        from game.simulation.combat.boundary import ExitPolicy

        if policy is None or policy == ExitPolicy.NONE:
            return
        if policy == ExitPolicy.DESTROY:
            # Destroy the ship by applying lethal damage. Uses the normal
            # damage pipeline so SHIP_DESTROYED events fire correctly.
            remaining_hp = max(ship.hp, 1)
            ship.combat_engine.take_damage(remaining_hp)
            self.logger.log(
                f"Boundary DESTROY: {ship.name} crossed boundary at "
                f"({ship.x:.0f}, {ship.y:.0f})"
            )
            return
        if policy == ExitPolicy.RETREAT:
            # Remove ship from active battle, track for outcome reporting.
            if ship in self.ships:
                self.retreated_ships.append(ship)
                self.remove_ship(ship)
                self.logger.log(
                    f"Boundary RETREAT: {ship.name} exited battle at "
                    f"({ship.x:.0f}, {ship.y:.0f})"
                )
            return
        if policy == ExitPolicy.BOUNCE:
            # Clamp to closest in-bounds point and reflect velocity.
            new_pos = self.boundary.closest_inside_point(ship.position)
            self._bounce_ship(ship, new_pos)
            return
        logger.warning(f"Unknown ExitPolicy: {policy!r}; treating as NONE.")

    def _bounce_ship(self, ship: 'Ship', new_pos: Vector2) -> None:
        """Clamp `ship.position` to `new_pos` and reflect velocity along
        the outward normal. For Rect boundaries we flip whichever velocity
        component was carrying the ship out; for Circle boundaries we
        reflect along the radial vector.
        """
        from game.simulation.combat.boundary import CircleBoundary, RectBoundary

        old_x, old_y = ship.x, ship.y
        ship.x = float(new_pos.x)
        ship.y = float(new_pos.y)
        vel = getattr(ship, "velocity", None)
        if vel is None:
            return

        boundary = self.boundary
        if isinstance(boundary, RectBoundary):
            # Ship crossed either the X or Y extent; flip the component(s)
            # that exceed the boundary.
            half_w = boundary.width / 2.0
            half_h = boundary.height / 2.0
            if abs(old_x) > half_w:
                vel.x = -vel.x
            if abs(old_y) > half_h:
                vel.y = -vel.y
        elif isinstance(boundary, CircleBoundary):
            # Reflect velocity about the radial normal.
            r = (new_pos.x ** 2 + new_pos.y ** 2) ** 0.5
            if r > 0:
                nx = new_pos.x / r
                ny = new_pos.y / r
                dot = vel.x * nx + vel.y * ny
                vel.x -= 2 * dot * nx
                vel.y -= 2 * dot * ny
        else:
            # Fallback: flip both components.
            vel.x = -vel.x
            vel.y = -vel.y

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
