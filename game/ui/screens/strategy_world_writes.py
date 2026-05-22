"""Narrow scene-owned write handle for the strategy screen (PROJ-477 Phase 2).

The Category B mutator WRITE seams that used to read the live session off the
``StrategyScreen.session`` getter — set-active-empire (turn rotation), set fleet
path, pop fleet order (order editing) — route through this tiny composition-root
handle instead. Retiring the public ``session`` GETTER (Phase 3) leaves these
writes without a session reference; this handle gives them exactly the three
mutations they need, backed by the screen's private ``_session``
(``active_empire`` attribute + ``fleet_mutator`` service).

This is deliberately NOT a general-purpose session escape: it exposes three
named verbs and nothing else. The screen constructs it with a provider callable
so a test-swapped session (``screen.session = mock``) is honoured at call time.
"""

from __future__ import annotations

from typing import Any, Callable


class StrategyOrderWrites:
    """Composition-root write seam for the three Category B mutations.

    Backed by the screen's private session through a provider callable so the
    handle always resolves the CURRENT session (honours test ``session`` swaps).
    """

    __slots__ = ("_session_provider",)

    def __init__(self, session_provider: Callable[[], Any]) -> None:
        self._session_provider = session_provider

    def set_active_empire(self, empire: Any) -> None:
        """Set the session's acting empire (BUG-125 turn-rotation seam)."""
        self._session_provider().active_empire = empire

    def set_fleet_path(self, fleet: Any, path: list) -> None:
        """Set a fleet's path via the session fleet mutator (PROJ-370)."""
        self._session_provider().fleet_mutator.set_path(fleet, path)

    def pop_fleet_order(self, fleet: Any, index: int) -> None:
        """Pop a fleet order via the session fleet mutator (PROJ-370)."""
        self._session_provider().fleet_mutator.pop_order(fleet, index=index)
