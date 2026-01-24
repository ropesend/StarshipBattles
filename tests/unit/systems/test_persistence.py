"""
Tests for persistence module (ShipIO).
"""
import pytest
from unittest.mock import patch, MagicMock


class TestShipIOInitLogging:
    """Tests for tkinter initialization logging (ERR-006)."""

    def test_tkinter_init_failure_logs_warning(self, caplog):
        """If Tkinter fails to initialize, should log a warning."""
        import logging
        import importlib

        # Force reimport to trigger the try/except
        import game.simulation.systems.persistence as persistence_module

        # Mock tkinter.Tk to raise
        with patch('tkinter.Tk', side_effect=Exception("Display not available")):
            # Need to force module reload
            with caplog.at_level(logging.WARNING):
                # Reload the module to re-execute module-level code
                importlib.reload(persistence_module)

            # Should have logged a warning
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when Tkinter init fails"
