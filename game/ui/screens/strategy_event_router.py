"""Strategy UI event routing and handling.

This module contains the StrategyEventRouter class that handles all event
routing for the StrategyUI, including button presses, window management,
and click handling.

PROJ-86: God Class Decomposition - UI Tier
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

        # Check for build queue screen.
        # PROJ-376 Phase 2: gate on is_visible() — the cached screen
        # persists across opens; the modal-block semantics here mean
        # "is the build queue currently the focused overlay?".
        if (
            self.ui.scene.build_queue_screen is not None
            and self.ui.scene.build_queue_screen.is_visible()
        ):
            return True

        # PROJ-313 Phases 3-6: all strategy modal windows migrated to
        # StrategyModalWindow and tracked via wm.iter_live_modals()
        # (OR-bridge below). The slot-based scan path is empty.
        wm = self.ui.window_manager

        # PROJ-313: Live-list of StrategyModalWindow subclasses. Phases
        # 3-7 migrate the slot-based windows above into this list; Phase
        # 8 deletes the slot scans entirely. During the migration this
        # OR-bridge keeps both tracks active so each commit stays green.
        for _ in wm.iter_live_modals():
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

        # Esc handling (issue #18 + #20): precedence chain is top-bar menu
        # panel -> fleet context menu -> topmost live StrategyModalWindow.
        # PROJ-411 Task 2.5: modal close uses ``request_close()`` so
        # reusable subclasses (PlanetList/StarList/EmpireOverview/EventLog)
        # can hide() instead of kill(). Legacy modals' default
        # implementation routes through kill() unchanged.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.ui.menu_panel:
                self.ui.close_menu_panel()
                return
            if getattr(self.ui, "fleet_context_menu", None):
                self.ui.close_fleet_context_menu()
                return
            modals = list(self.ui.window_manager.iter_live_modals())
            if modals:
                modals[-1].request_close()
                return

        # Close menu panel on click outside
        if event.type == pygame.MOUSEBUTTONDOWN and self.ui.menu_panel:
            panel_rect = self.ui.menu_panel.get_abs_rect()
            menu_btn_rect = self.ui.btn_menu.get_abs_rect()
            if not panel_rect.collidepoint(event.pos) and not menu_btn_rect.collidepoint(event.pos):
                self.ui.close_menu_panel()

        # Close fleet context menu on click outside (issue #20). The menu
        # itself consumes button presses on its own buttons via the
        # pygame_gui UI_BUTTON_PRESSED path; this branch handles clicks
        # that landed elsewhere.
        fleet_menu = getattr(self.ui, "fleet_context_menu", None)
        if event.type == pygame.MOUSEBUTTONDOWN and fleet_menu:
            menu_rect = fleet_menu.get_abs_rect()
            if not menu_rect.collidepoint(event.pos):
                self.ui.close_fleet_context_menu()

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
        # Full modality (issue #12): top-bar buttons are inert while any
        # StrategyModalWindow is live. The user must close the modal first.
        # Mirrors the existing wheel-zoom guard in
        # StrategyInputHandler._handle_scroll.
        if self.has_modal_open():
            return

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

        # Get race config for species ideal button (PROJ-475: via facade)
        race_config = None
        try:
            race_config = scene.facade.empires.race_config(planet.owner_id)
        except Exception:  # Intentional broad catch: empire/race lookup may fail on save drift or library load errors; editor opens without race-specific UI
            pass

        def on_apply(planet_id, target) -> None:
            cmd = SetAtmosphereTargetCommand(planet_id=planet_id, atmosphere_target=target)
            scene.facade.handle_command(cmd)

        rect = create_centered_rect(700, 500, ui.width, ui.height)
        AtmosphereTargetEditor(
            rect=rect,
            manager=ui.manager,
            planet=planet,
            window_manager=ui.window_manager,
            on_apply_callback=on_apply,
            race_config=race_config,
        )

    def _open_planet_target_editor(
        self,
        planet,
        editor_cls,
        command_cls,
        target_kwarg: str,
        rect_size=(400, 300),
    ) -> None:
        """Open a planet target editor with the standard wiring.

        Extracted in PROJ-319 (DUP-X-06) from the three near-identical
        `_open_gravity_editor`, `_open_water_editor`, `_open_radiation_shield_editor`
        methods. Callers pass the editor class, the command class, and the
        keyword the command expects to receive the new target value under.
        """
        from game.ui.utils import create_centered_rect

        ui = self.ui
        scene = ui.scene
        race_config = self._get_race_config(planet)

        def on_apply(planet_id, target_value) -> None:
            cmd = command_cls(planet_id=planet_id, **{target_kwarg: target_value})
            scene.facade.handle_command(cmd)

        width, height = rect_size
        rect = create_centered_rect(width, height, ui.width, ui.height)
        editor_cls(
            rect=rect, manager=ui.manager, planet=planet,
            window_manager=ui.window_manager,
            on_apply_callback=on_apply, race_config=race_config,
        )

    def _open_gravity_editor(self, planet) -> None:
        """Open gravity target editor for a planet."""
        from game.ui.screens.gravity_target_editor import GravityTargetEditor
        from game.strategy.engine.commands import SetGravityTargetCommand
        self._open_planet_target_editor(
            planet, GravityTargetEditor, SetGravityTargetCommand, "gravity_target",
        )

    def _open_water_editor(self, planet) -> None:
        """Open water target editor for a planet."""
        from game.ui.screens.water_target_editor import WaterTargetEditor
        from game.strategy.engine.commands import SetWaterTargetCommand
        self._open_planet_target_editor(
            planet, WaterTargetEditor, SetWaterTargetCommand, "water_target",
        )

    def _open_radiation_shield_editor(self, planet) -> None:
        """Open radiation shield editor for a planet."""
        from game.ui.screens.radiation_shield_editor import RadiationShieldEditor
        from game.strategy.engine.commands import SetRadiationShieldTargetCommand
        self._open_planet_target_editor(
            planet, RadiationShieldEditor, SetRadiationShieldTargetCommand,
            "shielding_target",
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
        except Exception:  # Intentional broad catch: registry provider may be uninitialized; food editor opens without resource catalog
            pass

        def resolve_race(race_id) -> Any:
            # Prefer empire's own race_config when race_ids match.
            empire_race = self._get_race_config(planet)
            if empire_race is not None and getattr(empire_race, "race_id", None) == race_id:
                return empire_race
            # Fallback: try RaceLibrary (covers multi-species colonies).
            try:
                from game.strategy.systems.race_library import RaceLibrary
                return RaceLibrary().get_race(race_id)
            except Exception:  # Intentional broad catch: RaceLibrary load surfaces I/O, JSON, and schema-validation errors; resolver returns None on failure
                return None

        def on_apply(planet_id, allocations) -> None:
            apply_allocations(planet, allocations)

        rect = create_centered_rect(640, 420, ui.width, ui.height)
        FoodAllocationEditor(
            rect=rect,
            manager=ui.manager,
            planet=planet,
            economy_config=economy,
            resource_catalog=resource_catalog,
            race_resolver=resolve_race,
            window_manager=ui.window_manager,
            on_apply_callback=on_apply,
        )

    def _get_race_config(self, planet) -> Any:
        """Get the race config for the planet's owning empire (PROJ-475: via facade)."""
        ui = self.ui
        scene = ui.scene
        try:
            return scene.facade.empires.race_config(planet.owner_id)
        except Exception:  # Intentional broad catch: empire/race lookup may fail on save drift or library load errors; caller falls back to None
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

        # Find System (PROJ-477 Phase 4: live system via scene.world; the
        # caller iterates the resolved system's LIVE .planets, so this needs
        # the live StarSystem, NOT a SystemInfo summary — POST-FLESH B2).
        system = ui.scene.world.system_for_object(obj)
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
            def on_planet_selected(planet) -> None:
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

        # Check active windows that should block clicks.
        # PROJ-313: Slot scans here are being phased out as windows migrate
        # to StrategyModalWindow; migrated windows participate via
        # wm.iter_live_modals() in the OR-bridge below.
        blocking_windows = [
            ('_pending_confirmation_dialog', getattr(wm, '_pending_confirmation_dialog', None)),
        ]
        for name, window in blocking_windows:
            if window is not None:
                is_alive = window.alive()
                if is_alive and window.rect.collidepoint((mx, my)):
                    return True

        # Full modality (issue #12): any live StrategyModalWindow blocks
        # all background clicks regardless of click position. This
        # replaces the prior rect-coincident check so that clicks in the
        # gutter outside a 90%-screen registry/empire window cannot leak
        # through to the hex grid behind it. iter_live_modals already
        # filters dead refs.
        for _ in wm.iter_live_modals():
            return True

        # Check menu panel
        if self.ui.menu_panel is not None:
            if self.ui.menu_panel.get_abs_rect().collidepoint((mx, my)):
                return True

        # Check fleet right-click context menu (issue #20). Without this
        # branch, a left-click on a menu row falls through to
        # ``_handle_picking``, which calls ``on_ui_selection`` mid
        # MOUSEBUTTONDOWN/UP cycle and prevents the queued
        # UI_BUTTON_PRESSED from reaching the panel's dispatcher.
        fleet_menu = getattr(self.ui, "fleet_context_menu", None)
        if fleet_menu is not None:
            if fleet_menu.get_abs_rect().collidepoint((mx, my)):
                return True

        # Check top bar and resource bar (they are above the map)
        if hasattr(self.ui, 'top_bar') and self.ui.top_bar.rect.collidepoint((mx, my)):
            return True
        if hasattr(self.ui, 'resource_bar') and self.ui.resource_bar.rect.collidepoint((mx, my)):
            return True

        return False
