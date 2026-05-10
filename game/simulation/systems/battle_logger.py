"""Battle logger — toggleable file-based event recorder.

PROJ-382 Phase 5: extracted from ``battle_engine.py`` to bring the
parent module under the 500 LOC ceiling.  ``BattleLogger`` is a thin
wrapper around an open file handle with ``__enter__``/``__exit__``,
``__del__`` cleanup, and IOError-tolerant writes.  The class is
imported by ``BattleEngine`` and constructed once per battle session.
"""
from __future__ import annotations

import logging
import os

from game.core.paths import Paths


logger = logging.getLogger(__name__)


class BattleLogger:
    """Toggleable logger that writes battle events to file."""

    def __init__(self, filename: str = None, enabled: bool = True):
        if filename is None:
            filename = os.path.join(Paths.LOGS_DIR, "battle_log.txt")
        self.enabled = enabled
        self.filename = filename
        self.file = None

    def __enter__(self):
        """Context manager entry."""
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed."""
        self.close()
        return False

    def __del__(self):
        """Destructor - ensures file is closed on garbage collection."""
        self.close()

    def start_session(self) -> None:
        """Start a new logging session.

        ERR-010: Uses try/except/finally for proper cleanup on failure.
        """
        if self.enabled:
            self.close()  # Ensure existing file is closed before opening new one
            new_file = None
            try:
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                new_file = open(self.filename, 'w', encoding='utf-8')
                new_file.write("=== BATTLE LOG STARTED ===\n")
                self.file = new_file  # Only assign on success
            except IOError as e:
                logger.warning(f"Could not open battle log '{self.filename}': {e}")
                self.enabled = False
                if new_file:
                    try:
                        new_file.close()
                    except IOError:
                        pass  # Already in error state, ignore close failure

    def log(self, message: str) -> None:
        """Log a message if logging is enabled."""
        if self.enabled and self.file:
            try:
                self.file.write(f"{message}\n")

            except IOError as e:
                logger.warning(f"BattleLogger: Failed to write to '{self.filename}': {e}")

    def close(self) -> None:
        """Close the log file."""
        if self.file:
            try:
                self.log("=== BATTLE LOG ENDED ===")
                self.file.close()
            except IOError as e:
                logger.warning(f"BattleLogger: Failed to close '{self.filename}': {e}")
            finally:
                self.file = None
