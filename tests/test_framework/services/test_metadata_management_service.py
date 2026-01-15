"""
Unit tests for MetadataManagementService.

Tests validation, failure collection, and metadata file updates.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from test_framework.services.metadata_management_service import MetadataManagementService
from test_framework.services.scenario_data_service import ScenarioDataService
from tests.test_framework.services.conftest import create_test_metadata


class TestMetadataManagementServiceInit:
    """Test MetadataManagementService initialization."""

    def test_init(self):
        """Test service initialization."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        assert service.scenario_data_service is scenario_data_service


class TestValidateAllScenarios:
    """Test validation of all scenarios."""

    def test_validate_all_scenarios_basic(self, temp_data_dir, sample_validation_rule):
        """Test basic validation of scenarios."""
        scenario_data_service = ScenarioDataService(data_dir=temp_data_dir)
        service = MetadataManagementService(scenario_data_service)

        metadata = create_test_metadata(
            test_id="TEST-001",
            name="Test",
            conditions=[
                "Attacker: Test_Attacker_Beam360_Low.json",
                "Target: Test_Target_Stationary.json"
            ],
            validation_rules=[sample_validation_rule]
        )

        all_scenarios = {
            "TEST-001": {
                'test_id': 'TEST-001',
                'metadata': metadata,
                'class': Mock()
            }
        }

        results = service.validate_all_scenarios(all_scenarios)

        assert "TEST-001" in results
        assert 'validation_results' in results["TEST-001"]
        assert 'validation_summary' in results["TEST-001"]
        assert 'has_validation_failures' in results["TEST-001"]

    def test_validate_all_scenarios_skip_no_rules(self):
        """Test that scenarios without rules are skipped."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        metadata = create_test_metadata(
            test_id="TEST-002",
            name="Test No Rules",
            validation_rules=[]
        )

        all_scenarios = {
            "TEST-002": {
                'test_id': 'TEST-002',
                'metadata': metadata
            }
        }

        results = service.validate_all_scenarios(all_scenarios)

        assert "TEST-002" not in results  # Should be skipped

    def test_validate_all_scenarios_skip_statistical_rules(self):
        """Test that only ExactMatchRules are validated."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        from simulation_tests.scenarios.validation import StatisticalTestRule

        stat_rule = StatisticalTestRule(
            name="Hit Rate",
            test_type="binomial",
            expected_probability=0.5,
            equivalence_margin=0.02,
            trials_expr="ticks_run",
            successes_expr="hit_count"
        )

        metadata = create_test_metadata(
            test_id="TEST-003",
            name="Test Stat Only",
            validation_rules=[stat_rule]
        )

        all_scenarios = {
            "TEST-003": {
                'test_id': 'TEST-003',
                'metadata': metadata
            }
        }

        results = service.validate_all_scenarios(all_scenarios)

        assert "TEST-003" not in results  # Should be skipped (no ExactMatchRules)

    def test_validate_all_scenarios_multiple_tests(self, temp_data_dir):
        """Test validation of multiple scenarios."""
        from simulation_tests.scenarios.validation import ExactMatchRule

        scenario_data_service = ScenarioDataService(data_dir=temp_data_dir)
        service = MetadataManagementService(scenario_data_service)

        rule1 = ExactMatchRule(name="Test1", path="attacker.mass", expected=400.0)
        rule2 = ExactMatchRule(name="Test2", path="attacker.mass", expected=400.0)

        metadata1 = create_test_metadata(
            test_id="TEST-001",
            name="Test 1",
            conditions=["Attacker: Test_Attacker_Beam360_Low.json"],
            validation_rules=[rule1]
        )

        metadata2 = create_test_metadata(
            test_id="TEST-002",
            name="Test 2",
            conditions=["Attacker: Test_Target_Stationary.json"],
            validation_rules=[rule2]
        )

        all_scenarios = {
            "TEST-001": {'test_id': 'TEST-001', 'metadata': metadata1, 'class': Mock()},
            "TEST-002": {'test_id': 'TEST-002', 'metadata': metadata2, 'class': Mock()}
        }

        results = service.validate_all_scenarios(all_scenarios)

        assert len(results) == 2
        assert "TEST-001" in results
        assert "TEST-002" in results

    def test_validate_all_scenarios_error_handling(self):
        """Test error handling during validation."""
        scenario_data_service = Mock()
        scenario_data_service.build_validation_context = Mock(side_effect=Exception("Test error"))
        service = MetadataManagementService(scenario_data_service)

        from simulation_tests.scenarios.validation import ExactMatchRule

        rule = ExactMatchRule(name="Test", path="test", expected=1)
        metadata = create_test_metadata(
            test_id="TEST-ERR",
            name="Test Error",
            validation_rules=[rule]
        )

        all_scenarios = {
            "TEST-ERR": {'test_id': 'TEST-ERR', 'metadata': metadata, 'class': Mock()}
        }

        # Should not raise exception
        results = service.validate_all_scenarios(all_scenarios)

        assert "TEST-ERR" not in results  # Failed validation not included


class TestCollectValidationFailures:
    """Test collection of validation failures."""

    def test_collect_validation_failures_basic(self):
        """Test basic failure collection."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {
            'validation_results': [
                {
                    'name': 'Beam Weapon Damage',
                    'status': 'FAIL',
                    'expected': 1,
                    'actual': 2
                }
            ]
        }

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 1
        assert changes[0]['field'] == 'Beam Weapon Damage'
        assert changes[0]['old_value'] == 1
        assert changes[0]['new_value'] == 2

    def test_collect_validation_failures_multiple(self):
        """Test collecting multiple failures."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {
            'validation_results': [
                {'name': 'Damage', 'status': 'FAIL', 'expected': 1, 'actual': 2},
                {'name': 'Range', 'status': 'FAIL', 'expected': 100, 'actual': 200},
                {'name': 'Accuracy', 'status': 'PASS', 'expected': 0.5, 'actual': 0.5}
            ]
        }

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 2  # Only failures
        assert changes[0]['field'] == 'Damage'
        assert changes[1]['field'] == 'Range'

    def test_collect_validation_failures_no_results(self):
        """Test collection when no validation results."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {}

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 0

    def test_collect_validation_failures_empty_results(self):
        """Test collection with empty results list."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {'validation_results': []}

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 0

    def test_collect_validation_failures_skip_none_values(self):
        """Test that failures with None values are skipped."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {
            'validation_results': [
                {'name': 'Test1', 'status': 'FAIL', 'expected': None, 'actual': 5},
                {'name': 'Test2', 'status': 'FAIL', 'expected': 5, 'actual': None}
            ]
        }

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 0  # Both skipped due to None

    def test_collect_validation_failures_skip_pass(self):
        """Test that passing validations are not collected."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        last_run_results = {
            'validation_results': [
                {'name': 'Test', 'status': 'PASS', 'expected': 1, 'actual': 1}
            ]
        }

        changes = service.collect_validation_failures(last_run_results)

        assert len(changes) == 0


class TestApplyMetadataUpdates:
    """Test applying metadata updates to files."""

    def test_apply_metadata_updates_beam_damage(self, tmp_path):
        """Test updating beam weapon damage."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        # Create test file
        scenario_file = tmp_path / "test_scenario.py"
        content = '''
class TestScenario:
    metadata = TestMetadata(
        conditions=[
            "Beam Damage: 1 per hit"
        ],
        validation_rules=[
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=1
            )
        ]
    )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Beam Weapon Damage', 'old_value': 1, 'new_value': 2}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        assert error is None

        # Check file was updated
        updated_content = scenario_file.read_text()
        assert '"Beam Damage: 2' in updated_content
        assert 'expected=2' in updated_content

    def test_apply_metadata_updates_base_accuracy(self, tmp_path):
        """Test updating base accuracy."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = '''
            "Base Accuracy: 0.5"
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=0.5
            )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Base Accuracy', 'old_value': 0.5, 'new_value': 0.6}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        updated_content = scenario_file.read_text()
        assert '"Base Accuracy: 0.6"' in updated_content
        assert 'expected=0.6' in updated_content

    def test_apply_metadata_updates_accuracy_falloff(self, tmp_path):
        """Test updating accuracy falloff."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = '''
            "Accuracy Falloff: 0.002 per pixel"
            ExactMatchRule(
                name='Accuracy Falloff',
                path='attacker.weapon.accuracy_falloff',
                expected=0.002
            )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Accuracy Falloff', 'old_value': 0.002, 'new_value': 0.003}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        updated_content = scenario_file.read_text()
        assert '"Accuracy Falloff: 0.003' in updated_content
        assert 'expected=0.003' in updated_content

    def test_apply_metadata_updates_weapon_range(self, tmp_path):
        """Test updating weapon range."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = '''
            ExactMatchRule(
                name='Weapon Range',
                path='attacker.weapon.range',
                expected=1000
            )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Weapon Range', 'old_value': 1000, 'new_value': 1200}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        updated_content = scenario_file.read_text()
        assert 'expected=1200' in updated_content

    def test_apply_metadata_updates_target_mass(self, tmp_path):
        """Test updating target mass."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = '''
            ExactMatchRule(
                name='Target Mass',
                path='target.mass',
                expected=400.0
            )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Target Mass', 'old_value': 400.0, 'new_value': 500.0}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        updated_content = scenario_file.read_text()
        assert 'expected=500.0' in updated_content

    def test_apply_metadata_updates_multiple_changes(self, tmp_path):
        """Test applying multiple changes at once."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = '''
            "Beam Damage: 1 per hit"
            "Base Accuracy: 0.5"
            ExactMatchRule(
                name='Beam Weapon Damage',
                path='attacker.weapon.damage',
                expected=1
            )
            ExactMatchRule(
                name='Base Accuracy',
                path='attacker.weapon.base_accuracy',
                expected=0.5
            )
'''
        scenario_file.write_text(content)

        changes = [
            {'field': 'Beam Weapon Damage', 'old_value': 1, 'new_value': 2},
            {'field': 'Base Accuracy', 'old_value': 0.5, 'new_value': 0.6}
        ]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        updated_content = scenario_file.read_text()
        assert '"Beam Damage: 2' in updated_content
        assert '"Base Accuracy: 0.6"' in updated_content
        assert 'expected=2' in updated_content
        assert 'expected=0.6' in updated_content

    def test_apply_metadata_updates_file_not_found(self):
        """Test error handling for missing file."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = Path("/nonexistent/file.py")
        changes = [{'field': 'Test', 'old_value': 1, 'new_value': 2}]

        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is False
        assert error is not None
        assert "Error updating metadata" in error

    def test_apply_metadata_updates_empty_changes(self, tmp_path):
        """Test applying empty changes list."""
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)

        scenario_file = tmp_path / "test_scenario.py"
        content = "# Test file"
        scenario_file.write_text(content)

        success, error = service.apply_metadata_updates(scenario_file, [])

        assert success is True
        assert error is None
        assert scenario_file.read_text() == content  # Unchanged
