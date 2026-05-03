"""Shared base class for planet target editors.

Extracted in PROJ-319 (DUP-X-05) to remove the duplicated `process_event`
body and the close-callback wiring that lived in `AtmosphereTargetEditor`,
`GravityTargetEditor`, `WaterTargetEditor`, and `RadiationShieldEditor`.

Subclasses provide a `_button_handlers()` mapping each `UIButton` reference
to the method that should run when it is pressed. The base class owns:

  - The `process_event` button-dispatch loop.
  - The `UI_WINDOW_CLOSE` -> `on_close_callback` wiring.

Per-editor logic (`_on_apply`, `_set_species_ideal`, `_set_match_current`,
`_clear_target`, `_set_auto`, etc.) stays on the subclass — the editors
diverge enough on slider geometry and unit handling that consolidating those
bodies would obscure intent.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import pygame
import pygame_gui

from game.ui.screens.species_selector_mixin import RaceConfigResolverMixin
from game.ui.screens.strategy_modal_window import StrategyModalWindow


class PlanetTargetEditor(RaceConfigResolverMixin, StrategyModalWindow):
    """Base class for the four planet target editors.

    Subclasses are responsible for building their own UI (sliders, labels,
    buttons) and for assigning `self.on_close_callback`. They override
    `_button_handlers()` to map each button to its action.
    """

    on_close_callback: Optional[Callable[[], None]] = None

    def _button_handlers(self) -> Dict[Any, Callable[[], None]]:
        """Return a mapping `{button_widget: zero-arg callable}`.

        Subclasses override this. The base `process_event` invokes the
        callable when the matching button is pressed and returns True.
        """
        return {}

    def process_event(self, event: pygame.event.Event) -> bool:
        """Dispatch button presses and the standard close-callback path."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button, action in self._button_handlers().items():
                if event.ui_element is button:
                    action()
                    return True

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element is self:
                if self.on_close_callback is not None:
                    self.on_close_callback()
                return True

        return handled
