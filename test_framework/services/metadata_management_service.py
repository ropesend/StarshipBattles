"""
Metadata Management Service

Collects validation failures from test results and applies updates
to scenario files when expected values don't match actual values.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class MetadataManagementService:
    """Service for managing and updating test metadata."""

    def __init__(self, scenario_data_service):
        self.scenario_data_service = scenario_data_service

    def validate_all_scenarios(
        self,
        all_scenarios: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Static validation is no longer supported.

        Validation now happens at runtime via scenario.validate().
        This method returns an empty dict for backward compatibility.
        """
        return {}

    def collect_validation_failures(
        self,
        last_run_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Collect failed validation checks from the new ValidationReport.

        Args:
            last_run_results: Results dict containing 'validation' key.

        Returns:
            List of changes: [{'field': name, 'old_value': expected, 'new_value': actual}]
        """
        report = last_run_results.get('validation', {})
        checks = report.get('checks', [])

        changes = []
        for check in checks:
            if not check['passed'] and check['phase'] == 'data':
                changes.append({
                    'field': check['name'],
                    'old_value': check['expected'],
                    'new_value': check['actual'],
                })

        return changes

    def apply_metadata_updates(
        self,
        scenario_file: Path,
        changes: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Apply metadata updates to a test scenario file.

        Args:
            scenario_file: Path to scenario Python file
            changes: List of dicts with 'field', 'old_value', 'new_value'

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with open(scenario_file, 'r') as f:
                content = f.read()

            for change in changes:
                field = change['field']
                old_val = change['old_value']
                new_val = change['new_value']

                # Update check_exact expected values in validate() methods
                old_pattern = f'check_exact("{field}", {old_val},'
                new_pattern = f'check_exact("{field}", {new_val},'
                content = content.replace(old_pattern, new_pattern)
                logger.info(f"Updated {field}: {old_val} -> {new_val}")

            with open(scenario_file, 'w') as f:
                f.write(content)

            return (True, None)

        except Exception as e:
            error_msg = f"Error updating metadata: {e}"
            logger.error(error_msg)
            return (False, error_msg)
