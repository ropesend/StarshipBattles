"""PROJ-475 Phase 1 Task 1.1 — ``facade.empires.race_config(empire_id)``.

The empire DTO carries no race identity (``empire_dto.py``), but
``strategy_event_router`` needs the owning empire's ``race_config`` to seed the
species-ideal button. This surface returns the live ``RaceConfig`` (an
immutable race-definition value object, per decisions.md B12) or ``None`` for an
unknown empire / an empire with no race config.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _facade_with_empires(empires: list) -> StrategySessionFacade:
    session = MagicMock()
    session.galaxy.systems = {}
    session.empires = empires
    return StrategySessionFacade(session)


class TestEmpireRaceConfig:
    def test_returns_race_config_for_seeded_empire(self) -> None:
        race_cfg = SimpleNamespace(race_id="humans", name="Humans")
        empire = SimpleNamespace(id=3, race_config=race_cfg)
        facade = _facade_with_empires([empire])

        assert facade.empires.race_config(3) is race_cfg

    def test_returns_none_for_unknown_empire(self) -> None:
        empire = SimpleNamespace(id=3, race_config=SimpleNamespace(race_id="x"))
        facade = _facade_with_empires([empire])

        assert facade.empires.race_config(999) is None

    def test_returns_none_when_empire_has_no_race_config(self) -> None:
        empire = SimpleNamespace(id=3, race_config=None)
        facade = _facade_with_empires([empire])

        assert facade.empires.race_config(3) is None
