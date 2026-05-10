"""Unit tests for the state snapshot utilities (PROJ-223 Phase 6).

Tests that don't require a GameSession. Integration tests are in
tests/integration/save_load/test_live_verification.py.
"""

import copy

from tests.infrastructure.state_snapshot import (
    compare_game_states,
    VerificationReport,
)


class TestCompareGameStatesUnit:
    """Unit tests for compare_game_states with plain dicts."""

    def test_identical_dicts_no_diffs(self):
        d = {"turn_number": 5, "config": {"radius": 100}}
        diffs = compare_game_states(d, copy.deepcopy(d))
        assert diffs == []

    def test_detects_value_change(self):
        d1 = {"turn_number": 5}
        d2 = {"turn_number": 99}
        diffs = compare_game_states(d1, d2)
        assert len(diffs) > 0

    def test_ignore_fields(self):
        d1 = {"turn_number": 5, "name": "test"}
        d2 = {"turn_number": 99, "name": "test"}
        diffs = compare_game_states(d1, d2, ignore_fields={"turn_number"})
        assert diffs == []


class TestVerificationReport:
    """Test VerificationReport dataclass."""

    def test_fields(self):
        report = VerificationReport(
            passed=True,
            differences=[],
            save_time_ms=10.5,
            load_time_ms=8.2,
            save_size_bytes=1024,
        )
        assert report.passed is True
        assert report.differences == []
        assert report.save_time_ms == 10.5
