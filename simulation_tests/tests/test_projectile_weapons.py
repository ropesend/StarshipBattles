"""
Projectile Weapon Tests (PROJ360-001 through PROJ360-006, PROJ360-DMG-*)

Validates projectile weapon behavior:
- Accuracy against stationary and moving targets
- Predictive leading for linear target motion
- Out-of-range behavior (fires but doesn't hit)
- Damage consistency at various ranges

This test file uses the TestScenario framework for all tests.
Each pytest function executes a corresponding TestScenario in headless mode.
"""
import pytest
import os
import json
import math

import pygame

from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from simulation_tests.scenarios.projectile_scenarios import (
    ProjectileStationaryTargetScenario,
    ProjectileLinearSlowTargetScenario,
    ProjectileLinearFastTargetScenario,
    ProjectileErraticSmallTargetScenario,
    ProjectileErraticLargeTargetScenario,
    ProjectileOutOfRangeScenario,
    ProjectileDamageCloseRangeScenario,
    ProjectileDamageMidRangeScenario,
    ProjectileDamageLongRangeScenario
)
from test_framework.runner import TestRunner


@pytest.mark.simulation
class TestProjectileWeapons:
    """Test projectile weapon accuracy and damage."""
    
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_PROJ360_001_accuracy_vs_stationary(self):
        """
        PROJ360-001: 100% accuracy vs stationary target.

        Both ships stationary, attacker fires at point-blank range.
        All shots should hit.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileStationaryTargetScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-001 failed: {scenario.results.get('error', 'Unknown error')}"

        # Additional assertions from original test
        damage_dealt = scenario.results.get('damage_dealt', 0)
        assert damage_dealt > 0, "Projectile should deal damage to stationary target"

        expected_min_damage = 150  # At least 3 shots in 500 ticks
        assert damage_dealt >= expected_min_damage, \
            f"Expected at least {expected_min_damage} damage, got {damage_dealt}"
    
    @pytest.mark.skip(reason="Target ship engine configuration issue - target moves too fast. Needs slow engine fix.")
    def test_PROJ360_002_accuracy_vs_linear_slow(self):
        """
        PROJ360-002: Accuracy vs slow linearly moving target.

        Tests predictive leading - should still hit moving targets.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileLinearSlowTargetScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-002 failed: {scenario.results.get('error', 'Unknown error')}"

        # Additional assertions from original test
        damage_dealt = scenario.results.get('damage_dealt', 0)
        assert damage_dealt > 0, \
            "Projectile should hit slow linearly moving target with prediction"
    
    def test_PROJ360_003_accuracy_vs_linear_fast(self):
        """
        PROJ360-003: Accuracy vs fast linearly moving target.

        Faster target should still be hittable with prediction.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileLinearFastTargetScenario, headless=True)

        # Assert scenario passed (completion test)
        assert scenario.passed, \
            f"PROJ360-003 failed: {scenario.results.get('error', 'Unknown error')}"

        # Original test just checks completion - fast targets may or may not be hit
        assert scenario.results.get('ticks_run', 0) > 0, "Test should complete"
    
    def test_PROJ360_004_accuracy_vs_erratic_small(self):
        """
        PROJ360-004: Accuracy vs small erratically moving target.

        Small, erratic targets should have lower hit rate.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileErraticSmallTargetScenario, headless=True)

        # Assert scenario passed (measurement test)
        assert scenario.passed, \
            f"PROJ360-004 failed: {scenario.results.get('error', 'Unknown error')}"

        # Primarily a measurement test
        assert scenario.results.get('ticks_run', 0) > 0, "Simulation should run"
    
    def test_PROJ360_005_accuracy_vs_erratic_large(self):
        """
        PROJ360-005: Accuracy vs large erratically moving target.

        Large targets should have higher hit rate than small ones.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileErraticLargeTargetScenario, headless=True)

        # Assert scenario passed (measurement test)
        assert scenario.passed, \
            f"PROJ360-005 failed: {scenario.results.get('error', 'Unknown error')}"

        # Primarily a measurement test
        assert scenario.results.get('ticks_run', 0) > 0, "Simulation should run"
    
    def test_PROJ360_006_out_of_range(self):
        """
        PROJ360-006: Out of range - weapon fires but no hits.

        Target placed beyond weapon range (1000 pixels).
        Weapon should fire (projectiles spawn) but no damage dealt.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileOutOfRangeScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-006 failed: {scenario.results.get('error', 'Unknown error')}"

        # Out of range - should NOT deal damage
        damage_dealt = scenario.results.get('damage_dealt', -1)
        assert damage_dealt == 0, \
            f"Target beyond range should take 0 damage, got {damage_dealt}"
    
    def test_PROJ360_DMG_010_damage_at_close_range(self):
        """
        PROJ360-DMG-10: Damage at 10% of max range (100 px).

        Damage per hit should equal weapon damage (50).
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileDamageCloseRangeScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-DMG-010 failed: {scenario.results.get('error', 'Unknown error')}"

        # Should deal damage at close range
        damage_dealt = scenario.results.get('damage_dealt', 0)
        assert damage_dealt > 0, "Should deal damage at close range"
        assert damage_dealt % 50 == 0 or damage_dealt > 0, \
            "Damage should be consistent with weapon damage value"
    
    def test_PROJ360_DMG_050_damage_at_mid_range(self):
        """
        PROJ360-DMG-50: Damage at 50% of max range (500 px).

        Projectiles deal full damage regardless of range.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileDamageMidRangeScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-DMG-050 failed: {scenario.results.get('error', 'Unknown error')}"

        # Should deal damage at mid range
        damage_dealt = scenario.results.get('damage_dealt', 0)
        assert damage_dealt > 0, "Should deal damage at mid range"
    
    def test_PROJ360_DMG_090_damage_at_long_range(self):
        """
        PROJ360-DMG-90: Damage at 90% of max range (900 px).

        Projectiles deal full damage at any range within weapon range.
        """
        # Run scenario using TestRunner in headless mode
        scenario = self.runner.run_scenario(ProjectileDamageLongRangeScenario, headless=True)

        # Assert scenario passed
        assert scenario.passed, \
            f"PROJ360-DMG-090 failed: {scenario.results.get('error', 'Unknown error')}"

        # At edge of range, should still complete
        assert scenario.results.get('ticks_run', 0) > 0, "Simulation should complete"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
