"""
Unit tests for MetadataManagementService.

Tests failure collection from ValidationReport and metadata file updates.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from test_framework.services.metadata_management_service import MetadataManagementService


class TestMetadataManagementServiceInit:
    """Test MetadataManagementService initialization."""

    def test_init(self):
        scenario_data_service = Mock()
        service = MetadataManagementService(scenario_data_service)
        assert service.scenario_data_service is scenario_data_service


class TestValidateAllScenarios:
    """Test that validate_all_scenarios returns empty (static validation removed)."""

    def test_returns_empty(self):
        service = MetadataManagementService(Mock())
        result = service.validate_all_scenarios({"TEST-001": {}})
        assert result == {}


class TestCollectValidationFailures:
    """Test collection of validation failures from new ValidationReport format."""

    def test_collect_data_phase_failures(self):
        service = MetadataManagementService(Mock())
        results = {
            'validation': {
                'checks': [
                    {'phase': 'data', 'name': 'Ship Mass', 'expected': 400, 'actual': 500, 'passed': False, 'detail': ''},
                    {'phase': 'data', 'name': 'Beam Damage', 'expected': 1, 'actual': 1, 'passed': True, 'detail': ''},
                    {'phase': 'outcome', 'name': 'Hit Rate', 'expected': 0.5, 'actual': 0.3, 'passed': False, 'detail': ''},
                ]
            }
        }
        changes = service.collect_validation_failures(results)
        # Only data-phase failures are collected (not outcome failures)
        assert len(changes) == 1
        assert changes[0]['field'] == 'Ship Mass'
        assert changes[0]['old_value'] == 400
        assert changes[0]['new_value'] == 500

    def test_collect_no_failures(self):
        service = MetadataManagementService(Mock())
        results = {
            'validation': {
                'checks': [
                    {'phase': 'data', 'name': 'Mass', 'expected': 400, 'actual': 400, 'passed': True, 'detail': ''},
                ]
            }
        }
        assert service.collect_validation_failures(results) == []

    def test_collect_empty_results(self):
        service = MetadataManagementService(Mock())
        assert service.collect_validation_failures({}) == []

    def test_collect_no_validation_key(self):
        service = MetadataManagementService(Mock())
        assert service.collect_validation_failures({'damage_dealt': 100}) == []


class TestApplyMetadataUpdates:
    """Test applying metadata updates to scenario files."""

    def test_apply_check_exact_update(self, tmp_path):
        service = MetadataManagementService(Mock())
        scenario_file = tmp_path / "test_scenario.py"
        scenario_file.write_text('checks.append(check_exact("Ship Mass", 400, self.ship.mass))\n')

        changes = [{'field': 'Ship Mass', 'old_value': 400, 'new_value': 500}]
        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        assert error is None
        assert 'check_exact("Ship Mass", 500,' in scenario_file.read_text()

    def test_apply_multiple_changes(self, tmp_path):
        service = MetadataManagementService(Mock())
        scenario_file = tmp_path / "test_scenario.py"
        scenario_file.write_text(
            'checks.append(check_exact("Ship Mass", 400, self.ship.mass))\n'
            'checks.append(check_exact("Beam Damage", 1, beam.damage))\n'
        )

        changes = [
            {'field': 'Ship Mass', 'old_value': 400, 'new_value': 500},
            {'field': 'Beam Damage', 'old_value': 1, 'new_value': 2},
        ]
        success, error = service.apply_metadata_updates(scenario_file, changes)

        assert success is True
        content = scenario_file.read_text()
        assert 'check_exact("Ship Mass", 500,' in content
        assert 'check_exact("Beam Damage", 2,' in content

    def test_apply_file_not_found(self):
        service = MetadataManagementService(Mock())
        success, error = service.apply_metadata_updates(
            Path("/nonexistent/file.py"),
            [{'field': 'Test', 'old_value': 1, 'new_value': 2}]
        )
        assert success is False
        assert error is not None

    def test_apply_empty_changes(self, tmp_path):
        service = MetadataManagementService(Mock())
        scenario_file = tmp_path / "test_scenario.py"
        scenario_file.write_text("# unchanged")
        success, error = service.apply_metadata_updates(scenario_file, [])
        assert success is True
        assert scenario_file.read_text() == "# unchanged"
