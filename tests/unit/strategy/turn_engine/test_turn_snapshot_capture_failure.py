"""
PROJ-343 T1.2-snapshot — Failing API test: snapshot-capture failure must
surface, not silently disable rollback.

Bug shape (verified by planning instance 2026-05-04):
- `turn_engine.py:514-524` wraps `TurnStateSnapshot.capture` in a broad
  `except Exception` that logs and continues with `snapshot=None`.
- The rollback site at `:583/:586` is gated `if snapshot and …`. So if
  capture fails, ANY subsequent `EnginePhaseError` runs to completion
  WITHOUT triggering snapshot restore — the turn is unsafe and we don't know.

Fix shape (PROJ-343 Phase 3): re-raise capture failures verbatim. The turn
aborts BEFORE the tick loop runs; downstream engines are never invoked.

Currently this test FAILS — capture raises, but the turn proceeds to the
tick loop and downstream engines DO execute. Will PASS once T1.2-snapshot
is fixed (capture failure surfaces immediately).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.interfaces.engines import IOrganicsConsumptionEngine


def test_snapshot_capture_failure_surfaces_and_aborts_turn_before_engines_run(
    fresh_registries, mock_empire, mock_galaxy
):
    """If `TurnStateSnapshot.capture` raises and a session was provided, the
    turn must abort before any engine runs — capture failure is fatal because
    rollback is disabled and we cannot guarantee state integrity.

    Currently FAILS: the broad except swallows capture failure, the turn
    proceeds, organics_consumption_engine.process_consumption IS called.
    After T1.2-snapshot fix: capture failure re-raises; organics is NOT
    called.
    """
    mock_empire.fleets = []
    organics = MagicMock(spec=IOrganicsConsumptionEngine)

    engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock(),
        organics_consumption_engine=organics,
    )

    session = MagicMock()
    session.turn_number = 1

    with patch(
        'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
        side_effect=RuntimeError("simulated capture failure"),
    ), patch(
        'game.strategy.engine.quality_engine.QualityEngine'
    ), patch(
        'game.strategy.engine.atmosphere_engine.AtmosphereEngine'
    ), patch(
        'game.strategy.engine.water_engine.WaterEngine'
    ):
        # After fix: process_turn raises (any exception type acceptable as long
        # as it's not silently swallowed). Currently no exception is raised.
        with pytest.raises(Exception):
            engine.process_turn([mock_empire], mock_galaxy, session=session)

    # End-of-turn engines must NOT have been invoked — the turn aborted at
    # snapshot capture. Currently FAILS: organics IS called because the
    # broad except swallowed the capture error and the tick loop ran.
    organics.process_consumption.assert_not_called()
