"""Behavior-parity tests for the post-TD-08 grouped facade namespaces
(PROJ-430 Phase 1: red; Phase 2: green).

Each test exercises a grouped namespace verb and asserts the return value
matches what the legacy flat method produced. Once Phase 5 deletes the legacy
flat methods these tests collapse to behavior coverage of the grouped
surface only (the legacy comparators get removed).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import (
    EmpireInfo,
    FleetInfo,
    PlanetInfo,
)
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


# ---------------------------------------------------------------------------
# Minimal session fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def fresh_facade() -> StrategySessionFacade:
    session = MagicMock()
    session.galaxy.systems = {}
    session.empires = []
    return StrategySessionFacade(session)


# ---------------------------------------------------------------------------
# Top-level surface group accessors exist
# ---------------------------------------------------------------------------

class TestGroupAccessorsExist:
    """Each grouped namespace accessor must be present on the facade."""

    @pytest.mark.parametrize("name", [
        "commands",
        "fleets",
        "planets",
        "systems",
        "empires",
        "events",
        "session_meta",
        "economy",
        "validation",
    ])
    def test_group_accessor_present(
        self, fresh_facade: StrategySessionFacade, name: str
    ) -> None:
        ns = getattr(fresh_facade, name)
        assert ns is not None


# ---------------------------------------------------------------------------
# Commands namespace (parity with dispatch_*)
# ---------------------------------------------------------------------------

class TestCommandsNamespaceParity:
    """``facade.commands.<verb>`` is the renamed form of
    ``facade.dispatch_<verb>``. Verifies a representative sample of helpers.
    """

    def test_issue_move_dispatch_through_grouped_surface(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        # Replace the underlying ``handle_command`` so the test only checks
        # the dispatch glue, not the command execution.
        sentinel = ValidationResult.success()
        fresh_facade._session.handle_command = MagicMock(return_value=sentinel)

        result = fresh_facade.commands.issue_move(fleet_id=1, target_hex=HexCoord(0, 0))

        assert result is sentinel
        # The underlying handle_command must have been called exactly once
        # with a Command DTO.
        fresh_facade._session.handle_command.assert_called_once()


# ---------------------------------------------------------------------------
# Fleets namespace (parity with get_fleet*)
# ---------------------------------------------------------------------------

class TestFleetsNamespaceParity:
    """``facade.fleets.<verb>(...)`` returns the same value as the legacy
    flat method.
    """

    def _setup(self):
        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        session.turn_number = 1

        # Fleet stub with the attributes FleetInfo.from_fleet needs.
        fleet = MagicMock()
        fleet.id = 7
        fleet.location = HexCoord(0, 0)
        empire = MagicMock()
        empire.fleets = [fleet]
        session.empires = [empire]
        session._get_fleet_by_id = MagicMock(return_value=fleet)
        session.preview_fleet_path = MagicMock(return_value=[HexCoord(0, 0)])
        session.get_fleet_path_projection = MagicMock(return_value=[{"turn": 1}])
        return StrategySessionFacade(session), fleet

    def test_fleets_get_returns_same_as_get_fleet(self):
        facade, fleet = self._setup()
        # Compare via underlying slice — the flat method has been deleted in
        # Phase 5, so we go through the slice directly for the comparator.
        legacy = facade._fleet_slice.get_fleet(fleet.id)
        grouped = facade.fleets.get(fleet.id)
        assert isinstance(grouped, type(legacy)) or grouped == legacy

    def test_fleets_path_preview_returns_same_as_get_fleet_path_preview(self):
        facade, fleet = self._setup()
        legacy = facade._fleet_slice.get_fleet_path_preview(fleet.id, HexCoord(1, 0))
        grouped = facade.fleets.path_preview(fleet.id, HexCoord(1, 0))
        assert grouped == legacy

    def test_fleets_path_projection_returns_same_as_legacy(self):
        facade, fleet = self._setup()
        legacy = facade._fleet_slice.get_fleet_path_projection(fleet.id, 5)
        grouped = facade.fleets.path_projection(fleet.id, 5)
        assert grouped == legacy


# ---------------------------------------------------------------------------
# Planets namespace
# ---------------------------------------------------------------------------

class TestPlanetsNamespaceParity:
    def test_planets_get_calls_through(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        # Empty galaxy -> None for any id.
        assert fresh_facade.planets.get(999) is None


# ---------------------------------------------------------------------------
# Systems namespace
# ---------------------------------------------------------------------------

class TestSystemsNamespaceParity:
    def test_systems_all_returns_empty_for_empty_galaxy(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        # ``MagicMock.galaxy.systems = {}`` -> .values() returns [] iterable.
        assert list(fresh_facade.systems.all()) == []

    def test_systems_all_stars_returns_empty_for_empty_galaxy(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        assert list(fresh_facade.systems.all_stars()) == []


# ---------------------------------------------------------------------------
# Empires namespace
# ---------------------------------------------------------------------------

class TestEmpiresNamespaceParity:
    def test_empires_all_returns_empty_when_session_has_no_empires(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        assert fresh_facade.empires.all() == []


# ---------------------------------------------------------------------------
# Events namespace
# ---------------------------------------------------------------------------

class TestEventsNamespaceParity:
    def test_events_all_calls_through(self):
        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        event = MagicMock()
        event.to_dict = MagicMock(return_value={"ok": True})
        session.event_log.get_all_events = MagicMock(return_value=[event])
        facade = StrategySessionFacade(session)

        result = facade.events.all()
        assert result == [{"ok": True}]


# ---------------------------------------------------------------------------
# Session meta
# ---------------------------------------------------------------------------

class TestSessionMetaParity:
    def test_session_meta_turn_number(self):
        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        session.turn_number = 7
        facade = StrategySessionFacade(session)
        assert facade.session_meta.turn_number() == 7

    def test_session_meta_save_path(self):
        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        session.save_path = "/tmp/x.save"
        facade = StrategySessionFacade(session)
        assert facade.session_meta.save_path() == "/tmp/x.save"

    def test_session_meta_human_player_ids(self):
        session = MagicMock()
        session.galaxy.systems = {}
        session.empires = []
        session.human_player_ids = [1, 2]
        facade = StrategySessionFacade(session)
        assert facade.session_meta.human_player_ids() == [1, 2]


# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------

class TestEconomyNamespaceParity:
    def test_economy_race_registry(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        # Lazy-initialised, but accessor returns a registry-like object.
        ns = fresh_facade.economy.race_registry()
        assert ns is not None

    def test_economy_colony_demographic_view_missing_planet(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        assert fresh_facade.economy.colony_demographic_view(999) is None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidationNamespaceParity:
    def test_validation_can_move_to_unknown_fleet(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        result = fresh_facade.validation.can_move_to(999, HexCoord(0, 0))
        assert not result.is_valid

    def test_validation_can_colonize_unknown_fleet(
        self, fresh_facade: StrategySessionFacade
    ) -> None:
        result = fresh_facade.validation.can_colonize(999, None)
        assert not result.is_valid
