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
- Mid-battle state capture via save_state()
- Retreat and reinforcement mechanics
- Result collection and state extraction
"""
from typing import List, Optional, Dict, Callable, Tuple, Any, TYPE_CHECKING  # noqa: F401

from game.core.exceptions import StateException, ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.services.battle_service import BattleService, BattleServiceResult
from game.simulation.battle_state import BattleState, BattleResults, ShipState
from game.simulation.systems.battle_end_conditions import IEndCondition
from game.simulation.managers.retreat_manager import (
    RetreatManager,
    RetreatMethod,
)
from game.simulation.managers.battle_state_manager import BattleStateManager
from game.simulation.battle_config import BattleConfig
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
    from game.core.registry import GameRegistries
    from game.simulation.battle_outcome import BattleOutcome
    from game.simulation.battle_spec import BattleSpec
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory


class BattleController:
    """
    Central orchestrator for all battle modes.

    Provides unified interface for:
    - Starting battles with ships in any state
    - Running visual or headless
    - Mid-battle state capture via save_state()
    - Retreat and reinforcement handling
    - Result collection and state extraction
    """

    def __init__(
        self,
        service: Optional[BattleService] = None,
        ai_factory: Optional['IAIControllerFactory'] = None,
        registries: Optional['GameRegistries'] = None,
    ):
        """
        Initialize BattleController.

        Args:
            service: BattleService instance (creates new one if not provided)
            ai_factory: Optional AIControllerFactory for creating AI controllers.
                       PROJ-126: Must be injected from higher layers (UI/strategy)
                       to maintain proper layer dependencies (AI depends on simulation,
                       not vice versa).
            registries: Optional GameRegistries used when rebuilding ships from
                       serialized battle state (e.g. `add_ships_from_state`).
        """
        self._service = service or BattleService()
        self._ai_factory = ai_factory
        self._registries = registries
        self._config: Optional[BattleConfig] = None
        self._initial_state: Optional[BattleState] = None
        self._is_configured: bool = False
        self._is_started: bool = False

        # Ship ID tracking (for state capture/restore)
        self._ship_id_map: Dict[str, str] = {}  # ship.id -> battle state ship_id

        # Extracted managers (initialized in configure when boundary is known)
        self._retreat_manager: Optional[RetreatManager] = None
        self._state_manager: BattleStateManager = BattleStateManager()

        # Callbacks
        self._on_ship_escaped: Optional[Callable[['Ship'], None]] = None

        # PROJ-270 Phase 4: BattleSpec + BattleOutcome for outcome-consuming
        # visual-mode UI. `_spec` is set via `set_spec()` by the caller that
        # compiled the spec (e.g. `Game.start_battle`). `_outcome` is
        # populated lazily when the battle first finishes and exposed via
        # `get_outcome()`.
        from game.simulation.battle_spec import BattleSpec  # noqa: PLC0415 — local to avoid cycle
        from game.simulation.battle_outcome import BattleOutcome  # noqa: PLC0415
        self._spec: Optional[BattleSpec] = None
        self._outcome: Optional[BattleOutcome] = None

    # === Configuration ===

    def configure(
        self,
        config: BattleConfig,
        spec: Optional["BattleSpec"] = None,
    ) -> BattleServiceResult:
        """
        Set up a new battle with given configuration.

        Args:
            config: Battle configuration
            spec: Optional BattleSpec for outcome extraction. Production
                callers (app.py, test_lab/screen.py) pass the spec they
                compiled so the controller can emit a `BattleOutcome` at
                battle end via `get_outcome()`.

        Returns:
            BattleResult indicating success/failure
        """
        self._config = config
        self._ship_id_map.clear()
        self._initial_state = None
        self._is_started = False

        # PROJ-270 Task 5.4: boundary comes from the spec (origin-centered
        # `BoundaryRegion` ADT). When no spec is supplied, default to
        # `UnboundedRegion` — no edge retreat, but warp retreat and the
        # rest of the controller still work.
        from game.simulation.combat.boundary import UnboundedRegion  # noqa: PLC0415
        boundary = spec.boundary if (spec is not None and spec.boundary is not None) else UnboundedRegion()
        self._retreat_manager = RetreatManager(boundary=boundary)

        if spec is not None:
            self.set_spec(spec)

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

        try:
            registries = self._require_registries_for_state_restore(state_count=len(states))
        except ValidationException as e:
            return BattleServiceResult(success=False, errors=[str(e)])

        errors = []
        for state in states:
            try:
                ship = state.to_ship(registries=registries)
                result = self._service.add_ship(ship, team_id)
                if result.success:
                    # Track the ship ID mapping
                    self._ship_id_map[ship.id] = state.ship_id
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
            end_condition=self._config.end_condition,
            absolute_max_ticks=self._config.absolute_max_ticks
        )

        if result.success:
            self._is_started = True

            # Assign ship IDs to any ships that don't have them yet
            for ship in self._service.get_all_ships():
                if ship.id not in self._ship_id_map:
                    self._ship_id_map[ship.id] = ship.id

            # Capture initial state (routed through BattleStateManager)
            self._initial_state = self._state_manager.capture_state(
                self._service.get_engine(),
                self._config
            )

            logger.info(
                f"Battle started: ships={len(self._service.get_all_ships())}"
            )

        return result

    def start_from_spec(
        self,
        spec: "BattleSpec",
        *,
        ai_factory: "IAIControllerFactory",
        ship_builder: Optional["Callable"] = None,
        registry_provider: Optional["IRegistryProvider"] = None,
        config: Optional[BattleConfig] = None,
        capture_context: "Optional[Any]" = None,
    ) -> "tuple[BattleServiceResult, Dict[str, 'Ship']]":
        """Configure + start a battle directly from a `BattleSpec`.

        Delegates to build_controller_from_spec in battle_controller_spec.py
        (PROJ-460 Phase 2). See that module for the full flow.
        """
        from game.simulation.battle_controller_spec import build_controller_from_spec  # noqa: PLC0415
        return build_controller_from_spec(
            self, spec, ai_factory=ai_factory, ship_builder=ship_builder,
            registry_provider=registry_provider, config=config,
            capture_context=capture_context,
        )

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

        # PROJ-270 Phase 4: when the battle first transitions to "over",
        # extract a BattleOutcome so visual-mode consumers can read a
        # proper DTO instead of the live engine. Only extracts once per
        # battle (guarded by `_outcome is None`).
        if self._outcome is None and self._spec is not None and self.is_battle_over():
            self._extract_outcome_on_battle_end()

        return result

    def set_spec(self, spec: "BattleSpec") -> None:
        """Set the `BattleSpec` this battle was compiled from.

        PROJ-270 Phase 4: visual-mode callers (e.g. `Game.start_battle`)
        call this after `configure()` + `add_ships()` so the controller
        can extract a `BattleOutcome` at battle end.
        """
        self._spec = spec

    def get_outcome(self) -> Optional["BattleOutcome"]:
        """Return the `BattleOutcome` for this battle.

        Lazy extraction (PROJ-281 Phase 3): if the battle's natural
        end-transition hasn't fired yet but a consumer asks for the
        outcome (e.g. UI force-end via the "End Battle" button), extract
        on demand from current engine state. Returns `None` only when
        the controller was never handed a spec via `set_spec()` or the
        engine is not yet started.
        """
        if self._outcome is None and self._spec is not None:
            self._extract_outcome_on_battle_end()
        return self._outcome

    def _extract_outcome_on_battle_end(self) -> None:
        """Extract the `BattleOutcome` from the engine's final state.

        Called once by `update()` the first tick after `is_battle_over()`
        becomes True.

        PROJ-312: fires the matching ``on_battle_ended`` hand-off if the
        engine carries a non-empty ``replay_id`` (set by capture's
        on_battle_started call in ``start_engine_from_spec``). Same
        contract as ``run_battle`` for headless battles.
        """
        from game.simulation.battle_runner import extract_outcome  # noqa: PLC0415
        engine = self._service.get_engine()
        if engine is None or self._spec is None:
            return
        self._outcome = extract_outcome(engine, self._spec)

        replay_id = getattr(engine, "replay_id", None)
        if replay_id and self._outcome is not None:
            from game.simulation.replay import (  # noqa: PLC0415
                ReplayOutcome,
                get_default_capture_sink,
            )
            try:
                replay_outcome = ReplayOutcome.from_battle_outcome(self._outcome)
                get_default_capture_sink().on_battle_ended(replay_id, replay_outcome)
            except Exception:  # Intentional broad catch: capture must not crash visual-mode battle end
                import logging
                logging.getLogger(__name__).exception(
                    "PROJ-312 replay capture: visual-mode on_battle_ended failed"
                )

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
                self._ship_id_map[ship.id] = ship.id

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
                if self._ship_id_map.get(s.id) == ship_id:
                    return s
            return None

        # Set callback before update
        self._retreat_manager.set_on_ship_escaped(self._on_ship_escaped)

        # Delegate to manager
        self._retreat_manager.update(get_ship_by_id)

    def _retreat_allowed(self) -> bool:
        """Whether retreat is allowed (PROJ-269: now config-driven only).

        Pre-PROJ-269 the answer was OR'd with a per-mode default
        (`StrategyBattleModeHandler.can_retreat() == True`). Post-PROJ-269
        the strategy compiler doesn't go through `BattleController` at
        all (`run_battle` bypasses it), so the only callers that need
        retreat are ones that explicitly set `config.allow_retreat=True`.
        """
        return bool(self._config and self._config.allow_retreat)

    def _reinforcements_allowed(self) -> bool:
        """Whether reinforcements are allowed (PROJ-269: config-driven only)."""
        return bool(self._config and self._config.allow_reinforcements)

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
                code=ErrorCode.STATE_FROZEN.value,
                context={"operation": "save_state"}
            )

        return self._state_manager.capture_state(
            self._service.get_engine(),
            self._config
        )

    def _require_registries_for_state_restore(
        self,
        *,
        state_count: int
    ) -> Optional['GameRegistries']:
        """
        Return registries for state restoration.

        Empty states can be restored without registries, but any state that
        contains ships must have registries injected into the controller.
        """
        if self._registries is not None:
            return self._registries

        if state_count == 0:
            return None

        raise ValidationException(
            "registries is required for restoring ships from battle state",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"class": "BattleController", "parameter": "registries"}
        )

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

    # PROJ-269 Phase 6: `mode_handler` property removed alongside the
    # `BattleModeHandler` hierarchy. Callers that need per-battle
    # behavior consult the config flags directly.

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

    # PROJ-269 Phase 6: `apply_results_to_fleets` removed. Strategy
    # battles now go through `run_battle(spec)` whose
    # `spec.post_battle_hook` (`apply_outcome_to_fleets`) writes outcome
    # state back into ShipInstance / Fleet / Empire as a side effect.

    # === Callbacks ===

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
        if self._retreat_manager:
            self._retreat_manager.reset()
