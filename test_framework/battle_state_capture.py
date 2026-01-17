"""
Battle State Capture - Save battle states for test run analysis.

This module provides utilities to capture and save battle states (initial and final)
when running combat tests. The saved JSON files can be viewed side-by-side in the
Combat Lab UI to understand what happened during a test.
"""
import os
import json
from datetime import datetime
from typing import Optional, Tuple, TYPE_CHECKING

from game.simulation.battle_state import BattleState
from game.core.logger import log_debug, log_warning

if TYPE_CHECKING:
    from game.simulation.systems.battle_engine import BattleEngine


# Directory where battle state files are stored
BATTLE_STATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'simulation_tests',
    'battle_states'
)


def ensure_states_dir() -> str:
    """Ensure the battle states directory exists."""
    os.makedirs(BATTLE_STATES_DIR, exist_ok=True)
    return BATTLE_STATES_DIR


def generate_state_filename(test_id: str, timestamp: str, state_type: str) -> str:
    """
    Generate a unique filename for a battle state file.

    Args:
        test_id: Test identifier (e.g., "BEAM360-001")
        timestamp: ISO format timestamp
        state_type: "initial" or "final"

    Returns:
        Filename like "BEAM360-001_2026-01-17T10-30-45_initial.json"
    """
    # Clean timestamp for filename (replace colons with dashes)
    safe_timestamp = timestamp.replace(':', '-').replace('.', '-')
    return f"{test_id}_{safe_timestamp}_{state_type}.json"


def capture_battle_state(
    engine: 'BattleEngine',
    test_id: str,
    state_type: str,
    seed: Optional[int] = None
) -> Optional[str]:
    """
    Capture current battle state and save to JSON file.

    Args:
        engine: BattleEngine to capture state from
        test_id: Test identifier
        state_type: "initial" or "final"
        seed: Random seed used for this battle

    Returns:
        Path to saved file, or None if capture failed
    """
    try:
        ensure_states_dir()

        # Generate timestamp and filename
        timestamp = datetime.now().isoformat()
        filename = generate_state_filename(test_id, timestamp, state_type)
        filepath = os.path.join(BATTLE_STATES_DIR, filename)

        # Capture state using BattleState
        state = BattleState.capture_from_engine(
            engine,
            mode="test",
            seed=seed,
        )

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(state.to_json(indent=2))

        log_debug(f"Saved {state_type} battle state to {filepath}")
        return filepath

    except Exception as e:
        log_warning(f"Failed to capture {state_type} battle state: {e}")
        return None


def capture_test_states(
    engine: 'BattleEngine',
    test_id: str,
    seed: Optional[int] = None,
    initial_engine: Optional['BattleEngine'] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Capture both initial and final states for a test run.

    This is a convenience function for capturing both states. The initial state
    should be captured right after scenario.setup(), and the final state should
    be captured after the test completes.

    Args:
        engine: BattleEngine with final state
        test_id: Test identifier
        seed: Random seed used
        initial_engine: BattleEngine with initial state (if different from final)

    Returns:
        Tuple of (initial_state_path, final_state_path)
    """
    timestamp = datetime.now().isoformat()

    # Capture final state from current engine
    final_path = capture_battle_state(engine, test_id, "final", seed)

    # If initial engine provided, capture from that; otherwise skip initial
    initial_path = None
    if initial_engine:
        initial_path = capture_battle_state(initial_engine, test_id, "initial", seed)

    return initial_path, final_path


def load_battle_state(filepath: str) -> Optional[BattleState]:
    """
    Load a battle state from JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        BattleState object, or None if load failed
    """
    try:
        if not os.path.exists(filepath):
            log_warning(f"Battle state file not found: {filepath}")
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()

        return BattleState.from_json(json_str)

    except Exception as e:
        log_warning(f"Failed to load battle state from {filepath}: {e}")
        return None


def load_battle_state_json(filepath: str) -> Optional[str]:
    """
    Load battle state JSON as raw string (for display).

    Args:
        filepath: Path to the JSON file

    Returns:
        JSON string, or None if load failed
    """
    try:
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        log_warning(f"Failed to load battle state JSON from {filepath}: {e}")
        return None


def cleanup_old_states(max_age_days: int = 7) -> int:
    """
    Remove old battle state files.

    Args:
        max_age_days: Remove files older than this many days

    Returns:
        Number of files removed
    """
    import time

    try:
        states_dir = ensure_states_dir()
        now = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        removed = 0

        for filename in os.listdir(states_dir):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(states_dir, filename)
            file_age = now - os.path.getmtime(filepath)

            if file_age > max_age_seconds:
                os.remove(filepath)
                removed += 1
                log_debug(f"Removed old battle state file: {filename}")

        if removed > 0:
            log_debug(f"Cleaned up {removed} old battle state files")

        return removed

    except Exception as e:
        log_warning(f"Failed to cleanup old battle states: {e}")
        return 0


class BattleStateCapture:
    """
    Context manager for capturing battle states during test execution.

    Usage:
        with BattleStateCapture(engine, test_id, seed) as capture:
            # Run test...
            pass

        # After context exits:
        initial_path = capture.initial_state_file
        final_path = capture.final_state_file
    """

    def __init__(self, engine: 'BattleEngine', test_id: str, seed: Optional[int] = None):
        self.engine = engine
        self.test_id = test_id
        self.seed = seed
        self.initial_state_file: Optional[str] = None
        self.final_state_file: Optional[str] = None
        self._timestamp: Optional[str] = None

    def __enter__(self) -> 'BattleStateCapture':
        """Capture initial state on entry."""
        self._timestamp = datetime.now().isoformat()
        self.initial_state_file = self._capture_state("initial")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Capture final state on exit."""
        self.final_state_file = self._capture_state("final")
        return False  # Don't suppress exceptions

    def _capture_state(self, state_type: str) -> Optional[str]:
        """Capture state with consistent timestamp."""
        try:
            ensure_states_dir()

            filename = generate_state_filename(self.test_id, self._timestamp, state_type)
            filepath = os.path.join(BATTLE_STATES_DIR, filename)

            state = BattleState.capture_from_engine(
                self.engine,
                mode="test",
                seed=self.seed,
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(state.to_json(indent=2))

            log_debug(f"Captured {state_type} state: {filepath}")
            return filepath

        except Exception as e:
            log_warning(f"Failed to capture {state_type} state: {e}")
            return None

    def get_results_dict(self) -> dict:
        """
        Get dict to merge into scenario.results.

        Returns:
            Dict with initial_state_file, final_state_file, and seed
        """
        return {
            'initial_state_file': self.initial_state_file,
            'final_state_file': self.final_state_file,
            'seed': self.seed,
        }
