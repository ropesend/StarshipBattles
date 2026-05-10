"""PROJ-381 Phase 2 (B-7): modifier-collection logging regression test.

`ConflictResolutionEngine._collect_team_modifiers` previously emitted
`logger.warning` (information-loss demoted) when the external combat
modifier collector raised. The fix promotes to `logger.error` and
includes hex coord + empire identifiers so log-side debugging is
actionable.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest


def _make_engine_with_galaxy() -> "ConflictResolutionEngine":  # noqa: F821
    """Build a minimally-wired ConflictResolutionEngine for unit testing.

    Avoids the heavy fixtures used elsewhere — we only need the helper
    method `_collect_team_modifiers`, the `_galaxy` attribute (truthy),
    and `_empires` / `_registries`.
    """
    from game.strategy.engine.conflict_resolution_engine import (
        ConflictResolutionEngine,
    )

    engine = ConflictResolutionEngine.__new__(ConflictResolutionEngine)
    engine._galaxy = MagicMock(name="galaxy")
    engine._empires = []
    engine._registries = MagicMock(name="registries")
    return engine


def test_collector_failure_logs_error_with_hex_and_empire_context(monkeypatch, caplog):
    """B-7: a collector raise must surface as an ERROR log carrying the
    hex coordinate and empire IDs."""
    from game.strategy.services import combat_modifier_collector as mod

    def _boom(*args, **kwargs):  # noqa: ANN001
        raise RuntimeError("simulated collector crash")

    monkeypatch.setattr(mod, "collect_combat_modifiers", _boom)

    engine = _make_engine_with_galaxy()
    fleet0 = MagicMock(); fleet0.id = 1
    fleet1 = MagicMock(); fleet1.id = 2
    fleets_by_empire = {0: [fleet0], 1: [fleet1]}
    empire_order = [0, 1]
    location = (3, 4)

    with caplog.at_level(logging.ERROR, logger="game.strategy.engine.conflict_resolution_engine"):
        result = engine._collect_team_modifiers(
            fleets_by_empire, empire_order, location=location,
        )

    # Collector failure must NOT propagate; result is None so battle
    # still resolves with a degraded modifier stack.
    assert result is None

    # Must be ERROR (was WARNING before the fix).
    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert error_records, (
        f"Expected an ERROR log line; got: {[(r.levelname, r.getMessage()) for r in caplog.records]}"
    )
    msg = error_records[0].getMessage()
    # PROJ-395 MAJ-008: hex coordinate and empire IDs must appear in
    # the message for debug-able log mining, but the formatting is not
    # part of the contract — only the values are. Asserting on the
    # exact ``(3, 4)`` / ``[0, 1]`` repr forms (the prior assertion)
    # would break under a refactor like ``hex=3,4`` or ``empires=0,1``.
    # Accept any rendering that contains the discrete coordinate and
    # empire-ID values.
    assert "3" in msg and "4" in msg, (
        f"Hex coordinate values 3 and 4 must appear in the log message; got: {msg!r}"
    )
    assert "0" in msg and "1" in msg, (
        f"Empire IDs 0 and 1 must appear in the log message; got: {msg!r}"
    )
