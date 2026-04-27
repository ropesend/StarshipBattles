"""Combat Lab renderer package.

PROJ-309 sub-phase 3.3 — split from a 1195-line `renderer.py` into per-panel
modules. The canonical class home is `orchestrator.py`; this `__init__`
re-exports it so callers can keep using the historical import path:

    from game.ui.screens.test_lab.renderer import TestLabRenderer
"""
from __future__ import annotations

from .orchestrator import TestLabRenderer

__all__ = ["TestLabRenderer"]
