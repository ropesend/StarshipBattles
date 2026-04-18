"""Strategy UI event routing and handling.

This module contains the StrategyEventRouter class that handles all event
routing for the StrategyUI, including button presses, window management,
and click handling.

PROJ-86: God Class Decomposition - UI Tier
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui

import logging

logger = logging.getLogger(__name__)
from game.core.protocols import is_fleet, is_planet

if TYPE_CHECKING:
    from game.ui.screens.strategy_ui import StrategyUI


class StrategyEventRouter:
    """Routes and handles events for the StrategyUI.

    Extracted from StrategyUI to reduce god class size. Handles:
    - pygame_gui UI_BUTTON_PRESSED events
    - Menu panel open/close via Escape and click-outside
    - Window close events
    - Tree panel events
    - Click handling for sidebar and modal detection

    Args:
        ui: Reference to the parent StrategyUI instance.
    """

    def __init__(self, ui: 'StrategyUI'):
        """Initialize the event router.

        Args:
            ui: The parent StrategyUI instance.
        """
        self.ui = ui

    def has_modal_open(self) -> bool:
        """Check if any modal sub-panel is currently open.

        Returns:
            True if any modal window or panel is open, False otherwise.
        """
        # Check for menu panel (PROJ-72)
        if self.ui.menu_panel:
            return True

        # Check for build queue screen
        if self.ui.scene.build_queue_screen is not None:
            return True

        # Check window manager for open windows (PROJ-86)
        wm = self.ui.window_manager
        if wm.fleet_orders_window is not None:
            return True
        if wm.planet_list_window is not None:
            return True
        if wm.star_list_window is not None:
            return True
        if wm.fleet_report_window is not None:
            return True
        if wm.transfer_dialog is not None:
            return True
        if wm.build_queue_list_window is not None:
            return True
        if wm.empire_build_queue_window is not None:
            return True
        if wm.event_log_window is not None:
            return True
        if wm.empire_panel_window is not None:
            return True
        if wm.move_choice_window is not None:
            return True
        if wm.cargo_quick_dialog is not None:
            return True
        if wm.planet_selection_window is not None:
            return True
        if wm.system_selection_window is not None:
            return True
        if wm.fleet_selection_window is not None:
            return True

        return False

    def on_ui_selection(self, obj) -> None:
        """Handle selection of an object from any UI panel.

        Args:
            obj: The selected object (Planet, Fleet, etc.).
        """
        self.ui.scene.on_ui_selection(obj)

    def route_event(self, event) -> None:
        """Route an event through the StrategyUI event handling chain.

        This is the main entry point for event handling. Processes pygame_gui
        events, tree panel events, button presses, and window close events.

        Args:
            event: The pygame event to process.
        """
        self.ui.manager.process_events(event)
        # PROJ-86: Use window manager for UI callbacks
        self.ui.window_manager.process_ui_callbacks(event)

        # Pass generic events to orders window if active (e.g. for confirmation dialogs)
        if self.ui.window_manager.fleet_orders_window:
            self.ui.window_manager.fleet_orders_window.handle_global_event(event)

        # Close menu panel on Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.ui.menu_panel:
            self.ui.close_menu_panel()
            return

        # Close menu panel on click outside
        if event.type == pygame.MOUSEBUTTONDOWN and self.ui.menu_panel:
            panel_rect = self.ui.menu_panel.get_abs_rect()
            menu_btn_rect = self.ui.btn_menu.get_abs_rect()
            if not panel_rect.collidepoint(event.pos) and not menu_btn_rect.collidepoint(event.pos):
                self.ui.close_menu_panel()

        if self.ui.system_tree.process_event(event):
            pass

        if self.ui.sector_tree.process_event(event):
            pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_pressed(event)

        # Handle quit-to-menu confirmation (PROJ-72)
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.ui.scene._quit_confirm_dialog:
                self.ui.scene._handle_quit_confirmed()
            # PROJ-198: Route superweapon confirmations via window manager
            elif self.ui.window_manager.process_confirmation_event(event):
                pass

        # PROJ-86: Handle window close via window manager
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            self._handle_window_close(event)

    def _handle_button_pressed(self, event) -> None:
        """Handle UI_BUTTON_PRESSED events.

        Args:
            event: The pygame_gui button pressed event.
        """
        ui = self.ui

        if event.ui_element == ui.btn_planets:
            ui.open_planet_list()
        elif event.ui_element == ui.btn_stars:
            ui.open_star_list()
        elif event.ui_element == ui.btn_design:
            ui.scene.on_design_click()
        elif event.ui_element == ui.btn_build_queues:
            ui.open_build_queue_list()
        elif event.ui_element == ui.btn_all_queues:
            ui.open_empire_build_queue_window()
        elif event.ui_element == ui.btn_menu:
            ui.toggle_menu_panel()
        elif event.ui_element == ui.btn_events:
            ui.open_event_log()
        elif event.ui_element == ui.btn_empire:
            ui.open_empire_panel()
        elif event.ui_element == ui.btn_raw_data:
            ui.show_raw_data_popup()
        elif event.ui_element == ui.btn_colonize:
            self._handle_colonize_button()
        elif event.ui_element == ui.btn_orders:
            obj = ui.current_selection
            if obj and is_fleet(obj):
                ui.open_orders_window(obj)
        elif event.ui_element == ui.btn_planet_orders:  # PROJ-238
            obj = ui.current_selection
            if obj and is_planet(obj):
                ui.open_orders_window(obj, entity_type="planet")
        elif event.ui_element == ui.btn_fleet_report:
            obj = ui.current_selection
            if obj and is_fleet(obj):
                ui.open_fleet_report_window(obj)
        # NOTE: btn_build_yard is handled in strategy_input_handler.py - do not duplicate here

    def _open_atmosphere_editor(self, planet) -> None:
        """Open atmosphere target editor for a planet."""
        from game.ui.screens.atmosphere_target_editor import AtmosphereTargetEditor
        from game.strategy.engine.commands import SetAtmosphereTargetCommand
        from game.ui.utils import create_centered_rect

        ui = self.ui
        scene = ui.scene

        # Get race config for species ideal button
        race_config = None
        try:
            empire = scene.session.get_empire(planet.owner_id)
            if empire and hasattr(empire, 'race_config'):
                race_config = empire.race_config
            elif empire:
                from game.strategy.systems.race_library import RaceLibrary
                race_lib = RaceLibrary()
                race_id = getattr(empire, 'race_id', None)
                if race_id:
                    race_config = race_lib.get_race(race_id)
        except Exception:
            pass

        def on_apply(planet_id, target):
            cmd = SetAtmosphereTargetCommand(planet_id=planet_id, atmosphere_target=target)
            scene.facade.handle_command(cmd)

        rect = create_centered_rect(700, 500, ui.width, ui.height)
        AtmosphereTargetEditor(
            rect=rect,
            manager=ui.manager,
            planet=planet,
            on_apply_callback=on_apply,
            race_config=race_config,
        )

    def _open_gravity_editor(self, planet) -> None:
        """Open gravity target editor for a planet."""
        from game.ui.screens.gravity_target_editor import GravityTargetEditor
        from game.strategy.engine.commands import SetGravityTargetCommand
        from game.ui.utils import create_centered_rect

        ui = self.ui
        scene = ui.scene
        race_config = self._get_race_config(planet)

        def on_apply(planet_id, gravity_target):
            cmd = SetGravityTargetCommand(planet_id=planet_id, gravity_target=gravity_target)
            scene.facade.handle_command(cmd)

        rect = create_centered_rect(400, 300, ui.width, ui.height)
        GravityTargetEditor(
            rect=rect, manager=ui.manager, planet=planet,
            on_apply_callback=on_apply, race_config=race_config,
        )

    def _open_water_editor(self, planet) -> None:
        """Open water target editor for a planet."""
        from game.ui.screens.water_target_editor import WaterTargetEditor
        from game.strategy.engine.commands import SetWaterTargetCommand
        from game.ui.utils import create_centered_rect

        ui = self.ui
        scene = ui.scene
        race_config = self._get_race_config(planet)

        def on_apply(planet_id, water_target):
            cmd = SetWaterTargetCommand(planet_id=planet_id, water_target=water_target)
            scene.facade.handle_command(cmd)

        rect = create_centered_rect(400, 300, ui.width, ui.height)
        WaterTargetEditor(
            rect=rect, manager=ui.manager, planet=planet,
            on_apply_callback=on_apply, race_config=race_config,
        )

    def _open_radiation_shield_editor(self, planet) -> None:
        """Open radiation shield editor for a planet."""
        from game.ui.screens.radiation_shield_editor import RadiationShieldEditor
        from game.strategy.engine.commands import SetRadiationShieldTargetCommand
        from game.ui.utils import create_centered_rect

        ui = self.ui
        scene = ui.scene
        race_config = self._get_race_config(planet)

        def on_apply(planet_id, shielding_target):
            cmd = SetRadiationShieldTargetCommand(planet_id=planet_id, shielding_target=shielding_target)
            scene.facade.handle_command(cmd)

        rect = create_centered_rect(400, 300, ui.width, ui.height)
        RadiationShieldEditor(
            rect=rect, manager=ui.manager, planet=planet,
            on_apply_callback=on_apply, race_config=race_config,
        )

    def _open_food_allocation_editor(self, planet) -> None:
        """Open the PROJ-284 food allocation editor for a colony.

        Unlike the environment editors (atmosphere / gravity / water /
        radiation), food allocation is a direct mutation on
        `ColonySpeciesConfig.food_allocation` rather than a
        strategy-layer command — there's no need for replay / undo and
        the config lives on the planet, not in a command-sourced
        register. Direct mutation is also what the PROJ-284 Phase 4
        checklist explicitly allows ("direct mutation — follow the
        local pattern").
        """
        from game.ui.screens.food_allocation_editor import (
            FoodAllocationEditor,
            apply_allocations,
        )
        from game.strategy.config.economy_config import get_default_economy_config
        from game.ui.utils import create_centered_rect

        ui = self.ui

        economy = get_default_economy_config()
        resource_catalog = None
        try:
            from game.core.registry import get_default_registry_provider
            resource_catalog = get_default_registry_provider().get_resource_catalog()
        except Exception:
            pass

        def resolve_race(race_id):
            # Prefer empire's own race_config when race_ids match.
            empire_race = self._get_race_config(planet)
            if empire_race is not None and getattr(empire_race, "race_id", None) == race_id:
                return empire_race
            # Fallback: try RaceLibrary (covers multi-species colonies).
            try:
                from game.strategy.systems.race_library import RaceLibrary
                return RaceLibrary().get_race(race_id)
            except Exception:
                return None

        def on_apply(planet_id, allocations):
            apply_allocations(planet, allocations)

        rect = create_centered_rect(640, 420, ui.width, ui.height)
        FoodAllocationEditor(
            rect=rect,
            manager=ui.manager,
            planet=planet,
            economy_config=economy,
            resource_catalog=resource_catalog,
            race_resolver=resolve_race,
            on_apply_callback=on_apply,
        )

    def _get_race_config(self, planet):
        """Get the race config for the planet's owning empire."""
        ui = self.ui
        scene = ui.scene
        try:
            empire = scene.session.get_empire(planet.owner_id)
            if empire and hasattr(empire, 'race_config'):
                return empire.race_config
            elif empire:
                from game.strategy.systems.race_library import RaceLibrary
                race_lib = RaceLibrary()
                race_id = getattr(empire, 'race_id', None)
                if race_id:
                    return race_lib.get_race(race_id)
        except Exception:
            pass
        return None

    def _handle_colonize_button(self) -> None:
        """Handle the Colonize button press.

        Finds uncolonized planets at the selected fleet's location and
        either issues a colonize order directly (single planet) or
        prompts for planet selection (multiple planets).
        """
        ui = self.ui
        obj = ui.current_selection

        if not obj or not is_fleet(obj):
            return

        # Find Uncolonized Planets at Fleet Location
        from game.core.hex_math import hex_distance  # noqa: F401

        if not ui.scene.galaxy:
            return

        # Find System
        system = ui.scene.galaxy.get_system_of_object(obj)
        if not system:
            logger.debug("Colonize: Fleet not in system?")
            return

        # Find planets at this location (SYSTEM)
        candidates = []
        for p in system.planets:
            # Any planet in system is reachable if fleet is at system
            if p.owner_id is None:  # Unowned
                candidates.append(p)

        if not candidates:
            logger.debug("No unowned planets at this location.")
            return

        if len(candidates) == 1:
            # Single candidate, order directly
            ui.scene.request_colonize_order(obj, candidates[0])
        else:
            # Multiple -> Dialog
            def on_planet_selected(planet):
                ui.scene.request_colonize_order(obj, planet)

            ui.prompt_planet_selection(candidates, on_planet_selected)

    def _handle_window_close(self, event) -> None:
        """Handle UI_WINDOW_CLOSE events.

        Args:
            event: The pygame_gui window close event.
        """
        wm = self.ui.window_manager

        if event.ui_element == wm.fleet_orders_window:
            wm.fleet_orders_window = None
        elif event.ui_element == wm.star_list_window:
            wm._on_star_list_closed()
        elif event.ui_element == wm.fleet_report_window:
            wm.fleet_report_window = None
        elif event.ui_element == wm.transfer_dialog:
            wm.transfer_dialog = None
        elif event.ui_element == wm.build_queue_list_window:
            wm.build_queue_list_window = None
        elif event.ui_element == wm.empire_build_queue_window:
            wm._on_empire_build_queue_closed()
        elif event.ui_element == wm.event_log_window:
            wm._on_event_log_closed()
        elif event.ui_element == wm.empire_panel_window:
            wm._on_empire_panel_closed()
        elif event.ui_element == wm.move_choice_window:
            wm.move_choice_window = None
        elif event.ui_element == wm.cargo_quick_dialog:
            wm.cargo_quick_dialog = None
        elif event.ui_element == wm.planet_selection_window:
            wm.planet_selection_window = None
        elif event.ui_element == wm.system_selection_window:
            wm.system_selection_window = None
        elif event.ui_element == wm.fleet_selection_window:
            wm.fleet_selection_window = None

    def process_custom_events(self, event) -> None:
        """Process custom UI events from window callbacks.

        Args:
            event: The pygame event to check for custom UI callbacks.
        """
        # Custom UI callbacks are processed via window manager
        self.ui.window_manager.process_ui_callbacks(event)

    def handle_click(self, mx: int, my: int, button: int) -> bool:
        """Handle mouse clicks.

        Args:
            mx: Mouse x coordinate.
            my: Mouse y coordinate.
            button: Mouse button number.

        Returns:
            True if click was handled by UI, False otherwise.
        """
        # 1. Check logical sidebar area
        if mx > self.ui.width - self.ui.sidebar_width:
            return True

        # 2. Check if mouse is over an active modal/window that should block map clicks
        # PROJ-216: Replaced get_hovering_any_element() which was too broad and blocked
        # ALL clicks when hidden buttons (visible=0) were registered with pygame_gui.
        if self._is_blocking_ui_element_at(mx, my):
            return True

        return False

    def _is_blocking_ui_element_at(self, mx: int, my: int) -> bool:
        """Check if a blocking UI element (modal window, menu panel) is at the given position.

        Only actual interactive overlays should block map clicks - NOT hidden buttons,
        container panels, or decorative elements.

        PROJ-216: This replaces the overly broad get_hovering_any_element() check
        that was blocking all clicks due to hidden UI elements being registered.

        Args:
            mx: Mouse x coordinate.
            my: Mouse y coordinate.

        Returns:
            True if a blocking element is at the position, False otherwise.
        """
        wm = self.ui.window_manager

        # Check active windows that should block clicks
        blocking_windows = [
            ('fleet_orders_window', wm.fleet_orders_window),
            ('planet_list_window', wm.planet_list_window),
            ('star_list_window', wm.star_list_window),
            ('fleet_report_window', wm.fleet_report_window),
            ('transfer_dialog', wm.transfer_dialog),
            ('build_queue_list_window', wm.build_queue_list_window),
            ('empire_build_queue_window', wm.empire_build_queue_window),
            ('event_log_window', wm.event_log_window),
            ('empire_panel_window', wm.empire_panel_window),
            ('_pending_confirmation_dialog', getattr(wm, '_pending_confirmation_dialog', None)),
            ('move_choice_window', wm.move_choice_window),
            ('cargo_quick_dialog', wm.cargo_quick_dialog),
            ('planet_selection_window', wm.planet_selection_window),
            ('system_selection_window', wm.system_selection_window),
            ('fleet_selection_window', wm.fleet_selection_window),
        ]
        for name, window in blocking_windows:
            if window is not None:
                is_alive = window.alive()
                if is_alive and window.rect.collidepoint((mx, my)):
                    return True

        # Check menu panel
        if self.ui.menu_panel is not None:
            if self.ui.menu_panel.get_abs_rect().collidepoint((mx, my)):
                return True

        # Check top bar and resource bar (they are above the map)
        if hasattr(self.ui, 'top_bar') and self.ui.top_bar.rect.collidepoint((mx, my)):
            return True
        if hasattr(self.ui, 'resource_bar') and self.ui.resource_bar.rect.collidepoint((mx, my)):
            return True

        return False
