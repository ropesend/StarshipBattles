"""
Validation management for TestLabScreen.

This module contains static validation logic with minimal UI dependencies:
- TestLabValidationManager: Validates test scenarios against component data,
  handles expected value updates, and applies metadata changes

Extracted from screen.py to reduce file size and improve testability.
"""
import json

from simulation_tests.logging_config import get_logger
from .dialogs import ConfirmationDialog

logger = get_logger(__name__)


class TestLabValidationManager:
    """
    Handles validation operations for TestLabScreen.

    Validates test scenarios against component/ship JSON data and manages
    expected value updates when validation fails.
    """

    def __init__(self, registry, data_extractor, scenarios_getter):
        """
        Initialize the validation manager.

        Args:
            registry: TestRegistry instance for looking up test scenarios
            data_extractor: TestLabDataExtractor instance for loading ship/component data
            scenarios_getter: Callable that returns the current all_scenarios dict
        """
        self.registry = registry
        self.data_extractor = data_extractor
        self._get_scenarios = scenarios_getter

    def validate_all(self):
        """
        Validate all test scenarios against component/ship data files.

        This performs static validation without running tests, checking if
        test metadata matches actual component data.
        """
        logger.info("\n=== Static Validation: Checking test metadata against component data ===")

        from simulation_tests.scenarios.validation import Validator

        all_scenarios = self._get_scenarios()

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
                context = self.build_context_from_files(test_id, metadata)

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

                # Update registry with validation results
                scenario_info['last_run_results'] = results

                # Log results
                summary = results['validation_summary']
                pass_count = summary.get('pass', 0)
                fail_count = summary.get('fail', 0)
                warn_count = summary.get('warn', 0)

                if fail_count > 0 or warn_count > 0:
                    logger.info(f"  {test_id}: {pass_count} pass, {fail_count} fail, {warn_count} warn")

            except (OSError, ValueError, KeyError, json.JSONDecodeError) as e:
                logger.info(f"  {test_id}: Validation error - {e}")

        logger.info("=== Static Validation Complete ===\n")

    def build_context_from_files(self, test_id, metadata):
        """
        Build validation context from ship and component JSON files.

        Args:
            test_id: Test ID
            metadata: TestMetadata object

        Returns:
            Dict with 'attacker', 'target', etc. containing component data
        """
        context = {}

        # Parse conditions for ship files
        ships = self.data_extractor.extract_ships(test_id)

        for ship_info in ships:
            role = ship_info['role'].lower()  # 'Attacker' -> 'attacker'
            ship_data = ship_info['ship_data']
            component_ids = ship_info['component_ids']

            # Build ship validation data structure
            ship_validation_data = {
                'mass': ship_data.get('expected_stats', {}).get('mass', 0)
            }

            # Extract weapon data from first component with BeamWeaponAbility
            components_cache = self.data_extractor._components_cache
            if components_cache is None:
                # Load components.json
                self.data_extractor.load_component("dummy")  # This will populate cache
                components_cache = self.data_extractor._components_cache

            for comp_id in component_ids:
                comp_data = components_cache.get(comp_id) if components_cache else None
                if comp_data and 'abilities' in comp_data:
                    abilities = comp_data['abilities']

                    # Check for BeamWeaponAbility
                    if 'BeamWeaponAbility' in abilities:
                        weapon_ability = abilities['BeamWeaponAbility']
                        ship_validation_data['weapon'] = {
                            'damage': weapon_ability.get('damage'),
                            'range': weapon_ability.get('range'),
                            'base_accuracy': weapon_ability.get('base_accuracy'),
                            'accuracy_falloff': weapon_ability.get('accuracy_falloff'),
                            'reload': weapon_ability.get('reload'),
                            'firing_arc': weapon_ability.get('firing_arc')
                        }
                        break  # Found weapon, use first one

            context[role] = ship_validation_data

        return context

    def handle_update_expected_values(self, selected_test_id, ui_manager, screen_width, screen_height):
        """
        Handle click on Update Expected Values button.

        Args:
            selected_test_id: Currently selected test ID
            ui_manager: pygame_gui UIManager for dialogs
            screen_width: Screen width for dialog positioning
            screen_height: Screen height for dialog positioning

        Returns:
            ConfirmationDialog if there are changes to confirm, None otherwise
        """
        if not selected_test_id:
            return None

        # Get the scenario and its last run results
        scenario_info = self.registry.get_by_id(selected_test_id)
        if not scenario_info:
            return None

        last_run_results = scenario_info.get('last_run_results')
        if not last_run_results:
            logger.info("No test results available. Run the test first.")
            return None

        validation_results = last_run_results.get('validation_results', [])
        if not validation_results:
            return None

        # Collect failed ExactMatchRules
        changes = []
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

        if not changes:
            logger.info("No failed validation rules to update.")
            return None

        # Show confirmation dialog
        return ConfirmationDialog(
            title="Update Expected Values",
            changes=changes,
            screen_width=screen_width,
            screen_height=screen_height,
            on_confirm=lambda: self.apply_metadata_updates(changes, selected_test_id),
            on_cancel=lambda: logger.info("Update canceled"),
            ui_manager=ui_manager
        )

    def apply_metadata_updates(self, changes, selected_test_id=None):
        """
        Apply metadata updates to the test scenario file.

        Args:
            changes: List of dicts with 'field', 'old_value', 'new_value'
            selected_test_id: Test ID to update (optional, for callback usage)
        """
        if not selected_test_id:
            return

        scenario_info = self.registry.get_by_id(selected_test_id)
        if not scenario_info:
            return

        # Get the file path for the scenario
        scenario_file = scenario_info['file']

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
                    logger.info(f"Updated condition text for {field}: {old_val} -> {new_val}")
                elif "Base Accuracy" in field:
                    old_pattern = f'"Base Accuracy: {old_val}"'
                    new_pattern = f'"Base Accuracy: {new_val}"'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} -> {new_val}")
                elif "Accuracy Falloff" in field:
                    old_pattern = f'"Accuracy Falloff: {old_val}'
                    new_pattern = f'"Accuracy Falloff: {new_val}'
                    content = content.replace(old_pattern, new_pattern)
                    logger.info(f"Updated condition text for {field}: {old_val} -> {new_val}")

                # 2. Update ExactMatchRule expected value in validation_rules
                if "Damage" in field and "Beam" in field:
                    # ExactMatchRule(name='Beam Weapon Damage', path='...', expected=1)
                    old_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Beam Weapon Damage',\n                path='attacker.weapon.damage',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} -> {new_val}")
                elif "Base Accuracy" in field:
                    old_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Base Accuracy',\n                path='attacker.weapon.base_accuracy',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} -> {new_val}")
                elif "Accuracy Falloff" in field:
                    old_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Accuracy Falloff',\n                path='attacker.weapon.accuracy_falloff',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} -> {new_val}")
                elif "Weapon Range" in field or "Range" in field:
                    old_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Weapon Range',\n                path='attacker.weapon.range',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} -> {new_val}")
                elif "Target Mass" in field or "Mass" in field:
                    old_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={old_val}\n            )"
                    new_rule = f"ExactMatchRule(\n                name='Target Mass',\n                path='target.mass',\n                expected={new_val}\n            )"
                    content = content.replace(old_rule, new_rule)
                    logger.info(f"Updated ExactMatchRule for {field}: expected={old_val} -> {new_val}")

            # Write back to file
            with open(scenario_file, 'w') as f:
                f.write(content)

            logger.info(f"Successfully updated {scenario_file}")

            # Refresh the registry to reload the modified scenario
            self.registry.refresh()

            logger.info("Registry refreshed. Metadata updated successfully!")

        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Error updating metadata: {e}")
