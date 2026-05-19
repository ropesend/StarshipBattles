"""PROJ-282 Phase 8: `FleetBattleSetupScreen` thin scene shell.

Terminal PROJ-282 location for the Battle Setup screen. The screen owns
only:
  - IScene protocol implementation (handle_event / update / draw / handle_resize)
  - Delegate wiring (state, view_model, renderer, input_handler, controller)
  - Lifecycle delegation to the controller

Panel builders read selection state via ``screen.view_model.<X>`` /
``screen.state.<X>`` / ``screen.controller.<X>`` directly; the legacy
``screen.active_side`` / ``screen.tick_limit`` etc. property shims were
retired in PROJ-456 Phase 5.

All mutations, event dispatch, pygame_gui construction, TF/SQ CRUD, save/
load, and battle launch live on dedicated delegates in this package.

This screen follows the MVVM pattern documented in
`docs/03_CONVENTIONS.md § 2.4 UI Screen Line Budget`. Target: keep the
class under 300 lines — delegate logic to ViewModel / Renderer /
InputHandler / Controller / domain helpers. TestLabScreen is the sibling
exemplar.
"""
from __future__ import annotations

from typing import Any
import logging

from game.ui.screens.battle_setup.controller import BattleSetupController
from game.ui.screens.battle_setup.input_handler import BattleSetupInputHandler
from game.ui.screens.battle_setup.renderer import BattleSetupRenderer
from game.ui.screens.battle_setup.view_model import BattleSetupViewModel
from game.ui.screens.battle_setup_state import BattleSetupState

logger = logging.getLogger(__name__)


class FleetBattleSetupScreen:
    """Fleet-based battle setup screen with full hierarchy support.

    Implements `IScene` via `handle_event` / `update` / `draw` /
    `handle_resize`. Delegates panel construction to `BattleSetupRenderer`,
    event dispatch to `BattleSetupInputHandler`, and state mutations +
    lifecycle to `BattleSetupController`.
    """

    def __init__(self, width: int, height: int, scene_callback=None):
        self.screen_width = width
        self.screen_height = height
        self.scene_callback = scene_callback

        self.state = BattleSetupState()
        self.view_model = BattleSetupViewModel()
        self.renderer = BattleSetupRenderer()
        self.controller = BattleSetupController(
            state=self.state,
            view_model=self.view_model,
            scene_callback=scene_callback,
            on_change=self._rebuild_ui,
        )
        self.input_handler = BattleSetupInputHandler(self)

        self._ui_manager = None
        self._panels_built = False

    # === IScene Protocol ===

    def handle_event(self, event) -> None:
        if self._ui_manager:
            self._ui_manager.process_events(event)
        self.input_handler.handle_event(event)

    def update(self, dt: float) -> None:
        if self._ui_manager:
            self._ui_manager.update(dt)

    def draw(self, screen) -> None:
        screen.fill((20, 25, 35))
        if self._ui_manager:
            self._ui_manager.draw_ui(screen)

    def handle_resize(self, width: int, height: int) -> None:
        self.screen_width = width
        self.screen_height = height
        if self._ui_manager:
            self._ui_manager.set_window_resolution((width, height))
        self._rebuild_ui()

    # === Lifecycle ===

    def start(self, preserve_teams: bool = False) -> None:
        self.controller.start(preserve_teams=preserve_teams)

    def _rebuild_ui(self) -> None:
        self.renderer.rebuild(self)

    def _get_toggle(self, side_id: int, scope: str, design_id: str) -> bool:
        """Complex-toggle read accessor for the left-panel renderer."""
        return self.controller.get_complex_toggle(side_id, scope, design_id)
