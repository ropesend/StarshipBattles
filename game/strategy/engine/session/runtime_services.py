"""PROJ-423: SessionRuntimeServices and SessionBootstrapState value objects.

These are the two internal frozen dataclasses that both fresh construction
and rehydration paths agree on. By centralising the wired-service bag here
we eliminate the duplicated mutator-service / turn-engine / event-bus
construction the PROJ-396 CRIT-002 history captures.

The dataclasses are intentionally typed loosely (`Any` for service members)
to keep this layer free of upward dependencies on
`game.strategy.services.*` / `game.strategy.engine.turn_engine.TurnEngine`.
The actual concrete classes are wired by `SessionBootstrap` (Phase 2).

Note: `race_registry` is **not** part of `SessionRuntimeServices`. It stays
lazy on `GameSession` per the source plan.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.core.event_logging import EventBus
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.engine.game_config import GameConfig
    from game.strategy.engine.turn_engine import TurnEngine
    from game.strategy.events import EventLog


@dataclass(frozen=True)
class SessionRuntimeServices:
    """The wired-service bag GameSession exposes through properties.

    Fields:
        registries: GameRegistries the session was constructed against.
        event_log: Session-scoped EventLog instance.
        event_bus: Session-scoped EventBus wrapping the event-log handler.
        fleet_mutator: IFleetMutator (FleetWriteService composed with
            FleetNavigationService).
        planet_mutator: IPlanetMutator (PlanetWriteService).
        empire_mutator: IEmpireMutator (EmpireWriteService).
        ship_mutator: IShipInstanceMutator (ShipInstanceWriteService).
        turn_engine: TurnEngine instance for this session.
        command_registry: Command dispatch registry
            (`create_default_registry()` output).
    """

    registries: "GameRegistries"
    event_log: "EventLog"
    event_bus: "EventBus"
    fleet_mutator: Any
    planet_mutator: Any
    empire_mutator: Any
    ship_mutator: Any
    turn_engine: "TurnEngine"
    command_registry: Any


@dataclass(frozen=True)
class SessionBootstrapState:
    """The single internal payload `GameSession.__init__` and
    `GameSession.from_dict` both feed into `_apply_bootstrap_state(...)`.

    Fields:
        config: GameConfig the session is built around.
        services: SessionRuntimeServices bag (fully wired).
        galaxy: Galaxy (may be None if construction failed via the
            new-game null-object substitution path).
        empires: List of Empires.
        turn_number: 1 for new games; restored value for loaded games.
        save_path: None for new games; restored value for loaded games.
        human_player_ids: Computed from `config.players` for new games;
            restored from the save dict with the `[0, 1]` fallback for
            loaded games.
    """

    config: "GameConfig"
    services: SessionRuntimeServices
    galaxy: "Galaxy | None"
    empires: list["Empire"]
    turn_number: int
    save_path: str | None
    human_player_ids: list[int] = field(default_factory=list)
