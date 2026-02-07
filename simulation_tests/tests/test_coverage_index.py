"""
Coverage Index Meta-Test

This test validates that all combat-layer abilities have at least one
test scenario in the Combat Lab simulation tests. It serves as a living
checklist that fails informatively when new abilities lack coverage.

Usage:
    pytest simulation_tests/tests/test_coverage_index.py -v
"""
import pytest


@pytest.mark.simulation
class TestCoverageIndex:
    """Meta-tests for simulation test coverage completeness."""

    def test_all_combat_abilities_covered(self):
        """Asserts all combat-layer abilities have at least 1 test scenario."""
        from simulation_tests.coverage_index import get_uncovered_abilities
        uncovered = get_uncovered_abilities()
        assert len(uncovered) == 0, (
            f"The following abilities lack Combat Lab test coverage:\n"
            + "\n".join(f"  - {name}" for name in uncovered)
        )

    def test_coverage_report_has_all_entries(self):
        """Verifies coverage report includes all tracked abilities."""
        from simulation_tests.coverage_index import (
            get_coverage_report,
            ABILITY_TO_TESTS,
        )
        report = get_coverage_report()
        report_names = {entry['name'] for entry in report}
        expected_names = set(ABILITY_TO_TESTS.keys())
        assert report_names == expected_names, (
            f"Coverage report missing entries: {expected_names - report_names}"
        )

    def test_coverage_report_entries_have_correct_structure(self):
        """Verifies each coverage report entry has required fields."""
        from simulation_tests.coverage_index import get_coverage_report
        report = get_coverage_report()
        assert len(report) > 0, "Coverage report should not be empty"
        for entry in report:
            assert 'name' in entry, f"Entry missing 'name': {entry}"
            assert 'covered' in entry, f"Entry missing 'covered': {entry}"
            assert 'test_ids' in entry, f"Entry missing 'test_ids': {entry}"
            assert 'test_count' in entry, f"Entry missing 'test_count': {entry}"
            assert isinstance(entry['covered'], bool)
            assert isinstance(entry['test_ids'], list)
            assert isinstance(entry['test_count'], int)
            assert entry['test_count'] == len(entry['test_ids'])

    def test_known_abilities_are_covered(self):
        """Spot-check that known tested abilities show as covered."""
        from simulation_tests.coverage_index import get_coverage_report
        report = get_coverage_report()
        report_by_name = {e['name']: e for e in report}

        # These should definitely be covered based on existing scenarios
        must_be_covered = [
            'BeamWeaponAbility',
            'ProjectileWeaponAbility',
            'SeekerWeaponAbility',
            'CombatPropulsion',
            'ShieldProjection',
            'EmissiveArmor',
        ]
        for name in must_be_covered:
            assert name in report_by_name, f"{name} not in coverage report"
            entry = report_by_name[name]
            assert entry['covered'], (
                f"{name} should be covered but has 0 tests. "
                f"test_ids: {entry['test_ids']}"
            )
            assert entry['test_count'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
