"""PROJ-282 Phase 8: `FleetBattleSetupScreen` thin scene shell.

Terminal PROJ-282 location for the Battle Setup screen. The screen owns
only:
  - IScene protocol implementation (handle_event / update / draw / handle_resize)
  - Delegate wiring (state, view_model, renderer, input_handler, controller)
  - Lifecycle delegation to the controller
  - Backward-compat property shims so the renderer's panel builders can
    keep reading `screen.active_side` / `screen.tick_limit` / etc.

All mutations, event dispatch, pygame_gui construction, TF/SQ CRUD, save/
load, and battle launch live on dedicated delegates in this package.

This screen follows the MVVM pattern documented in
`docs/03_CONVENTIONS.md § 2.4 UI Screen Line Budget`. Target: keep the
class under 300 lines — delegate logic to ViewModel / Renderer /
InputHandler / Controller / domain helpers. TestLabScreen is the sibling
exemplar.
"""
from __future__ import annotations

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

    def handle_event(self, event):
        if self._ui_manager:
            self._ui_manager.process_events(event)
        self.input_handler.handle_event(event)

    def update(self, dt: float):
        if self._ui_manager:
            self._ui_manager.update(dt)

    def draw(self, screen):
        screen.fill((20, 25, 35))
        if self._ui_manager:
            self._ui_manager.draw_ui(screen)

    def handle_resize(self, width: int, height: int):
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

    # === View-model property shims ===
    # Renderer/panels read selection state via `screen.active_side` etc.;
    # shims route to `self.view_model.*`.

    @property
    def active_side(self) -> int:
        return self.view_model.active_side

    @active_side.setter
    def active_side(self, value: int) -> None:
        self.view_model.active_side = value

    @property
    def active_fleet_index(self) -> int:
        return self.view_model.active_fleet_index

    @active_fleet_index.setter
    def active_fleet_index(self, value: int) -> None:
        self.view_model.active_fleet_index = value

    @property
    def selected_tf_index(self):
        return self.view_model.selected_tf_index

    @selected_tf_index.setter
    def selected_tf_index(self, value) -> None:
        self.view_model.selected_tf_index = value

    @property
    def selected_sq_index(self):
        return self.view_model.selected_sq_index

    @selected_sq_index.setter
    def selected_sq_index(self, value) -> None:
        self.view_model.selected_sq_index = value

    @property
    def selected_ship_index(self):
        return self.view_model.selected_ship_index

    @selected_ship_index.setter
    def selected_ship_index(self, value) -> None:
        self.view_model.selected_ship_index = value

    @property
    def available_designs(self) -> list:
        return self.view_model.available_designs

    @available_designs.setter
    def available_designs(self, value: list) -> None:
        self.view_model.available_designs = value

    # === Controller property shims (end-condition + toggles) ===

    @property
    def tick_limit(self) -> int:
        return self.controller.tick_limit

    @tick_limit.setter
    def tick_limit(self, value: int) -> None:
        self.controller.tick_limit = value

    @property
    def end_all_destroyed(self) -> bool:
        return self.controller.end_all_destroyed

    @end_all_destroyed.setter
    def end_all_destroyed(self, value: bool) -> None:
        self.controller.end_all_destroyed = value

    @property
    def end_all_derelict(self) -> bool:
        return self.controller.end_all_derelict

    @end_all_derelict.setter
    def end_all_derelict(self, value: bool) -> None:
        self.controller.end_all_derelict = value

    @property
    def end_mass_ratio(self) -> bool:
        return self.controller.end_mass_ratio

    @end_mass_ratio.setter
    def end_mass_ratio(self, value: bool) -> None:
        self.controller.end_mass_ratio = value

    @property
    def mass_ratio_threshold(self) -> float:
        return self.controller.mass_ratio_threshold

    @mass_ratio_threshold.setter
    def mass_ratio_threshold(self, value: float) -> None:
        self.controller.mass_ratio_threshold = value

    def _get_toggle(self, side_id: int, scope: str, design_id: str) -> bool:
        """Complex-toggle read accessor for the left-panel renderer."""
        return self.controller.get_complex_toggle(side_id, scope, design_id)
