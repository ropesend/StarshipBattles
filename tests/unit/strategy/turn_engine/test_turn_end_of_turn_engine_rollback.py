"""
PROJ-343 T1.2-engines — Failing API test: end-of-turn engine raise must
trigger rollback, not propagate unwrapped.

Bug shape (verified by planning instance 2026-05-04):
- `turn_engine.py:550-573` calls organics_consumption / happiness /
  population_engine / QualityEngine / AtmosphereEngine / WaterEngine
  OUTSIDE `_time_phase`. Their raw exceptions escape the
  `except EnginePhaseError` rollback site at lines 575-589.
- A raw exception from happiness (or any of those six) propagates without
  rollback, AFTER the tick loop has already mutated state.

Fix shape (PROJ-343 Phase 4): wrap each end-of-turn engine call in
`_time_phase(<name>, <fn>, <args>)` so the existing helper re-raises as
`EnginePhaseError`, which the existing rollback path catches.

Currently FAILS: a happiness `RuntimeError` propagates as-is and rollback
is NOT called. Will PASS once T1.2-engines is fixed.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.interfaces.engines import (
    IHappinessEngine,
    IOrganicsConsumptionEngine,
)


def test_happiness_engine_raise_wraps_in_engine_phase_error_and_triggers_rollback(
    fresh_registries, mock_empire, mock_galaxy
):
    """A raise from `happiness_engine.process_happiness` must surface as
    `EnginePhaseError` so the rollback site at `turn_engine.py:575-589`
    invokes `snapshot.restore(session)`.

    Currently FAILS: raw `RuntimeError` propagates; `snapshot.restore` is
    never called.
    """
    mock_empire.fleets = []
    organics = MagicMock(spec=IOrganicsConsumptionEngine)
    happiness = MagicMock(spec=IHappinessEngine)
    happiness.process_happiness.side_effect = RuntimeError("forced happiness failure")

    engine = TurnEngine(
        registries=fresh_registries,
        ai_factory=MagicMock(),
        organics_consumption_engine=organics,
        happiness_engine=happiness,
    )

    session = MagicMock()
    session.turn_number = 1
    fake_snapshot = MagicMock()

    with patch(
        'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
        return_value=fake_snapshot,
    ), patch(
        'game.strategy.engine.quality_engine.QualityEngine'
    ), patch(
        'game.strategy.engine.atmosphere_engine.AtmosphereEngine'
    ), patch(
        'game.strategy.engine.water_engine.WaterEngine'
    ):
        # After fix: EnginePhaseError raised. Currently RuntimeError raised.
        with pytest.raises(EnginePhaseError):
            engine.process_turn([mock_empire], mock_galaxy, session=session)

    # Rollback must have run. Currently FAILS: rollback site never reached
    # because RuntimeError isn't caught by `except EnginePhaseError`.
    fake_snapshot.restore.assert_called_once_with(session)
