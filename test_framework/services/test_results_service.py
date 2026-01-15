"""
Test Results Service

Wraps TestHistory and provides a clean interface for managing test results.
Integrates with registry updates and provides query capabilities for the UI.
"""

from typing import Dict, List, Any, Optional
from test_framework.test_history import TestHistory
from test_framework.registry import TestRegistry
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class TestResultsService:
    """Service for managing test results and history."""

    def __init__(self, test_history: TestHistory, registry: TestRegistry):
        """
        Initialize test results service.

        Args:
            test_history: TestHistory instance for persistent storage
            registry: TestRegistry instance for updating last run results
        """
        self.test_history = test_history
        self.registry = registry

    def add_run(
        self,
        test_id: str,
        results: Dict[str, Any],
        update_registry: bool = True
    ):
        """
        Add a test run to the history.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
            results: Test results dictionary
            update_registry: Whether to update registry with last run results
        """
        try:
            # Add to persistent test history
            self.test_history.add_run(test_id, results)

            # Update registry if requested
            if update_registry:
                self.registry.update_last_run_results(test_id, results)

            logger.debug(f"Added test run for {test_id}")

        except Exception as e:
            logger.error(f"Error adding test run: {e}")

    def get_run_history(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get run history for a test.

        Args:
            test_id: Test ID

        Returns:
            List of run records (most recent first)
        """
        try:
            return self.test_history.get_runs(test_id)
        except Exception as e:
            logger.error(f"Error getting run history: {e}")
            return []

    def get_latest_run(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent run for a test.

        Args:
            test_id: Test ID

        Returns:
            Latest run record or None if no runs exist
        """
        runs = self.get_run_history(test_id)
        return runs[0] if runs else None

    def get_run_count(self, test_id: str) -> int:
        """
        Get the number of runs for a test.

        Args:
            test_id: Test ID

        Returns:
            Number of runs
        """
        return len(self.get_run_history(test_id))

    def clear_history(self, test_id: Optional[str] = None):
        """
        Clear test history.

        Args:
            test_id: Optional test ID to clear. If None, clears all history.
        """
        try:
            if test_id:
                # Clear specific test
                self.test_history.history[test_id] = []
                self.test_history.save()
                logger.info(f"Cleared history for {test_id}")
            else:
                # Clear all
                self.test_history.clear()
                logger.info("Cleared all test history")

        except Exception as e:
            logger.error(f"Error clearing history: {e}")

    def get_all_test_ids_with_history(self) -> List[str]:
        """
        Get all test IDs that have run history.

        Returns:
            List of test IDs
        """
        return list(self.test_history.history.keys())

    def has_runs(self, test_id: str) -> bool:
        """
        Check if a test has any run history.

        Args:
            test_id: Test ID

        Returns:
            True if test has runs
        """
        return self.get_run_count(test_id) > 0

    def get_pass_rate(self, test_id: str) -> float:
        """
        Calculate pass rate for a test.

        Args:
            test_id: Test ID

        Returns:
            Pass rate (0.0-1.0) or 0.0 if no runs
        """
        runs = self.get_run_history(test_id)
        if not runs:
            return 0.0

        passed_count = sum(1 for run in runs if run.get('passed', False))
        return passed_count / len(runs)
