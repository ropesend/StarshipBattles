"""
AIControllerFactory - Creates AI controllers for ships.

PROJ-126: Moved from game/simulation/factories/ to correct the layer violation.
AI layer can depend on simulation, but simulation should not import from AI.

This factory creates AIController instances for the simulation layer, which
interacts with them via the IAIController protocol defined in simulation.

The factory uses a two-phase initialization:
1. Factory is created (without grid)
2. set_grid() is called when BattleEngine's grid is available

Usage:
    factory = AIControllerFactory()
    # Later, when BattleEngine is created:
    factory.set_grid(engine.grid)
    controller = factory.create_for_ship(ship, enemy_team_id=1)
    controllers = factory.create_for_ships([ship1, ship2], enemy_team_id=1)
"""
import random
from typing import List, Optional, TYPE_CHECKING

from game.core.exceptions import StateException
from game.core.error_codes import ErrorCode
from game.ai.controller import AIController
from game.ai.carrier_controller import CarrierAIController
from game.ai.fighter_controller import FighterAIController
from game.ai.satellite_controller import SatelliteAIController
from game.ai.interfaces import ShipControllableAdapter
from game.simulation.interfaces.ai_controller import IAIController

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid
    from game.simulation.systems.battle_engine import BattleEngine


class AIControllerFactory:
    """
    Factory for creating AI controllers.

    Lives in the AI layer (game/ai/) to maintain proper layer dependencies:
    - AI layer can import from simulation layer
    - Simulation layer uses IAIControllerFactory protocol (doesn't import AI)

    The factory uses a two-phase initialization pattern:
    1. Factory is created without dependencies
    2. set_grid() and set_rng() are called when the grid + RNG become
       available (PROJ-312: seeded RNG is required for replay determinism)

    This allows the factory to be created before BattleEngine exists, then
    configured once the engine's grid and per-battle RNG are available.
    """

    def __init__(self):
        """Create an AI controller factory (without grid or rng)."""
        self._grid: Optional['SpatialGrid'] = None
        self._rng: Optional[random.Random] = None
        # PROJ-FMS-C audit Fix 1: carriers with TacticalFighterLaunchAbility
        # need a reference back to the BattleEngine so their auto-launch path
        # can call ``engine.launch_fighters_in_battle(...)``. Set by
        # ``BattleEngine`` after construction — see ``set_engine``.
        self._engine: Optional['BattleEngine'] = None

    def set_grid(self, grid: 'SpatialGrid') -> None:
        """
        Set the spatial grid for AI queries.

        Called by BattleEngine after the grid is created, before any
        AI controllers are needed.

        Args:
            grid: The spatial grid for spatial queries
        """
        self._grid = grid

    def set_engine(self, engine: 'BattleEngine') -> None:
        """Set the owning BattleEngine for engine-aware controllers.

        PROJ-FMS-C audit Fix 1: :class:`CarrierAIController` calls
        :meth:`BattleEngine.launch_fighters_in_battle` from inside its
        per-tick update. The factory threads ``engine`` into each
        :class:`CarrierAIController` it builds.

        Called by :class:`BattleEngine` after ``__init__`` (the engine
        passes ``self``) but before any controllers are created.
        Optional — controllers built before this is set fall back to
        the standard :class:`AIController` path.
        """
        self._engine = engine

    def set_rng(self, rng: random.Random) -> None:
        """Set the per-battle seeded RNG forwarded to AI controllers.

        PROJ-312: replay determinism requires that every RNG consumer in
        the battle hot path receive ``BattleEngine.rng`` (a seeded
        ``random.Random`` instance) via DI. The factory threads this rng
        into each ``AIController`` it builds.

        Called by ``BattleEngine.start_teams`` after
        ``_initialize_start_state(seed)`` constructs the per-battle RNG and
        BEFORE controllers are created.
        """
        self._rng = rng

    def create_for_ship(self, ship: 'Ship', enemy_team_id: int) -> IAIController:
        """
        Create an AI controller for a single ship.

        Args:
            ship: The ship to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            An AIController instance that implements IAIController

        Raises:
            StateException: If set_grid() or set_rng() hasn't been called
        """
        if self._grid is None:
            raise StateException(
                "AIControllerFactory grid not initialized",
                code=ErrorCode.NOT_INITIALIZED.value,
                context={"state": "grid_missing"}
            )
        if self._rng is None:
            raise StateException(
                "AIControllerFactory rng not initialized",
                code=ErrorCode.NOT_INITIALIZED.value,
                context={"state": "rng_missing"}
            )
        adapter = ShipControllableAdapter(ship)
        # PROJ-FMS-C Phase 2: tactical fighters get the lightweight
        # ``FighterAIController`` (target nearest enemy, turn-and-thrust,
        # fire when in range). Kamikaze fighters with a set ram target
        # are handled inside the FighterAIController by deferring to
        # the engine's RamTargetResolver. All other ship types get the
        # full :class:`AIController` policy pipeline.
        vehicle_type = self._resolve_vehicle_type(ship)
        if vehicle_type == "Fighter":
            return FighterAIController(
                adapter, self._grid, enemy_team_id, rng=self._rng,
            )
        # PROJ-FMS-D Phase 1: satellites are stationary — dedicated
        # controller that forces zero throttles and never pulls into
        # movement / formation behavior.
        if vehicle_type == "Satellite":
            return SatelliteAIController(
                adapter, self._grid, enemy_team_id, rng=self._rng,
            )
        # PROJ-FMS-C audit Fix 1: ships with ``TacticalFighterLaunchAbility``
        # or PROJ-FMS-D ``TacticalSatelliteLaunchAbility`` get the carrier-
        # aware controller so auto-launch goes through the engine action
        # surface (:meth:`launch_fighters_in_battle` /
        # :meth:`launch_satellites_in_battle`).
        if self._engine is not None and self._ship_has_tactical_launch(ship):
            return CarrierAIController(
                adapter,
                self._grid,
                enemy_team_id,
                rng=self._rng,
                engine=self._engine,
            )
        return AIController(adapter, self._grid, enemy_team_id, rng=self._rng)

    @staticmethod
    def _ship_has_tactical_launch(ship: 'Ship') -> bool:
        """Best-effort detection of tactical launch abilities on ship.

        Walks ``ship.iter_components()`` looking for any active component
        whose abilities include ``TacticalFighterLaunch`` (PROJ-FMS-C) or
        ``TacticalSatelliteLaunch`` (PROJ-FMS-D). Falls back to ``False``
        for stubs that don't implement the iteration surface.
        """
        iter_components = getattr(ship, "iter_components", None)
        if iter_components is None:
            return False
        try:
            for _layer, comp in iter_components():
                if not getattr(comp, "is_active", True):
                    continue
                has_ab = getattr(comp, "has_ability", None)
                if has_ab is None:
                    continue
                if has_ab("TacticalFighterLaunch"):
                    return True
                if has_ab("TacticalSatelliteLaunch"):
                    return True
        except Exception:  # Intentional broad catch: iter_components on minimal stubs raises across many shapes; default to "no tactical launch".
            return False
        return False

    @staticmethod
    def _resolve_vehicle_type(ship: 'Ship') -> str:
        """Best-effort lookup of the ship's vehicle_type.

        Falls back to "Ship" when the attribute is missing (test stubs).
        """
        return getattr(ship, "vehicle_type", "Ship") or "Ship"

    def create_for_ships(self, ships: List['Ship'], enemy_team_id: int) -> List[IAIController]:
        """
        Create AI controllers for multiple ships.

        Args:
            ships: List of ships to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            List of AIController instances, one per ship
        """
        return [self.create_for_ship(ship, enemy_team_id) for ship in ships]
