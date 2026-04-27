"""Re-export shim for `TestRunDetailsPanel` (PROJ-309 sub-phase 3.6).

The implementation moved to the `details/` subpackage; this shim keeps the
historical import path working for `panel_manager.py` and `results_panel.py`:

    from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel
"""
from __future__ import annotations

from game.ui.screens.test_lab.details import TestRunDetailsPanel

__all__ = ["TestRunDetailsPanel"]
