"""Public-API contract guard for ``StrategySessionFacade``.

Originally part of ``test_strategy_session_facade_public_api.py`` (which was
deleted by PROJ-321 as part of the trivial-pass test cleanup). The OpenCode
PROJ-321 review (MIN-002) recommended restoring focused public-API tests as a
contract guard — the original deletion was correct on the trivial-pass tests
but lost the regression value of "if a public method's contract changes, a
test fails and reviewers see it."

Each test here exercises a public method and asserts on **observable
behavior** — never ``assert facade.method() is not None``. If a public
method signature or contract changes, these tests fail.

Origin: PROJ-326 Phase 2 Task 2.3.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _mock_empire(empire_id: int, name: str = "Test Empire"):
    empire = Mock()
    empire.id = empire_id
    empire.name = name
    empire.color = (255, 0, 0)
    empire.fleets = []
    empire.colonies = []
    empire.race_theme = Mock()
    empire.race_theme.theme_id = "test"
    empire.flag_id = 1
    return empire


@pytest.fixture
def facade():
    """Build a facade against a Mock GameSession with two empires + a turn."""
    session = Mock()
    session.empires = [_mock_empire(1, "Alpha"), _mock_empire(2, "Beta")]
    session.galaxy.systems = {}
    session.galaxy.get_system_at_location = Mock(return_value=None)
    session.turn_number = 7
    session.savegame_path = "/tmp/test.save"
    session.human_player_ids = [1]
    # Lookup helpers must be callable returning None for unknown ids; if we
    # leave them as default Mocks they return Mock() and downstream DTO
    # builders crash trying to iterate Mock attributes.
    session._get_fleet_by_id = Mock(return_value=None)
    session._get_planet_by_id = Mock(return_value=None)
    session._get_empire_by_id = lambda eid: next(
        (e for e in session.empires if e.id == eid), None
    )
    return StrategySessionFacade(session)


class TestStrategySessionFacadeContract:
    """Behavioral guards on the canonical public-API surface."""

    # --- Empire queries ---

    def test_get_all_empires_returns_one_dto_per_empire(self, facade):
        empires = facade.empires.all()
        assert len(empires) == 2
        assert {e.empire_id for e in empires} == {1, 2}

    def test_get_empire_by_id_resolves(self, facade):
        empire = facade.empires.get(1)
        assert empire is not None
        assert empire.empire_id == 1
        assert empire.name == "Alpha"

    def test_get_empire_unknown_id_returns_none(self, facade):
        assert facade.empires.get(999) is None

    # --- System / map queries ---

    def test_get_all_systems_returns_empty_list_for_empty_galaxy(self, facade):
        # Behavioral: empty galaxy yields empty list (NOT None).
        systems = facade.systems.all()
        assert systems == []

    def test_get_system_at_unknown_hex_returns_none(self, facade):
        # Behavioral: unknown coordinate yields None (NOT raises).
        assert facade.systems.at_hex(HexCoord(99, 99)) is None

    # --- Fleet queries ---

    def test_get_fleet_unknown_id_returns_none(self, facade):
        assert facade.fleets.get(404) is None

    def test_get_fleets_at_empty_hex_returns_empty_list(self, facade):
        assert facade.fleets.at_hex(HexCoord(0, 0)) == []

    # --- Game state ---

    def test_get_turn_number_forwards_session_value(self, facade):
        assert facade.session_meta.turn_number() == 7

    # --- Command dispatch ---

    def test_handle_command_returns_validation_result(self, facade):
        # Behavioral: handle_command always returns a ValidationResult, even
        # when the underlying session rejects the command.
        facade._session.handle_command = Mock(return_value=ValidationResult())
        cmd = Mock()
        result = facade.handle_command(cmd)
        assert isinstance(result, ValidationResult)
        facade._session.handle_command.assert_called_once_with(cmd)
