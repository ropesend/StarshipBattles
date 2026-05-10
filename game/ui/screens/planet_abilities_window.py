"""Planet Abilities Window — List and toggle all activatable abilities on a planet.

Shows environment editor buttons (Atmosphere, Gravity, Water, Radiation) at the top,
followed by each toggleable ability with its current status and a toggle button.
Status displays: Active, Inactive, Activating (ticks), Deactivating (ticks).

PROJ-329C Phase 1: Migrated to two-stage construction. Cheap state
(planet, callbacks, slot dicts, controller delegate) lives before
``super().__init__``; widget construction is behind
``PlanetAbilitiesUiBuilder`` so tests can swap in a Mock under
``bypass_init``. The facade-side queries + command dispatch live in
``PlanetAbilitiesController`` (see ``planet_abilities_controller.py``).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
import logging

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel

from game.ui.screens.planet_abilities_controller import (
    FOOD_EDITOR_LABEL as _FOOD_EDITOR_LABEL,
    FOOD_EDITOR_TYPE as _FOOD_EDITOR_TYPE,
    PlanetAbilitiesController,
)
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class PlanetAbilitiesUiBuilder:
    """Production widget builder. Reads from ``screen.controller`` and
    populates editor buttons + ability rows on the screen.

    Writes to ``screen._toggle_buttons``, ``screen._editor_buttons``,
    ``screen._status_labels``, and ``screen._widgets``.
    """

    ROW_HEIGHT = 36

    def build(self, screen: "PlanetAbilitiesWindow") -> None:
        container = screen.get_container()
        y = 10

        # --- Environment editor buttons (conditional on facility presence) ---
        available_editors = screen.controller.get_available_editors()
        show_food_editor = screen.controller.should_show_food_editor()
        if available_editors or show_food_editor:
            btn_w = 100
            btn_h = 30
            gap = 8
            x = 10
            for ability_key, label in available_editors:
                btn = UIButton(
                    relative_rect=pygame.Rect(x, y, btn_w, btn_h),
                    text=label,
                    manager=screen.ui_manager,
                    container=container,
                )
                btn._editor_type = label.lower()
                screen._editor_buttons.append(btn)
                screen._widgets.append(btn)
                x += btn_w + gap
            if show_food_editor:
                food_btn = UIButton(
                    relative_rect=pygame.Rect(x, y, btn_w, btn_h),
                    text=_FOOD_EDITOR_LABEL,
                    manager=screen.ui_manager,
                    container=container,
                )
                food_btn._editor_type = _FOOD_EDITOR_TYPE
                screen._editor_buttons.append(food_btn)
                screen._widgets.append(food_btn)
            y += btn_h + 10

        # --- Toggleable ability rows ---
        abilities_found = screen.controller.scan_abilities()

        if not abilities_found and not available_editors:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 350, 30),
                text="No abilities on this planet.",
                manager=screen.ui_manager,
                container=container,
            )
            screen._widgets.append(lbl)
            return

        if not abilities_found:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 350, 30),
                text="No toggleable abilities.",
                manager=screen.ui_manager,
                container=container,
            )
            screen._widgets.append(lbl)
            return

        for entry in abilities_found:
            ability_name = entry['ability_name']
            display_name = entry['display_name']
            facility_id = entry['facility_id']
            facility_name = entry['facility_name']
            component_key = entry['component_key']
            instance_label = entry['instance_label']
            row_key = f"{facility_id}:{component_key}"

            name_text = f"{display_name} ({facility_name}{instance_label})"
            name_lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 290, self.ROW_HEIGHT),
                text=name_text,
                manager=screen.ui_manager,
                container=container,
            )
            screen._widgets.append(name_lbl)

            status = screen.controller.get_component_status(
                facility_id, component_key
            )
            status_lbl = UILabel(
                relative_rect=pygame.Rect(305, y, 110, self.ROW_HEIGHT),
                text=status,
                manager=screen.ui_manager,
                container=container,
            )
            screen._widgets.append(status_lbl)
            screen._status_labels[row_key] = status_lbl

            is_active = screen.controller.is_component_active(
                facility_id, component_key
            )

            btn_text = "Deactivate" if is_active else "Activate"
            btn = UIButton(
                relative_rect=pygame.Rect(420, y + 2, 90, self.ROW_HEIGHT - 4),
                text=btn_text,
                manager=screen.ui_manager,
                container=container,
            )
            btn._ability_name = ability_name
            btn._facility_id = facility_id
            btn._component_key = component_key
            btn._is_active = is_active
            screen._widgets.append(btn)
            screen._toggle_buttons[row_key] = btn

            y += self.ROW_HEIGHT


class PlanetAbilitiesWindow(StrategyModalWindow):
    """Window listing all toggleable abilities on a planet with toggle buttons.

    Also provides environment editor buttons at the top for setting atmosphere,
    gravity, water, and radiation targets.

    PROJ-313: Migrated to StrategyModalWindow base class.
    PROJ-329C Phase 1: two-stage construction with ``ui_builder`` test
    seam + ``PlanetAbilitiesController`` for facade I/O.
    """

    ROW_HEIGHT = 36

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet,
        facade,
        component_registry=None,
        *,
        window_manager: "StrategyWindowManager",
        on_open_editor: Optional[Callable[[str, Any], None]] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        ui_builder: Optional[PlanetAbilitiesUiBuilder] = None,
        controller: Optional[PlanetAbilitiesController] = None,
    ):
        """Initialize the abilities window.

        Args:
            relative_rect: Window position and size.
            manager: UI manager.
            planet: Planet object.
            facade: StrategySessionFacade for command dispatch.
            component_registry: Component registry for ability lookup.
            on_open_editor: Callback(editor_type, planet) to open environment editors.
            on_close_callback: Callback fired from kill() so the registrar can
                reset its slot to None (BUG-121).
            ui_builder: Optional UI builder override (test seam).
            controller: Optional controller override (test seam). Defaults
                to a real ``PlanetAbilitiesController(planet, facade,
                component_registry)``.
        """
        # ---- Stage 1: cheap state + delegates (no facade I/O) ----
        self.planet = planet
        self.facade = facade
        self.component_registry = component_registry
        self._on_open_editor = on_open_editor
        self._on_close_callback = on_close_callback
        self._toggle_buttons: Dict[str, UIButton] = {}
        self._editor_buttons: List[UIButton] = []
        self._status_labels: Dict[str, UILabel] = {}
        self._widgets: List = []
        self.controller = controller or PlanetAbilitiesController(
            planet, facade, component_registry
        )

        # ---- Stage 2: shell ----
        super().__init__(
            relative_rect,
            manager,
            window_display_title=f"Abilities: {planet.name}",
            resizable=False,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or PlanetAbilitiesUiBuilder()).build(self)

    def kill(self) -> None:
        if self._on_close_callback is not None:
            self._on_close_callback()
        super().kill()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle button clicks and editor button clicks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check editor buttons first
            editor_type = getattr(event.ui_element, '_editor_type', None)
            if editor_type and self._on_open_editor:
                self._on_open_editor(editor_type, self.planet)
                return True

            ability_name = getattr(event.ui_element, '_ability_name', None)
            facility_id = getattr(event.ui_element, '_facility_id', None)
            component_key = getattr(event.ui_element, '_component_key', None)
            is_active = getattr(event.ui_element, '_is_active', None)

            if ability_name and facility_id is not None and component_key:
                result = self.controller.toggle_ability(
                    facility_id=facility_id,
                    component_key=component_key,
                    ability_name=ability_name,
                    is_active=is_active,
                )
                if result and not result.is_valid:
                    logger.warning(f"Ability toggle failed: {result.message}")
                else:
                    new_active = not is_active
                    event.ui_element._is_active = new_active
                    event.ui_element.set_text(
                        "Deactivate" if new_active else "Activate"
                    )
                    row_key = f"{facility_id}:{component_key}"
                    if row_key in self._status_labels:
                        self._status_labels[row_key].set_text(
                            self.controller.get_component_status(
                                facility_id, component_key
                            )
                        )
                return True

        return super().process_event(event)


__all__ = [
    "PlanetAbilitiesWindow",
    "PlanetAbilitiesUiBuilder",
]
