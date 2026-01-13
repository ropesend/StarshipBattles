"""
Example Test Scenarios (Pytest Wrapper)

This file demonstrates how to use TestScenario classes in pytest.

Key Points:
1. TestScenario classes are defined in simulation_tests/scenarios/
2. Pytest tests are thin wrappers that run scenarios via TestRunner
3. Both pytest and Combat Lab run the EXACT same scenario code
4. The only difference is headless=True (pytest) vs headless=False (Combat Lab)

Usage:
    pytest simulation_tests/tests/test_example_scenarios.py -v
"""

import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.example_beam_test import ExampleBeamPointBlankTest


@pytest.mark.simulation
class TestExampleScenarios:
    """
    Example tests using the TestScenario pattern.

    This class demonstrates how to wrap TestScenario classes in pytest tests.
    Each test method:
    1. Creates a TestRunner
    2. Runs the scenario in headless mode
    3. Asserts that the scenario passed
    """

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """
        Setup fixture that runs before each test.

        Uses isolated_registry to ensure test data is loaded and
        registries are cleared between tests.
        """
        self.runner = TestRunner()

    def test_EXAMPLE_001_beam_point_blank(self):
        """
        EXAMPLE-001: Example beam weapon at point-blank range.

        This test validates that a beam weapon can hit a stationary target
        at close range (50px).

        Expected: Beam hits and deals damage.
        """
        # Run scenario in headless mode
        scenario = self.runner.run_scenario(
            ExampleBeamPointBlankTest,
            headless=True
        )

        # Assert scenario passed
        assert scenario.passed, \
            f"Example beam test failed. Results: {scenario.results}"

        # Optional: Additional assertions on results
        assert scenario.results.get('damage_dealt', 0) > 0, \
            "Expected damage to be dealt at point-blank range"

        print(f"Test passed! Damage dealt: {scenario.results['damage_dealt']}")
        print(f"Ticks run: {scenario.results['ticks_run']}")


# Additional example showing how to run multiple related scenarios
@pytest.mark.simulation
class TestBeamRangeExamples:
    """
    Example showing how to organize related scenarios.

    In a real test suite, you might have multiple beam tests at different
    ranges, all using the same pattern.
    """

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_example_beam_point_blank(self):
        """Example: Beam at point-blank (50px)."""
        scenario = self.runner.run_scenario(
            ExampleBeamPointBlankTest,
            headless=True
        )
        assert scenario.passed

    # In a real test suite, you would add more tests here:
    # def test_beam_mid_range(self):
    #     scenario = self.runner.run_scenario(BeamMidRangeTest, headless=True)
    #     assert scenario.passed
    #
    # def test_beam_max_range(self):
    #     scenario = self.runner.run_scenario(BeamMaxRangeTest, headless=True)
    #     assert scenario.passed


if __name__ == '__main__':
    # Allow running this test file directly
    pytest.main([__file__, '-v'])
