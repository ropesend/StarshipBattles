"""PROJ-423 Phase 2: tests for SessionBootstrap.

The bootstrap is the canonical wiring path both fresh-construction and
rehydration must agree on. The anti-drift test
(`test_init_and_from_dict_use_identical_service_classes`) is the safeguard
against future re-occurrence of the PROJ-396 CRIT-002 drift.
"""
from __future__ import annotations

import pytest

from game.core.event_logging import EventBus
from game.core.registry import GameRegistries
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.session.bootstrap import SessionBootstrap
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
    SessionRuntimeServices,
)
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.events import EventLog
from game.strategy.services.empire_write_service import EmpireWriteService
from game.strategy.services.fleet_write_service import FleetWriteService
from game.strategy.services.planet_write_service import PlanetWriteService
from game.strategy.services.ship_instance_write_service import (
    ShipInstanceWriteService,
)


def _minimal_config() -> GameConfig:
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="A", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="B", is_human=False, color=(200, 100, 0)),
    ]
    return config


def _mixed_humans_config() -> GameConfig:
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 3
    config.players = [
        PlayerConfig(name="Human0", is_human=True, color=(10, 20, 30)),
        PlayerConfig(name="AI1", is_human=False, color=(40, 50, 60)),
        PlayerConfig(name="Human2", is_human=True, color=(70, 80, 90)),
    ]
    return config


class TestBuildServices:
    def test_build_services_returns_fully_wired_runtime_services(self) -> None:
        registries = GameSession._resolve_registries()
        services = SessionBootstrap._build_services(registries=registries)

        assert isinstance(services, SessionRuntimeServices)
        assert services.registries is registries
        assert isinstance(services.event_log, EventLog)
        assert isinstance(services.event_bus, EventBus)
        assert isinstance(services.fleet_mutator, FleetWriteService)
        assert isinstance(services.planet_mutator, PlanetWriteService)
        assert isinstance(services.empire_mutator, EmpireWriteService)
        assert isinstance(services.ship_mutator, ShipInstanceWriteService)
        assert isinstance(services.turn_engine, TurnEngine)
        assert services.command_registry is not None

    def test_build_services_reuses_injected_event_log(self) -> None:
        registries = GameSession._resolve_registries()
        existing_log = EventLog()
        services = SessionBootstrap._build_services(
            registries=registries,
            event_log=existing_log,
        )

        assert services.event_log is existing_log

    def test_build_services_constructs_fresh_event_log_when_none(self) -> None:
        registries = GameSession._resolve_registries()
        services = SessionBootstrap._build_services(registries=registries)

        assert isinstance(services.event_log, EventLog)
        assert len(services.event_log.get_all_events()) == 0


class TestNewGameState:
    def test_new_game_state_returns_bootstrap_state(self) -> None:
        state = SessionBootstrap.new_game_state(_minimal_config())
        assert isinstance(state, SessionBootstrapState)
        assert state.turn_number == 1
        assert state.save_path is None
        assert state.galaxy is not None
        assert len(state.empires) >= 1
        assert isinstance(state.services, SessionRuntimeServices)

    def test_new_game_state_builds_human_player_ids_exactly_as_today(self) -> None:
        state = SessionBootstrap.new_game_state(_mixed_humans_config())
        # Current __init__ semantics: [i for i, p in enumerate(config.players)
        # if p.is_human]. For the mixed config above that is [0, 2].
        assert state.human_player_ids == [0, 2]


class TestAntiDrift:
    """The canonical anti-drift test: a session built via __init__ and one
    built via from_dict must have identical service classes for all five
    mutators plus the turn engine plus the command registry. This is the
    safeguard against PROJ-396 CRIT-002 ever re-occurring."""

    def test_init_and_from_dict_use_identical_service_classes(self) -> None:
        fresh = GameSession(config=_minimal_config())
        loaded = GameSession.from_dict(fresh.to_dict())

        assert type(loaded.fleet_mutator) is type(fresh.fleet_mutator)
        assert type(loaded.planet_mutator) is type(fresh.planet_mutator)
        assert type(loaded.empire_mutator) is type(fresh.empire_mutator)
        assert type(loaded.ship_mutator) is type(fresh.ship_mutator)
        assert type(loaded.turn_engine) is type(fresh.turn_engine)
        assert type(loaded._command_registry) is type(fresh._command_registry)
        assert type(loaded._event_bus) is type(fresh._event_bus)
        # PROJ-427 Phase 2: design_repository + design_catalogs_by_empire
        # join the anti-drift set. Both paths must produce the same
        # types (DesignRepository instance + a Mapping[int, DesignCatalog]
        # populated with DesignCatalog instances).
        assert type(loaded.services.design_repository) is type(
            fresh.services.design_repository
        )
        assert type(loaded.services.design_catalogs_by_empire) is type(
            fresh.services.design_catalogs_by_empire
        )
        # Anti-drift across the per-empire catalogs themselves.
        for empire_id in fresh.services.design_catalogs_by_empire:
            assert empire_id in loaded.services.design_catalogs_by_empire
            assert type(
                loaded.services.design_catalogs_by_empire[empire_id]
            ) is type(fresh.services.design_catalogs_by_empire[empire_id])


class TestProj427Phase2CatalogAbsorption:
    """PROJ-427 Phase 2: SessionRuntimeServices gains design_repository
    and design_catalogs_by_empire. SessionBootstrap._build_services
    constructs them at session boundaries."""

    def test_build_services_populates_design_repository(self) -> None:
        from game.strategy.systems.design_repository import DesignRepository

        registries = GameSession._resolve_registries()
        services = SessionBootstrap._build_services(registries=registries)
        assert hasattr(services, "design_repository")
        assert isinstance(services.design_repository, DesignRepository)

    def test_build_services_populates_design_catalogs_by_empire_mapping(self) -> None:
        from typing import Mapping
        from game.strategy.systems.design_catalog import DesignCatalog

        registries = GameSession._resolve_registries()
        services = SessionBootstrap._build_services(registries=registries)
        assert hasattr(services, "design_catalogs_by_empire")
        catalogs = services.design_catalogs_by_empire
        # Mapping shape — but at the build_services boundary we may not
        # have empire IDs yet (those come in via new_game_state). The
        # mapping should at least be a Mapping instance and contain
        # only DesignCatalog values.
        assert isinstance(catalogs, Mapping)
        for cat in catalogs.values():
            assert isinstance(cat, DesignCatalog)

    def test_new_game_state_builds_per_empire_catalogs(self) -> None:
        """New-game bootstrap constructs one DesignCatalog per empire,
        keyed by empire.id."""
        from game.strategy.systems.design_catalog import DesignCatalog

        state = SessionBootstrap.new_game_state(_minimal_config())
        catalogs = state.services.design_catalogs_by_empire
        assert len(catalogs) == len(state.empires)
        for emp in state.empires:
            assert emp.id in catalogs
            assert isinstance(catalogs[emp.id], DesignCatalog)
            assert catalogs[emp.id].empire_id == emp.id
