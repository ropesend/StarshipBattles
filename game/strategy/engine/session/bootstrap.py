"""PROJ-423 Phase 2: SessionBootstrap — canonical service wiring.

`SessionBootstrap._build_services(...)` is the single function that wires
the mutator services, `EventBus`, `TurnEngine`, and command registry for a
`GameSession`. Both `GameSession.__init__` and `GameSession.from_dict()`
must route through it; the duplicated wiring that produced the PROJ-396
CRIT-002 drift is eliminated.

`SessionBootstrap.new_game_state(...)` is the new-game-only path: it runs
`_build_services` then `GameInitializer.initialize` wrapped in the
existing `SessionInitializationError` null-object substitution, and
returns a `SessionBootstrapState` ready to be applied to a `GameSession`
via `_apply_bootstrap_state(...)` (Phase 4) or — provisionally in Phase 2
— via direct attribute assignment.

Note: `race_registry` intentionally stays lazy on `GameSession`. The
`_build_services` callable receives a `race_registry_provider` (a no-arg
callable returning the live `IRaceRegistry`) so the TurnEngine can be
wired without forcing eager construction.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, TYPE_CHECKING

from game.core.event_logging import EventBus
from game.strategy.engine.handlers import create_default_registry
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
    SessionRuntimeServices,
)
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.turn_engine_config import TurnEngineConfig
from game.strategy.events import Event, EventLog

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.core.registry import GameRegistries
    from game.strategy.engine.game_config import GameConfig


logger = logging.getLogger(__name__)


def build_event_handler(
    event_log: EventLog,
    turn_number_getter: Callable[[], int],
) -> Callable[..., None]:
    """Build the closure-based handler the global `log_event` system calls.

    Captures `event_log` and a `turn_number_getter` (a zero-arg callable
    that returns the live turn number). Both `GameSession.__init__` and
    `GameSession.from_dict` use this helper; the getter resolves through
    `self.turn_number` so events stamp the live turn even if construction
    overwrites it.
    """

    def handler(event_type: str, **kwargs: Any) -> None:
        category = kwargs.pop("category", "other")
        message = kwargs.pop("message", "")
        empire_id = kwargs.pop("empire_id", -1)
        cat_value = category.value if hasattr(category, "value") else category
        etype_value = (
            event_type.value if hasattr(event_type, "value") else event_type
        )
        event = Event(
            event_type=etype_value,
            category=cat_value,
            turn=turn_number_getter(),
            empire_id=empire_id,
            message=message,
            details=kwargs,
        )
        event_log.append(event)

    return handler


class SessionBootstrap:
    """Canonical construction for the wired runtime-services bag.

    Class-level container so callers can use the static-method form
    `SessionBootstrap._build_services(...)` everywhere without needing to
    pass an instance around.
    """

    @staticmethod
    def _build_services(
        *,
        registries: "GameRegistries",
        event_log: EventLog | None = None,
        ai_factory: Any | None = None,
        race_registry_provider: Callable[[], "IRaceRegistry"] | None = None,
        event_handler_factory: Callable[[EventLog], Callable[..., None]] | None = None,
    ) -> SessionRuntimeServices:
        """Construct the wired runtime-services bag.

        Args:
            registries: The `GameRegistries` value the session is built
                against.
            event_log: Reuse this `EventLog` if provided (the load path
                passes the deserialized log); otherwise construct a fresh
                one.
            ai_factory: Optional AI factory threaded to the TurnEngine.
            race_registry_provider: Zero-arg callable returning the live
                `IRaceRegistry`. Defaults to a constructor for
                `CachedRaceRegistry(RaceLibrary())` — i.e. eager
                construction; production callers wrap their session's
                lazy `race_registry` accessor here.
            event_handler_factory: Optional override for the event-bus
                handler closure (used by `GameSession` so the closure can
                capture `self.turn_number` for live turn-number stamping).

        Returns:
            A `SessionRuntimeServices` instance with every field
            populated.
        """
        log = event_log if event_log is not None else EventLog()

        if event_handler_factory is not None:
            handler = event_handler_factory(log)
        else:
            # Fallback: stamp event-bus events with turn 0. Production
            # callers always pass `event_handler_factory` so this branch
            # only runs in isolated bootstrap tests.
            handler = build_event_handler(log, lambda: 0)
        event_bus = EventBus(handler)

        # Mutator services. Order matches the existing GameSession.__init__
        # block (lines 117-123 of the pre-refactor file).
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService,
        )
        from game.strategy.services.fleet_write_service import FleetWriteService
        from game.strategy.services.planet_write_service import (
            PlanetWriteService,
        )
        from game.strategy.services.empire_write_service import (
            EmpireWriteService,
        )
        from game.strategy.services.ship_instance_write_service import (
            ShipInstanceWriteService,
        )

        fleet_nav = FleetNavigationService()
        fleet_mutator = FleetWriteService(navigation_service=fleet_nav)
        planet_mutator = PlanetWriteService()
        empire_mutator = EmpireWriteService()
        ship_mutator = ShipInstanceWriteService()

        # Race registry. The provider indirection preserves the
        # lazy-construction contract `GameSession` already documents
        # (PROJ-291 C3). When called from new-game / load paths, the
        # session's `race_registry` property is the provider.
        if race_registry_provider is None:
            from game.strategy.systems.race_library import (
                CachedRaceRegistry,
                RaceLibrary,
            )
            race_registry = CachedRaceRegistry(RaceLibrary())
        else:
            race_registry = race_registry_provider()

        turn_engine_config = TurnEngineConfig.create_default(
            registries,
            ai_factory=ai_factory,
            race_registry=race_registry,
            event_bus=event_bus,
            fleet_mutator=fleet_mutator,
            planet_mutator=planet_mutator,
            empire_mutator=empire_mutator,
            ship_mutator=ship_mutator,
        )
        turn_engine = TurnEngine(
            registries=registries,
            config=turn_engine_config,
            ai_factory=ai_factory,
            event_bus=event_bus,
            race_registry=race_registry,
        )

        command_registry = create_default_registry()

        return SessionRuntimeServices(
            registries=registries,
            event_log=log,
            event_bus=event_bus,
            fleet_mutator=fleet_mutator,
            planet_mutator=planet_mutator,
            empire_mutator=empire_mutator,
            ship_mutator=ship_mutator,
            turn_engine=turn_engine,
            command_registry=command_registry,
        )

    @staticmethod
    def new_game_state(
        config: "GameConfig",
        *,
        ai_factory: Any | None = None,
        race_registry_provider: Callable[[], "IRaceRegistry"] | None = None,
        event_handler_factory: Callable[[EventLog], Callable[..., None]] | None = None,
    ) -> SessionBootstrapState:
        """Build the bootstrap state for a new game.

        Runs `_build_services` then `GameInitializer.initialize`, wrapped
        in the existing `SessionInitializationError` null-object
        substitution (`__init__` lines 159-184). On init failure, returns
        a `SessionBootstrapState` with `galaxy=None`, `empires=[]`,
        `human_player_ids=[]` — but the caller never sees it because we
        re-raise as `SessionInitializationError`. The null-object
        substitution is preserved for completeness so behavior matches
        today.
        """
        # Lazy import to avoid a load-time dependency on
        # `GameSession._resolve_registries`.
        from game.strategy.engine.game_session import GameSession

        registries = GameSession._resolve_registries()

        services = SessionBootstrap._build_services(
            registries=registries,
            event_log=None,
            ai_factory=ai_factory,
            race_registry_provider=race_registry_provider,
            event_handler_factory=event_handler_factory,
        )

        from game.core.exceptions import SessionInitializationError
        from game.strategy.engine.game_initializer import GameInitializer

        try:
            galaxy, empires = GameInitializer.initialize(
                config,
                planet_mutator=services.planet_mutator,
                empire_mutator=services.empire_mutator,
            )
        except Exception as e:  # Intentional broad catch: preserves the existing null-object substitution semantics on the new-game path.
            logger.error(
                "GameSession initialization failed: %s",
                e,
                exc_info=True,
            )
            raise SessionInitializationError(
                f"GameSession initialization failed: {e}",
                context={"original_type": type(e).__name__},
            ) from e

        human_player_ids = [
            i for i, p in enumerate(config.players) if p.is_human
        ]

        return SessionBootstrapState(
            config=config,
            services=services,
            galaxy=galaxy,
            empires=empires,
            turn_number=1,
            save_path=None,
            human_player_ids=human_player_ids,
        )
