"""Combat Lab test-run-details package.

PROJ-309 sub-phase 3.6 — split from a 960-line `test_run_details.py` into
per-section modules. The canonical class home is `panel.py`; this
`__init__` re-exports it so callers can use the canonical path:

    from game.ui.screens.test_lab.details import TestRunDetailsPanel
"""
from __future__ import annotations

from .panel import TestRunDetailsPanel

__all__ = ["TestRunDetailsPanel"]
