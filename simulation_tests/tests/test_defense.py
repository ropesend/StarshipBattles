"""
Defense Ability Tests (SHIELD-001 to SHIELD-003, ARMOR-001 to ARMOR-002, ECM-001, SENSOR-001)

Pytest wrappers for defense ability test scenarios. These tests validate
shield, armor, ECM, and sensor mechanics using the TestScenario framework.

Test Coverage:
- SHIELD-001: Shield absorbs beam damage before hull
- SHIELD-002: Shield overflow - damage exceeds shield capacity
- SHIELD-003: Shield regeneration sustains over time
- ARMOR-001: Emissive armor blocks low damage (1 < 5)
- ARMOR-002: Emissive armor reduces high damage (5 == 5)
- ECM-001: ECM defense modifier reduces hit rate
- SENSOR-001: Sensor attack modifier improves hit rate
"""
import pytest
from test_framework.runner import TestRunner
from simulation_tests.logging_config import get_logger
from simulation_tests.scenarios.defense_scenarios import (
    ShieldAbsorbsDamageScenario,
    ShieldOverflowToHullScenario,
    ShieldRegenerationScenario,
    EmissiveArmorBlocksLowDamageScenario,
    EmissiveArmorReducesHighDamageScenario,
    ECMReducesHitRateScenario,
    SensorImprovesHitRateScenario,
)

logger = get_logger(__name__)


@pytest.mark.simulation
class TestShieldDefense:
    """Test shield absorption and regeneration mechanics."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_SHIELD_001_absorbs_damage(self):
        """
        SHIELD-001: Shield absorbs beam damage before hull.

        Expected: Shields decrease, hull stays at full HP.
        """
        scenario = self.runner.run_scenario(
            ShieldAbsorbsDamageScenario,
            headless=True
        )

        assert scenario.passed, \
            f"SHIELD-001 failed: {scenario.results}"
        assert scenario.results['damage_dealt'] > 0, \
            "Beam should deal damage (absorbed by shields)"
        assert scenario.results['shield_damage_absorbed'] > 0, \
            "Shields should absorb some damage"

        logger.info(f"\nSHIELD-001 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Shield Absorbed: {scenario.results['shield_damage_absorbed']}")
        logger.info(f"  Final Shields: {scenario.results['final_shields']}")

    def test_SHIELD_002_overflow_to_hull(self):
        """
        SHIELD-002: Damage exceeding shield capacity reaches hull.

        Expected: Total damage > 200 (shield capacity), shields depleted.
        """
        scenario = self.runner.run_scenario(
            ShieldOverflowToHullScenario,
            headless=True
        )

        assert scenario.passed, \
            f"SHIELD-002 failed: {scenario.results}"
        assert scenario.results['shields_depleted'], \
            "Shields should be fully depleted"
        assert scenario.results['damage_dealt'] > 200, \
            f"Total damage should exceed shield capacity (200), got {scenario.results['damage_dealt']}"

        logger.info(f"\nSHIELD-002 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Shields Depleted: {scenario.results['shields_depleted']}")
        logger.info(f"  Hull Damage: {scenario.results['hull_damage']}")

    def test_SHIELD_003_regeneration(self):
        """
        SHIELD-003: Shield regeneration restores shields between hits.

        Expected: Shields regenerate, reducing effective damage taken.
        """
        scenario = self.runner.run_scenario(
            ShieldRegenerationScenario,
            headless=True
        )

        assert scenario.passed, \
            f"SHIELD-003 failed: {scenario.results}"
        assert scenario.results['ticks_run'] > 0, \
            "Simulation should complete"

        logger.info(f"\nSHIELD-003 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Final Shields: {scenario.results['final_shields']}")
        logger.info(f"  Shields Intact: {scenario.results['shields_intact']}")


@pytest.mark.simulation
class TestEmissiveArmorDefense:
    """Test emissive armor damage reduction mechanics."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_ARMOR_001_blocks_low_damage(self):
        """
        ARMOR-001: EmissiveArmor(5) blocks 1-damage beam entirely.

        Expected: Zero damage dealt (1 dmg < 5 armor).
        """
        scenario = self.runner.run_scenario(
            EmissiveArmorBlocksLowDamageScenario,
            headless=True
        )

        assert scenario.passed, \
            f"ARMOR-001 failed: {scenario.results}"
        assert scenario.results['damage_dealt'] == 0, \
            f"Expected 0 damage with EmissiveArmor(5) vs 1-damage beam, got {scenario.results['damage_dealt']}"

        logger.info(f"\nARMOR-001 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Emissive Armor: {scenario.results['emissive_armor_value']}")
        logger.info(f"  Beam Damage/Hit: {scenario.results['beam_damage_per_hit']}")

    def test_ARMOR_002_reduces_high_damage(self):
        """
        ARMOR-002: EmissiveArmor(5) reduces 5-damage beam to 0.

        Expected: Zero damage dealt (5 dmg - 5 armor = 0).
        """
        scenario = self.runner.run_scenario(
            EmissiveArmorReducesHighDamageScenario,
            headless=True
        )

        assert scenario.passed, \
            f"ARMOR-002 failed: {scenario.results}"
        assert scenario.results['damage_dealt'] == 0, \
            f"Expected 0 damage with EmissiveArmor(5) vs 5-damage beam, got {scenario.results['damage_dealt']}"

        logger.info(f"\nARMOR-002 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Emissive Armor: {scenario.results['emissive_armor_value']}")
        logger.info(f"  Beam Damage/Hit: {scenario.results['beam_damage_per_hit']}")


@pytest.mark.simulation
class TestToHitModifiers:
    """Test ECM and sensor to-hit modifier effects."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_ECM_001_reduces_hit_rate(self):
        """
        ECM-001: ECM defense modifier reduces beam hit rate.

        Expected: Hit rate with ECM < baseline hit rate.
        """
        scenario = self.runner.run_scenario(
            ECMReducesHitRateScenario,
            headless=True
        )

        assert scenario.passed, \
            f"ECM-001 failed: {scenario.results}"
        assert scenario.results['expected_hit_chance_with_ecm'] < scenario.results['expected_hit_chance_baseline'], \
            "ECM should reduce expected hit chance"

        logger.info(f"\nECM-001 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Hit Chance (with ECM): {scenario.results['expected_hit_chance_with_ecm']:.2%}")
        logger.info(f"  Hit Chance (baseline): {scenario.results['expected_hit_chance_baseline']:.2%}")
        logger.info(f"  Hit Rate Reduction: {scenario.results['hit_rate_reduction']:.2%}")

    def test_SENSOR_001_improves_hit_rate(self):
        """
        SENSOR-001: Sensor attack modifier improves beam hit rate.

        Expected: Hit rate with sensor > baseline hit rate.
        """
        scenario = self.runner.run_scenario(
            SensorImprovesHitRateScenario,
            headless=True
        )

        assert scenario.passed, \
            f"SENSOR-001 failed: {scenario.results}"
        assert scenario.results['expected_hit_chance_with_sensor'] > scenario.results['expected_hit_chance_baseline'], \
            "Sensor should improve expected hit chance"

        logger.info(f"\nSENSOR-001 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Hit Chance (with sensor): {scenario.results['expected_hit_chance_with_sensor']:.2%}")
        logger.info(f"  Hit Chance (baseline): {scenario.results['expected_hit_chance_baseline']:.2%}")
        logger.info(f"  Hit Rate Improvement: {scenario.results['hit_rate_improvement']:.2%}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
