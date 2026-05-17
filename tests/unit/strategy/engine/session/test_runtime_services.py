"""PROJ-423 Phase 1: tests for SessionRuntimeServices + SessionBootstrapState.

These tests pin the value-object shape that both `GameSession.__init__` and
`GameSession.from_dict` will eventually be routed through. In Phase 1 only the
dataclasses themselves are required to exist, plus a `services` property on
`GameSession` that returns a `SessionRuntimeServices` assembled from the
already-constructed services.
"""
from __future__ import annotations

import dataclasses

import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
    SessionRuntimeServices,
)


def _make_minimal_config() -> GameConfig:
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return config


# Expected field sets pinned by the source plan (TD-02) and design.md.
_EXPECTED_RUNTIME_SERVICE_FIELDS = {
    "registries",
    "event_log",
    "event_bus",
    "fleet_mutator",
    "planet_mutator",
    "empire_mutator",
    "ship_mutator",
    "turn_engine",
    "command_registry",
}

_EXPECTED_BOOTSTRAP_STATE_FIELDS = {
    "config",
    "services",
    "galaxy",
    "empires",
    "turn_number",
    "save_path",
    "human_player_ids",
}


class TestSessionRuntimeServices:
    """Pin the SessionRuntimeServices value-object contract."""

    def test_runtime_services_is_frozen_dataclass(self) -> None:
        """SessionRuntimeServices must be a frozen @dataclass."""
        assert dataclasses.is_dataclass(SessionRuntimeServices)
        # `frozen=True` is reflected on the params attribute.
        params = getattr(SessionRuntimeServices, "__dataclass_params__", None)
        assert params is not None
        assert params.frozen is True

    def test_runtime_services_exposes_current_service_members(self) -> None:
        """All currently-public GameSession services must appear on
        SessionRuntimeServices."""
        field_names = {f.name for f in dataclasses.fields(SessionRuntimeServices)}
        assert field_names == _EXPECTED_RUNTIME_SERVICE_FIELDS
        # race_registry stays OUTSIDE this bag — preserved as lazy on
        # GameSession per the source plan.
        assert "race_registry" not in field_names

    def test_runtime_services_cannot_reassign_field(self) -> None:
        """frozen=True must block field reassignment after construction."""
        # Construct via a real session so we have valid live wired services.
        session = GameSession(config=_make_minimal_config())
        services = session.services
        with pytest.raises(dataclasses.FrozenInstanceError):
            services.fleet_mutator = None  # type: ignore[misc]


class TestSessionBootstrapState:
    """Pin the SessionBootstrapState value-object contract."""

    def test_bootstrap_state_is_frozen_dataclass(self) -> None:
        assert dataclasses.is_dataclass(SessionBootstrapState)
        params = getattr(SessionBootstrapState, "__dataclass_params__", None)
        assert params is not None
        assert params.frozen is True

    def test_bootstrap_state_captures_session_owned_state(self) -> None:
        """Field set matches the seven owned-state attributes from design.md."""
        field_names = {f.name for f in dataclasses.fields(SessionBootstrapState)}
        assert field_names == _EXPECTED_BOOTSTRAP_STATE_FIELDS


class TestGameSessionServicesProperty:
    """`GameSession.services` returns a SessionRuntimeServices populated from
    the wired-up services produced by the existing construction path."""

    def test_game_session_services_property_returns_runtime_services(self) -> None:
        session = GameSession(config=_make_minimal_config())
        services = session.services
        assert isinstance(services, SessionRuntimeServices)

    def test_game_session_services_match_individual_service_attrs(self) -> None:
        """The services bag must be the same objects as the legacy attribute
        surface (no behavioral drift in Phase 1)."""
        session = GameSession(config=_make_minimal_config())
        services = session.services
        assert services.fleet_mutator is session.fleet_mutator
        assert services.planet_mutator is session.planet_mutator
        assert services.empire_mutator is session.empire_mutator
        assert services.ship_mutator is session.ship_mutator
        assert services.registries is session.registries
        assert services.event_log is session.event_log
        assert services.event_bus is session._event_bus
        assert services.turn_engine is session.turn_engine
        assert services.command_registry is session._command_registry
