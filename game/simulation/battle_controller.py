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
from typing import List, Optional, Dict, Callable, Tuple, Any, TYPE_CHECKING

from game.core.exceptions import StateException, ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.services.battle_service import BattleService, BattleServiceResult
from game.simulation.battle_state import BattleState, BattleResults, ShipState
from game.simulation.systems.battle_end_conditions import BattleEndCondition, BattleEndMode
from game.simulation.managers.retreat_manager import (
    RetreatManager,
    RetreatMethod,
)
from game.simulation.managers.battle_state_manager import BattleStateManager
from game.simulation.combat.battle_mode_handler import (
    BattleModeHandler,
    get_handler_for_mode,
)
from game.simulation.battle_config import BattleConfig, BattleMode
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory


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

    def __init__(
        self,
        service: Optional[BattleService] = None,
        ai_factory: Optional['IAIControllerFactory'] = None
    ):
        """
        Initialize BattleController.

        Args:
            service: BattleService instance (creates new one if not provided)
            ai_factory: Optional AIControllerFactory for creating AI controllers.
                       PROJ-126: Must be injected from higher layers (UI/strategy)
                       to maintain proper layer dependencies (AI depends on simulation,
                       not vice versa).
        """
        self._service = service or BattleService()
        self._ai_factory = ai_factory
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

    def configure(self, config: BattleConfig) -> BattleServiceResult:
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
            enable_logging=config.enable_logging,
            ai_factory=self._ai_factory
        )

        if result.success:
            self._is_configured = True

        return result

    def add_ships(self, ships: List['Ship'], team_id: int) -> BattleServiceResult:
        """
        Add ships to a team. Ships can have pre-existing damage.

        Args:
            ships: List of Ship objects to add
            team_id: Team identifier (0 or 1)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleServiceResult(success=False, errors=["Controller not configured"])

        errors = []
        for ship in ships:
            result = self._service.add_ship(ship, team_id)
            if not result.success:
                errors.extend(result.errors)

        return BattleServiceResult(success=len(errors) == 0, errors=errors)

    def add_ships_from_state(self, states: List[ShipState], team_id: int) -> BattleServiceResult:
        """
        Add ships from serialized state (for resume or strategy battles).

        Args:
            states: List of ShipState objects
            team_id: Team identifier (0 or 1)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleServiceResult(success=False, errors=["Controller not configured"])

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
            except (TypeError, ValueError, KeyError, AttributeError, ValidationException) as e:
                errors.append(f"Failed to create ship from state: {e}")

        return BattleServiceResult(success=len(errors) == 0, errors=errors)

    def start(self) -> BattleServiceResult:
        """
        Start the battle, capturing initial state.

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_configured:
            return BattleServiceResult(success=False, errors=["Controller not configured"])

        if self._is_started:
            return BattleServiceResult(success=False, errors=["Battle already started"])

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

            logger.info(f"Battle started: mode={self._config.mode.value}, "
                    f"ships={len(self._service.get_all_ships())}")

        return result

    # === Execution ===

    def update(self) -> BattleServiceResult:
        """
        Run one simulation tick (for visual mode).

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_started:
            return BattleServiceResult(success=False, errors=["Battle not started"])

        # Update retreat states if allowed by mode or config
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
            # Update retreat states if allowed by mode or config
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
                logger.warning(f"Battle reached max ticks limit: {max_ticks}")
                break

        return self.get_results()

    def run_ticks(self, count: int) -> BattleServiceResult:
        """
        Run multiple simulation ticks.

        Args:
            count: Number of ticks to run

        Returns:
            BattleResult indicating success/failure
        """
        if not self._is_started:
            return BattleServiceResult(success=False, errors=["Battle not started"])

        for _ in range(count):
            if self.is_battle_over():
                break

            # Check retreat allowed by mode or config
            if self._retreat_allowed():
                self._update_retreats()

            self._service.update()

        return BattleServiceResult(success=True, engine=self._service.get_engine())

    # === Retreat / Reinforcements ===

    def request_retreat(self, ship: 'Ship', method: str = "edge") -> BattleServiceResult:
        """
        Request a ship to retreat.

        Args:
            ship: Ship to retreat
            method: "edge" (navigate to map edge) or "warp" (charge warp drive)

        Returns:
            BattleResult indicating success/failure
        """
        if not self._retreat_allowed():
            return BattleServiceResult(success=False, errors=["Retreat not allowed in this battle"])

        # Convert string method to enum
        retreat_method = RetreatMethod.EDGE if method == "edge" else RetreatMethod.WARP
        if method not in ("edge", "warp"):
            return BattleServiceResult(success=False, errors=[f"Unknown retreat method: {method}"])

        success, error = self._retreat_manager.request_retreat(
            ship, self._ship_id_map, method=retreat_method
        )

        if success:
            return BattleServiceResult(success=True)
        return BattleServiceResult(success=False, errors=[error])

    def cancel_retreat(self, ship: 'Ship') -> BattleServiceResult:
        """Cancel a ship's retreat."""
        success, error = self._retreat_manager.cancel_retreat(ship, self._ship_id_map)
        if success:
            return BattleServiceResult(success=True)
        return BattleServiceResult(success=False, errors=[error])

    def add_reinforcements(
        self,
        ships: List['Ship'],
        team_id: int,
        entry_point: Tuple[float, float]
    ) -> BattleServiceResult:
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
            return BattleServiceResult(success=False, errors=["Reinforcements not allowed"])

        if not self._is_started:
            return BattleServiceResult(success=False, errors=["Battle not started"])

        engine = self._service.get_engine()
        if not engine:
            return BattleServiceResult(success=False, errors=["No battle engine"])

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

                logger.info(f"Reinforcement arrived: {ship.name} for team {team_id}")
            except ValidationException as e:
                errors.append(f"Failed to add reinforcement {ship.name}: {e}")

        return BattleServiceResult(success=len(errors) == 0, errors=errors)

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

    def _retreat_allowed(self) -> bool:
        """
        Check if retreat is allowed in current battle.

        Mode handler provides defaults per mode; config.allow_retreat can override to enable.
        """
        if self._mode_handler:
            return self._mode_handler.can_retreat() or (self._config and self._config.allow_retreat)
        return self._config.allow_retreat if self._config else False

    def _reinforcements_allowed(self) -> bool:
        """
        Check if reinforcements are allowed in current battle.

        Mode handler provides defaults per mode; config.allow_reinforcements can override to enable.
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

    def load_state(self, state: BattleState) -> BattleServiceResult:
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
            self._service.create_battle(seed=state.seed, ai_factory=self._ai_factory)

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

                logger.info(f"Restored {len(state.projectiles)} projectiles")

            logger.info(f"Battle state restored at tick {state.tick_count}")

            return BattleServiceResult(success=True, engine=engine)

        except (TypeError, ValueError, KeyError, AttributeError, ValidationException, StateException) as e:
            logger.warning(f"Failed to load battle state: {e}")
            return BattleServiceResult(success=False, errors=[str(e)])

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
    def service(self) -> BattleService:
        """Get underlying BattleService."""
        return self._service

    @property
    def mode_handler(self) -> Optional[BattleModeHandler]:
        """Get the current mode handler."""
        return self._mode_handler

    # === Results ===

    def get_results(self) -> BattleResults:
        """
        Get battle results after completion.

        Returns:
            BattleResults dataclass with the following fields:
            - winner: int - Winning team (0 or 1), -1 for draw, None if not over
            - tick_count: int - Total simulation ticks elapsed
            - seed: Optional[int] - Random seed used (for replay/determinism)
            - initial_state: BattleState - State captured at battle start
            - final_state: BattleState - State captured at battle end
            - surviving_ships: List[ShipState] - Ships still alive at end
            - destroyed_ships: List[ShipState] - Ships destroyed during battle
            - escaped_ships: List[ShipState] - Ships that successfully retreated
            - captured_ships: List[ShipState] - Future: derelicts captured by winner
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
            raise StateException(
                "apply_results_to_fleets only valid in STRATEGY mode",
                code=ErrorCode.INVALID_STATE.value,
                context={"mode": self._config.mode.value if self._config else None}
            )

        # Delegate to mode handler (always set after configure())
        self._mode_handler.apply_results(self, results)
        logger.info("Battle results applied to fleets via mode handler")

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


# PROJ-132: Factory functions (create_manual_battle, create_test_battle, etc.)
# have been moved to game/ui/services/battle_factories.py to maintain proper
# layer dependencies. The factory functions require importing from the AI layer,
# which is not allowed in the simulation layer.

