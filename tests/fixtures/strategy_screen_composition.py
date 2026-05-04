"""PROJ-327 Phase 4 — test composition fixtures for ``StrategyScreen``.

Pairs with the production ``StrategyScreenComposition`` /
``StrategyScreenCompositionFactory`` at
``game/ui/screens/strategy_screen_composition.py``. Both implement the same
``StrategyScreenComposition`` protocol — one ``make_*`` method per sub-object.

The ``MockStrategyScreenComposition`` returns ``MagicMock`` instances for
every sub-object slot, matching the shape that the legacy inline wiring in
``_make_strategy_screen`` (test_strategy_screen.py:65-77 pre-PROJ-327)
produced. Centralizing the wiring here means adding/renaming a sub-object
slot only requires one edit instead of one per test helper.

Tests can either:

1. Pass the composition through a real ``StrategyScreen(...)`` call —
   substitutes only the 8 sub-objects, lets the rest of ``__init__`` run.
   (Currently impractical because ``StrategyScreen.__init__`` also runs
   heavy upstream construction — Camera, StrategyUI, asset loading. Future
   refactor could split that into a ``_init_heavy`` stage like
   ``RaceSetupScreen``'s two-stage pattern.)

2. Use the bypass-init helper ``_make_strategy_screen`` — calls
   ``MockStrategyScreenComposition().populate(screen)`` after manually
   populating upstream state. This is the path the migrated 62 tests use.

Same shape as PROJ-325's ``MockRaceSetupUiBuilder`` / ``DefaultRaceSetupDelegateFactory``.
See ``docs/02_PATTERNS.md`` § "Compositional Construction".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen


class MockStrategyScreenComposition:
    """Composition that returns MagicMock for every sub-object slot.

    Implements the ``StrategyScreenComposition`` protocol structurally.
    Each ``make_*`` method records the call (for assertion) and returns the
    pre-stored mock; the same mock is returned on repeated calls so tests
    that do ``mock_comp.renderer.foo`` after construction see the same
    object the screen wired in.

    For the bypass-init path, call ``populate(screen)`` to wire all 8
    sub-object attributes onto an existing ``StrategyScreen`` instance.
    """

    # Maps screen attribute name -> composition method name.
    _SLOTS: tuple[tuple[str, str], ...] = (
        ("_renderer", "make_renderer"),
        ("_camera_nav", "make_camera_navigator"),
        ("_fleet_ops", "make_fleet_ops"),
        ("_colonization", "make_colonization"),
        ("_superweapons", "make_superweapons"),
        ("_build_queue", "make_build_queue_manager"),
        ("_game_state", "make_game_state_manager"),
        ("_input", "make_input_handler"),
    )

    def __init__(self) -> None:
        # Pre-create one mock per slot so repeated make_* calls return
        # the same object (production behavior — sub-objects are
        # constructed once per __init__).
        self.renderer = MagicMock(name="renderer")
        self.camera_nav = MagicMock(name="camera_nav")
        self.fleet_ops = MagicMock(name="fleet_ops")
        self.colonization = MagicMock(name="colonization")
        self.superweapons = MagicMock(name="superweapons")
        self.build_queue = MagicMock(name="build_queue")
        self.game_state = MagicMock(name="game_state")
        self.input_handler = MagicMock(name="input_handler")

    def make_renderer(self, screen: "StrategyScreen") -> Any:
        return self.renderer

    def make_camera_navigator(self, screen: "StrategyScreen") -> Any:
        return self.camera_nav

    def make_fleet_ops(self, screen: "StrategyScreen") -> Any:
        return self.fleet_ops

    def make_colonization(self, screen: "StrategyScreen") -> Any:
        return self.colonization

    def make_superweapons(self, screen: "StrategyScreen") -> Any:
        return self.superweapons

    def make_build_queue_manager(self, screen: "StrategyScreen") -> Any:
        return self.build_queue

    def make_game_state_manager(self, screen: "StrategyScreen") -> Any:
        return self.game_state

    def make_input_handler(self, screen: "StrategyScreen") -> Any:
        return self.input_handler

    def populate(self, screen: "StrategyScreen") -> None:
        """Wire all 8 sub-object attributes onto ``screen``.

        Used by the bypass-init helper ``_make_strategy_screen`` — fills
        the slots ``__init__`` would have filled via the composition seam,
        without running ``__init__``.
        """
        screen._renderer = self.renderer
        screen._camera_nav = self.camera_nav
        screen._fleet_ops = self.fleet_ops
        screen._colonization = self.colonization
        screen._superweapons = self.superweapons
        screen._build_queue = self.build_queue
        screen._game_state = self.game_state
        screen._input = self.input_handler


__all__ = ["MockStrategyScreenComposition"]
