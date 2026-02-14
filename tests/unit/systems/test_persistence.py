"""
Tests for ShipIO module.

PROJ-113: ShipIO moved from game.simulation.systems.persistence to game.ui.services.ship_io.
DUP-UI2-001: Tkinter initialization moved to tkinter_utils module.
"""
import logging
import os
import pytest
from unittest.mock import patch, MagicMock

from game.ui.services import tkinter_utils


class TestTkinterUtilsInitLogging:
    """Tests for tkinter initialization logging (ERR-006)."""

    def test_tkinter_init_failure_logs_warning(self, caplog):
        """If Tkinter fails to initialize, should log a warning."""
        import tkinter as real_tkinter

        # Reset tkinter_utils state
        tkinter_utils.reset_tk_root()

        # Mock tkinter.Tk to raise
        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                # Provide TclError so except clause works
                mock_tk_module.TclError = real_tkinter.TclError
                mock_tk_module.Tk.side_effect = RuntimeError("Display not available")

                with caplog.at_level(logging.WARNING):
                    # Call get_tk_root which will try to initialize
                    result = tkinter_utils.get_tk_root()

            # Should return None
            assert result is None

            # Should have logged a warning
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when Tkinter init fails"

        # Cleanup
        tkinter_utils.reset_tk_root()
