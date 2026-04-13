"""
Test Scenarios Module

This module provides the infrastructure for creating test scenarios that work
identically in both pytest (headless) and Combat Lab (visual) environments.

Concrete scenario classes live in sibling modules (``beam_scenarios``,
``projectile_scenarios``, ``shield_projection_scenarios``, etc.) and are
discovered dynamically by ``combat_lab.registry.TestRegistry``. They do not
need to be re-exported here — author new scenario classes by subclassing
``TestScenario`` (or a template) and defining a ``metadata`` attribute.

Usage (PROJ-270 post-unified-entry contract):
    from combat_lab.scenarios import StaticTargetScenario, TestMetadata
    from combat_lab.scenarios.validation import check_true

    class MyTest(StaticTargetScenario):
        metadata = TestMetadata(
            test_id="TEST-001",
            category="MyCategory",
            subcategory="MySubcategory",
            name="My test",
            summary="What this test validates",
            conditions=["Test condition 1"],
            edge_cases=["Edge case 1"],
            expected_outcome="What should happen",
            pass_criteria="How we verify success",
        )

        attacker_ship = 'Test_Attacker.json'
        target_ship = 'Test_Target.json'
        distance = 100

        def validate(self, outcome, telemetry=None):
            return [check_true("Something happened", True, phase="outcome")]
"""

from combat_lab.scenarios.base import TestScenario, TestMetadata
from combat_lab.scenarios.validation import (
    Check,
    ValidationReport,
    check_exact,
    check_approx,
    check_tost,
    check_true,
)
from combat_lab.scenarios.templates import (
    StaticTargetScenario,
    DuelScenario,
    PropulsionScenario,
    ResourceScenario,
    ComparisonScenario,
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
    'StaticTargetScenario',
    'DuelScenario',
    'PropulsionScenario',
    'ResourceScenario',
    'ComparisonScenario',
]
