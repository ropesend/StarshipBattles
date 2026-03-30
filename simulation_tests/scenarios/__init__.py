"""
Test Scenarios Module

This module provides the infrastructure for creating test scenarios that work
identically in both pytest (headless) and Combat Lab (visual) environments.

Key Components:
    - TestScenario: Base class for all test scenarios
    - TestMetadata: Rich metadata for test documentation and UI

Usage:
    from simulation_tests.scenarios import TestScenario, TestMetadata

    class MyTest(TestScenario):
        metadata = TestMetadata(
            test_id="TEST-001",
            category="MyCategory",
            subcategory="MySubcategory",
            name="My test",
            summary="What this test validates",
            conditions=["Test condition 1", "Test condition 2"],
            edge_cases=["Edge case 1"],
            expected_outcome="What should happen",
            pass_criteria="How we verify success"
        )

        def setup(self, battle_engine):
            # Setup test
            pass

        def verify(self, battle_engine):
            # Verify results
            return True
"""

from simulation_tests.scenarios.base import TestScenario, TestMetadata
from simulation_tests.scenarios.validation import (
    Check,
    ValidationReport,
    check_exact,
    check_approx,
    check_tost,
    check_true,
)
from simulation_tests.scenarios.defense_scenarios import (
    ShieldAbsorbsDamageScenario,
    ShieldOverflowToHullScenario,
    ShieldRegenerationScenario,
    EmissiveArmorBlocksLowDamageScenario,
    EmissiveArmorReducesHighDamageScenario,
    ECMReducesHitRateScenario,
    SensorImprovesHitRateScenario,
    SensorDamageComparisonScenario,
)
from simulation_tests.scenarios.resource_scenarios import (
    EngineFuelConsumptionScenario,
    EngineFuelDepletionScenario,
    EngineFuelRegenerationScenario,
    BeamEnergyConsumptionScenario,
    BeamEnergyDepletionScenario,
    BeamEnergyRegenerationScenario,
    ProjectileAmmoConsumptionScenario,
    ProjectileAmmoDepletionScenario,
    SeekerAmmoConsumptionScenario
)
from simulation_tests.scenarios.modifier_scenarios import (
    DamageMultiplierScenario,
    RangeMultiplierScenario,
    ReloadReductionScenario,
    ThrustMultiplierScenario,
    AccuracyBoostScenario,
    TurretArcSetScenario,
)
from simulation_tests.scenarios.tohit_attack_scenarios import (
    SensorIncreasesAccuracyScenario,
    SameGroupDoesNotStackScenario,
    DifferentGroupsStackScenario,
    NegativeModifierReducesAccuracyScenario,
)
from simulation_tests.scenarios.propulsion_scenarios import (
    PropEngineAccelerationScenario,
    PropDualEngineScenario,
    PropThrustMassRatioScenario,
    PropThrusterTurnRateScenario,
    PropThrusterRotationScenario,
    PropDualThrusterScenario,
    PropNoEngineStationaryScenario,
    PropThrusterOnlyScenario,
    PropMassAffectsTurnRateScenario,
)

__all__ = [
    'TestScenario',
    'TestMetadata',
    'Check',
    'ValidationReport',
    'check_exact',
    'check_approx',
    'check_tost',
    'check_true',
    # Defense scenarios
    'ShieldAbsorbsDamageScenario',
    'ShieldOverflowToHullScenario',
    'ShieldRegenerationScenario',
    'EmissiveArmorBlocksLowDamageScenario',
    'EmissiveArmorReducesHighDamageScenario',
    'ECMReducesHitRateScenario',
    'SensorImprovesHitRateScenario',
    'SensorDamageComparisonScenario',
    # Resource scenarios
    'EngineFuelConsumptionScenario',
    'EngineFuelDepletionScenario',
    'EngineFuelRegenerationScenario',
    'BeamEnergyConsumptionScenario',
    'BeamEnergyDepletionScenario',
    'BeamEnergyRegenerationScenario',
    'ProjectileAmmoConsumptionScenario',
    'ProjectileAmmoDepletionScenario',
    'SeekerAmmoConsumptionScenario',
    # Modifier scenarios
    'DamageMultiplierScenario',
    'RangeMultiplierScenario',
    'ReloadReductionScenario',
    'ThrustMultiplierScenario',
    'AccuracyBoostScenario',
    'TurretArcSetScenario',
    # Propulsion scenarios
    'PropEngineAccelerationScenario',
    'PropDualEngineScenario',
    'PropThrustMassRatioScenario',
    'PropThrusterTurnRateScenario',
    'PropThrusterRotationScenario',
    'PropDualThrusterScenario',
    'PropNoEngineStationaryScenario',
    'PropThrusterOnlyScenario',
    'PropMassAffectsTurnRateScenario',
    # ToHitAttackModifier scenarios
    'SensorIncreasesAccuracyScenario',
    'SameGroupDoesNotStackScenario',
    'DifferentGroupsStackScenario',
    'NegativeModifierReducesAccuracyScenario',
]
