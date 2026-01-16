"""
Test History - Persistent Storage for Test Run Results

This module provides persistent storage for test run history, allowing users
to track test results across multiple sessions and compare performance over time.

Key Features:
    - JSON-based persistence (survives app restarts)
    - Automatic history management (keeps last N runs per test)
    - Flexible metric storage (supports different test types)
    - Validation result tracking with p-values

Architecture:
    TestRunRecord - Single test run with timestamp, metrics, validation results
    TestHistory - Manages collection of runs per test with JSON persistence

Usage:
    ```python
    history = TestHistory()

    # After test runs
    history.add_run("BEAM360-001", scenario.results)

    # Retrieve runs
    runs = history.get_runs("BEAM360-001")
    for run in runs:
        print(f"{run.timestamp}: {'PASS' if run.passed else 'FAIL'}")

    # Clear history
    history.clear_test("BEAM360-001")
    history.clear_all()
    ```
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os
from simulation_tests.logging_config import get_logger, setup_combat_lab_logging
from game.core.json_utils import load_json, save_json

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)


@dataclass
class TestRunRecord:
    """
    Record of a single test run with metrics and validation results.

    Attributes:
        timestamp: ISO format timestamp (e.g., "2026-01-14T10:30:45")
        ticks_run: Number of simulation ticks executed
        passed: Overall pass/fail status
        metrics: Test-specific metrics (damage_dealt, hit_rate, etc.)
        validation_summary: Count of pass/fail/warn validations
        validation_results: Detailed validation results with p-values
    """
    timestamp: str
    ticks_run: int
    passed: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    validation_summary: Optional[Dict[str, int]] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestRunRecord':
        """Deserialize from dictionary."""
        return cls(**data)

    @classmethod
    def from_scenario_results(cls, results: Dict[str, Any]) -> 'TestRunRecord':
        """
        Create record from scenario.results dictionary.

        Args:
            results: Dictionary from TestScenario.results after test execution

        Returns:
            TestRunRecord with extracted metrics and validation results
        """
        # Extract metrics (exclude validation-specific keys)
        excluded_keys = {
            'validation_results', 'validation_summary',
            'has_validation_failures', 'has_validation_warnings'
        }
        metrics = {
            k: v for k, v in results.items()
            if k not in excluded_keys
        }

        # Determine pass/fail status
        # A test passes if it has no validation failures
        passed = not results.get('has_validation_failures', False)

        return cls(
            timestamp=datetime.now().isoformat(),
            ticks_run=results.get('ticks_run', 0),
            passed=passed,
            metrics=metrics,
            validation_summary=results.get('validation_summary'),
            validation_results=results.get('validation_results', [])
        )

    def get_formatted_timestamp(self) -> str:
        """
        Get human-readable timestamp.

        Returns:
            Formatted string like "10:30 AM" or "Jan 14 10:30"
        """
        try:
            dt = datetime.fromisoformat(self.timestamp)
            # Today: show time only
            if dt.date() == datetime.now().date():
                return dt.strftime("%I:%M %p")
            # Other days: show date and time
            return dt.strftime("%b %d %I:%M %p")
        except (ValueError, TypeError):
            return self.timestamp

    def get_p_value(self) -> Optional[float]:
        """
        Extract p-value from validation results (for statistical tests).

        Returns:
            P-value if found, None otherwise
        """
        for vr in self.validation_results:
            if 'p_value' in vr and vr['p_value'] is not None:
                return vr['p_value']
        return None


class TestHistory:
    """
    Manages persistent test run history with JSON storage.

    Attributes:
        history_file: Path to JSON file storing test history
        history: Dict mapping test_id to list of TestRunRecord
    """

    def __init__(self, history_file: str = None):
        """
        Initialize test history manager.

        Args:
            history_file: Path to JSON file (default: simulation_tests/test_history.json)
        """
        if history_file is None:
            # Default to simulation_tests/test_history.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            history_file = os.path.join(base_dir, 'simulation_tests', 'test_history.json')

        self.history_file = history_file
        self.history: Dict[str, List[TestRunRecord]] = {}
        self._load()

    def _load(self):
        """Load history from JSON file."""
        data = load_json(self.history_file, default=None)
        if data is None:
            logger.info("No existing history file found, starting fresh")
            return

        # Convert dicts back to TestRunRecord objects
        for test_id, runs in data.items():
            self.history[test_id] = [
                TestRunRecord.from_dict(run) for run in runs
            ]
        logger.info(f"Loaded {len(self.history)} test histories from {self.history_file}")

    def _save(self):
        """Save history to JSON file."""
        # Convert to serializable format
        data = {
            test_id: [run.to_dict() for run in runs]
            for test_id, runs in self.history.items()
        }

        if save_json(self.history_file, data):
            logger.debug(f"Saved {sum(len(runs) for runs in self.history.values())} total runs")
        else:
            logger.error(f"Failed to save test history to {self.history_file}")

    def add_run(self, test_id: str, results: Dict[str, Any], max_runs: int = 10):
        """
        Add test run to history, keeping only last N runs.

        Args:
            test_id: Test identifier (e.g., "BEAM360-001")
            results: Test results dictionary from scenario.results
            max_runs: Maximum number of runs to keep per test (default: 10)
        """
        record = TestRunRecord.from_scenario_results(results)

        if test_id not in self.history:
            self.history[test_id] = []

        # Append new run
        self.history[test_id].append(record)

        # Keep only last N runs
        if len(self.history[test_id]) > max_runs:
            self.history[test_id] = self.history[test_id][-max_runs:]

        logger.info(f"Added run for {test_id} ({'PASS' if record.passed else 'FAIL'}), now {len(self.history[test_id])} runs")

        self._save()

    def get_runs(self, test_id: str) -> List[TestRunRecord]:
        """
        Get all runs for a test (newest last).

        Args:
            test_id: Test identifier

        Returns:
            List of TestRunRecord, ordered oldest to newest
        """
        return self.history.get(test_id, [])

    def get_run_count(self, test_id: str) -> int:
        """
        Get number of runs for a test.

        Args:
            test_id: Test identifier

        Returns:
            Number of runs recorded
        """
        return len(self.history.get(test_id, []))

    def clear_test(self, test_id: str):
        """
        Clear history for specific test.

        Args:
            test_id: Test identifier
        """
        if test_id in self.history:
            run_count = len(self.history[test_id])
            del self.history[test_id]
            logger.info(f"Cleared {run_count} runs for {test_id}")
            self._save()

    def clear_all(self):
        """Clear all test history."""
        total_runs = sum(len(runs) for runs in self.history.values())
        self.history = {}
        logger.info(f"Cleared all history ({total_runs} total runs)")
        self._save()

    def get_latest_run(self, test_id: str) -> Optional[TestRunRecord]:
        """
        Get most recent run for a test.

        Args:
            test_id: Test identifier

        Returns:
            Latest TestRunRecord or None if no runs
        """
        runs = self.get_runs(test_id)
        return runs[-1] if runs else None

    def get_pass_rate(self, test_id: str) -> Optional[float]:
        """
        Calculate pass rate for a test.

        Args:
            test_id: Test identifier

        Returns:
            Pass rate (0.0 to 1.0) or None if no runs
        """
        runs = self.get_runs(test_id)
        if not runs:
            return None

        passes = sum(1 for run in runs if run.passed)
        return passes / len(runs)
