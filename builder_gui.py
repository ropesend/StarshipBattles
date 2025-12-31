import json
import math
import tkinter
from tkinter import simpledialog
import os

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu, 
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from profiling import profile_action, profile_block

from ship import Ship, LayerType, SHIP_CLASSES, VEHICLE_CLASSES
from components import (
    get_all_components, MODIFIER_REGISTRY, Bridge, Weapon, 
    BeamWeapon, ProjectileWeapon, SeekerWeapon, Engine, Thruster, Armor, Tank, Generator,
    CrewQuarters, LifeSupport
)
from sprites import SpriteManager
from preset_manager import PresetManager
from ship_io import ShipIO
from builder_components import ModifierEditorPanel
from ship_theme import ShipThemeManager
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus

# Initialize Tkinter root and hide it (for simpledialog)
try:
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
        
        # UI Manager
        import os
        theme_path = os.path.join(os.path.dirname(__file__), 'builder_theme.json')
        with profile_block("Builder: Init UIManager"):
            self.ui_manager = pygame_gui.UIManager(
                (screen_width, screen_height),
                theme_path=theme_path if os.path.exists(theme_path) else None
            )
        
        # Ship
        self.ship = Ship("Custom Ship", screen_width // 2, screen_height // 2, (100, 100, 255))
        self.ship.recalculate_stats()
        
        # Managers
        self.available_components = get_all_components()
        self.template_modifiers = {}
        self.sprite_mgr = SpriteManager.get_instance()
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        with profile_block("Builder: Init Managers"):
            self.preset_manager = PresetManager(os.path.join(base_path, "data", "presets.json"))
            self.theme_manager = ShipThemeManager.get_instance()
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
        
        # New Selection System
        self.selected_components = [] # List of (layer_type, index, component) tuples or wrapped components

        
        self._create_ui()
        
    def _create_ui(self):
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
                os.path.join(base_path, "Resources", "Images", "Components"),
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
            ('clear_btn', "Clear Design", 140),
            ('save_btn', "Save", 140),
            ('load_btn', "Load", 140),
            ('arc_toggle_btn', "Show Firing Arcs", 160),
            ('target_btn', "Select Target", 140),
            ('verbose_btn', "Toggle Verbose", 160),
            ('start_btn', "Return", 140)
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
            if act_type == 'refresh_ui': 
                self.update_stats()
                
                
            elif act_type == 'select_component_type':
                with profile_block("Builder: Select Component Type"):
                    c = data
                    # Clear Layer Panel Selection (avoid confusion)
                    self.layer_panel.selected_group_key = None
                    self.layer_panel.selected_component_id = None
                    self.on_selection_changed(None) # Clear
                    self.layer_panel.rebuild()
                    
                    self.controller.dragged_item = c.clone()
                    # Apply template modifiers
                    for m_id, val in self.template_modifiers.items():
                       if m_id in MODIFIER_REGISTRY:
                           mod_def = MODIFIER_REGISTRY[m_id]
                           allow = True
                           if mod_def.restrictions:
                               if 'allow_types' in mod_def.restrictions and c.type_str not in mod_def.restrictions['allow_types']:
                                   allow = False
                           if allow:
                               self.controller.dragged_item.add_modifier(m_id)
                               m = self.controller.dragged_item.get_modifier(m_id)
                               if m: m.value = val
                    self.controller.dragged_item.recalculate_stats()
                    
                    # Set as selected so modifiers panel updates
                    self.on_selection_changed(self.controller.dragged_item)
                
            elif act_type == 'select_group':
                with profile_block("Builder: Select Group"):
                    # Check modifier keys for multi-select
                    keys = pygame.key.get_pressed()
                    append = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                    
                    if not append:
                        self.left_panel.deselect_all()
                    
                    # data is group_key
                    comps = []
                    from ui.builder.grouping_strategies import get_component_group_key
                    for layers in self.ship.layers.values():
                        for c in layers['components']:
                             if get_component_group_key(c) == data:
                                 comps.append(c)
                    
                    self.on_selection_changed(comps, append=append)
                    
                    # Rebuild layer panel now that builder state is updated
                    self.layer_panel.rebuild()
                
            elif act_type == 'select_individual':
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
                
            elif act_type == 'remove_group':
                 # User requested delete on group.
                 # Updated Requirement: Pressing - should delete ONE of the components.
                 
                 # data is group_key
                 from ui.builder.grouping_strategies import get_component_group_key
                 
                 # Find Last Component in this group to remove
                 found_layer = None
                 found_idx = -1
                 
                 # Iterate backwards to find one instance
                 for l_type, layers in self.ship.layers.items():
                    # Check safe iteration
                    comps = layers['components']
                    for idx in range(len(comps)-1, -1, -1):
                         c = comps[idx]
                         if get_component_group_key(c) == data:
                             found_layer = l_type
                             found_idx = idx
                             break
                    if found_layer: break
                 
                 if found_layer:
                     self.ship.remove_component(found_layer, found_idx)
                     # self.on_selection_changed(None) # Don't clear selection on partial remove?
                     # Better to clear if we removed the selected one.
                     self.update_stats()
                 
            elif act_type == 'remove_individual':
                 # data is component
                 removed = False
                 for l_type, layers in self.ship.layers.items():
                     for idx, c in enumerate(layers['components']):
                         if c is data:
                             self.ship.remove_component(l_type, idx)
                             removed = True
                             break
                     if removed:
                         break
                 
                 # Remove from selection list if present
                 if self.selected_components:
                      self.selected_components = [x for x in self.selected_components if x[2] is not data]
                      self.on_selection_changed(self.selected_components) # Update primary
                 
                 self.update_stats()
                 
            elif act_type == 'add_group' or act_type == 'add_individual':
                 # Clone and Add one instance
                 # data is group_key (for group) or component (for individual)
                 
                 target_comp = None
                 
                 if act_type == 'add_individual':
                     target_comp = data
                 else:
                     # Find first component of group
                     from ui.builder.grouping_strategies import get_component_group_key
                     for layers in self.ship.layers.values():
                         for c in layers['components']:
                             if get_component_group_key(c) == data:
                                 target_comp = c
                                 break
                         if target_comp: break
                         
                 if target_comp:
                     # Clone
                     new_comp = target_comp.clone()
                     for m in target_comp.modifiers:
                        new_comp.add_modifier(m.definition.id)
                        nm = new_comp.get_modifier(m.definition.id)
                        if nm: nm.value = m.value
                     new_comp.recalculate_stats()
                     
                     # Find layer of original
                     target_layer = None
                     for l_type, layers in self.ship.layers.items():
                         if target_comp in layers['components']:
                             target_layer = l_type
                             break
                             
                     if target_layer:
                         from ship import VALIDATOR
                         validation = VALIDATOR.validate_addition(self.ship, new_comp, target_layer)
                         if validation.is_valid:
                             self.ship.add_component(new_comp, target_layer)
                             self.update_stats()
                         else:
                             self.show_error(f"Cannot add: {', '.join(validation.errors)}")

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
            return
        
        # Pass to weapons panel
        self.weapons_report_panel.handle_event(event)
        
        self.controller.handle_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
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
            elif event.ui_element == self.verbose_btn:
                 self.weapons_report_panel.verbose_tooltip = not self.weapons_report_panel.verbose_tooltip
            elif event.ui_element == self.detail_panel.details_btn:
                self.detail_panel.show_details_popup()
                 
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.right_panel.class_dropdown:
                new_class = event.text
                if new_class == self.ship.ship_class: return
                
                self.pending_action = ('change_class', new_class)
                
                # Check if ship has components
                has_components = sum(len(l['components']) for l in self.ship.layers.values()) > 0
                
                if has_components:
                    msg = f"Change class to {new_class}?<br><br>Warning: This will attempt to refit existing components.<br>Some items may be resized or lost if they don't fit."
                    self.confirm_dialog = UIConfirmationDialog(pygame.Rect((self.width-400)//2, (self.height-200)//2, 400, 200),
                                                              manager=self.ui_manager,
                                                              action_long_desc=msg,
                                                              window_title="Confirm Refit")
                else:
                    self._execute_pending_action()
                                                          
            elif hasattr(self, 'right_panel') and hasattr(self.right_panel, 'vehicle_type_dropdown') and event.ui_element == self.right_panel.vehicle_type_dropdown:
                new_type = event.text
                if new_type == getattr(self.ship, 'vehicle_type', "Ship"): return
                
                # Determine default class for this type
                valid_classes = [(n, VEHICLE_CLASSES[n].get('max_mass', 0)) for n, c in VEHICLE_CLASSES.items() if c.get('type', 'Ship') == new_type]
                valid_classes.sort(key=lambda x: x[1])
                target_class = valid_classes[0][0] if valid_classes else "Escort"
                
                self.pending_action = ('change_type', target_class)
                
                # Check if ship has components
                has_components = sum(len(l['components']) for l in self.ship.layers.values()) > 0
                
                if has_components:
                    msg = f"Change type to {new_type}?<br><br><b>WARNING: This will CLEAR the current design.</b>"
                    self.confirm_dialog = UIConfirmationDialog(pygame.Rect((self.width-400)//2, (self.height-200)//2, 400, 200),
                                                              manager=self.ui_manager,
                                                              action_long_desc=msg,
                                                              window_title="Confirm Type Change")
                else:
                    self._execute_pending_action()

            elif hasattr(self.right_panel, 'theme_dropdown') and event.ui_element == self.right_panel.theme_dropdown:
                self.ship.theme_id = event.text
                self.right_panel.update_portrait_image()
                logger.info(f"Changed theme to {event.text}")
            elif event.ui_element == self.right_panel.ai_dropdown:
                from ai import COMBAT_STRATEGIES
                selected_name = event.text
                for strategy_id, strat in COMBAT_STRATEGIES.items():
                    if strat.get('name', '') == selected_name:
                        self.ship.ai_strategy = strategy_id
                        break
                else:
                    self.ship.ai_strategy = event.text.lower().replace(' ', '_')
                    
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
                
                # We also need to update the Class Dropdown options
                new_type = VEHICLE_CLASSES[data].get('type', 'Ship')
                valid_classes = [(n, VEHICLE_CLASSES[n].get('max_mass', 0)) for n, c in VEHICLE_CLASSES.items() if c.get('type', 'Ship') == new_type]
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
                     # Create preview with current template modifiers
                     comp_template = hovered_item.component
                     preview_comp = comp_template.clone()
                     for m_id, val in self.template_modifiers.items():
                        if m_id in MODIFIER_REGISTRY:
                            mod_def = MODIFIER_REGISTRY[m_id]
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
                        if m_id in MODIFIER_REGISTRY:
                            mod_def = MODIFIER_REGISTRY[m_id]
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
            layer_data['components'] = []
            layer_data['hp_pool'] = 0
            layer_data['max_hp_pool'] = 0
            layer_data['mass'] = 0
            layer_data['hp'] = 0
            
        self.template_modifiers = {}
        self.ship.ai_strategy = "optimal_firing_range"
        
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

