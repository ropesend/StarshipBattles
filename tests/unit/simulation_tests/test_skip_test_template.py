"""
Regression test for skip_test support in StaticTargetScenario template.

Verifies that scenarios with skip_test=True don't crash during setup() or update()
when ship files don't exist and self.attacker is never initialized.
"""
import pytest
from unittest.mock import Mock

from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.scenarios.base import TestMetadata


class SkippedPlaceholderScenario(StaticTargetScenario):
    """Minimal placeholder scenario that should be safely skipped."""

    attacker_ship = "Nonexistent_Attacker.json"
    target_ship = "Nonexistent_Target.json"
    distance = 1000

    skip_test = True
    skip_reason = "Placeholder - not yet implemented"

    metadata = TestMetadata(
        test_id="TEST-SKIP-001",
        category="Test",
        subcategory="Skip",
        name="Skipped Placeholder",
        summary="Test that skip_test works in setup/update",
        conditions=[],
        edge_cases=[],
        expected_outcome="Skipped",
        pass_criteria="skip",
        max_ticks=10,
        seed=42,
    )


class TestSkipTestTemplate:
    """Regression: skip_test scenarios must not crash in setup() or update()."""

    def test_setup_does_not_crash_when_skip_test_true(self):
        """setup() should return early when skip_test=True, not try to load ships."""
        scenario = SkippedPlaceholderScenario()
        engine = Mock()
        # This would crash with ValueError or FileNotFoundError if setup ran normally
        scenario.setup(engine)
        # attacker should NOT be set
        assert not hasattr(scenario, 'attacker') or scenario.attacker is None

    def test_update_does_not_crash_when_skip_test_true(self):
        """Regression: update() must not access self.attacker when skip_test=True."""
        scenario = SkippedPlaceholderScenario()
        engine = Mock()
        scenario.setup(engine)
        # This was the original crash: update() accessing self.attacker on a skipped scenario
        scenario.update(engine)

    def test_verify_marks_as_skipped(self):
        """verify() should mark results as skipped."""
        scenario = SkippedPlaceholderScenario()
        engine = Mock()
        scenario.setup(engine)
        result = scenario.verify(engine)
        assert result is False
        assert scenario.results['skipped'] is True
        assert scenario.results['skip_reason'] == "Placeholder - not yet implemented"
