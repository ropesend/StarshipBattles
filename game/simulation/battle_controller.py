"""
BattleController - Central orchestrator for all battle modes.

Provides unified interface for:
- Manual battles (from Battle Setup screen)
- Combat Lab tests (visual or headless)
- Strategy layer fleet combat
- Hypothetical simulations (isolated, no state mutation)

Handles:
- Battle setup and configuration
- Running visual or headless
- Mid-battle save/load
- Retreat and reinforcement mechanics
- Result collection and state extraction
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Callable, Tuple, Any, TYPE_CHECKING
import copy

from game.core.exceptions import StateException
from game.simulation.services.battle_service import BattleService, BattleResult
from game.simulation.battle_state import BattleState, BattleResults, ShipState
from game.simulation.systems.battle_end_conditions import BattleEndCondition, BattleEndMode
from game.simulation.managers.retreat_manager import (
    RetreatManager,
    RetreatState,
    RetreatMethod,
)
from game.simulation.managers.battle_state_manager import BattleStateManager
from game.simulation.combat.battle_mode_handler import (
    BattleModeHandler,
    get_handler_for_mode,
)
from game.core.logger import log_debug, log_info, log_warning
from game.core.constants import SimulationConstants

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from test_framework.scenario import CombatScenario


class BattleMode(Enum):
    """Types of battle execution modes."""
    MANUAL = "manual"           # Battle Setup screen
    TEST = "test"               # Combat Lab
    STRATEGY = "strategy"       # Strategy layer fleet combat
    HYPOTHETICAL = "hypothetical"  # Planning simulations (isolated)


@dataclass
class BattleConfig:
    """Configuration for a battle instance."""
    mode: BattleMode = BattleMode.MANUAL
    seed: Optional[int] = None
    max_ticks: int = SimulationConstants.DEFAULT_MAX_TICKS
    end_mode: BattleEndMode = BattleEndMode.HP_BASED

    # Mode-specific options
    headless: bool = False
    start_paused: bool = False
    enable_logging: bool = True
    allow_retreat: bool = False
    allow_reinforcements: bool = False

    # For test mode
    test_scenario: Optional['CombatScenario'] = None

    # For strategy mode
    source_fleets: Optional[Tuple[Any, Any]] = None

    # For hypothetical mode
    isolated: bool = True  # Never mutate source ships

    # Map bounds for retreat calculations
    map_bounds: Tuple[float, float, float, float] = (
        0, 0, SimulationConstants.DEFAULT_MAP_SIZE, SimulationConstants.DEFAULT_MAP_SIZE
    )


# RetreatState is imported directly from retreat_manager


class BattleController:
    """
    Central orchestrator for all battle modes.

    Provides unified interface for:
    - Starting battles with ships in any state
    - Running visual or headless
    - Mid-battle save/load
    - Retreat and reinforcement handling
    - Result collection and state extraction
    """

    def __init__(self, service: Optional[BattleService] = None):
        """
        Initialize BattleController.

        Args:
            service: BattleService instance (creates new one if not provided)
        """
        self._service = service or BattleService()
        self._config: Optional[BattleConfig] = None
        self._initial_state: Optional[BattleState] = None
        self._is_configured: bool = False
        self._is_started: bool = False

        # Ship ID tracking (for state capture/restore)
        self._ship_id_map: Dict[int, str] = {}  # object id -> string id

        # Extracted managers (initialized in configure when map_bounds are known)
        self._retreat_manager: Optional[RetreatManager] = None
        self._state_manager: BattleStateManager = BattleStateManager()

        # Mode handler (Strategy pattern for mode-specific behavior)
        self._mode_handler: Optional[BattleModeHandler] = None

        # Callbacks
        self._on_battle_complete: Optional[Callable[['BattleResults'], None]] = None
        self._on_ship_destroyed: Optional[Callable[['Ship'], None]] = None
        self._on_ship_escaped: Optional[Callable[['Ship'], None]] = None

    # === Configuration ===

    def configure(self, config: BattleConfig) -> BattleResult:
        """
        Set up a new battle with given configuration.

        Args:
            config: Battle configuration

        Returns:
            BattleResult indicating success/failure
        """
        self._config = config
        self._ship_id_map.clear()
        self._initial_state = None
        self._is_started = False

        # Initialize mode handler (Strategy pattern)
        self._mode_handler = get_handler_for_mode(config.mode)
        self._mode_handler.configure(self, config)

        # Initialize retreat manager with map bounds from config
        self._retreat_manager = RetreatManager(map_bounds=config.map_bounds)

        result = self._service.create_battle(
            seed=config.seed,
            enable_logging=config.enable_logging
        )

        if result.success:
            self._is_configured = True

        return result

    def add_ships(self, ships: List['Ship'], team_id: int) -> BattleResult:
        """
        Add ships to a team. Ships can have pre-existing damage.

        Args:
            ships: List of Ship objects to add
            team_id: Team identifier (0 or 1)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleResult(success=False, errors=["Controller not configured"])

        errors = []
        for ship in ships:
            result = self._service.add_ship(ship, team_id)
            if not result.success:
                errors.extend(result.errors)

        return BattleResult(success=len(errors) == 0, errors=errors)

    def add_ships_from_state(self, states: List[ShipState], team_id: int) -> BattleResult:
        """
        Add ships from serialized state (for resume or strategy battles).

        Args:
            states: List of ShipState objects
            team_id: Team identifier (0 or 1)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleResult(success=False, errors=["Controller not configured"])

        errors = []
        for state in states:
            try:
                ship = state.to_ship()
                result = self._service.add_ship(ship, team_id)
                if result.success:
                    # Track the ship ID mapping
                    self._ship_id_map[id(ship)] = state.ship_id
                else:
                    errors.extend(result.errors)
            except Exception as e:
                errors.append(f"Failed to create ship from state: {e}")

        return BattleResult(success=len(errors) == 0, errors=errors)

    def start(self) -> BattleResult:
        """
        Start the battle, capturing initial state.

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleResult(success=False, errors=["Controller not configured"])

        if self._is_started:
            return BattleResult(success=False, errors=["Battle already started"])

        result = self._service.start_battle(
            end_mode=self._config.end_mode,
            max_ticks=self._config.max_ticks
        )

        if result.success:
            self._is_started = True

            # Assign ship IDs to any ships that don't have them yet
            for ship in self._service.get_all_ships():
                if id(ship) not in self._ship_id_map:
                    import uuid
                    self._ship_id_map[id(ship)] = str(uuid.uuid4())

            # Capture initial state
            self._initial_state = BattleState.capture_from_engine(
                self._service.get_engine(),
                mode=self._config.mode.value,
                seed=self._config.seed,
                allow_retreat=self._config.allow_retreat,
                allow_reinforcements=self._config.allow_reinforcements,
            )

            log_info(f"Battle started: mode={self._config.mode.value}, "
                    f"ships={len(self._service.get_all_ships())}")

        return result

    # === Execution ===

    def update(self) -> BattleResult:
        """
        Run one simulation tick (for visual mode).

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_started:
            return BattleResult(success=False, errors=["Battle not started"])

        # Update retreat states (use mode handler or config for backward compat)
        if self._retreat_allowed():
            self._update_retreats()

        # Run one tick
        result = self._service.update()

        # Check for completion
        if self.is_battle_over() and self._on_battle_complete:
            self._on_battle_complete(self.get_results())

        return result

    def run_headless(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BattleResults:
        """
        Run battle to completion without rendering.

        Args:
            progress_callback: Optional callback(tick, max_ticks) for progress updates

        Returns:
            BattleResults with battle outcome
        """
        if not self._is_started:
            raise StateException(
                "Battle not started - call start() first",
                code="S001",
                context={"operation": "run_headless"}
            )

        tick = 0
        max_ticks = self._config.max_ticks

        while not self.is_battle_over():
            # Update retreat states (use mode handler or config for backward compat)
            if self._retreat_allowed():
                self._update_retreats()

            # Run one tick
            self._service.update()
            tick += 1

            # Progress callback
            if progress_callback and tick % 100 == 0:
                progress_callback(tick, max_ticks)

            # Safety limit
            if tick >= max_ticks:
                log_warning(f"Battle reached max ticks limit: {max_ticks}")
                break

        return self.get_results()

    def run_ticks(self, count: int) -> BattleResult:
        """
        Run multiple simulation ticks.

        Args:
            count: Number of ticks to run

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_started:
            return BattleResult(success=False, errors=["Battle not started"])

        for _ in range(count):
            if self.is_battle_over():
                break

            # Use mode handler or config for backward compat
            if self._retreat_allowed():
                self._update_retreats()

            self._service.update()

        return BattleResult(success=True, engine=self._service.get_engine())

    # === Retreat / Reinforcements ===

    def request_retreat(self, ship: 'Ship', method: str = "edge") -> BattleResult:
        """
        Request a ship to retreat.

        Args:
            ship: Ship to retreat
            method: "edge" (navigate to map edge) or "warp" (charge warp drive)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._retreat_allowed():
            return BattleResult(success=False, errors=["Retreat not allowed in this battle"])

        # Convert string method to enum
        retreat_method = RetreatMethod.EDGE if method == "edge" else RetreatMethod.WARP
        if method not in ("edge", "warp"):
            return BattleResult(success=False, errors=[f"Unknown retreat method: {method}"])

        success, error = self._retreat_manager.request_retreat(
            ship, self._ship_id_map, method=retreat_method
        )

        if success:
            return BattleResult(success=True)
        return BattleResult(success=False, errors=[error])

    def cancel_retreat(self, ship: 'Ship') -> BattleResult:
        """Cancel a ship's retreat."""
        success, error = self._retreat_manager.cancel_retreat(ship, self._ship_id_map)
        if success:
            return BattleResult(success=True)
        return BattleResult(success=False, errors=[error])

    def add_reinforcements(
        self,
        ships: List['Ship'],
        team_id: int,
        entry_point: Tuple[float, float]
    ) -> BattleResult:
        """
        Add ships mid-battle as reinforcements.

        Args:
            ships: Ships to add
            team_id: Team identifier (0 or 1)
            entry_point: (x, y) spawn position

        Returns:
            BattleResult indicating success/failure
        """
        if not self._reinforcements_allowed():
            return BattleResult(success=False, errors=["Reinforcements not allowed"])

        if not self._is_started:
            return BattleResult(success=False, errors=["Battle not started"])

        engine = self._service.get_engine()
        if not engine:
            return BattleResult(success=False, errors=["No battle engine"])

        errors = []
        for ship in ships:
            try:
                # Position the ship at entry point
                ship.x, ship.y = entry_point
                ship.team_id = team_id

                # Add to engine
                engine.add_ship_mid_battle(ship, team_id)

                # Track ship ID
                import uuid
                self._ship_id_map[id(ship)] = str(uuid.uuid4())

                log_info(f"Reinforcement arrived: {ship.name} for team {team_id}")
            except Exception as e:
                errors.append(f"Failed to add reinforcement {ship.name}: {e}")

        return BattleResult(success=len(errors) == 0, errors=errors)

    def _update_retreats(self) -> None:
        """Process retreat states each tick (delegates to RetreatManager)."""
        engine = self._service.get_engine()
        if not engine:
            return

        def get_ship_by_id(ship_id: str) -> Optional['Ship']:
            """Find ship by ID in current engine ships."""
            for s in engine.ships:
                if self._ship_id_map.get(id(s)) == ship_id:
                    return s
            return None

        # Set callback before update
        self._retreat_manager.set_on_ship_escaped(self._on_ship_escaped)

        # Delegate to manager
        self._retreat_manager.update(get_ship_by_id)

    def _find_nearest_edge(self, ship: 'Ship') -> Tuple[float, float]:
        """Find the nearest map edge for retreat (delegates to RetreatManager)."""
        return self._retreat_manager.find_nearest_edge(ship)

    def _is_at_map_edge(self, ship: 'Ship', threshold: float = 500) -> bool:
        """Check if ship is at map edge (delegates to RetreatManager)."""
        return self._retreat_manager.at_map_edge(ship, threshold)

    def _retreat_allowed(self) -> bool:
        """
        Check if retreat is allowed in current battle.

        Uses mode handler if available, falls back to config for backward compat.
        """
        if self._mode_handler:
            return self._mode_handler.can_retreat() or (self._config and self._config.allow_retreat)
        return self._config.allow_retreat if self._config else False

    def _reinforcements_allowed(self) -> bool:
        """
        Check if reinforcements are allowed in current battle.

        Uses mode handler if available, falls back to config for backward compat.
        """
        if self._mode_handler:
            return self._mode_handler.can_reinforce() or (self._config and self._config.allow_reinforcements)
        return self._config.allow_reinforcements if self._config else False

    # === State Management ===

    def save_state(self) -> BattleState:
        """
        Capture current battle state for save/resume (delegates to BattleStateManager).

        Returns:
            BattleState with complete battle state
        """
        if not self._is_started:
            raise StateException(
                "Cannot save state - battle not started",
                code="S001",
                context={"operation": "save_state"}
            )

        return self._state_manager.capture_state(
            self._service.get_engine(),
            self._config
        )

    def load_state(self, state: BattleState) -> BattleResult:
        """
        Restore battle from saved state (uses BattleStateManager for config restoration).

        Args:
            state: BattleState to restore from

        Returns:
            BattleResult indicating success/failure
        """
        try:
            # Recreate config from state using manager
            self._config = self._state_manager.restore_config_from_state(state)

            # Initialize retreat manager with config bounds
            self._retreat_manager = RetreatManager(map_bounds=self._config.map_bounds)

            # Create new battle
            self._service.create_battle(seed=state.seed)

            # Restore ships from state
            for ship_id, ship_state in state.ships.items():
                ship = ship_state.to_ship()
                team_id = ship_state.team_id
                self._service.add_ship(ship, team_id)
                self._ship_id_map[id(ship)] = ship_id

            # Start battle
            self._service.start_battle(
                end_mode=self._config.end_mode,
                max_ticks=self._config.max_ticks
            )

            # Set tick counter to match saved state
            engine = self._service.get_engine()
            if engine:
                engine.tick_counter = state.tick_count

            self._is_configured = True
            self._is_started = True

            # Restore projectiles
            if engine and state.projectiles:
                # Build ship_id -> Ship lookup for owner/target resolution
                ship_lookup: Dict[str, 'Ship'] = {}
                for ship in engine.ships:
                    ship_id = self._ship_id_map.get(id(ship))
                    if ship_id:
                        ship_lookup[ship_id] = ship

                # Restore each projectile
                for proj_state in state.projectiles:
                    if proj_state.is_alive:
                        proj = proj_state.to_projectile(ship_lookup)
                        engine.projectiles.append(proj)

                log_info(f"Restored {len(state.projectiles)} projectiles")

            log_info(f"Battle state restored at tick {state.tick_count}")

            return BattleResult(success=True, engine=engine)

        except Exception as e:
            log_warning(f"Failed to load battle state: {e}")
            return BattleResult(success=False, errors=[str(e)])

    # === Query Methods ===

    def is_battle_over(self) -> bool:
        """Check if the battle has ended."""
        return self._service.is_battle_over()

    def get_winner(self) -> Optional[int]:
        """Get the winning team ID (0, 1, -1 for draw, None if not over)."""
        return self._service.get_winner()

    def get_all_ships(self) -> List['Ship']:
        """Get all ships in the battle."""
        return self._service.get_all_ships()

    def get_alive_ships(self) -> List['Ship']:
        """Get all living ships."""
        return self._service.get_alive_ships()

    def get_tick_count(self) -> int:
        """Get current tick count."""
        engine = self._service.get_engine()
        return engine.tick_counter if engine else 0

    @property
    def config(self) -> Optional[BattleConfig]:
        """Get current battle configuration."""
        return self._config

    @property
    def engine(self):
        """Get underlying BattleEngine (for backward compatibility)."""
        return self._service.get_engine()

    @property
    def service(self) -> BattleService:
        """Get underlying BattleService."""
        return self._service

    @property
    def mode_handler(self) -> Optional[BattleModeHandler]:
        """Get the current mode handler."""
        return self._mode_handler

    @property
    def _retreating_ships(self) -> Dict[str, RetreatState]:
        """Backward compatibility: delegate to retreat manager."""
        if self._retreat_manager:
            return self._retreat_manager.retreating_ships
        return {}

    @_retreating_ships.setter
    def _retreating_ships(self, value: Dict[str, RetreatState]) -> None:
        """Backward compatibility: set retreat manager state directly."""
        if self._retreat_manager:
            self._retreat_manager.retreating_ships = value

    @property
    def _escaped_ships(self) -> List[str]:
        """Backward compatibility: delegate to retreat manager."""
        if self._retreat_manager:
            return self._retreat_manager.escaped_ships
        return []

    @_escaped_ships.setter
    def _escaped_ships(self, value: List[str]) -> None:
        """Backward compatibility: set retreat manager state directly."""
        if self._retreat_manager:
            self._retreat_manager.escaped_ships = value

    # === Results ===

    def get_results(self) -> BattleResults:
        """
        Get battle results after completion.

        Returns:
            BattleResults with battle outcome and ship states
        """
        engine = self._service.get_engine()

        # Capture final state
        final_state = self.save_state() if self._is_started else None

        # Categorize ships
        surviving = []
        destroyed = []
        escaped = []

        if final_state:
            escaped_ids = self._retreat_manager.escaped_ships if self._retreat_manager else []
            for ship_id, ship_state in final_state.ships.items():
                if ship_id in escaped_ids:
                    escaped.append(ship_state)
                elif ship_state.is_alive:
                    surviving.append(ship_state)
                else:
                    destroyed.append(ship_state)

        return BattleResults(
            winner=self.get_winner(),
            tick_count=self.get_tick_count(),
            seed=self._config.seed if self._config else None,
            initial_state=self._initial_state,
            final_state=final_state,
            surviving_ships=surviving,
            destroyed_ships=destroyed,
            escaped_ships=escaped,
            captured_ships=[],  # Future: derelicts captured by winner
        )

    def apply_results_to_fleets(self, results: BattleResults) -> None:
        """
        For strategy mode: Write battle results back to source fleets.

        Updates ship states, removes destroyed ships, handles escapes.
        Delegates to mode handler for actual implementation.
        """
        if not self._config or self._config.mode != BattleMode.STRATEGY:
            raise ValueError("apply_results_to_fleets only valid in STRATEGY mode")

        # Delegate to mode handler
        if self._mode_handler:
            self._mode_handler.apply_results(self, results)
            log_info(f"Battle results applied to fleets via mode handler")
            return

        # Legacy fallback (should not normally reach here)
        if not self._config.source_fleets:
            raise ValueError("No source fleets configured")

        fleet1, fleet2 = self._config.source_fleets

        # Build mapping of ship names to results
        # (In a real implementation, we'd use proper instance IDs)
        surviving_by_name = {s.name: s for s in results.surviving_ships}
        destroyed_by_name = {s.name: s for s in results.destroyed_ships}
        escaped_by_name = {s.name: s for s in results.escaped_ships}

        # Update fleet 1 (team 0)
        self._apply_results_to_fleet(
            fleet1, 0, surviving_by_name, destroyed_by_name, escaped_by_name
        )

        # Update fleet 2 (team 1)
        self._apply_results_to_fleet(
            fleet2, 1, surviving_by_name, destroyed_by_name, escaped_by_name
        )

        log_info(f"Battle results applied to fleets")

    def _apply_results_to_fleet(
        self,
        fleet: Any,
        team_id: int,
        surviving: Dict[str, ShipState],
        destroyed: Dict[str, ShipState],
        escaped: Dict[str, ShipState],
    ) -> None:
        """Apply battle results to a single fleet.

        BLOCKING DEPENDENCY: This method requires Fleet to track ships via ShipInstance
        rather than raw Ship objects. Once PROJ-41 (Fleet/ShipInstance Integration) is
        complete, implement this to:
        1. Mark destroyed ShipInstances as lost
        2. Update damage state on surviving ShipInstances
        3. Handle escaped ships appropriately

        Until then, battle results are captured in BattleResults but not applied
        back to the fleet's ShipInstance tracking.
        """
        pass

    # === Callbacks ===

    def set_on_battle_complete(self, callback: Callable[[BattleResults], None]) -> None:
        """Set callback for battle completion."""
        self._on_battle_complete = callback

    def set_on_ship_destroyed(self, callback: Callable[['Ship'], None]) -> None:
        """Set callback for ship destruction."""
        self._on_ship_destroyed = callback

    def set_on_ship_escaped(self, callback: Callable[['Ship'], None]) -> None:
        """Set callback for ship escape."""
        self._on_ship_escaped = callback

    # === Reset ===

    def reset(self) -> None:
        """Reset the controller state."""
        self._service.reset()
        self._config = None
        self._initial_state = None
        self._is_configured = False
        self._is_started = False
        self._ship_id_map.clear()
        self._mode_handler = None
        if self._retreat_manager:
            self._retreat_manager.reset()


# === Factory Functions ===

def create_manual_battle(
    team1_ships: List['Ship'],
    team2_ships: List['Ship'],
    seed: Optional[int] = None,
    headless: bool = False,
) -> BattleController:
    """
    Create a controller for a manual battle (Battle Setup screen).

    Args:
        team1_ships: Ships for team 0
        team2_ships: Ships for team 1
        seed: Random seed for determinism
        headless: Run without rendering

    Returns:
        Configured and started BattleController
    """
    controller = BattleController()

    config = BattleConfig(
        mode=BattleMode.MANUAL,
        seed=seed,
        headless=headless,
    )

    controller.configure(config)
    controller.add_ships(team1_ships, 0)
    controller.add_ships(team2_ships, 1)
    controller.start()

    return controller


def create_test_battle(
    scenario: 'CombatScenario',
    headless: bool = True,
    seed: Optional[int] = None,
) -> BattleController:
    """
    Create a controller for a Combat Lab test.

    Args:
        scenario: Test scenario to run
        headless: Run without rendering
        seed: Random seed for determinism

    Returns:
        Configured BattleController (not started - scenario handles setup)
    """
    controller = BattleController()

    config = BattleConfig(
        mode=BattleMode.TEST,
        seed=seed,
        headless=headless,
        test_scenario=scenario,
        max_ticks=scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000,
    )

    controller.configure(config)

    return controller


def create_strategy_battle(
    fleet1: Any,
    fleet2: Any,
    seed: Optional[int] = None,
    allow_retreat: bool = True,
) -> BattleController:
    """
    Create a controller for a strategy layer fleet battle.

    Args:
        fleet1: First fleet (team 0)
        fleet2: Second fleet (team 1)
        seed: Random seed for determinism
        allow_retreat: Allow ships to retreat

    Returns:
        Configured BattleController (ships not yet added - call to_battle_ships on fleets)
    """
    controller = BattleController()

    config = BattleConfig(
        mode=BattleMode.STRATEGY,
        seed=seed,
        headless=True,
        allow_retreat=allow_retreat,
        source_fleets=(fleet1, fleet2),
    )

    controller.configure(config)

    return controller


def create_hypothetical_battle(
    ships1: List['Ship'],
    ships2: List['Ship'],
    seed: Optional[int] = None,
) -> BattleController:
    """
    Create a controller for a hypothetical (what-if) battle.

    Ships are deep-cloned to ensure no mutation of originals.

    Args:
        ships1: Ships for team 0 (will be cloned)
        ships2: Ships for team 1 (will be cloned)
        seed: Random seed for determinism

    Returns:
        Configured and started BattleController
    """
    controller = BattleController()

    config = BattleConfig(
        mode=BattleMode.HYPOTHETICAL,
        seed=seed,
        headless=True,
        isolated=True,
    )

    controller.configure(config)

    # Clone ships to ensure isolation
    from game.simulation.entities.ship_serialization import ShipSerializer

    cloned1 = []
    for ship in ships1:
        data = ShipSerializer.to_dict(ship)
        cloned = ShipSerializer.from_dict(data)
        cloned.x, cloned.y = ship.x, ship.y
        cloned1.append(cloned)

    cloned2 = []
    for ship in ships2:
        data = ShipSerializer.to_dict(ship)
        cloned = ShipSerializer.from_dict(data)
        cloned.x, cloned.y = ship.x, ship.y
        cloned2.append(cloned)

    controller.add_ships(cloned1, 0)
    controller.add_ships(cloned2, 1)
    controller.start()

    return controller


def run_hypothetical_from_instances(
    instances1: List['ShipInstance'],
    instances2: List['ShipInstance'],
    seed: Optional[int] = None,
) -> 'BattleResults':
    """
    Run a hypothetical battle from ShipInstance lists.

    Convenience function for strategy layer "what-if" simulations.
    Clones ship instances so originals are never modified.

    Args:
        instances1: ShipInstances for team 0 (will be cloned)
        instances2: ShipInstances for team 1 (will be cloned)
        seed: Random seed for determinism

    Returns:
        BattleResults with outcome (source instances unchanged)
    """
    # Clone instances
    cloned1 = [inst.clone() for inst in instances1]
    cloned2 = [inst.clone() for inst in instances2]

    # Convert to ships
    ships1 = [inst.to_ship((20000, 50000 + i * 2000), 0) for i, inst in enumerate(cloned1)]
    ships2 = [inst.to_ship((80000, 50000 + i * 2000), 1) for i, inst in enumerate(cloned2)]

    # Run battle
    controller = create_hypothetical_battle(ships1, ships2, seed)
    results = controller.run_headless()

    return results
