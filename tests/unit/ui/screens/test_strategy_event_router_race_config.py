"""PROJ-475 Phase 2 Task 2.3 — event_router race-config reads via the facade.

The router seeds the species-ideal button (atmosphere editor) and the food
allocation resolver from the owning empire's race config. PROJ-475 routes those
reads through ``facade.empires.race_config(owner_id)`` instead of
``scene.session.get_empire(owner_id).race_config``.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.ui.screens.strategy_event_router import StrategyEventRouter


def _router_with_facade(race_config_return):
    facade = MagicMock()
    facade.empires.race_config.return_value = race_config_return
    scene = SimpleNamespace(facade=facade)
    ui = SimpleNamespace(scene=scene)
    router = StrategyEventRouter.__new__(StrategyEventRouter)
    router.ui = ui
    return router, facade


class TestGetRaceConfigViaFacade:
    def test_reads_race_config_from_facade_for_owner(self) -> None:
        race_cfg = SimpleNamespace(race_id="humans")
        router, facade = _router_with_facade(race_cfg)
        planet = SimpleNamespace(owner_id=4)

        result = router._get_race_config(planet)

        facade.empires.race_config.assert_called_once_with(4)
        assert result is race_cfg

    def test_returns_none_when_facade_raises(self) -> None:
        router, facade = _router_with_facade(None)
        facade.empires.race_config.side_effect = RuntimeError("save drift")
        planet = SimpleNamespace(owner_id=4)

        assert router._get_race_config(planet) is None
