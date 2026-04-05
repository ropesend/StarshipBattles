"""
Design Workshop Screen - MVVM-based ship design editor.

Production version of the ship builder with dependency injection and MVVM architecture.
"""
import logging
import os
from typing import Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UIWindow
from pygame_gui.windows import UIConfirmationDialog

from game.core.profiling import profile_block
from game.core.constants import LayerType
from game.core.paths import Paths
from game.ui.fonts import get_font
from game.ui.renderer.sprites import SpriteManager
from game.ui.panels.builder_widgets import ModifierEditorPanel
from game.ui.assets import ShipThemeManager
from game.ui.screens.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from game.ui.panels.component_modifier_grid_panel import ComponentModifierGridPanel
from game.ui.screens.builder.schematic_view import SchematicView
from game.ui.screens.builder.interaction_controller import InteractionController
from game.ui.screens.builder.event_bus import EventBus
from game.ui.screens.builder_utils import PANEL_WIDTHS, PANEL_HEIGHTS, BuilderEvents, calculate_dynamic_layer_width, calculate_bottom_panel_height
from game.ui.services.screenshot_manager import ScreenshotManager
from game.ui.screens.workshop_event_router import WorkshopEventRouter
from game.ui.screens.workshop_viewmodel import WorkshopViewModel
from game.ui.screens.builder_selection import process_selection_change, get_primary_selection
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.ui.services.ship_io_adapter import ShipIOAdapter
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.screens.workshop_ship_io import WorkshopShipIO
from game.ui.screens.workshop_data_reloader import WorkshopDataReloader
from game.ui.colors import COLORS
from game.ui.screens.builder.detail_panel import ComponentDetailPanel
from game.ui.screens.builder.modifier_logic import ModifierLogic
from game.ui.services.vehicle_class_service import VehicleClassService

logger = logging.getLogger(__name__)

BG_COLOR = COLORS['bg_deep']




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

        # PROJ-211: Initialize ModifierLogic with registry provider
        ModifierLogic.init_service(context.registries)

        # Instance-based service (used by panels that accept it)
        from game.ui.screens.builder.modifier_logic import ModifierLogicService
        self._modifier_logic = ModifierLogicService(context.registries)

        # PROJ-43: UI service adapters for ship I/O and design loading
        self._ship_io_adapter = ShipIOAdapter()
        self._design_loader_adapter = DesignLoaderAdapter(registry_provider=context.registries)

        # PROJ-211: Create VehicleClassService for sub-panels
        self._vehicle_class_service = VehicleClassService(context.registries)

        # MVVM: Create ViewModel to manage builder state
        # PROJ-38: Pass context for DI
        self.viewmodel = WorkshopViewModel(self.event_bus, screen_width, screen_height, context=context)
        
        # UI Manager
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
            logger.debug(f"Workshop set ship.theme_id to {self.viewmodel.ship.theme_id}")
        else:
            logger.debug(f"Workshop NOT setting theme - integrated={self.context.is_integrated()}, empire_theme_id={self.context.empire_theme_id}")
        
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
        # PROJ-211: Pass VehicleClassService for strict DI
        self.view = SchematicView(
            rect, self.sprite_mgr, self.theme_manager,
            vehicle_class_service=self._vehicle_class_service
        )
        self.controller = InteractionController(self, self.view)
        
        self.error_message = ""
        self.error_timer = 0
        self.show_firing_arcs = False

        # Event Router (composition pattern for event handling)
        self.event_router = WorkshopEventRouter(self)

        # Pre-declare all button attributes (mode-dependent buttons may not be created)
        self.clear_btn: Optional[UIButton] = None
        self.save_btn: Optional[UIButton] = None
        self.load_btn: Optional[UIButton] = None
        self.arc_toggle_btn: Optional[UIButton] = None
        self.target_btn: Optional[UIButton] = None
        self.hull_toggle_btn: Optional[UIButton] = None
        self.std_data_btn: Optional[UIButton] = None
        self.test_data_btn: Optional[UIButton] = None
        self.select_data_btn: Optional[UIButton] = None
        self.verbose_btn: Optional[UIButton] = None
        self.obsolete_btn: Optional[UIButton] = None
        self.start_btn: Optional[UIButton] = None
        self.pending_action = None

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

        # PROJ-61: Data reload orchestrator (after _create_ui so panels exist)
        self.data_reloader = WorkshopDataReloader(
            context=self.context,
            ship_io_adapter=self._ship_io_adapter,
            viewmodel=self.viewmodel,
            show_error_callback=self.show_error,
            get_vehicle_classes_callback=self._get_vehicle_classes,
            event_bus=self.event_bus,
            right_panel_ref=lambda: self.right_panel,
            left_panel_ref=lambda: self.left_panel,
            view_ref=lambda: self.view,
            controller_ref=lambda: self.controller,
            rebuild_modifier_ui_callback=self.rebuild_modifier_ui,
            update_stats_callback=self.update_stats
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
            
            # PROJ-211: Pass VehicleClassService for strict DI
            self.right_panel = BuilderRightPanel(
                self, self.ui_manager,
                pygame.Rect(self.width - self.right_panel_width, 0,
                            self.right_panel_width, self.height - self.bottom_bar_height),
                event_bus=self.event_bus,
                viewmodel=self.viewmodel,
                vehicle_class_service=self._vehicle_class_service,
                hide_theme_selector=self.context.is_integrated()
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
                registries=self.context.registries,
                modifier_logic=self._modifier_logic
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
                event_bus=self.event_bus,
                modifier_logic=self._modifier_logic
            )
        
        # Bottom Bar Buttons
        btn_y = self.height - self.bottom_bar_height + 10
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
        self.viewmodel.selected_components = new_list

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
        self.viewmodel.selected_components = value

    @property
    def available_components(self):
        return self.viewmodel.available_components

    @available_components.setter
    def available_components(self, value):
        self.viewmodel.available_components = value

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0
        
    def handle_event(self, event):
        """Route events through the event router (IScene protocol).

        All event handling logic has been extracted to WorkshopEventRouter
        for better maintainability.
        """
        return self.event_router.handle_event(event)

    def handle_resize(self, width: int, height: int):
        """Handle window resize (IScene protocol).

        Note: Full resize requires recreating UI panels. For now, just update dimensions.
        """
        self.width = width
        self.height = height
        self.ui_manager.set_window_resolution((width, height))
        # Recalculate dynamic widths
        self.layer_panel_width = calculate_dynamic_layer_width(width)
        # Note: Full panel recreation would require significant refactoring
        # For now, the workshop handles resize gracefully but may need manual reload

    def execute_pending_action(self):
        """Execute the action stored in self.pending_action."""
        if self.pending_action:
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

    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt
            
        self.left_panel.update(dt)
        self.layer_panel.update(dt)
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
        if not hovered and self.weapons_report_panel.hovered_weapon:
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
        
        if self.controller.dragged_item:
            mx, my = pygame.mouse.get_pos()
            sprite = self.sprite_mgr.get_sprite(self.controller.dragged_item.sprite_index)
            if sprite:
                screen.blit(sprite, (mx - 16, my - 16))
                
        if self.error_timer > 0:
            font = get_font(18)
            err_surf = font.render(self.error_message, True, COLORS['text_error'])
            x = (self.width - err_surf.get_width()) // 2
            screen.blit(err_surf, (x, 50))

    def save_ship(self):
        """Save ship design (delegates to WorkshopShipIO)."""
        self.ship_io.save_ship()

    def load_ship(self):
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
        logger.info(message)

    def show_clear_confirmation(self):
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

        self.weapons_report_panel.clear_target()

    def on_select_target_pressed(self):
        """Select target ship (delegates to WorkshopShipIO)."""
        self.ship_io.select_target()

    def cleanup(self):
        """
        Clean up all UI elements when exiting the workshop.

        This must be called when transitioning away from the workshop to prevent
        UI remnants from appearing in other screens.
        """
        # Clear the UI manager to remove all pygame_gui elements
        if self.ui_manager:
            self.ui_manager.clear_and_reset()

