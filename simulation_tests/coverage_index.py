"""
Combat Lab Coverage Index

Maps combat ability classes to their expected test scenario ID prefixes.
Provides functions to generate coverage reports by cross-referencing
the ABILITY_TO_TESTS mapping against scenarios registered in the TestRegistry.

Usage:
    from simulation_tests.coverage_index import get_coverage_report, get_uncovered_abilities

    report = get_coverage_report()
    for entry in report:
        print(f"{entry['name']}: {'covered' if entry['covered'] else 'UNCOVERED'} ({entry['test_count']} tests)")

    uncovered = get_uncovered_abilities()
    if uncovered:
        print(f"Missing coverage: {uncovered}")
"""
from typing import Dict, List

# Maps ability class names (or modifier effect names) to test ID prefixes.
# A test ID matches if it starts with any of the listed prefixes.
# When new abilities are added to the game, add entries here.
ABILITY_TO_TESTS: Dict[str, List[str]] = {
    # Weapon abilities
    'BeamWeaponAbility': ['BEAMWEAPON-'],
    'ProjectileWeaponAbility': ['PROJ360-'],
    'SeekerWeaponAbility': ['SEEK360-'],
    # Defense abilities
    'ShieldProjection': ['SHIELD-001', 'SHIELD-002'],
    'ShieldRegeneration': ['SHIELD-003'],
    'EmissiveArmor': ['ARMOR-'],
    'ToHitDefenseModifier': ['ECM-'],
    'ToHitAttackModifier': ['SENSOR-'],
    # Propulsion abilities
    'CombatPropulsion': ['PROP-'],
    'ManeuveringThruster': ['PROP-003', 'PROP-004', 'PROP-005'],
    # Resource abilities
    'ResourceConsumption': ['RESOURCE-'],
    'ResourceStorage': ['RESOURCE-'],
    'ResourceGeneration': ['RESOURCE-003', 'RESOURCE-005a'],
    # Modifier effects
    'damage_mult': ['MOD-001'],
    'range_mult': ['MOD-002'],
    'reload_mult': ['MOD-003'],
    'thrust_mult': ['MOD-004'],
    'accuracy_add': ['MOD-005'],
    'arc_set': ['MOD-006'],
}


def get_coverage_report() -> List[dict]:
    """
    Generate a coverage report by cross-referencing ABILITY_TO_TESTS
    against all scenarios registered in the TestRegistry.

    Returns:
        List of dicts, each with:
            - name: ability class or modifier effect name
            - covered: True if at least one matching test exists
            - test_ids: list of matching test IDs
            - test_count: number of matching tests
    """
    from test_framework.registry import TestRegistry

    registry = TestRegistry()
    all_scenarios = registry.get_all_scenarios()
    all_test_ids = list(all_scenarios.keys())

    report = []
    for ability_name, prefixes in ABILITY_TO_TESTS.items():
        matching_ids = []
        for test_id in all_test_ids:
            for prefix in prefixes:
                if test_id.startswith(prefix):
                    matching_ids.append(test_id)
                    break

        report.append({
            'name': ability_name,
            'covered': len(matching_ids) > 0,
            'test_ids': sorted(matching_ids),
            'test_count': len(matching_ids),
        })

    return report


def get_uncovered_abilities() -> List[str]:
    """
    Return ability class names that have zero test coverage.

    Returns:
        Sorted list of ability names with no matching test scenarios.
    """
    report = get_coverage_report()
    return sorted(entry['name'] for entry in report if not entry['covered'])
