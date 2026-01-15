"""
Metadata Management Service

Handles validation of test metadata against component data and applies updates
to scenario files when expected values don't match actual values.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class MetadataManagementService:
    """Service for managing and updating test metadata."""

    def __init__(self, scenario_data_service):
        """
        Initialize metadata management service.

        Args:
            scenario_data_service: ScenarioDataService instance for data access
        """
        self.scenario_data_service = scenario_data_service

    def validate_all_scenarios(
        self,
        all_scenarios: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Validate all test scenarios against component/ship data files.

        This performs static validation without running tests, checking if
        test metadata matches actual component data.

        Args:
            all_scenarios: Dict mapping test_id to scenario_info

        Returns:
            Dict with validation results for each scenario
        """
        logger.info("\n=== Static Validation: Checking test metadata against component data ===")

        from simulation_tests.scenarios.validation import Validator

        validation_results_map = {}

        for test_id, scenario_info in all_scenarios.items():
            metadata = scenario_info['metadata']

            # Skip scenarios without validation rules
            if not metadata.validation_rules:
                continue

            # Only validate ExactMatchRules (not StatisticalTestRules which need actual test runs)
            # Check by class name instead of isinstance due to import issues
            exact_match_rules = [
                rule for rule in metadata.validation_rules
                if rule.__class__.__name__ == 'ExactMatchRule'
            ]

            if not exact_match_rules:
                continue

            try:
                # Build validation context from file data
                context = self.scenario_data_service.build_validation_context(metadata)

                if not context:
                    logger.info(f"  {test_id}: Could not build validation context")
                    continue

                # Run validation
                validator = Validator(exact_match_rules)
                validation_results = validator.validate(context)

                # Store results
                results = {
                    'validation_results': [r.to_dict() for r in validation_results],
                    'validation_summary': validator.get_summary(validation_results),
                    'has_validation_failures': validator.has_failures(validation_results),
                    'has_validation_warnings': validator.has_warnings(validation_results)
                }

                validation_results_map[test_id] = results

                # Log results
                summary = results['validation_summary']
                pass_count = summary.get('pass', 0)
                fail_count = summary.get('fail', 0)
                warn_count = summary.get('warn', 0)

                if fail_count > 0 or warn_count > 0:
                    logger.info(f"  {test_id}: {pass_count} pass, {fail_count} fail, {warn_count} warn")

            except Exception as e:
                logger.info(f"  {test_id}: Validation error - {e}")
                import traceback
                traceback.print_exc()

        logger.info("=== Static Validation Complete ===\n")

        return validation_results_map

    def collect_validation_failures(
        self,
        last_run_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Collect failed validation rules that can be auto-updated.

        Args:
            last_run_results: Last run results containing validation_results

        Returns:
            List of changes: [
                {
                    'field': 'Beam Weapon Damage',
                    'old_value': 1,
                    'new_value': 2
                },
                ...
            ]
        """
        validation_results = last_run_results.get('validation_results', [])
        if not validation_results:
            return []

        changes = []

        # Collect failed ExactMatchRules
        for vr in validation_results:
            if vr['status'] == 'FAIL' and vr['expected'] is not None and vr['actual'] is not None:
                # This is a failed exact match rule
                field_name = vr['name']
                old_value = vr['expected']
                new_value = vr['actual']

                changes.append({
                    'field': field_name,
                    'old_value': old_value,
                    'new_value': new_value
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
            # Read the file
            with open(scenario_file, 'r') as f:
                content = f.read()

            # Apply changes using string replacement
            # Update both: 1) Conditions text, 2) ExactMatchRule expected values
            for change in changes:
                field = change['field']
                old_val = change['old_value']
                new_val = change['new_value']

                # 1. Update conditions text for display
                if "Damage" in field and "Beam" in field:
                    # Update condition line like "Beam Damage: 1 per hit"
                    old_pattern = f'"Beam Damage: {old_val}'
                    new_pattern = f'"Beam Damage: {new_val}'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")
                elif "Base Accuracy" in field:
                    old_pattern = f'"Base Accuracy: {old_val}"'
                    new_pattern = f'"Base Accuracy: {new_val}"'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")
                elif "Accuracy Falloff" in field:
                    old_pattern = f'"Accuracy Falloff: {old_val}'
                    new_pattern = f'"Accuracy Falloff: {new_val}'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} → {new_val}")

                # 2. Update ExactMatchRule expected value in validation_rules
                # Find the ExactMatchRule for this field and update its expected value
                if "Damage" in field and "Beam" in field:
                    # ExactMatchRule(name='Beam Weapon Damage', path='...', expected=1)
                    old_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Base Accuracy" in field:
                    old_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Accuracy Falloff" in field:
                    old_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Weapon Range" in field or "Range" in field:
                    old_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")
                elif "Target Mass" in field or "Mass" in field:
                    old_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} → {new_val}")

            # Write back to file
            with open(scenario_file, 'w') as f:
                f.write(content)

            logger.info(f"Successfully updated {scenario_file}")

            return (True, None)

        except Exception as e:
            error_msg = f"Error updating metadata: {e}"
            logger.error(error_msg)
            import traceback
            traceback.print_exc()

            return (False, error_msg)
