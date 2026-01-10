import json
import math
import tkinter
from tkinter import simpledialog, filedialog
import os

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu, 
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from game.core.profiling import profile_action, profile_block

from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager, get_component_registry, get_modifier_registry, get_vehicle_classes
from game.simulation.components.component import (
    get_all_components
)
from game.ui.renderer.sprites import SpriteManager
from game.simulation.preset_manager import PresetManager
from game.simulation.systems.persistence import ShipIO
from game.ui.panels.builder_widgets import ModifierEditorPanel
from game.simulation.ship_theme import ShipThemeManager
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from game.ui.screens.builder_utils import PANEL_WIDTHS, PANEL_HEIGHTS, MARGINS, BuilderEvents, calculate_dynamic_layer_width
from game.core.screenshot_manager import ScreenshotManager
from game.ui.screens.builder_event_router import BuilderEventRouter
from game.ui.screens.builder_data_loader import BuilderDataLoader
from game.ui.screens.builder_viewmodel import BuilderViewModel

# Initialize Tkinter root and hide it (for simpledialog)
# Initialize Tkinter root and hide it (for simpledialog)
try:
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        tk_root = None
    else:
        tk_root = tkinter.Tk()
        tk_root.withdraw()
except:
    tk_root = None


# Colors
from ui.colors import COLORS
BG_COLOR = COLORS['bg_deep']
PANEL_BG = '#14181f'

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from ui.builder.detail_panel import ComponentDetailPanel








class BuilderSceneGUI:
    def __init__(self, screen_width, screen_height, on_start_battle):
        self.width = screen_width
        self.height = screen_height
        self.on_start_battle = on_start_battle
        
        self.event_bus = EventBus()
        self.screenshot_manager = ScreenshotManager.get_instance()
        
        # MVVM: Create ViewModel to manage builder state
        self.viewmodel = BuilderViewModel(self.event_bus, screen_width, screen_height)
        
        # UI Manager
        from game.core.constants import ROOT_DIR, DATA_DIR, ASSET_DIR
        theme_path = os.path.join(DATA_DIR, 'builder_theme.json')
        with profile_block("Builder: Init UIManager"):
            self.ui_manager = pygame_gui.UIManager(
                (screen_width, screen_height),
                theme_path=theme_path if os.path.exists(theme_path) else None
            )
        
        # Ship - now managed by ViewModel
        self.viewmodel.create_default_ship()
        
        # Managers
        self.viewmodel.refresh_available_components()
        self.sprite_mgr = SpriteManager.get_instance()
        
        with profile_block("Builder: Init Managers"):
            self.preset_manager = PresetManager(os.path.join(DATA_DIR, "presets.json"))
            self.theme_manager = ShipThemeManager.get_instance()
            self.theme_manager.initialize() # No path needed anymore
        
        # Layout (from centralized constants)
        self.left_panel_width = PANEL_WIDTHS.component_palette
        self.right_panel_width = PANEL_WIDTHS.right_panel
        self.layer_panel_width = calculate_dynamic_layer_width(screen_width)
        self.detail_panel_width = PANEL_WIDTHS.detail_panel
        self.bottom_bar_height = PANEL_HEIGHTS.bottom_bar
        self.weapons_report_height = PANEL_HEIGHTS.weapons_report
        
        # MVC Lite
        # Schematic View shifted right
        sch_x = self.left_panel_width + self.layer_panel_width
        rect = pygame.Rect(
            sch_x, 0,
            self.width - sch_x - self.right_panel_width,
            self.height - self.bottom_bar_height - self.weapons_report_height
        )
        self.view = SchematicView(rect, self.sprite_mgr, self.theme_manager)
        self.controller = InteractionController(self, self.view)
        
        self.error_message = ""
        self.error_timer = 0
        self.show_firing_arcs = False
        
        self.show_firing_arcs = False
        
        # Selection now managed by ViewModel - proxy property below

        
        # Event Router (composition pattern for event handling)
        self.event_router = BuilderEventRouter(self)
        
        self._create_ui()
        
    def _create_ui(self):
        # New Layout Dimensions
        self.modifier_panel_height = 360
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
                            self.right_panel_width, self.height - self.bottom_bar_height - self.weapons_report_height),
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
            
            self.modifier_panel = ModifierEditorPanel(
                manager=self.ui_manager,
                container=self.modifier_container_panel,
                width=mod_panel_rect.width,
                preset_manager=self.preset_manager,
                on_change_callback=self._on_modifier_change
            )
        
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

        # Detail Panel
        detail_x = self.width - self.right_panel_width - self.detail_panel_width
        avail_height = self.height - self.bottom_bar_height - self.weapons_report_height
        
        # Component Image Path
        from game.core.constants import ASSET_DIR
        comp_img_path = os.path.join(ASSET_DIR, "Images", "Components")
        
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
        
        # Define buttons to create in order
        # (Attribute Name, Text, Width)
        button_defs = [
            ('clear_btn', "Clear Design", 110),
            ('save_btn', "Save", 80),
            ('load_btn', "Load", 80),
            ('arc_toggle_btn', "Show Firing Arcs", 140),
            ('target_btn', "Select Target", 110),
            ('std_data_btn', "Standard Data", 110),
            ('test_data_btn', "Test Data", 90),
            ('select_data_btn', "Select Data...", 110),
            ('verbose_btn', "Toggle Verbose", 120),
            ('start_btn', "Return", 100)
        ]
        
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
        self.event_bus.emit('SHIP_UPDATED', self.ship)
        
    def on_selection_changed(self, new_selection, append=False, toggle=False):
        """
        Handle selection changes.
        new_selection: can be a single component tuple (layer, idx, comp), a list of them, or None.
        append: If True, add to existing selection instead of replacing.
        toggle: If True, toggles selection state of existing items (Ctrl+Click behavior).
        """
        if new_selection is None:
            if not append:
                self.selected_components = []
        else:
            if not isinstance(new_selection, list):
                new_selection = [new_selection]
            
            # Normalize to tuples if possible, or wrapping objects
            # Ideally we want (layer, index, comp)
            # If we get just component, we'll have to find it or wrap it
            
            norm_selection = []
            for item in new_selection:
                if isinstance(item, tuple) and len(item) == 3:
                    norm_selection.append(item)
                elif hasattr(item, 'id'): # It's a component
                     # Find it in ship?
                     found = False
                     for l_type, l_data in self.ship.layers.items():
                         try:
                             idx = l_data['components'].index(item)
                             norm_selection.append((l_type, idx, item))
                             found = True
                             break
                         except ValueError:
                             continue
                     if not found:
                         # Maybe it's a template (dragged)
                         norm_selection.append((None, -1, item))
            
            if append:
                # 1. Enforce Homogeneity
                # Check if new items match the type (definition ID) of existing selection
                if self.selected_components and norm_selection:
                    # Get definition ID of currently selected items (assuming they are homogeneous)
                    # We can check the first one.
                    current_def_id = self.selected_components[0][2].id
                    
                    # Check if all new items match this ID
                    matches_type = all(item[2].id == current_def_id for item in norm_selection)
                    
                    if not matches_type:
                        # User clicked a different type. Standard behavior: Replace selection.
                        # This feels cleaner than ignoring it.
                        self.selected_components = norm_selection
                        append = False # Treat as replace
                    else:
                        # Add unique items (Uniqueness based on OBJECT IDENTITY, not Def ID)
                        current_objs = {c[2] for c in self.selected_components}
                        for item in norm_selection:
                            if item[2] in current_objs:
                                if toggle:
                                    # Toggle OFF
                                    self.selected_components = [x for x in self.selected_components if x[2] is not item[2]]
                                else:
                                    # Ensure selected (do nothing if already there)
                                    pass
                            else:
                                self.selected_components.append(item)
                else:
                    # Nothing currently selected, just append (which effectively is a set)
                     self.selected_components = norm_selection
            else:
                self.selected_components = norm_selection

        # Update dependent UI
        # For properties panel, we generally show the LAST selected item (or first?)
        # Let's show the last one added to selection as "primary"
        self.selected_component = self.selected_components[-1] if self.selected_components else None
        
        # Update Builder State for Panel
        if self.selected_components:
             # If we have a group selected, layer panel needs to know?
             # Layer panel now highlights based on builder.selected_components check in its rebuild
             pass

        self.rebuild_modifier_ui()
        self.event_bus.emit('SELECTION_CHANGED', self.selected_component)

    def _on_modifier_change(self):
        # Propagate to ALL selected components
        if self.selected_components:
            # The modifier panel edits "editing_component".
            # We need to sync that to others.
            editing_comp = self.selected_component[2]
            
            for item in self.selected_components:
                comp = item[2]
                if comp is editing_comp: continue
                
                # Apply modifiers from editing_comp to comp
                # Copy modifiers
                comp.modifiers = []
                for m in editing_comp.modifiers:
                    new_m = m.__class__(m.definition, m.value)
                    comp.modifiers.append(new_m)
                comp.recalculate_stats()
                
            editing_comp.recalculate_stats()
            
        self.ship.recalculate_stats()
        # self.right_panel.update_stats_display(self.ship) # Now handled by event
        self.event_bus.emit('SHIP_UPDATED', self.ship)

    def rebuild_modifier_ui(self):
        editing_component = self.selected_component[2] if self.selected_component else None
        
        is_readonly = False
        if editing_component and editing_component.layer_assigned == LayerType.HULL:
             is_readonly = True
             
        # Start Y is 0 relative to the modifier container panel
        self.modifier_panel.rebuild(editing_component, self.template_modifiers, is_readonly=is_readonly)
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
    
    # ─────────────────────────────────────────────────────────────────
    # Backward-Compatible Proxy Properties (delegate to ViewModel)
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def ship(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.ship
        
    @ship.setter
    def ship(self, value):
        self.viewmodel.ship = value
        
    @property
    def selected_components(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.selected_components
        
    @selected_components.setter
    def selected_components(self, value):
        # Direct assignment to internal list for backward compat
        self.viewmodel._selected_components = value
        
    @property
    def template_modifiers(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.template_modifiers
        
    @template_modifiers.setter
    def template_modifiers(self, value):
        self.viewmodel.template_modifiers = value
        
    @property
    def available_components(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.available_components

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0
        
    def _show_error(self, msg):
        self.show_error(msg)
        
    def handle_event(self, event):
        """Route events through the event router.
        
        All event handling logic has been extracted to BuilderEventRouter
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
                # Refit
                self.ship.change_class(data, migrate_components=True)
                self.update_stats()
                self.right_panel.update_portrait_image()
                self.left_panel.update_component_list()
            elif act == 'change_type':
                # Clear and Change
                self.ship.change_class(data, migrate_components=False)
                
                # We also need to update the Class Dropdown options
                classes = get_vehicle_classes()
                new_type = classes[data].get('type', 'Ship')
                valid_classes = [(n, classes[n].get('max_mass', 0)) for n, c in classes.items() if c.get('type', 'Ship') == new_type]
                valid_classes.sort(key=lambda x: x[1])
                valid_class_names = [n for n, m in valid_classes]
                if not valid_class_names: valid_class_names = ["Escort"]
                
                self.right_panel.class_dropdown.kill()
                self.right_panel.class_dropdown = UIDropDownMenu(valid_class_names, data, 
                                                   pygame.Rect(70, self.right_panel.class_dropdown.relative_rect.y, 195, 30), 
                                                   manager=self.ui_manager, container=self.right_panel.panel)
                
                self.update_stats()
                self.right_panel.update_portrait_image()
                self.left_panel.update_component_list()
            
            self.pending_action = None
        else:
            # Fallback for simple clear if pending_action not set
            self._clear_design()

    def _debug_sequence_capture(self):
        """test sequence capture for draw order debugging."""
        logger.info("Starting debug sequence capture...")
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
        
        logger.info("Debug sequence capture complete.")


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
                     # Create preview with current template modifiers
                     comp_template = hovered_item.component
                     preview_comp = comp_template.clone()
                     for m_id, val in self.template_modifiers.items():
                        mods = get_modifier_registry()
                        if m_id in mods:
                            mod_def = mods[m_id]
                            if mod_def.restrictions and 'allow_types' in mod_def.restrictions and preview_comp.type_str not in mod_def.restrictions['allow_types']:
                                continue
                            preview_comp.add_modifier(m_id)
                            m = preview_comp.get_modifier(m_id)
                            if m: m.value = val
                     preview_comp.recalculate_stats()
                     target_comp = preview_comp
        
        self.detail_panel.show_component(target_comp)
        self.ui_manager.update(dt)
        
        # Check name entry
        if self.right_panel.name_entry.get_text() != self.ship.name:
            self.ship.name = self.right_panel.name_entry.get_text()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        
        # Determine efficient hover
        hovered = self.controller.hovered_component
        if not hovered:
             mx, my = pygame.mouse.get_pos()
             if not self.view.rect.collidepoint(mx, my):
                 hovered_item = self.left_panel.get_hovered_list_item(mx, my)
                 if hovered_item:
                     comp_template = hovered_item.component
                     preview_comp = comp_template.clone()
                     for m_id, val in self.template_modifiers.items():
                        mods = get_modifier_registry()
                        if m_id in mods:
                            mod_def = mods[m_id]
                            if mod_def.restrictions and 'allow_types' in mod_def.restrictions and preview_comp.type_str not in mod_def.restrictions['allow_types']:
                                continue
                            preview_comp.add_modifier(m_id)
                            m = preview_comp.get_modifier(m_id)
                            if m: m.value = val
                     preview_comp.recalculate_stats()
                     hovered = preview_comp
        
        # Also check if hovering a weapon in the weapons report panel
        if not hovered and hasattr(self, 'weapons_report_panel'):
            if self.weapons_report_panel.hovered_weapon:
                hovered = self.weapons_report_panel.hovered_weapon
                     
        self.view.draw(screen, self.ship, self.show_firing_arcs, self.controller.selected_component, hovered)
        
        self.ui_manager.draw_ui(screen)
        self.left_panel.draw(screen)  # Draw hover highlights AFTER UI manager
        # Layer panel drawing removed (it's handled by UI manager + overlay highlights handled by panel.draw if any)
        self.layer_panel.draw(screen)  # Draw selection highlights AFTER UI manager
        self.weapons_report_panel.draw(screen)
        
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
            ShipIO.default_ships_folder = "ships"
            self.show_error("Loaded Standard Data • Ships: ships/")

    def _load_test_data(self):
        """Load test data from 'tests/data/' directory and set ship directory to 'tests/data/ships/'."""
        with profile_block("Builder: Load Test Data"):
            directory = os.path.join(os.getcwd(), "tests", "data")
            self._reload_data(directory)
            ShipIO.default_ships_folder = os.path.join("tests", "data", "ships")
            self.show_error("Loaded Test Data • Ships: tests/data/ships/")

    def _reload_data(self, directory: str):
        """Reload global game data from the specified directory.
        
        Data loading is delegated to BuilderDataLoader for better testability.
        UI refresh logic remains in this class.
        """
        try:
            # 1. Load data via dedicated loader
            loader = BuilderDataLoader(directory)
            result = loader.load_all()
            
            if not result.success:
                for error in result.errors:
                    logger.error(error)
                self.show_error(f"Data loading failed: {result.errors[0] if result.errors else 'Unknown error'}")
                return
            
            # 2. Refresh UI (stays in BuilderSceneGUI)
            self._refresh_ui_after_data_reload(result.default_class)
            
            # Show success
            self.show_error(f"Reloaded data from {os.path.basename(directory)}")
            
        except Exception as e:
            logger.error(f"Failed to reload data: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Refresh Builder State
        self.available_components = get_all_components()
        self.template_modifiers = {}
        
        # Reset Ship with new default class
        self.ship = Ship("Custom Ship", self.width // 2, self.height // 2, (100, 100, 255), ship_class=default_class)
        self.ship.recalculate_stats()
        
        # Reset UI Panels
        self.left_panel.update_component_list()
        
        # Center View
        self.view.selected_component = None
        self.controller.selected_component = None
        self.selected_components = []
        
        # Update Class Dropdown
        classes = get_vehicle_classes()
        valid_classes = [(n, classes[n].get('max_mass', 0)) for n, c in classes.items()]
        valid_classes.sort(key=lambda x: x[1])
        valid_class_names = [n for n, m in valid_classes]
        if not valid_class_names: valid_class_names = ["Escort"]
        
        if hasattr(self.right_panel, 'class_dropdown'):
            self.right_panel.class_dropdown.kill()
            self.right_panel.class_dropdown = UIDropDownMenu(
                valid_class_names, 
                default_class,
                pygame.Rect(70, self.right_panel.class_dropdown.relative_rect.y, 195, 30), 
                manager=self.ui_manager, 
                container=self.right_panel.panel
            )
            
        # Update Type Dropdown if it exists
        if hasattr(self.right_panel, 'vehicle_type_dropdown'):
            classes = get_vehicle_classes()
            types = sorted(list(set(c.get('type', 'Ship') for c in classes.values())))
            if not types: types = ["Ship"]
            default_type = classes[default_class].get('type', 'Ship')
            
            self.right_panel.vehicle_type_dropdown.kill()
            self.right_panel.vehicle_type_dropdown = UIDropDownMenu(
                 types,
                 default_type,
                 pygame.Rect(70, self.right_panel.vehicle_type_dropdown.relative_rect.y, 195, 30),
                 manager=self.ui_manager,
                 container=self.right_panel.panel
            )
        
        self.update_stats()
        self.rebuild_modifier_ui()
        
        # Emit registry reload event for decoupled UI sync
        self.event_bus.emit(BuilderEvents.REGISTRY_RELOADED, None)
    
    # Tooltip method removed


    @profile_action("Builder: Save Ship")
    def _save_ship(self):
        success, message = ShipIO.save_ship(self.ship)
        if success: print(message)
        elif message: self.show_error(message)

    @profile_action("Builder: Load Ship")
    def _load_ship(self):
        new_ship, message = ShipIO.load_ship(self.width, self.height)
        if new_ship:
            self.ship = new_ship
            # Fully refresh UI controls to match new ship state
            self.right_panel.refresh_controls()
            
            self.update_stats()
            # Also update the layers panel in case components changed
            self.layer_panel.rebuild()
            self.left_panel.update_component_list() # Update available components based on hull type
            self.rebuild_modifier_ui()
            print(message)
        elif message:
            self.show_error(message)

    def _show_clear_confirmation(self):
        self.pending_action = ('clear_design', None)
        self.confirm_dialog = UIConfirmationDialog(
            rect=pygame.Rect((self.width // 2 - 150, self.height // 2 - 100), (300, 200)),
            action_long_desc="Clear all components and reset to default settings?",
            manager=self.ui_manager,
            window_title="Confirm Clear"
        )

    def _clear_design(self):
        logger.info("Clearing ship design")
        for layer_type, layer_data in self.ship.layers.items():
            if layer_type == LayerType.HULL:
                continue
            layer_data['components'] = []
            layer_data['hp_pool'] = 0
            layer_data['max_hp_pool'] = 0
            layer_data['mass'] = 0
            layer_data['hp'] = 0
            
        self.template_modifiers = {}
        self.ship.ai_strategy = "standard_ranged"
        
        # Reset Name
        self.ship.name = "Custom Ship"
        
        self.ship.recalculate_stats()
        
        # Refresh UI
        self.right_panel.refresh_controls()
        self.update_stats()
        self.rebuild_modifier_ui()
        self.controller.selected_component = None
        self.on_selection_changed(None)
        
        if hasattr(self, 'weapons_report_panel'):
            self.weapons_report_panel.clear_target()

    def _on_select_target_pressed(self):
        target_ship, message = ShipIO.load_ship(self.width, self.height)
        if target_ship:
            self.weapons_report_panel.set_target(target_ship)
            logger.info(f"Selected target: {target_ship.name}")
        elif message and "Cancelled" not in message:
            self.show_error(message)

