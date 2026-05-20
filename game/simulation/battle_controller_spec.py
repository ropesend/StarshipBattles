"""Spec-in initialization for BattleController.

Extracted from BattleController.start_from_spec (PROJ-460 Phase 2,
F-D-011 partial). The spec-in flow is self-contained orchestration —
it constructs the engine from a BattleSpec and adopts it into the
controller's service — and does not share state with the visual-mode
per-frame update logic. BattleController.start_from_spec is now a
1-line facade delegating here.
"""
from typing import List, Optional, Dict, Callable, Any, TYPE_CHECKING  # noqa: F401
import logging

from game.simulation.battle_config import BattleConfig
from game.simulation.managers.retreat_manager import RetreatManager

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
    from game.simulation.battle_controller import BattleController
    from game.simulation.battle_spec import BattleSpec
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory
    from game.simulation.services.battle_service import BattleServiceResult

__all__ = ["build_controller_from_spec"]


def build_controller_from_spec(
    controller: "BattleController",
    spec: "BattleSpec",
    *,
    ai_factory: "IAIControllerFactory",
    ship_builder: Optional["Callable"] = None,
    registry_provider: Optional["IRegistryProvider"] = None,
    config: Optional[BattleConfig] = None,
    capture_context: "Optional[Any]" = None,
) -> "tuple[BattleServiceResult, Dict[str, 'Ship']]":
    """Configure + start a battle directly from a `BattleSpec`.

    PROJ-270 Phase 10 — single entry point for visual-mode battles.
    Routes through `start_engine_from_spec` (the same code path
    `run_battle` uses), eliminating the duplicated `engine.boundary
    = spec.boundary; engine.modifier_stack = spec.modifier_stack;
    materialize_spec_ships; controller.add_ships; controller.start`
    blocks that previously lived in `app.py` and `test_lab/screen.py`.

    Args:
        controller: The `BattleController` whose state is configured and
            started in place (PROJ-460 Phase 2 — passed explicitly now
            that this is a free function rather than a method).
        spec: The `BattleSpec` describing the battle.
        ai_factory: AI controller factory (UI/strategy-owned).
        ship_builder: Optional callable that builds a `Ship` from a
            `ShipSpec`. When `None`, `registry_provider` MUST be
            supplied; the context materializer is then used. Tests
            pass an explicit stub for isolation.
        registry_provider: REQUIRED when `ship_builder is None`. Per
            PROJ-252, the Simulation layer cannot fetch the registry
            provider via global lookup — non-Simulation callers must
            pass it explicitly.
        config: Optional `BattleConfig` for operational concerns
            (`headless`, `start_paused`, `return_destination`). If
            None, a default `BattleConfig` is constructed using
            `spec.seed`, `spec.end_condition`, and
            `spec.absolute_max_ticks`.

    Returns:
        `(result, ships_by_role)` — `result` is the standard
        BattleServiceResult; `ships_by_role` is the role-tagged
        ship lookup from `materialize_spec_ships` for callers that
        need it (Combat Lab scenarios).

    Raises:
        RuntimeError: When neither `ship_builder` nor `registry_provider`
            is supplied (PROJ-306).
    """
    from game.simulation.battle_runner import (  # noqa: PLC0415
        build_context_ship_builder,
        start_engine_from_spec,
    )
    if ship_builder is None:
        if registry_provider is None:
            raise RuntimeError(
                "BattleController.start_from_spec requires either an "
                "explicit `ship_builder` callable or a "
                "`registry_provider` (so the context materializer "
                "can build one). Per PROJ-252, Simulation code "
                "cannot resolve the registry provider via global "
                "lookup. Non-Simulation callers (Strategy adapter, "
                "app.py, Combat Lab services) should pass "
                "`registry_provider=get_default_registry_provider()`."
            )
        ship_builder = build_context_ship_builder(
            registry_provider=registry_provider,
        )

    # Build / merge the operational config.
    if config is None:
        config = BattleConfig(
            seed=spec.seed,
            end_condition=spec.end_condition,
            absolute_max_ticks=spec.absolute_max_ticks,
        )

    controller._config = config
    controller._ship_id_map.clear()
    controller._initial_state = None
    controller._is_started = False

    # Boundary comes from the spec (PROJ-270 Task 5.4); wire retreat
    # manager before the engine starts so any tick-0 retreat checks
    # have the right arena shape.
    from game.simulation.combat.boundary import UnboundedRegion  # noqa: PLC0415
    boundary = spec.boundary if spec.boundary is not None else UnboundedRegion()
    controller._retreat_manager = RetreatManager(boundary=boundary)

    # Inject spec + ai_factory so outcome extraction works at battle end.
    controller.set_spec(spec)
    controller._ai_factory = ai_factory

    # Drive the shared spec-in engine constructor (same as run_battle).
    # PROJ-312: forward capture_context so visual-mode battles capture
    # via the same hook as headless run_battle.
    engine, ships_by_role = start_engine_from_spec(
        spec, ai_factory=ai_factory, ship_builder=ship_builder,
        capture_context=capture_context,
    )

    # Adopt the running engine into the service so per-frame update() works.
    teams_by_id: Dict[int, List['Ship']] = {}
    for ship in engine.ships:
        teams_by_id.setdefault(ship.team_id, []).append(ship)
    result = controller._service.adopt_started_engine(
        engine,
        team_ships_by_id=teams_by_id,
        seed=spec.seed,
    )

    controller._is_configured = True
    controller._is_started = True

    # Initial state capture (routed through BattleStateManager).
    controller._initial_state = controller._state_manager.capture_state(engine, controller._config)
    # Ship ID map.
    for ship in engine.ships:
        if ship.id not in controller._ship_id_map:
            controller._ship_id_map[ship.id] = ship.id

    logger.info(
        f"Battle started from spec: ships={len(engine.ships)} "
        f"across {len(teams_by_id)} teams (spec-in path)"
    )

    return result, ships_by_role
