"""
Legacy standalone ship builder GUI.

This is the original BuilderSceneGUI implementation, used for standalone
ship design testing. The newer DesignWorkshopScreen (workshop_screen.py) is
the production version with MVVM architecture and dependency injection.

PROJ-43: Migrated to use UI services layer for Ship, VEHICLE_CLASSES,
get_all_components, MODIFIER_REGISTRY.

PROJ-44: Refactored _reload_data() to use WorkshopDataLoader instead of
direct registry manipulation. No more direct simulation layer imports for
registry clearing.

PROJ-44 Phase 7 Task 7.3: Extracted state management to BuilderStateManager.
Selection, template modifiers, pending actions, and drag/drop state are now
managed by a dedicated BuilderStateManager class for better testability and
reduced complexity.
"""
import json
import math
import tkinter
from tkinter import filedialog
import os

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu,
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from game.core.profiling import profile_action, profile_block
from game.core.constants import LayerType

from game.ui.services.ship_factory import ShipFactory
from game.ui.services.component_service import ComponentService
from game.ui.services.vehicle_class_service import VehicleClassService
from game.ui.services.validation_service import ValidationService
from game.ui.renderer.sprites import SpriteManager
from game.ui.screens.planet_list_presets import PresetManager
from game.ui.screens.workshop_data_loader import WorkshopDataLoader
from game.simulation.systems.persistence import ShipIO
from game.ui.screens.builder.legacy_components import ModifierEditorPanel
from game.ui.assets import ShipThemeManager
from .left_panel import BuilderLeftPanel
from .right_panel import BuilderRightPanel
from .weapons_panel import WeaponsReportPanel
from .layer_panel import LayerPanel
from .schematic_view import SchematicView
from .interaction_controller import InteractionController
from .event_bus import EventBus
from .state_manager import BuilderStateManager

# Initialize Tkinter root and hide it (for filedialog)
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except (tkinter.TclError, RuntimeError) as e:
    # TclError occurs when display unavailable; RuntimeError when Tcl not initialized
    import logging
    logging.getLogger(__name__).debug(f"Tkinter not available: {e}")
    tk_root = None

# Colors
from game.ui.colors import COLORS
BG_COLOR = COLORS['bg_deep']
PANEL_BG = '#14181f'

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .detail_panel import ComponentDetailPanel





class BuilderScreen:
    def __init__(self, screen_width, screen_height, on_start_battle):
        self.width = screen_width
        self.height = screen_height
        self.on_start_battle = on_start_battle

        self.event_bus = EventBus()

        # PROJ-43/PROJ-50: UI Services for decoupling from simulation layer
        # Use RegistryManager-backed provider for strict DI
        from game.core.registry import get_default_registry_provider
        self._registry_provider = get_default_registry_provider()
        self._ship_factory = ShipFactory()
        self._component_service = ComponentService()
        self._vehicle_class_service = VehicleClassService(self._registry_provider)
        self._validation_service = ValidationService()

        # UI Manager
        import os
        theme_path = os.path.join(os.path.dirname(__file__), 'builder_theme.json')
        with profile_block("Builder: Init UIManager"):
            self.ui_manager = pygame_gui.UIManager(
                (screen_width, screen_height),
                theme_path=theme_path if os.path.exists(theme_path) else None
            )

        # Ship (created via factory)
        self.ship = self._ship_factory.create_from_design({
            'name': 'Custom Ship',
            'ship_class': 'Escort',
            'theme_id': 'Federation',
            'color': [100, 100, 255],
            'layers': {}
        })
        self.ship.position = pygame.math.Vector2(screen_width // 2, screen_height // 2)
        self.ship.recalculate_stats()

        # Managers
        self.available_components = self._component_service.get_all_components()
        self.sprite_mgr = SpriteManager.instance()

        # PROJ-44 Phase 7: State management extracted to BuilderStateManager
        self._state_manager = BuilderStateManager(self.ship)
        self._state_manager.on_selection_changed_callback = self._on_state_selection_changed
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        with profile_block("Builder: Init Managers"):
            self.preset_manager = PresetManager()
            self.theme_manager = ShipThemeManager.instance()
            self.theme_manager.initialize(base_path)
        
        # Layout
        self.left_panel_width = 450
        self.right_panel_width = 750 # Widened for ship portrait and 2-column stats
        self.layer_panel_width = 450 # Widened
        self.detail_panel_width = 550
        self.bottom_bar_height = 60
        self.weapons_report_height = 600
        
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

        # PROJ-44: Selection managed by BuilderStateManager
        # self.selected_components property delegates to state_manager


        self._create_ui()
        
    def _create_ui(self):
        """Initialize all UI panels for the ship builder screen.

        Creates and lays out:
        - Left panel: Component/hull selection list
        - Right panel: Ship stats and portrait
        - Layer panel: Component slots by layer
        - Detail panel: Selected component details
        - Bottom bar: Save/load/exit buttons
        - Modifier panel: Modifier controls for selected component
        - Weapons report: Weapon summary table
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # New Layout Dimensions
        self.modifier_panel_height = 360
        avail_height = self.height - self.bottom_bar_height
        panels_height = avail_height - self.modifier_panel_height
        
        with profile_block("Builder: Init Panels (Left/Right/Layer)"):
            self.left_panel = BuilderLeftPanel(
                self, self.ui_manager,
                pygame.Rect(0, 0, self.left_panel_width, panels_height)
            )
            
            # New Layer Panel
            self.layer_panel = LayerPanel(
                self, self.ui_manager,
                pygame.Rect(self.left_panel_width, 0, self.layer_panel_width, panels_height)
            )
            # Register Drop Target
            self.controller.register_drop_target(self.layer_panel)
            
            self.right_panel = BuilderRightPanel(
                self, self.ui_manager,
                pygame.Rect(self.width - self.right_panel_width, 0, 
                            self.right_panel_width, self.height - self.bottom_bar_height - self.weapons_report_height),
                event_bus=self.event_bus
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
        weapons_panel_width = self.width - weapons_panel_x
        with profile_block("Builder: Init Weapons Panel"):
            self.weapons_report_panel = WeaponsReportPanel(
                self, self.ui_manager,
                pygame.Rect(weapons_panel_x, weapons_panel_y, weapons_panel_width, self.weapons_report_height),
                self.sprite_mgr
            )

        # Detail Panel
        detail_x = self.width - self.right_panel_width - self.detail_panel_width
        avail_height = self.height - self.bottom_bar_height - self.weapons_report_height
        with profile_block("Builder: Init Detail Panel"):
            self.detail_panel = ComponentDetailPanel(
                self.ui_manager,
                pygame.Rect(detail_x, 0, self.detail_panel_width, avail_height),
                os.path.join(base_path, "assets", "Images", "Components"),
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

        PROJ-44 Phase 7: Delegates to BuilderStateManager for state management.

        Args:
            new_selection: Component, tuple (layer, idx, comp), list of them, or None
            append: If True, add to existing selection instead of replacing
            toggle: If True, toggles selection state (Ctrl+Click behavior)
        """
        self._state_manager.on_selection_changed(new_selection, append=append, toggle=toggle)

    def _on_state_selection_changed(self, selected_component):
        """
        Callback from BuilderStateManager when selection changes.

        Updates dependent UI components (modifier panel, event bus).
        """
        # Sync with controller (for schematic view highlighting)
        self.controller.selected_component = selected_component

        self.rebuild_modifier_ui()
        self.event_bus.emit('SELECTION_CHANGED', selected_component)

    @property
    def selected_components(self):
        """List of (layer, index, component) tuples. Delegates to state manager."""
        return self._state_manager.selected_components

    @selected_components.setter
    def selected_components(self, value):
        """Set selected components directly. Delegates to state manager."""
        self._state_manager.selected_components = value

    @property
    def template_modifiers(self):
        """Template modifiers for new components. Delegates to state manager."""
        return self._state_manager.template_modifiers

    @template_modifiers.setter
    def template_modifiers(self, value):
        """Set template modifiers. Delegates to state manager."""
        self._state_manager.set_template_modifiers(value)

    @property
    def pending_action(self):
        """Pending action awaiting confirmation. Delegates to state manager."""
        return self._state_manager.pending_action

    @pending_action.setter
    def pending_action(self, value):
        """Set pending action. Delegates to state manager."""
        if value is None:
            self._state_manager.clear_pending_action()
        else:
            self._state_manager.set_pending_action(value[0], value[1])

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
        # Start Y is 0 relative to the modifier container panel
        self.modifier_panel.rebuild(editing_component, self.template_modifiers)
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

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0
        
    def _show_error(self, msg):
        self.show_error(msg)

    def _handle_panel_action(self, act_type: str, data) -> None:
        """Handle actions from left panel, layer panel, and modifier panel.

        Dispatches to specific handlers based on action type.
        """
        if act_type == 'refresh_ui':
            self.update_stats()

        elif act_type == 'select_component_type':
            self._handle_select_component_type(data)

        elif act_type == 'select_group':
            self._handle_select_group(data)

        elif act_type == 'select_individual':
            self._handle_select_individual(data)

        elif act_type == 'remove_group':
            self._handle_remove_group(data)

        elif act_type == 'remove_individual':
            self._handle_remove_individual(data)

        elif act_type == 'add_group' or act_type == 'add_individual':
            self._handle_add_component(act_type, data)

        elif act_type == 'apply_preset':
            self.template_modifiers = data
            self.rebuild_modifier_ui()

        elif act_type == 'clear_settings':
            with profile_block("Builder: Clear Settings"):
                self.controller.selected_component = None
                self.template_modifiers = {}
                self.on_selection_changed(None)
                self.rebuild_modifier_ui()
                logger.debug("Cleared settings or deselected component")

        elif act_type == 'toggle_layer':
            # Layer header toggle - already handled by callback
            pass

    def _handle_select_component_type(self, data) -> None:
        """Handle component type selection from left panel."""
        with profile_block("Builder: Select Component Type"):
            c = data
            # Clear Layer Panel Selection (avoid confusion)
            self.layer_panel.selected_group_key = None
            self.layer_panel.selected_component_id = None
            self.on_selection_changed(None)  # Clear
            self.layer_panel.rebuild()

            self.controller.dragged_item = c.clone()
            # Apply template modifiers (PROJ-43: via ComponentService)
            for m_id, val in self.template_modifiers.items():
                if self._component_service.is_modifier_allowed(m_id, c):
                    self.controller.dragged_item.add_modifier(m_id)
                    m = self.controller.dragged_item.get_modifier(m_id)
                    if m:
                        m.value = val
            self.controller.dragged_item.recalculate_stats()

            # Set as selected so modifiers panel updates
            self.on_selection_changed(self.controller.dragged_item)

    def _handle_select_group(self, data) -> None:
        """Handle group selection from layer panel."""
        with profile_block("Builder: Select Group"):
            # Check modifier keys for multi-select
            keys = pygame.key.get_pressed()
            append = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            if not append:
                self.left_panel.deselect_all()

            # data is group_key
            comps = []
            from game.ui.screens.builder.grouping_strategies import get_component_group_key
            for layers in self.ship.layers.values():
                for c in layers.components:
                    if get_component_group_key(c) == data:
                        comps.append(c)

            self.on_selection_changed(comps, append=append)

            # Rebuild layer panel now that builder state is updated
            self.layer_panel.rebuild()

    def _handle_select_individual(self, data) -> None:
        """Handle individual component selection from layer panel."""
        with profile_block("Builder: Select Individual"):
            keys = pygame.key.get_pressed()
            is_ctrl = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            is_shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            if not (is_ctrl or is_shift):
                self.left_panel.deselect_all()

            if is_shift and self.selected_component:
                # Range Selection
                start_comp = self.selected_component[2]
                end_comp = data
                range_comps = self.layer_panel.get_range_selection(start_comp, end_comp)
                self.on_selection_changed(range_comps, append=is_ctrl, toggle=False)
            else:
                # Single Click (Toggle if Ctrl)
                self.on_selection_changed(data, append=is_ctrl, toggle=is_ctrl)

            # Rebuild layer panel now that builder state is updated
            self.layer_panel.rebuild()

    def _handle_remove_group(self, data) -> None:
        """Handle removing one component from a group."""
        from game.ui.screens.builder.grouping_strategies import get_component_group_key

        # Unpack layer-targeted data
        if isinstance(data, tuple) and len(data) == 2:
            group_key, target_layer = data
        else:
            group_key = data
            target_layer = None

        found_layer = None
        found_idx = -1

        if target_layer is not None:
            if target_layer in self.ship.layers:
                comps = self.ship.layers[target_layer].components
                for idx in range(len(comps)-1, -1, -1):
                    c = comps[idx]
                    if get_component_group_key(c) == group_key:
                        found_layer = target_layer
                        found_idx = idx
                        break
        else:
            for l_type, layers in self.ship.layers.items():
                comps = layers.components
                for idx in range(len(comps)-1, -1, -1):
                    c = comps[idx]
                    if get_component_group_key(c) == group_key:
                        found_layer = l_type
                        found_idx = idx
                        break
                if found_layer:
                    break

        if found_layer:
            self.ship.remove_component(found_layer, found_idx)
            self.update_stats()

    def _handle_remove_individual(self, data) -> None:
        """Handle removing a specific component."""
        # Unpack layer-targeted data
        if isinstance(data, tuple) and len(data) == 2:
            comp, target_layer = data
        else:
            comp = data
            target_layer = None

        removed = False
        layers_to_search = [target_layer] if target_layer else list(self.ship.layers.keys())
        for l_type in layers_to_search:
            if l_type in self.ship.layers:
                for idx, c in enumerate(self.ship.layers[l_type].components):
                    if c is comp:
                        self.ship.remove_component(l_type, idx)
                        removed = True
                        break
            if removed:
                break

        if self.selected_components:
            self.selected_components = [x for x in self.selected_components if x[2] is not comp]
            self.on_selection_changed(self.selected_components)

        self.update_stats()

    def _handle_add_component(self, act_type: str, data) -> None:
        """Handle adding a component (clone and add to correct layer)."""
        target_comp = None
        target_layer = None

        if act_type == 'add_individual':
            if isinstance(data, tuple) and len(data) == 2:
                target_comp, target_layer = data
            else:
                target_comp = data
        else:
            if isinstance(data, tuple) and len(data) == 2:
                group_key, target_layer = data
            else:
                group_key = data

            from game.ui.screens.builder.grouping_strategies import get_component_group_key
            if target_layer and target_layer in self.ship.layers:
                for c in self.ship.layers[target_layer].components:
                    if get_component_group_key(c) == group_key:
                        target_comp = c
                        break
            if not target_comp:
                for layers in self.ship.layers.values():
                    for c in layers.components:
                        if get_component_group_key(c) == group_key:
                            target_comp = c
                            break
                    if target_comp:
                        break

        if target_comp:
            new_comp = target_comp.clone()
            for m in target_comp.modifiers:
                new_comp.add_modifier(m.definition.id)
                nm = new_comp.get_modifier(m.definition.id)
                if nm:
                    nm.value = m.value
            new_comp.recalculate_stats()

            if not target_layer:
                for l_type, layers in self.ship.layers.items():
                    if target_comp in layers.components:
                        target_layer = l_type
                        break

            if target_layer:
                validation = self._validation_service.validate_addition(self.ship, new_comp, target_layer)
                if validation.is_valid:
                    self.ship.add_component(new_comp, target_layer)
                    self.update_stats()
                else:
                    self.show_error(f"Cannot add: {', '.join(validation.errors)}")

    def _handle_button_pressed(self, event) -> None:
        """Handle UI_BUTTON_PRESSED events."""
        if event.ui_element == self.start_btn:
            self.on_start_battle(None)
        elif event.ui_element == self.save_btn:
            self._save_ship()
        elif event.ui_element == self.load_btn:
            self._load_ship()
        elif event.ui_element == self.clear_btn:
            self._show_clear_confirmation()
        elif event.ui_element == self.arc_toggle_btn:
            self.show_firing_arcs = not self.show_firing_arcs
            self.arc_toggle_btn.set_text("Hide Firing Arcs" if self.show_firing_arcs else "Show Firing Arcs")
        elif event.ui_element == self.target_btn:
            self._on_select_target_pressed()
        elif event.ui_element == self.std_data_btn:
            self._load_standard_data()
        elif event.ui_element == self.test_data_btn:
            self._load_test_data()
        elif event.ui_element == self.select_data_btn:
            self._on_select_data_pressed()
        elif event.ui_element == self.verbose_btn:
            self.weapons_report_panel.verbose_tooltip = not self.weapons_report_panel.verbose_tooltip
        elif event.ui_element == self.detail_panel.details_btn:
            self.detail_panel.show_details_popup()

    def _handle_dropdown_changed(self, event) -> None:
        """Handle UI_DROP_DOWN_MENU_CHANGED events."""
        if event.ui_element == self.right_panel.class_dropdown:
            self._handle_class_dropdown(event)
        elif hasattr(self, 'right_panel') and hasattr(self.right_panel, 'vehicle_type_dropdown') and event.ui_element == self.right_panel.vehicle_type_dropdown:
            self._handle_vehicle_type_dropdown(event)
        elif hasattr(self.right_panel, 'theme_dropdown') and event.ui_element == self.right_panel.theme_dropdown:
            self.ship.theme_id = event.text
            self.right_panel.update_portrait_image()
            logger.info(f"Changed theme to {event.text}")
        elif event.ui_element == self.right_panel.ai_dropdown:
            self._handle_ai_dropdown(event)

    def _handle_class_dropdown(self, event) -> None:
        """Handle ship class dropdown changes."""
        new_class = event.text
        if new_class == self.ship.ship_class:
            return

        self.pending_action = ('change_class', new_class)

        # Check if ship has components (PROJ-44: use Ship helper method)
        has_components = self.ship.has_components()

        if has_components:
            msg = f"Change class to {new_class}?<br><br>Warning: This will attempt to refit existing components.<br>Some items may be resized or lost if they don't fit."
            self.confirm_dialog = UIConfirmationDialog(
                pygame.Rect((self.width-400)//2, (self.height-200)//2, 400, 200),
                manager=self.ui_manager,
                action_long_desc=msg,
                window_title="Confirm Refit"
            )
        else:
            self._execute_pending_action()

    def _handle_vehicle_type_dropdown(self, event) -> None:
        """Handle vehicle type dropdown changes."""
        new_type = event.text
        if new_type == getattr(self.ship, 'vehicle_type', "Ship"):
            return

        # Determine default class for this type (PROJ-43: via VehicleClassService)
        valid_classes = self._vehicle_class_service.get_classes_for_type(new_type)
        valid_classes.sort(key=lambda x: x[1])
        target_class = valid_classes[0][0] if valid_classes else "Escort"

        self.pending_action = ('change_type', target_class)

        # Check if ship has components (PROJ-44: use Ship helper method)
        has_components = self.ship.has_components()

        if has_components:
            msg = f"Change type to {new_type}?<br><br><b>WARNING: This will CLEAR the current design.</b>"
            self.confirm_dialog = UIConfirmationDialog(
                pygame.Rect((self.width-400)//2, (self.height-200)//2, 400, 200),
                manager=self.ui_manager,
                action_long_desc=msg,
                window_title="Confirm Type Change"
            )
        else:
            self._execute_pending_action()

    def _handle_ai_dropdown(self, event) -> None:
        """Handle AI strategy dropdown changes."""
        from game.ai.strategy_manager import StrategyManager
        selected_name = event.text
        for strategy_id, strat in StrategyManager.instance().strategies.items():
            if strat.get('name', '') == selected_name:
                self.ship.ai_strategy = strategy_id
                break
        else:
            self.ship.ai_strategy = event.text.lower().replace(' ', '_')

    def handle_event(self, event):
        self.ui_manager.process_events(event)
        
         # Pass to modifier panel
        action = self.left_panel.handle_event(event)
        if not action:
            # Pass to layer panel (headers and items)
            action = self.layer_panel.handle_event(event)
            
        if not action:
            # Pass to relocated modifier panel
            action = self.modifier_panel.handle_event(event)

        if action:
            if isinstance(action, bool):
                # Just consumed event, no data
                return

            act_type, data = action
            self._handle_panel_action(act_type, data)
            return
        
        # Pass to weapons panel
        self.weapons_report_panel.handle_event(event)
        
        self.controller.handle_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_pressed(event)

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_dropdown_changed(event)

        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirm_dialog:
                self._execute_pending_action()
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for preset_name, btn in getattr(self, 'preset_buttons', []):
                if btn.rect.collidepoint(event.pos):
                    self.preset_manager.delete_preset(preset_name)
                    self.left_panel.rebuild_modifier_ui()
                    logger.info(f"Deleted preset: {preset_name}")
                    break

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

                # We also need to update the Class Dropdown options (PROJ-43: via VehicleClassService)
                new_type = self._vehicle_class_service.get_type_for_class(data)
                valid_classes = self._vehicle_class_service.get_classes_for_type(new_type)
                valid_classes.sort(key=lambda x: x[1])
                valid_class_names = [n for n, m in valid_classes]
                if not valid_class_names:
                    valid_class_names = ["Escort"]

                self.right_panel.class_dropdown.kill()
                self.right_panel.class_dropdown = UIDropDownMenu(
                    valid_class_names, data,
                    pygame.Rect(70, self.right_panel.class_dropdown.relative_rect.y, 195, 30),
                    manager=self.ui_manager, container=self.right_panel.panel
                )
                
                self.update_stats()
                self.right_panel.update_portrait_image()
                self.left_panel.update_component_list()
            
            self.pending_action = None
        else:
            # Fallback for simple clear if pending_action not set (legacy support)
            self._clear_design()

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
                     # Create preview with current template modifiers (PROJ-43: via ComponentService)
                     comp_template = hovered_item.component
                     preview_comp = comp_template.clone()
                     for m_id, val in self.template_modifiers.items():
                         if self._component_service.is_modifier_allowed(m_id, preview_comp):
                             preview_comp.add_modifier(m_id)
                             m = preview_comp.get_modifier(m_id)
                             if m:
                                 m.value = val
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
                    # PROJ-43: Apply modifiers via ComponentService
                    comp_template = hovered_item.component
                    preview_comp = comp_template.clone()
                    for m_id, val in self.template_modifiers.items():
                        if self._component_service.is_modifier_allowed(m_id, preview_comp):
                            preview_comp.add_modifier(m_id)
                            m = preview_comp.get_modifier(m_id)
                            if m:
                                m.value = val
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

        PROJ-44: Refactored to use WorkshopDataLoader instead of direct
        registry manipulation. This centralizes data loading logic and
        reduces cross-layer coupling.

        PROJ-50: Pass registries to loader (uses global singleton since
        legacy builder doesn't use context DI pattern).
        """
        from game.core.registry import RegistryManager
        try:
            # 1. Load all data via WorkshopDataLoader
            loader = WorkshopDataLoader(directory, registries=RegistryManager.instance())
            result = loader.load_all()

            if not result.success:
                for error in result.errors:
                    logger.error(f"Data load error: {error}")
                self.show_error("Failed to reload data!")
                return

            for warning in result.warnings:
                logger.warning(warning)

            default_class = result.default_class

            # 2. Refresh UI
            self.right_panel.refresh_controls()
            self.left_panel.update_component_list()
            self.rebuild_modifier_ui()
            
            self.show_error("Data Reloaded Successfully!")
            
            # 3. Refresh Builder State (PROJ-43: use services after reload)
            self.available_components = self._component_service.get_all_components()
            self._state_manager.clear_all()  # Clear selection, modifiers, etc.
            all_classes = self._vehicle_class_service.get_all_classes()

            self.ship = self._ship_factory.create_from_design({
                'name': 'Custom Ship',
                'ship_class': default_class,
                'theme_id': 'Federation',
                'color': [100, 100, 255],
                'layers': {}
            })
            self.ship.position = pygame.math.Vector2(self.width // 2, self.height // 2)
            self.ship.recalculate_stats()

            # Update state manager with new ship
            self._state_manager.ship = self.ship

            # Reset UI Panels
            # Left Panel needs to rebuild list
            self.left_panel.update_component_list()

            # Center View
            self.view.selected_component = None
            self.controller.selected_component = None

            # Right Panel needs to refresh dropdowns
            # We need to recreate the class dropdown or update its items
            # Accessing right_panel internals (tight coupling, but needed for quick fix)

            # Update Class Dropdown (PROJ-43: via VehicleClassService)
            valid_classes = [(name, self._vehicle_class_service.get_max_mass(name))
                            for name in all_classes.keys()]
            valid_classes.sort(key=lambda x: x[1])
            valid_class_names = [n for n, m in valid_classes]
            if not valid_class_names:
                valid_class_names = ["Escort"]

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
                types = self._vehicle_class_service.get_vehicle_types()
                if not types:
                    types = ["Ship"]
                default_type = self._vehicle_class_service.get_type_for_class(default_class)

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
            
            # Show success
            self.show_error(f"Reloaded data from {os.path.basename(directory)}")
            
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to reload data: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Error reloading data: {e}")
            
    
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
            # Update state manager with new ship
            self._state_manager.ship = self.ship
            self._state_manager.clear_selection()

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
            layer_data.clear()  # Use LayerData.clear() method
            
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

