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
from simulation_tests.scenarios.resource_scenarios import (
    EngineFuelConsumptionScenario,
    EngineFuelDepletionScenario,
    EngineFuelRegenerationScenario,
    BeamEnergyConsumptionScenario,
    BeamEnergyDepletionScenario,
    BeamEnergyRegenerationScenario,
    ProjectileAmmoConsumptionScenario,
    ProjectileAmmoDepletionScenario,
    SeekerAmmoConsumptionScenario,
    EnergyContentionBeamRegenScenario,
)
from simulation_tests.scenarios.shield_projection_scenarios import (
    ShieldAbsorbsDamageComparisonScenario,
    ShieldDepletionOverflowScenario,
    MultipleShieldsStackScenario,
    SingleHitOverflowScenario,
    ShieldWithSufficientEnergyScenario,
    ShieldWithEnergyZeroDamageScenario,
    ShieldFailsOnEnergyDepletionScenario,
    ShieldWithoutEnergyScenario,
    ShieldWithMetalsProtects,
    ShieldWithoutMetalsNoProtection,
)
from simulation_tests.scenarios.cnc_scenarios import (
    CNCBeamDisabledScenario,
    CNCProjectileDisabledScenario,
    CNCShieldDisabledScenario,
    CNCEngineDisabledScenario,
    CNCBridgeDestroyedScenario,
    CNCBridgeRedundancyScenario,
)
from simulation_tests.scenarios.armor_layer_scenarios import (
    ArmorAbsorbsAllScenario,
    ArmorDepletesOverflowScenario,
    ArmorStackingScenario,
)
from simulation_tests.scenarios.emissive_armor_scenarios import (
    EmissiveBlocksLowDamageScenario,
    EmissiveReducesHighDamageScenario,
    EmissiveSameGroupNoStackScenario,
    EmissiveDiffGroupStackScenario,
    EmissiveNegativeValueScenario,
    EmissiveThreeSameGroupScenario,
    EmissiveExactDamageBlockScenario,
)
from simulation_tests.scenarios.shield_regen_scenarios import (
    RegenReducesNetDamageScenario,
    RegenExceedsDamageScenario,
    RegenStackingScenario,
    RegenWithFullEnergyScenario,
    RegenWithNoEnergyScenario,
    RegenStopsMidBattleScenario,
    RegenEqualsDamageRateScenario,
)
from simulation_tests.scenarios.tohit_defense_scenarios import (
    ECMReducesHitRateComparisonScenario,
    ECMSameGroupDoesNotStackScenario,
    ECMDifferentGroupsStackScenario,
    NegativeDefenseModifierScenario,
)
from simulation_tests.scenarios.tohit_attack_scenarios import (
    SensorIncreasesAccuracyScenario,
    SameGroupDoesNotStackScenario,
    DifferentGroupsStackScenario,
    NegativeModifierReducesAccuracyScenario,
    MixedModifiersNetPositiveScenario,
)
from simulation_tests.scenarios.mod_range_scenarios import (
    RangeBoostInRangeScenario,
    RangeIdentityScenario,
    RangeBoostBeyondBaseScenario,
    RangeBoostComparisonScenario,
    RangeBoostOutOfRangeScenario,
)
from simulation_tests.scenarios.damage_pipeline_scenarios import (
    PipelineShieldEmissiveScenario,
    PipelineShieldSRAScenario,
    PipelineEmissiveSRAScenario,
    PipelineFullVsNoneScenario,
    PipelineFullRegenScenario,
    PipelineSRAOverflowScenario,
)
from simulation_tests.scenarios.mod_thrust_scenarios import (
    ModThrustStaticScenario,
    ModThrustBaselineScenario,
    ModThrustDynamicVelocityScenario,
    ModThrustAccelerationScenario,
)
from simulation_tests.scenarios.mod_damage_scenarios import (
    ModDmg001_StandardBoostScenario,
    ModDmg002_IdentityBoostScenario,
    ModDmg003_MaxBoostScenario,
    ModDmg004_BoostVsBaselineScenario,
    ModDmg005_MaxVsMinScenario,
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
    'EnergyContentionBeamRegenScenario',
    # Modifier scenarios
    # Modifier - Thrust Multiplier scenarios
    'ModThrustStaticScenario',
    'ModThrustBaselineScenario',
    'ModThrustDynamicVelocityScenario',
    'ModThrustAccelerationScenario',
    # Modifier - Range Multiplier scenarios
    'RangeBoostInRangeScenario',
    'RangeIdentityScenario',
    'RangeBoostBeyondBaseScenario',
    'RangeBoostComparisonScenario',
    'RangeBoostOutOfRangeScenario',
    # Modifier - Damage Multiplier scenarios
    'ModDmg001_StandardBoostScenario',
    'ModDmg002_IdentityBoostScenario',
    'ModDmg003_MaxBoostScenario',
    'ModDmg004_BoostVsBaselineScenario',
    'ModDmg005_MaxVsMinScenario',
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
    # ShieldProjection scenarios
    'ShieldAbsorbsDamageComparisonScenario',
    'ShieldDepletionOverflowScenario',
    'MultipleShieldsStackScenario',
    'SingleHitOverflowScenario',
    'ShieldWithSufficientEnergyScenario',
    'ShieldWithEnergyZeroDamageScenario',
    'ShieldFailsOnEnergyDepletionScenario',
    'ShieldWithoutEnergyScenario',
    'ShieldWithMetalsProtects',
    'ShieldWithoutMetalsNoProtection',
    # CommandAndControl scenarios
    'CNCBeamDisabledScenario',
    'CNCProjectileDisabledScenario',
    'CNCShieldDisabledScenario',
    'CNCEngineDisabledScenario',
    'CNCBridgeDestroyedScenario',
    'CNCBridgeRedundancyScenario',
    # EmissiveArmor scenarios
    'EmissiveBlocksLowDamageScenario',
    'EmissiveReducesHighDamageScenario',
    'EmissiveSameGroupNoStackScenario',
    'EmissiveDiffGroupStackScenario',
    'EmissiveNegativeValueScenario',
    'EmissiveThreeSameGroupScenario',
    'EmissiveExactDamageBlockScenario',
    # ArmorLayer scenarios
    'ArmorAbsorbsAllScenario',
    'ArmorDepletesOverflowScenario',
    'ArmorStackingScenario',
    # ShieldRegeneration scenarios
    'RegenReducesNetDamageScenario',
    'RegenExceedsDamageScenario',
    'RegenStackingScenario',
    'RegenWithFullEnergyScenario',
    'RegenWithNoEnergyScenario',
    'RegenStopsMidBattleScenario',
    'RegenEqualsDamageRateScenario',
    # ToHitDefenseModifier scenarios
    'ECMReducesHitRateComparisonScenario',
    'ECMSameGroupDoesNotStackScenario',
    'ECMDifferentGroupsStackScenario',
    'NegativeDefenseModifierScenario',
    # ToHitAttackModifier scenarios
    'SensorIncreasesAccuracyScenario',
    'SameGroupDoesNotStackScenario',
    'DifferentGroupsStackScenario',
    'NegativeModifierReducesAccuracyScenario',
    'MixedModifiersNetPositiveScenario',
    # DamagePipeline scenarios
    'PipelineShieldEmissiveScenario',
    'PipelineShieldSRAScenario',
    'PipelineEmissiveSRAScenario',
    'PipelineFullVsNoneScenario',
    'PipelineFullRegenScenario',
    'PipelineSRAOverflowScenario',
]
