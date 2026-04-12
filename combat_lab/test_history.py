"""
Test History - Sharded, Lazy-Loaded Persistent Storage for Test Run Results

One JSON file per test_id under ``combat_lab/test_history/``. Shards load on
demand and are written atomically via ``save_json`` (temp + rename). A one-shot
migration splits any legacy monolithic ``test_history.json`` into shards.

Key Features:
    - JSON-based persistence (survives app restarts)
    - Per-test-id shards (bounded file size, fault isolation)
    - Automatic history management (keeps last N runs per test)
    - Lazy load on first access per test_id
    - Atomic per-shard writes

Usage:
    ```python
    history = TestHistory()

    # After test runs
    history.add_run("BEAM360-001", scenario.results)

    # Retrieve runs (loads on first call)
    runs = history.get_runs("BEAM360-001")

    # Clear history
    history.clear_test("BEAM360-001")
    history.clear_all()
    ```
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os
import shutil
from pathlib import Path

from combat_lab.logging_config import get_logger, setup_combat_lab_logging
from game.core.json_utils import load_json, save_json

# Setup logging
setup_combat_lab_logging()
logger = get_logger(__name__)


DEFAULT_MAX_RUNS = 10


@dataclass
class TestRunRecord:
    __test__ = False  # Not a pytest test class

    """
    Record of a single test run with metrics and validation results.

    Attributes:
        timestamp: ISO format timestamp (e.g., "2026-01-14T10:30:45")
        ticks_run: Number of simulation ticks executed
        passed: Overall pass/fail status
        metrics: Test-specific metrics (damage_dealt, hit_rate, etc.)
        validation_summary: Count of pass/fail/warn validations
        validation_results: Detailed validation results with p-values
        initial_state_file: Path to JSON file with battle state at start
        final_state_file: Path to JSON file with battle state at end
        seed: Random seed used for this test run (for deterministic replay)
    """
    timestamp: str
    ticks_run: int
    passed: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    validation_summary: Optional[Dict[str, int]] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    initial_state_file: Optional[str] = None
    final_state_file: Optional[str] = None
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestRunRecord':
        """Deserialize from dictionary."""
        return cls(**data)

    @classmethod
    def from_scenario_results(cls, results: Dict[str, Any]) -> 'TestRunRecord':
        """Create record from scenario.results dictionary."""
        excluded_keys = {
            'validation_results', 'validation_summary',
            'has_validation_failures', 'has_validation_warnings',
            'initial_state_file', 'final_state_file', 'seed'
        }
        metrics = {k: v for k, v in results.items() if k not in excluded_keys}

        passed = not results.get('has_validation_failures', False)

        return cls(
            timestamp=datetime.now().isoformat(),
            ticks_run=results.get('ticks_run', 0),
            passed=passed,
            metrics=metrics,
            validation_summary=results.get('validation_summary'),
            validation_results=results.get('validation_results', []),
            initial_state_file=results.get('initial_state_file'),
            final_state_file=results.get('final_state_file'),
            seed=results.get('seed'),
        )

    def get_formatted_timestamp(self) -> str:
        """Get human-readable timestamp."""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            if dt.date() == datetime.now().date():
                return dt.strftime("%I:%M %p")
            return dt.strftime("%b %d %I:%M %p")
        except (ValueError, TypeError):
            return self.timestamp

    def get_p_value(self) -> Optional[float]:
        """Extract p-value from validation results (for statistical tests)."""
        for vr in self.validation_results:
            if 'p_value' in vr and vr['p_value'] is not None:
                return vr['p_value']
        return None

    def has_battle_states(self) -> bool:
        """Check if this run has saved battle state files."""
        if not self.initial_state_file or not self.final_state_file:
            return False
        return os.path.exists(self.initial_state_file) and os.path.exists(self.final_state_file)


class TestHistory:
    __test__ = False  # Not a pytest test class

    """
    Sharded, lazy-loading persistent test history.

    Each test_id has its own JSON file under ``history_dir``. Shards are
    loaded on demand when queried and cached in memory. ``add_run`` reads
    (if not cached), mutates, trims, and atomically rewrites just the
    affected shard.

    Attributes:
        history_dir: Directory containing per-test shard files
        history: In-memory cache: test_id -> list of records
        max_runs: Maximum number of runs kept per test_id
    """

    def __init__(self, history_dir: Optional[str] = None, max_runs: int = DEFAULT_MAX_RUNS):
        """
        Initialize sharded test history.

        Args:
            history_dir: Directory for shard files (default:
                combat_lab/test_history/).
            max_runs: Max runs kept per test_id (default: 10).
        """
        if history_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            history_dir = os.path.join(base_dir, 'combat_lab', 'test_history')

        self.history_dir: Path = Path(history_dir)
        self.max_runs: int = max_runs

        # In-memory cache (populated lazily per test_id)
        self.history: Dict[str, List[TestRunRecord]] = {}
        self._loaded: Set[str] = set()

        # Ensure shard directory exists
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # One-shot migration from the legacy monolithic file (if present)
        legacy_file = self.history_dir.parent / 'test_history.json'
        if legacy_file.exists():
            self._migrate_from_monolith(legacy_file)

    # ------------------------------------------------------------------
    # Paths and shard I/O
    # ------------------------------------------------------------------

    def _shard_path(self, test_id: str) -> Path:
        """Path to the shard file for a given test_id."""
        return self.history_dir / f"{test_id}.json"

    def _load_test(self, test_id: str) -> List[TestRunRecord]:
        """Load a shard on demand; cache the result."""
        if test_id in self._loaded:
            return self.history.get(test_id, [])

        path = self._shard_path(test_id)
        data = load_json(path, default=None)

        if data is None and path.exists():
            # Parse failure — back up the corrupt shard and start fresh
            corrupt_path = path.with_suffix(path.suffix + '.corrupt')
            try:
                shutil.copy2(path, corrupt_path)
                logger.warning(
                    f"Corrupt history shard backed up to {corrupt_path}, starting fresh for {test_id}"
                )
            except OSError:
                logger.warning(
                    f"Corrupt history shard for {test_id} could not be backed up, starting fresh"
                )
            data = []

        runs = [TestRunRecord.from_dict(r) for r in (data or [])]
        self.history[test_id] = runs
        self._loaded.add(test_id)
        return runs

    def _save_test(self, test_id: str) -> None:
        """Atomically write the shard for a given test_id."""
        data = [run.to_dict() for run in self.history.get(test_id, [])]
        path = self._shard_path(test_id)
        if not save_json(path, data):
            logger.error(f"Failed to save history shard for {test_id} to {path}")

    def _migrate_from_monolith(self, legacy_file: Path) -> None:
        """One-shot migration: split legacy test_history.json into shards.

        Reads the monolithic file, writes per-test shards, and renames the
        original to ``test_history.json.migrated`` so it is not processed
        again on next startup.
        """
        logger.info(f"Migrating legacy history file {legacy_file} to shards...")
        data = load_json(legacy_file, default=None)
        if data is None:
            logger.warning(
                f"Legacy history file {legacy_file} could not be parsed; leaving in place."
            )
            return

        migrated = 0
        for test_id, runs in data.items():
            if not isinstance(runs, list):
                continue
            shard_path = self._shard_path(test_id)
            # Don't overwrite an existing shard with legacy data
            if shard_path.exists():
                continue
            if not save_json(shard_path, runs):
                logger.error(f"Failed to migrate shard for {test_id}")
                continue
            migrated += 1

        # Rename legacy file so migration only runs once
        migrated_path = legacy_file.with_suffix(legacy_file.suffix + '.migrated')
        try:
            legacy_file.replace(migrated_path)
            logger.info(
                f"Migrated {migrated} test histories to shards; "
                f"legacy file moved to {migrated_path}"
            )
        except OSError as e:
            logger.warning(f"Legacy history file could not be renamed: {e}")

    # ------------------------------------------------------------------
    # Public API (same shape as the pre-shard TestHistory)
    # ------------------------------------------------------------------

    def add_run(self, test_id: str, results: Dict[str, Any], max_runs: Optional[int] = None) -> None:
        """
        Add a test run, keeping only the last N runs for this test_id.

        Args:
            test_id: Test identifier (e.g., "BEAM360-001")
            results: Test results dictionary from scenario.results
            max_runs: Override the configured max_runs (default: self.max_runs)
        """
        cap = max_runs if max_runs is not None else self.max_runs
        record = TestRunRecord.from_scenario_results(results)

        runs = self._load_test(test_id)
        runs.append(record)
        if len(runs) > cap:
            runs = runs[-cap:]
        self.history[test_id] = runs

        logger.info(
            f"Added run for {test_id} ({'PASS' if record.passed else 'FAIL'}), "
            f"now {len(runs)} runs"
        )
        self._save_test(test_id)

    def get_runs(self, test_id: str) -> List[TestRunRecord]:
        """Get all runs for a test (oldest to newest)."""
        return list(self._load_test(test_id))

    def get_run_count(self, test_id: str) -> int:
        """Get number of runs for a test."""
        return len(self._load_test(test_id))

    def get_latest_run(self, test_id: str) -> Optional[TestRunRecord]:
        """Get the most recent run for a test."""
        runs = self._load_test(test_id)
        return runs[-1] if runs else None

    def get_pass_rate(self, test_id: str) -> Optional[float]:
        """Calculate pass rate for a test (0.0 - 1.0), or None if no runs."""
        runs = self._load_test(test_id)
        if not runs:
            return None
        passes = sum(1 for run in runs if run.passed)
        return passes / len(runs)

    def clear_test(self, test_id: str) -> None:
        """Clear history for a specific test (delete shard + cache entry)."""
        path = self._shard_path(test_id)
        if path.exists():
            try:
                path.unlink()
            except OSError as e:
                logger.warning(f"Failed to delete shard {path}: {e}")
        self.history.pop(test_id, None)
        self._loaded.discard(test_id)
        logger.info(f"Cleared history for {test_id}")

    def clear_all(self) -> None:
        """Clear history for all tests (delete every shard)."""
        count = 0
        for shard in list(self.history_dir.glob('*.json')):
            try:
                shard.unlink()
                count += 1
            except OSError as e:
                logger.warning(f"Failed to delete shard {shard}: {e}")
        self.history.clear()
        self._loaded.clear()
        logger.info(f"Cleared all history ({count} shard files removed)")
