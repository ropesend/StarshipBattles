"""
Test Lab UI Controller

Coordinates between UI and business logic services. Handles user actions
and orchestrates service calls, keeping UI rendering separate from business logic.
"""

from typing import Optional, List, Dict, Any
from combat_lab.services import (
    ScenarioDataService,
    UIStateService,
)
from combat_lab.registry import TestRegistry
from combat_lab.test_history import TestHistory
from combat_lab.logging_config import get_logger

logger = get_logger(__name__)


class TestLabUIController:
    __test__ = False  # Not a pytest test class

    """Controller for Combat Lab UI, coordinating services and handling user actions."""

    def __init__(self, registry: TestRegistry, test_history: TestHistory) -> None:
        """
        Initialize controller with services.

        Args:
            registry: TestRegistry instance
            test_history: TestHistory instance
        """
        self.registry = registry

        # Initialize services
        self.scenario_data = ScenarioDataService()
        self.ui_state = UIStateService()

        # Output log for UI display
        self.output_log: List[str] = []

        # Load all scenarios from registry
        self.all_scenarios = registry.get_all_scenarios()

        # Load historical results so status dots show on startup
        self._load_history_into_registry(test_history)

    def _load_history_into_registry(self, test_history: TestHistory):
        """Load latest run results from history into registry for status display.

        Without this, the pass/fail dots in the test list are empty until
        a test is run in the current session.
        """
        loaded = 0
        for test_id in self.all_scenarios:
            latest = test_history.get_latest_run(test_id)
            if latest is not None:
                self.registry.update_last_run_results(test_id, latest.to_dict())
                loaded += 1
        if loaded:
            logger.debug(f"Loaded {loaded} test histories from prior runs")

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
