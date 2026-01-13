"""
Resource Consumption Tests

Validates that weapons correctly consume and respect resource limits:
- Energy consumption per beam shot
- Ammo consumption per projectile/seeker shot
- Weapons stop firing when resources depleted

These tests use the TestScenario pattern, allowing them to run in both
pytest (headless) and Combat Lab (visual) with identical behavior.

These tests use small storage components (25 energy, 10 ammo) to verify
depletion behavior without requiring many shots.
"""
import pytest

from test_framework.runner import TestRunner
from simulation_tests.scenarios.resource_scenarios import (
    BeamEnergyConsumptionWithGeneratorScenario,
    BeamEnergyDepletionScenario,
    ProjectileAmmoConsumptionScenario,
    ProjectileAmmoDepletionScenario,
    SeekerAmmoConsumptionScenario,
    SeekerAmmoDepletionScenario
)


@pytest.mark.simulation
class TestBeamResourceConsumption:
    """Test beam weapon energy consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_001_beam_consumes_energy(self):
        """
        RESOURCE-001: Beam weapon consumes energy per shot (with generator).

        Beam with 10 energy cost fires successfully with energy regeneration.
        Generator regenerates faster than weapon consumes.
        """
        scenario = self.runner.run_scenario(
            BeamEnergyConsumptionWithGeneratorScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_002_beam_stops_when_depleted(self):
        """
        RESOURCE-002: Beam stops firing when energy depleted (no generator).

        With 25 energy and 10 per shot, weapon stops after 2 shots.
        Energy should be depleted to below 10 (insufficient for another shot).
        """
        scenario = self.runner.run_scenario(
            BeamEnergyDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


@pytest.mark.simulation
class TestProjectileResourceConsumption:
    """Test projectile weapon ammo consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_003_projectile_consumes_ammo(self):
        """
        RESOURCE-003: Projectile weapon consumes ammo per shot.

        Projectile weapon consumes 1 ammo per shot. With 10 ammo storage,
        weapon can fire 10 shots maximum.
        """
        scenario = self.runner.run_scenario(
            ProjectileAmmoConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_004_projectile_stops_when_depleted(self):
        """
        RESOURCE-004: Projectile weapon stops firing when ammo depleted.

        With 10 ammo and 1 per shot, weapon fires 10 times then stops.
        Ammo should be fully depleted to 0.
        """
        scenario = self.runner.run_scenario(
            ProjectileAmmoDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


@pytest.mark.simulation
class TestSeekerResourceConsumption:
    """Test seeker weapon ammo consumption using TestScenario pattern."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry and create runner."""
        self.runner = TestRunner()

    def test_RESOURCE_005_seeker_consumes_ammo(self):
        """
        RESOURCE-005: Seeker weapon consumes ammo per launch.

        Seeker consumes 5 ammo per shot, so 10 ammo = 2 launches maximum.
        """
        scenario = self.runner.run_scenario(
            SeekerAmmoConsumptionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"

    def test_RESOURCE_006_seeker_stops_when_depleted(self):
        """
        RESOURCE-006: Seeker weapon stops launching when ammo depleted.

        With 10 ammo and 5 per launch, weapon fires 2 times then stops.
        Ammo should be fully depleted to 0.
        """
        scenario = self.runner.run_scenario(
            SeekerAmmoDepletionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"Test failed: {scenario.results}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
