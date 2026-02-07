import math
from tkinter import filedialog
import os

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UIButton, UIDropDownMenu, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from game.core.logger import log_info
from game.core.profiling import profile_block
from game.core.constants import LayerType
from game.core.paths import Paths
from game.ui.renderer.sprites import SpriteManager
from game.ui.panels.builder_widgets import ModifierEditorPanel
from game.ui.assets import ShipThemeManager
from game.ui.screens.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel
from game.ui.screens.builder.schematic_view import SchematicView
from game.ui.screens.builder.interaction_controller import InteractionController
from game.ui.screens.builder.event_bus import EventBus
from game.ui.screens.builder_utils import PANEL_WIDTHS, PANEL_HEIGHTS, BuilderEvents, calculate_dynamic_layer_width, calculate_bottom_panel_height
from game.core.screenshot_manager import ScreenshotManager
from game.ui.screens.workshop_event_router import WorkshopEventRouter
from game.ui.screens.workshop_data_loader import WorkshopDataLoader
from game.ui.screens.workshop_viewmodel import WorkshopViewModel
from game.ui.screens.builder_selection import process_selection_change, get_primary_selection
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.ui.services.ship_io_adapter import ShipIOAdapter
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.screens.workshop_ship_io import WorkshopShipIO
from game.ui.colors import COLORS
from game.ui.screens.builder.detail_panel import ComponentDetailPanel
from game.core.logger import log_debug, log_error, log_warning

BG_COLOR = COLORS['bg_deep']
PANEL_BG = '#14181f'








class DesignWorkshopScreen:
    def __init__(self, screen_width, screen_height, context: WorkshopContext):
        """
        Initialize Design Workshop GUI.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            context: WorkshopContext defining launch mode and configuration

        Example:
            >>> context = WorkshopContext.standalone(tech_preset_name="early_game")
            >>> workshop = DesignWorkshopScreen(1920, 1080, context)
        """
        self.width = screen_width
        self.height = screen_height
        self.context = context
        self.on_start_battle = context.on_return  # Use context's callback

        self.event_bus = EventBus()
        self.screenshot_manager = ScreenshotManager.instance()

        # PROJ-43: UI service adapters for ship I/O and design loading
        self._ship_io_adapter = ShipIOAdapter()
        self._design_loader_adapter = DesignLoaderAdapter(registries=context.registries)

        # MVVM: Create ViewModel to manage builder state
        # PROJ-38: Pass context for DI
        self.viewmodel = WorkshopViewModel(self.event_bus, screen_width, screen_height, context=context)
        
        # UI Manager
        from game.core.paths import Paths
        theme_path = os.path.join(Paths.DATA_DIR, 'builder_theme.json')
        with profile_block("Builder: Init UIManager"):
            self.ui_manager = pygame_gui.UIManager(
                (screen_width, screen_height),
                theme_path=theme_path if os.path.exists(theme_path) else None
            )
        
        # Ship - now managed by ViewModel
        self.viewmodel.create_default_ship()

        # In integrated mode, set ship theme from empire
        if self.context.is_integrated() and self.context.empire_theme_id:
            self.viewmodel.set_ship_theme(self.context.empire_theme_id)
            log_debug(f"Workshop set ship.theme_id to {self.viewmodel.ship.theme_id}")
        else:
            log_debug(f"Workshop NOT setting theme - integrated={self.context.is_integrated()}, empire_theme_id={self.context.empire_theme_id}")
        
        # Managers
        self.viewmodel.refresh_available_components()
        self.sprite_mgr = SpriteManager.instance()
        
        with profile_block("Builder: Init Managers"):
            self.theme_manager = ShipThemeManager.instance()
            self.theme_manager.initialize() # No path needed anymore
        
        # Layout (from centralized constants)
        self.left_panel_width = PANEL_WIDTHS.component_palette
        self.right_panel_width = PANEL_WIDTHS.right_panel
        self.layer_panel_width = calculate_dynamic_layer_width(screen_width)
        self.detail_panel_width = PANEL_WIDTHS.detail_panel
        self.bottom_bar_height = PANEL_HEIGHTS.bottom_bar
        self.weapons_report_height = PANEL_HEIGHTS.weapons_report
        self.modifier_grid_panel_height = PANEL_HEIGHTS.modifier_grid_panel
        
        # MVC Lite
        # Schematic View shifted right
        sch_x = self.left_panel_width + self.layer_panel_width
        rect = pygame.Rect(
            sch_x, 0,
            self.width - sch_x - self.right_panel_width,
            self.height - self.bottom_bar_height - self.weapons_report_height - self.modifier_grid_panel_height
        )
        self.view = SchematicView(rect, self.sprite_mgr, self.theme_manager)
        self.controller = InteractionController(self, self.view)
        
        self.error_message = ""
        self.error_timer = 0
        self.show_firing_arcs = False
        
        self.show_firing_arcs = False
        
        # Selection now managed by ViewModel - proxy property below

        
        # Event Router (composition pattern for event handling)
        self.event_router = WorkshopEventRouter(self)

        self._create_ui()

        # PROJ-61: Ship I/O handler (after _create_ui so weapons_report_panel exists)
        self.ship_io = WorkshopShipIO(
            context=self.context,
            ui_manager=self.ui_manager,
            screen_width=screen_width,
            screen_height=screen_height,
            ship_io_adapter=self._ship_io_adapter,
            design_loader_adapter=self._design_loader_adapter,
            viewmodel=self.viewmodel,
            weapons_report_panel_ref=lambda: self.weapons_report_panel,
            show_error_callback=self.show_error,
            apply_loaded_ship_callback=self._apply_loaded_ship
        )

    def _get_vehicle_classes(self):
        """PROJ-50: Get vehicle_classes from context registries (required)."""
        return self.context.registries.vehicle_classes

    def _create_ui(self):
        """Initialize all UI panels for the workshop screen.

        Creates and lays out:
        - Left panel: Design library / component selection
        - Right panel: Ship stats display and portrait
        - Layer panel: Component slots organized by layer type
        - Detail panel: Selected component or design details
        - Bottom bar: Action buttons (new, save, load, exit)
        - Modifier panel: Modifier controls for selected component
        - Weapons report: Weapon loadout summary
        """
        # Use shared height calculation for bottom panels
        self.bottom_panel_height = calculate_bottom_panel_height(self.height)
        self.modifier_panel_height = self.bottom_panel_height
        self.weapons_report_height = self.bottom_panel_height  # Override instance variable
        avail_height = self.height - self.bottom_bar_height
        panels_height = avail_height - self.modifier_panel_height
        
        with profile_block("Builder: Init Panels (Left/Right/Layer)"):
            self.left_panel = BuilderLeftPanel(
                self, self.ui_manager,
                pygame.Rect(0, 0, self.left_panel_width, panels_height),
                event_bus=self.event_bus,
                viewmodel=self.viewmodel
            )
            
            # New Layer Panel
            self.layer_panel = LayerPanel(
                self, self.ui_manager,
                pygame.Rect(self.left_panel_width, 0, self.layer_panel_width, panels_height),
                viewmodel=self.viewmodel
            )
            # Register Drop Target
            self.controller.register_drop_target(self.layer_panel)
            
            self.right_panel = BuilderRightPanel(
                self, self.ui_manager,
                pygame.Rect(self.width - self.right_panel_width, 0,
                            self.right_panel_width, self.height - self.bottom_bar_height),
                event_bus=self.event_bus,
                viewmodel=self.viewmodel
            )
            
            # Modifier Panel (Bottom Spanning Left+Layer)
            mod_panel_rect = pygame.Rect(
                0, panels_height,
                self.left_panel_width + self.layer_panel_width,
                self.modifier_panel_height
            )
            
            # We need a wrapper panel for the modifier editor to draw into? 
            # ModifierEditorPanel expects a 'container' (UIPanel). 
            # Let's create one.
            self.modifier_container_panel = UIPanel(
                relative_rect=mod_panel_rect,
                manager=self.ui_manager,
                object_id='#modifier_panel_container'
            )
            
            # PROJ-38: Pass context registries to ModifierEditorPanel
            self.modifier_panel = ModifierEditorPanel(
                manager=self.ui_manager,
                container=self.modifier_container_panel,
                width=mod_panel_rect.width,
                on_change_callback=self._on_modifier_change,
                registries=self.context.registries
            )
            self.modifier_panel.set_panel_height(self.modifier_panel_height)
        
        weapons_panel_y = self.height - self.bottom_bar_height - self.weapons_report_height
        # Shifted weapons panel
        weapons_panel_x = self.left_panel_width + self.layer_panel_width
        weapons_panel_width = self.width - weapons_panel_x - self.right_panel_width
        with profile_block("Builder: Init Weapons Panel"):
            self.weapons_report_panel = WeaponsReportPanel(
                self, self.ui_manager,
                pygame.Rect(weapons_panel_x, weapons_panel_y, weapons_panel_width, self.weapons_report_height),
                self.sprite_mgr
            )

        # Detail Panel X position (needed for modifier grid width calculation)
        detail_x = self.width - self.right_panel_width - self.detail_panel_width

        # Component Modifier Grid Panel (above Weapons Report, ends at Component Report)
        modifier_grid_y = weapons_panel_y - self.modifier_grid_panel_height
        modifier_grid_width = detail_x - weapons_panel_x  # End at left edge of Component Report
        with profile_block("Builder: Init Modifier Grid Panel"):
            self.component_modifier_grid_panel = ComponentModifierGridPanel(
                self.ui_manager,
                pygame.Rect(weapons_panel_x, modifier_grid_y, modifier_grid_width, self.modifier_grid_panel_height),
                event_bus=self.event_bus
            )
        avail_height = self.height - self.bottom_bar_height - self.weapons_report_height
        
        # Component Image Path
        comp_img_path = os.path.join(Paths.ASSET_DIR, "Images", "Components")
        
        with profile_block("Builder: Init Detail Panel"):
            self.detail_panel = ComponentDetailPanel(
                self.ui_manager,
                pygame.Rect(detail_x, 0, self.detail_panel_width, avail_height),
                comp_img_path,
                event_bus=self.event_bus
            )
        
        # Bottom Bar Buttons
        btn_y = self.height - self.bottom_bar_height + 10
        btn_w = 140
        btn_h = 40
        spacing = 10

        # Define buttons to create based on launch mode
        # (Attribute Name, Text, Width)
        button_defs = self._get_button_definitions()
        
        total_width = sum(b[2] for b in button_defs) + spacing * (len(button_defs) - 1)
        start_x = (self.width - total_width) // 2
        
        current_x = start_x
        for attr_name, text, w in button_defs:
            btn = UIButton(pygame.Rect(current_x, btn_y, w, btn_h), text, self.ui_manager)
            setattr(self, attr_name, btn)
            current_x += w + spacing
        
        self.confirm_dialog = None
        
        self.update_stats()
        self.left_panel.update_component_list()
        self.rebuild_modifier_ui()


    def update_stats(self):
        # self.right_panel.update_stats_display(self.ship) # Now handled by event
        self.layer_panel.rebuild()
        self.event_bus.emit(BuilderEvents.SHIP_UPDATED, self.viewmodel.ship)
        
    def on_selection_changed(self, new_selection, append=False, toggle=False):
        """Handle selection changes.

        Args:
            new_selection: Single component tuple (layer, idx, comp), list of them, or None
            append: If True, add to existing selection instead of replacing
            toggle: If True, toggle selection state of existing items (Ctrl+Click)
        """
        # Use extracted selection logic
        new_list, _ = process_selection_change(
            self.viewmodel.selected_components, new_selection, self.viewmodel.ship,
            append=append, toggle=toggle
        )
        self.viewmodel._selected_components = new_list

        # Update primary selection
        self.selected_component = get_primary_selection(self.viewmodel.selected_components)

        self.rebuild_modifier_ui()
        self.event_bus.emit(BuilderEvents.SELECTION_CHANGED, self.selected_component)

    def _on_modifier_change(self):
        # Delegate to ViewModel - syncs modifiers across selection and emits SHIP_UPDATED
        self.viewmodel.sync_modifiers_to_selection()

    def rebuild_modifier_ui(self):
        editing_component = self.selected_component[2] if self.selected_component else None
        
        is_readonly = False
        if editing_component and editing_component.layer_assigned == LayerType.HULL:
             is_readonly = True
             
        # Start Y is 0 relative to the modifier container panel
        self.modifier_panel.rebuild(editing_component, is_readonly=is_readonly)
        self.modifier_panel.layout(0)
        
    @property
    def selected_component(self):
        return self.controller.selected_component
        
    @selected_component.setter
    def selected_component(self, value):
        self.controller.selected_component = value
        
    @property
    def dragged_item(self):
        return self.controller.dragged_item
        
    @dragged_item.setter
    def dragged_item(self, value):
        self.controller.dragged_item = value

    # --- Viewmodel delegation properties (used by builder sub-panels) ---
    @property
    def ship(self):
        return self.viewmodel.ship

    @property
    def selected_components(self):
        return self.viewmodel.selected_components

    @selected_components.setter
    def selected_components(self, value):
        self.viewmodel._selected_components = value

    @property
    def available_components(self):
        return self.viewmodel.available_components

    @available_components.setter
    def available_components(self, value):
        self.viewmodel.available_components = value

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0
        
    def _show_error(self, msg):
        self.show_error(msg)
        
    def handle_event(self, event):
        """Route events through the event router.
        
        All event handling logic has been extracted to WorkshopEventRouter
        for better maintainability.
        """
        return self.event_router.handle_event(event)

    def _execute_pending_action(self):
        """Execute the action stored in self.pending_action."""
        if hasattr(self, 'pending_action') and self.pending_action:
            act, data = self.pending_action
            if act == 'clear_design':
                self._clear_design()
            elif act == 'change_class':
                # Refit - use viewmodel which delegates to service
                self.viewmodel.change_ship_class(data, migrate_components=True)
                self.update_stats()
                self.right_panel.update_portrait_image()
                self.left_panel.update_component_list()
            elif act == 'change_type':
                # Clear and Change - use viewmodel which delegates to service
                self.viewmodel.change_ship_class(data, migrate_components=False)

                # Update the Class Dropdown options via right_panel method
                classes = self._get_vehicle_classes()
                new_type = classes[data].get('type', 'Ship')
                valid_classes = [(n, classes[n].get('max_mass', 0)) for n, c in classes.items() if c.get('type', 'Ship') == new_type]
                valid_classes.sort(key=lambda x: x[1])
                valid_class_names = [n for n, _ in valid_classes]
                if not valid_class_names:
                    valid_class_names = ["Escort"]

                self.right_panel.update_class_dropdown(data, valid_class_names)

                self.update_stats()
                self.right_panel.update_portrait_image()
                self.left_panel.update_component_list()
            
            self.pending_action = None
        else:
            # Fallback for simple clear if pending_action not set
            self._clear_design()

    def _debug_sequence_capture(self):
        """test sequence capture for draw order debugging."""
        log_info("Starting debug sequence capture...")
        # Note: In a real scenario, this would likely be hooked into the draw loop 
        # or a specific event. For this test, we will simulate a multi-step capture 
        # by manually capturing the current state with different labels, 
        # implying we would call this between draw calls.
        
        # 1. Capture "Start"
        self.screenshot_manager.capture_step("1_start_sequence")
        
        # 2. Simulate "Draw Background" (just capturing same frame for test)
        self.screenshot_manager.capture_step("2_draw_background")
        
        # 3. Simulate "Draw Ships"
        self.screenshot_manager.capture_step("3_draw_ships")
        
        # 4. Simulate "Draw UI"
        self.screenshot_manager.capture_step("4_draw_ui")
        
        log_info("Debug sequence capture complete.")


    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt
            
        self.left_panel.update(dt)
        self.layer_panel.update(dt)
        if hasattr(self.modifier_panel, 'update'):
            self.modifier_panel.update(dt)
            
        self.weapons_report_panel.update()
        self.controller.update()

        # Update Detail Panel
        target_comp = None
        if self.controller.selected_component:
            target_comp = self.controller.selected_component[2]
        else:
            # Check schematic hover
            if self.controller.hovered_component:
                target_comp = self.controller.hovered_component
            else:
                 # Check left panel hover
                 mx, my = pygame.mouse.get_pos()
                 hovered_item = self.left_panel.get_hovered_list_item(mx, my)
                 if hovered_item:
                     # Show preview with default modifiers
                     target_comp = hovered_item.component

        self.detail_panel.show_component(target_comp)
        self.ui_manager.update(dt)
        
        # Check name entry - use ViewModel to update name
        new_name = self.right_panel.name_entry.get_text()
        if new_name != self.viewmodel.ship.name:
            self.viewmodel.set_ship_name(new_name)

    def draw(self, screen):
        screen.fill(BG_COLOR)
        
        # Determine efficient hover
        hovered = self.controller.hovered_component
        if not hovered:
             mx, my = pygame.mouse.get_pos()
             if not self.view.rect.collidepoint(mx, my):
                 hovered_item = self.left_panel.get_hovered_list_item(mx, my)
                 if hovered_item:
                     # Show component with default modifiers
                     hovered = hovered_item.component
        
        # Also check if hovering a weapon in the weapons report panel
        if not hovered and hasattr(self, 'weapons_report_panel'):
            if self.weapons_report_panel.hovered_weapon:
                hovered = self.weapons_report_panel.hovered_weapon
                     
        self.view.draw(screen, self.viewmodel.ship, self.show_firing_arcs, self.controller.selected_component, hovered)
        
        self.ui_manager.draw_ui(screen)
        self.left_panel.draw(screen)  # Draw hover highlights AFTER UI manager
        # Layer panel drawing removed (it's handled by UI manager + overlay highlights handled by panel.draw if any)
        self.layer_panel.draw(screen)  # Draw selection highlights AFTER UI manager
        self.weapons_report_panel.draw(screen)

        # Skip custom drawing when modal windows are open to avoid z-order issues
        has_open_window = any(
            isinstance(el, UIWindow) and el.visible
            for el in self.ui_manager.get_root_container().elements
        )
        if not has_open_window:
            self.component_modifier_grid_panel.draw(screen)  # Draw modifier impact grid
            self.detail_panel.draw(screen)
        
        if hovered and not self.controller.dragged_item:
            # Tooltip removed
            pass
            
        if self.controller.dragged_item:
            mx, my = pygame.mouse.get_pos()
            sprite = self.sprite_mgr.get_sprite(self.controller.dragged_item.sprite_index)
            if sprite:
                screen.blit(sprite, (mx - 16, my - 16))
                
        if self.error_timer > 0:
            font = pygame.font.SysFont("Arial", 18)
            err_surf = font.render(self.error_message, True, COLORS['text_error'])
            x = (self.width - err_surf.get_width()) // 2
            screen.blit(err_surf, (x, 50))

    def _on_select_data_pressed(self):
        """Open dialog to select a data directory and reload game data."""
        if not tk_root:
            self.show_error("Tkinter not initialized, cannot open dialog")
            return
            
        initial_dir = os.path.join(os.getcwd(), "data")
        directory = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Data Directory"
        )
        
        if directory:
            with profile_block(f"Builder: Reload Data from {os.path.basename(directory)}"):
                self._reload_data(directory)

    def _load_standard_data(self):
        """Load standard data from 'data/' directory and set ship directory to 'ships/'."""
        with profile_block("Builder: Load Standard Data"):
            directory = os.path.join(os.getcwd(), "data")
            self._reload_data(directory)
            # PROJ-43: Use adapter instead of direct ShipIO access
            self._ship_io_adapter.set_ships_folder("ships")
            self.show_error("Loaded Standard Data • Ships: ships/")

    def _load_test_data(self):
        """Load test data from 'tests/data/' directory and set ship directory to 'tests/data/ships/'."""
        with profile_block("Builder: Load Test Data"):
            directory = os.path.join(os.getcwd(), "tests", "data")
            self._reload_data(directory)
            # PROJ-43: Use adapter instead of direct ShipIO access
            self._ship_io_adapter.set_ships_folder(os.path.join("tests", "data", "ships"))
            self.show_error("Loaded Test Data • Ships: tests/data/ships/")

    def _reload_data(self, directory: str):
        """Reload global game data from the specified directory.
        
        Data loading is delegated to WorkshopDataLoader for better testability.
        UI refresh logic remains in this class.
        """
        try:
            # 1. Load data via dedicated loader (PROJ-50: pass registries)
            loader = WorkshopDataLoader(directory, registries=self.context.registries)
            result = loader.load_all()
            
            if not result.success:
                for error in result.errors:
                    log_error(error)
                self.show_error(f"Data loading failed: {result.errors[0] if result.errors else 'Unknown error'}")
                return
            
            # 2. Refresh UI (stays in BuilderScreen)
            self._refresh_ui_after_data_reload(result.default_class)
            
            # Show success
            self.show_error(f"Reloaded data from {os.path.basename(directory)}")
            
        except Exception as e:
            import traceback
            log_error(f"Failed to reload data: {e}\n{traceback.format_exc()}")
            self.show_error(f"Error reloading data: {e}")
    
    def _refresh_ui_after_data_reload(self, default_class: str):
        """Refresh all UI panels after data reload.
        
        Extracted from _reload_data to separate data loading from UI concerns.
        
        Args:
            default_class: The default ship class to use after reload
        """
        # Refresh UI panels
        self.right_panel.refresh_controls()
        self.left_panel.update_component_list()
        self.rebuild_modifier_ui()

        # Refresh Builder State (PROJ-43: Use viewmodel instead of direct get_all_components)
        self.viewmodel.refresh_available_components()

        # Reset Ship with new default class (using service layer via viewmodel)
        self.viewmodel.ship = self.viewmodel.create_default_ship(ship_class=default_class)
        
        # Reset UI Panels
        self.left_panel.update_component_list()
        
        # Center View
        self.view.selected_component = None
        self.controller.selected_component = None
        self.viewmodel._selected_components = []
        
        # Update dropdowns via right_panel method
        classes = self._get_vehicle_classes()
        self.right_panel.update_dropdowns_for_data_reload(default_class, classes)

        self.update_stats()
        self.rebuild_modifier_ui()
        
        # Emit registry reload event for decoupled UI sync
        self.event_bus.emit(BuilderEvents.REGISTRY_RELOADED, None)
    
    # Tooltip method removed


    def _save_ship(self):
        """Save ship design (delegates to WorkshopShipIO)."""
        self.ship_io.save_ship()

    def _load_ship(self):
        """Load ship design (delegates to WorkshopShipIO)."""
        self.ship_io.load_ship()

    def _apply_loaded_ship(self, new_ship, message):
        """Apply a loaded ship to the workshop"""
        self.viewmodel.ship = new_ship
        # Fully refresh UI controls to match new ship state
        self.right_panel.refresh_controls()

        self.update_stats()
        # Also update the layers panel in case components changed
        self.layer_panel.rebuild()
        self.left_panel.update_component_list() # Update available components based on hull type
        self.rebuild_modifier_ui()
        log_info(message)

    def _show_clear_confirmation(self):
        self.pending_action = ('clear_design', None)
        self.confirm_dialog = UIConfirmationDialog(
            rect=pygame.Rect((self.width // 2 - 150, self.height // 2 - 100), (300, 200)),
            action_long_desc="Clear all components and reset to default settings?",
            manager=self.ui_manager,
            window_title="Confirm Clear"
        )

    def _get_button_definitions(self):
        """
        Returns button definitions based on launch mode.

        Standalone mode shows all debug/testing buttons.
        Integrated mode shows only production-ready buttons.

        Returns:
            List of tuples: (attribute_name, button_text, width)
        """
        # Common buttons (always visible in both modes)
        buttons = [
            ('clear_btn', "Clear Design", 110),
            ('save_btn', "Save", 80),
            ('load_btn', "Load", 80),
            ('arc_toggle_btn', "Show Firing Arcs", 140),
            ('target_btn', "Select Target", 110),
        ]

        # Standalone-only buttons (debug/testing features)
        if self.context.mode == WorkshopMode.STANDALONE:
            buttons.extend([
                ('hull_toggle_btn', "Show Hull", 100),
                ('std_data_btn', "Standard Data", 110),
                ('test_data_btn', "Test Data", 90),
                ('select_data_btn', "Select Data...", 110),
                ('verbose_btn', "Toggle Verbose", 120),
            ])

        # Integrated-only buttons (strategy layer features)
        if self.context.mode == WorkshopMode.INTEGRATED:
            buttons.append(
                ('obsolete_btn', "Mark Obsolete", 130)
            )

        # Return button (always last)
        buttons.append(('start_btn', "Return", 100))

        return buttons

    def _clear_design(self):
        # Delegate ship mutation to ViewModel
        self.viewmodel.clear_design()

        # Refresh UI (ViewModel handles ship state; GUI handles UI refresh)
        self.right_panel.refresh_controls()
        self.update_stats()
        self.rebuild_modifier_ui()
        self.controller.selected_component = None
        self.on_selection_changed(None)

        if hasattr(self, 'weapons_report_panel'):
            self.weapons_report_panel.clear_target()

    def _on_select_target_pressed(self):
        """Select target ship (delegates to WorkshopShipIO)."""
        self.ship_io.select_target()

    def cleanup(self):
        """
        Clean up all UI elements when exiting the workshop.

        This must be called when transitioning away from the workshop to prevent
        UI remnants from appearing in other screens.
        """
        # Clear the UI manager to remove all pygame_gui elements
        if hasattr(self, 'ui_manager') and self.ui_manager:
            self.ui_manager.clear_and_reset()

