"""
Regression test for skip_test support in StaticTargetScenario template.

Verifies that TestRunner.run_scenario records a skipped scenario in results
without invoking the spec compiler or any scenario hooks beyond the initial
`skip_test` check.

PROJ-270 Phase 1.3: the two earlier tests that invoked `scenario.setup(engine)`
directly are gone — the `setup()` entry point is deleted. Skip-test handling
is verified end-to-end via `test_runner_records_skip_in_results`.
"""
from combat_lab.runner import TestRunner
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.scenarios.base import TestMetadata


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
        summary="Test that skip_test works via the runner's short-circuit.",
        conditions=[],
        edge_cases=[],
        expected_outcome="Skipped",
        pass_criteria="skip",
        max_ticks=10,
        seed=42,
    )


class TestSkipTestTemplate:
    """Regression: skip_test scenarios short-circuit via the runner."""

    def test_runner_records_skip_in_results(self):
        """TestRunner.run_scenario marks a skipped scenario without running it."""
        runner = TestRunner()
        result = runner.run_scenario(SkippedPlaceholderScenario, headless=True, log_results=False)

        assert result.passed is False
        assert result.results['skipped'] is True
        assert result.results['skip_reason'] == "Placeholder - not yet implemented"
