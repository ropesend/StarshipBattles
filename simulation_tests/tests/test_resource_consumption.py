"""
Resource System Tests

Validates resource consumption, depletion, and regeneration mechanics:
- Fuel consumption by engines (constant drain)
- Fuel starvation stops engine thrust
- Fuel generation sustains engine operation
- Energy consumption by beam weapons (per-shot)
- Energy depletion stops weapon firing
- Energy regeneration sustains weapon firing
- Ammo consumption by projectile/seeker weapons

These tests use the TestScenario pattern, allowing them to run in both
pytest (headless) and Combat Lab (visual) with identical behavior.
"""
import pytest

from test_framework.runner import TestRunner
from simulation_tests.scenarios.resource_scenarios import (
    # Fuel scenarios (RESOURCE-001 to 003)
    EngineFuelConsumptionScenario,
    EngineFuelDepletionScenario,
    EngineFuelRegenerationScenario,
    # Energy scenarios (RESOURCE-004, 005, 005a)
    BeamEnergyConsumptionScenario,
    BeamEnergyDepletionScenario,
    BeamEnergyRegenerationScenario,
    # Ammo scenarios (RESOURCE-006 to 008)
    ProjectileAmmoConsumptionScenario,
    ProjectileAmmoDepletionScenario,
    SeekerAmmoConsumptionScenario,
)


@pytest.mark.simulation
class TestFuelResourceConsumption:
    """Test engine fuel consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_001_engine_consumes_fuel(self):
        """
        RESOURCE-001: Engine consumes fuel at predictable rate.

        Engine with 1.0 fuel/sec consumption runs for 500 ticks (5 sec).
        Expected: 5.0 fuel consumed, leaving 995.0 remaining.
        """
        scenario = self.runner.run_scenario(
            EngineFuelConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_002_engine_starvation(self):
        """
        RESOURCE-002: Engine stops providing thrust when fuel depleted.

        Engine with 1.0 fuel/sec starts with only 2.5 fuel.
        Expected: Depletes at ~tick 250, ship velocity drops to 0.
        """
        scenario = self.runner.run_scenario(
            EngineFuelDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_003_fuel_regeneration(self):
        """
        RESOURCE-003: Fuel generator sustains engine operation.

        Engine (1.0/sec consumption) + Generator (1.0/sec generation).
        Expected: Fuel stays stable, ship keeps moving.
        """
        scenario = self.runner.run_scenario(
            EngineFuelRegenerationScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


@pytest.mark.simulation
class TestEnergyResourceConsumption:
    """Test beam weapon energy consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_004_beam_consumes_energy(self):
        """
        RESOURCE-004: Beam weapon consumes energy per shot.

        Rapid-fire beam (1 energy/shot) with 100,000 energy battery.
        Fires 100 times in 100 ticks, consuming 100 energy.
        """
        scenario = self.runner.run_scenario(
            BeamEnergyConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_005_beam_stops_when_depleted(self):
        """
        RESOURCE-005: Beam weapon stops firing when energy depleted.

        With 25 energy and 1 per shot, weapon fires 25 times then stops.
        Energy should be depleted to 0.
        """
        scenario = self.runner.run_scenario(
            BeamEnergyDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_005a_beam_with_generator(self):
        """
        RESOURCE-005a: Beam fires continuously with energy generator.

        Generator regenerates faster than beam consumes.
        Weapon fires every tick, energy stays stable.
        """
        scenario = self.runner.run_scenario(
            BeamEnergyRegenerationScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


@pytest.mark.simulation
class TestAmmoResourceConsumption:
    """Test projectile/seeker ammo consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_006_projectile_consumes_ammo(self):
        """
        RESOURCE-006: Projectile weapon consumes ammo per shot.

        Rapid-fire projectile (1 ammo/shot) with 100,000 ammo storage.
        Fires 100 times in 100 ticks, consuming 100 ammo.
        """
        scenario = self.runner.run_scenario(
            ProjectileAmmoConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_007_projectile_stops_when_depleted(self):
        """
        RESOURCE-007: Projectile weapon stops firing when ammo depleted.

        With 10 ammo and 1 per shot, weapon fires 10 times then stops.
        Ammo should be fully depleted to 0.
        """
        scenario = self.runner.run_scenario(
            ProjectileAmmoDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_008_seeker_consumes_ammo(self):
        """
        RESOURCE-008: Seeker weapon consumes ammo per launch.

        Rapid-fire seeker (1 ammo/launch) with 100,000 ammo storage.
        Launches 100 seekers in 100 ticks, consuming 100 ammo.
        """
        scenario = self.runner.run_scenario(
            SeekerAmmoConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
