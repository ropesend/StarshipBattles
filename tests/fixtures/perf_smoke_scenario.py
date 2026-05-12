"""Smoke scenario fixture for PROJ-411 strategy-panel perf tests.

Provides ``smoke_turn1_scenario``: the deterministic baseline scenario
used by every PROJ-411 panel-open perf test:

* Turn 1 (no turns processed yet)
* 2 empires
* 2 star systems (matching ``DEFAULT_SYSTEM_COUNT``)
* At least one colonised planet per empire
* Zero fleets

The fixture builds a real ``GameSession`` via ``GameInitializer`` so the
panel-open paths exercise the same code paths as production. To keep the
fixture cheap, it pins a deterministic ``galaxy_seed`` and uses the
default galaxy generator (random placement, system_count=2).

PROJ-411 contract:
    Panels under test (Galactic Planet Registry, Galactic Star Registry,
    Empire Overview, Build Queue, Event Log) must open against the
    fixture without further setup. Tests that need additional state
    (fleets, designs, events) should layer on top of this fixture
    rather than build their own scenario from scratch.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


_DETERMINISTIC_SEED = 411  # Stable across runs; matches the project id.


def _build_smoke_config() -> GameConfig:
    """Return a ``GameConfig`` for the turn-1 / 2-empires / 2-systems case.

    Uses the default ``system_count`` (2) and the default galaxy generator
    (``"random"``). Pins ``galaxy_seed`` so generation is deterministic.
    """
    config = GameConfig()
    config.system_count = 2
    config.galaxy_seed = _DETERMINISTIC_SEED
    config.players = [
        PlayerConfig(name="Smoke-A", theme="Federation", color=(0, 100, 200),
                     is_human=True),
        PlayerConfig(name="Smoke-B", theme="Romulans", color=(0, 180, 0),
                     is_human=False),
    ]
    return config


def make_smoke_turn1_scenario() -> tuple["GameSession", "Galaxy", list["Empire"]]:
    """Build the smoke scenario; equivalent to the fixture body.

    Exposed as a module-level helper so non-pytest perf scripts (e.g.
    Scalene runners that don't run under pytest) can construct the same
    state without going through the fixture machinery.
    """
    config = _build_smoke_config()
    session = GameSession(config=config)
    # GameInitializer.initialize is called in GameSession.__init__ and
    # populates galaxy + empires from the config + galaxy_seed.
    return session, session.galaxy, list(session.empires)


@pytest.fixture
def smoke_turn1_scenario() -> tuple["GameSession", "Galaxy", list["Empire"]]:
    """PROJ-411 deterministic perf-baseline scenario.

    See module docstring for the contract.
    """
    return make_smoke_turn1_scenario()
