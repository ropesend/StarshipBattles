"""
Test Lab UI Controller

Coordinates between UI and business logic services. Handles user actions
and orchestrates service calls, keeping UI rendering separate from business logic.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from test_framework.services import (
    ScenarioDataService,
    TestExecutionService,
    MetadataManagementService,
    UIStateService,
    TestResultsService
)
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class TestLabUIController:
    """Controller for Combat Lab UI, coordinating services and handling user actions."""

    def __init__(self, game, registry: TestRegistry, test_history: TestHistory):
        """
        Initialize controller with services.

        Args:
            game: Game instance for scene/engine access
            registry: TestRegistry instance
            test_history: TestHistory instance
        """
        self.game = game
        self.registry = registry

        # Initialize services
        self.scenario_data = ScenarioDataService()
        self.test_execution = TestExecutionService()
        self.ui_state = UIStateService()
        self.test_results = TestResultsService(test_history, registry)
        self.metadata_mgmt = MetadataManagementService(self.scenario_data)

        # Output log for UI display
        self.output_log: List[str] = []

        # Load all scenarios from registry
        self.all_scenarios = registry.get_all_scenarios()

        # Run static validation on startup
        self._run_static_validation()

    def _run_static_validation(self):
        """Run static validation on all scenarios at startup."""
        validation_results = self.metadata_mgmt.validate_all_scenarios(self.all_scenarios)

        # Update registry with validation results
        for test_id, results in validation_results.items():
            if test_id in self.all_scenarios:
                self.all_scenarios[test_id]['last_run_results'] = results

    def handle_category_click(self, category: str):
        """
        Handle category selection.

        Args:
            category: Category name
        """
        self.ui_state.select_category(category)

    def handle_test_click(self, test_id: str):
        """
        Handle test selection.

        Args:
            test_id: Test ID
        """
        self.ui_state.select_test(test_id)

    def handle_run_visual(self):
        """Handle visual test execution button click."""
        test_id = self.ui_state.get_selected_test_id()
        if not test_id:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            self.output_log.append(f"ERROR: Test {test_id} not found!")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name}...")

        success = self.test_execution.run_visual(
            scenario_info,
            self.game.battle_scene,
            self.game
        )

        if success:
            self.output_log.append(f"Started test {test_id}")
        else:
            self.output_log.append(f"ERROR: Failed to start test {test_id}")

    def handle_run_headless(self, on_progress=None):
        """
        Handle headless test execution button click.

        Args:
            on_progress: Optional callback(tick, max_ticks) for progress updates
        """
        test_id = self.ui_state.get_selected_test_id()
        if not test_id:
            self.output_log.append("ERROR: No test selected!")
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            self.output_log.append(f"ERROR: Test {test_id} not found!")
            return

        metadata = scenario_info['metadata']
        self.output_log.append(f"Running {metadata.name} (headless)...")

        # Mark as running
        self.ui_state.set_headless_running(True)

        # Execute test
        result = self.test_execution.run_headless(
            scenario_info,
            self.game.battle_scene.engine,
            on_progress=on_progress
        )

        # Mark as not running
        self.ui_state.set_headless_running(False)

        # Handle results
        if result['error']:
            self.output_log.append(f"ERROR: {result['error']}")
        else:
            # Add to history and update registry
            self.test_results.add_run(test_id, result['results'], update_registry=True)

            # Log status
            status = "PASSED" if result['passed'] else "FAILED"
            self.output_log.append(
                f"Test {test_id} {status} ({result['ticks_run']} ticks, {result['duration_real']:.2f}s)"
            )

        return result

    def handle_update_expected_values(self):
        """Handle update expected values button click."""
        test_id = self.ui_state.get_selected_test_id()
        if not test_id:
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return

        last_run_results = scenario_info.get('last_run_results')
        if not last_run_results:
            logger.info("No test results available. Run the test first.")
            return

        # Collect failed validation rules
        changes = self.metadata_mgmt.collect_validation_failures(last_run_results)

        if not changes:
            logger.info("No failed validation rules to update.")
            return

        return changes  # Return changes for UI to show confirmation dialog

    def apply_metadata_updates(self, changes: List[Dict[str, Any]]):
        """
        Apply metadata updates after user confirmation.

        Args:
            changes: List of changes to apply

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        test_id = self.ui_state.get_selected_test_id()
        if not test_id:
            return (False, "No test selected")

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return (False, "Test not found")

        # Get scenario file path
        scenario_file = Path(scenario_info['file'])

        # Apply updates
        success, error = self.metadata_mgmt.apply_metadata_updates(scenario_file, changes)

        if success:
            # Refresh registry to reload modified scenario
            self.registry.refresh()
            self.all_scenarios = self.registry.get_all_scenarios()
            logger.info("Registry refreshed. Metadata updated successfully!")

        return (success, error)

    def get_filtered_scenarios(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get scenarios filtered by category.

        Args:
            category: Category name or None for all scenarios

        Returns:
            Dict mapping test_id to scenario_info
        """
        if category is None:
            return self.all_scenarios

        return {
            test_id: info
            for test_id, info in self.all_scenarios.items()
            if info['metadata'].category == category
        }

    def get_ship_info(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get ship information for a test.

        Args:
            test_id: Test ID

        Returns:
            List of ship info dicts
        """
        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return []

        metadata = scenario_info['metadata']
        return self.scenario_data.extract_ships_from_scenario(metadata)

    def get_component_data(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get component data by ID.

        Args:
            component_id: Component ID

        Returns:
            Component data dict or None
        """
        return self.scenario_data.load_component_data(component_id)

    def reset_selection(self):
        """Reset all UI selections."""
        self.ui_state.reset_selection()

    def get_output_log(self) -> List[str]:
        """Get output log for UI display."""
        return self.output_log

    def clear_output_log(self):
        """Clear output log."""
        self.output_log.clear()
