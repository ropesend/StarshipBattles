import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIScrollingContainer, UIDropDownMenu

from game.simulation.entities.ship import LayerType
from ui.builder.structure_list_items import (
    LayerHeaderItem, 
    LayerComponentItem, 
    IndividualComponentItem,
    ACTION_ADD_GROUP, ACTION_ADD_INDIVIDUAL, 
    ACTION_REMOVE_GROUP, ACTION_REMOVE_INDIVIDUAL,
    ACTION_SELECT_GROUP, ACTION_SELECT_INDIVIDUAL,
    ACTION_TOGGLE_GROUP, ACTION_TOGGLE_LAYER
)
from ui.builder.grouping_strategies import DefaultGroupingStrategy, TypeGroupingStrategy, FlatGroupingStrategy
from ui.builder.panel_layout_config import StructurePanelLayoutConfig
from ui.builder.drop_target import DropTarget
from game.simulation.entities.ship import VALIDATOR

class LayerPanel(DropTarget):
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.items = [] 
        self.config = StructurePanelLayoutConfig()
        
        # UI Reconciliation Cache
        # Key: Unique Identifier (str or tuple), Value: UI Item Instance
        self.ui_cache = {} 
        
        # State
        self.selected_group_key = None
        self.selected_component_id = None 
        
        # Strategy
        self.grouping_strategies = {
            'Default': DefaultGroupingStrategy(),
            'Compact': TypeGroupingStrategy(),
            'Flat': FlatGroupingStrategy()
        }
        self.current_strategy_name = 'Default'
        self.grouping_strategy = self.grouping_strategies[self.current_strategy_name]
        
        self.toggle_suppress_timer = 0.0
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#layer_panel'
        )
        
        UILabel(
            relative_rect=pygame.Rect(10, 5, 200, 30),
            text="Ship Structure",
            manager=manager,
            container=self.panel
        )
        
        # Explicit Layers Header
        UILabel(
            relative_rect=pygame.Rect(10, 30, 200, 20),
            text="Layers",
            manager=manager,
            container=self.panel
        )
        
        self.list_y = 55 # Increased for headers
        self.scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, self.list_y, rect.width, rect.height - self.list_y),
            manager=manager,
            container=self.panel,
            starting_height=1,  # Keep scroll container and children on low layers
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # View Options Dropdown - standard creation
        self.view_dropdown = UIDropDownMenu(
            options_list=['Default', 'Compact', 'Flat'],
            starting_option=self.current_strategy_name,
            relative_rect=pygame.Rect(-110, 5, 100, 30),
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        self.view_dropdown.change_layer(100)
        
        self.expanded_layers = {
            LayerType.CORE: True,
            LayerType.INNER: True,
            LayerType.OUTER: True,
            LayerType.ARMOR: True
        }
        self.expanded_groups = {} # Map group_key -> bool
        
        self.rebuild()
        
    def rebuild(self):
        """
        Rebuilds the list using reconciliation to preserve UI instances.
        """
        y_pos = 0
        container_rect = self.scroll_container.get_container().get_rect()
        content_width = container_rect.width
        
        layer_order = [LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        ship = self.builder.ship
        
        # 1. Generate Logical List of Items needed
        # We process logical items and immediately reconcile them with the cache
        
        new_items_list = []
        visited_keys = set()
        
        for l_type in layer_order:
            if l_type not in ship.layers: continue
            
            data = ship.layers[l_type]
            components = data['components']
            
            current_mass = sum(c.mass for c in components)
            layer_max_mass = ship.max_mass_budget * data.get('max_mass_pct', 1.0)
            total_max_mass = ship.max_mass_budget
            
            # --- HEADER ---
            header_key = ("header", l_type)
            visited_keys.add(header_key)
            
            header = self.ui_cache.get(header_key)
            if header:
                header.update(current_mass, layer_max_mass, self.expanded_layers.get(l_type, True))
                header.panel.set_relative_position((0, y_pos))
            else:
                header = LayerHeaderItem(
                    self.manager,
                    self.scroll_container,
                    l_type,
                    current_mass,
                    layer_max_mass,
                    self.expanded_layers.get(l_type, True),
                    self, # Event Handler
                    y_pos,
                    content_width,
                    self.config
                )
                self.ui_cache[header_key] = header
                
            new_items_list.append(header)
            y_pos += header.height
            
            if self.expanded_layers.get(l_type, True):
                groups = self.grouping_strategy.group_components(components)
                for comp_list, count, mass_total, group_key in groups:
                    pct_val = (mass_total / total_max_mass * 100) if total_max_mass > 0 else 0
                    
                    if count <= 1:
                        is_expanded = False
                    else:
                        is_expanded = self.expanded_groups.get(group_key, False)
                    
                    is_selected_group = False
                    if self.builder.selected_components:
                         selected_objs = [x[2] for x in self.builder.selected_components]
                         if comp_list[0] in selected_objs:
                             is_selected_group = True
                             
                    comp_template = comp_list[0]
                    
                    # --- GROUP ITEM ---
                    item_key = ("group", group_key)
                    visited_keys.add(item_key)
                    
                    item = self.ui_cache.get(item_key)
                    if item:
                        item.update(count, mass_total, pct_val, is_expanded, is_selected_group, comp_template.name)
                        item.panel.set_relative_position((0, y_pos))
                    else:
                        item = LayerComponentItem(
                            self.manager,
                            self.scroll_container,
                            comp_template,
                            count,
                            mass_total,
                            pct_val,
                            is_expanded,
                            group_key,
                            is_selected_group,
                            y_pos,
                            content_width,
                            self.builder.sprite_mgr,
                            self,
                            self.config
                        )
                        self.ui_cache[item_key] = item
                        
                    new_items_list.append(item)
                    y_pos += item.height
                    
                    if is_expanded:
                        for idx, comp in enumerate(comp_list):
                             is_last = (idx == len(comp_list) - 1)
                             is_sel_ind = False
                             if self.builder.selected_components:
                                 if any(x[2] is comp for x in self.builder.selected_components):
                                     is_sel_ind = True
                                     
                             # --- INDIVIDUAL ITEM ---
                             ind_key = ("ind", comp)
                             visited_keys.add(ind_key)
                             
                             ind_item = self.ui_cache.get(ind_key)
                             if ind_item:
                                 ind_item.update(comp, total_max_mass, is_sel_ind, is_last)
                                 ind_item.panel.set_relative_position((0, y_pos))
                             else:
                                 ind_item = IndividualComponentItem(
                                    self.manager,
                                    self.scroll_container,
                                    comp,
                                    total_max_mass,
                                    y_pos,
                                    content_width,
                                    self.builder.sprite_mgr,
                                    self,
                                    is_sel_ind,
                                    is_last,
                                    self.config
                                 )
                                 self.ui_cache[ind_key] = ind_item
                                 
                             new_items_list.append(ind_item)
                             y_pos += ind_item.height
            
        # Cleanup Unvisited
        keys_to_remove = []
        for key, item in self.ui_cache.items():
            if key not in visited_keys:
                item.kill()
                keys_to_remove.append(key)
        
        for k in keys_to_remove:
            del self.ui_cache[k]
            
        self.items = new_items_list
        self.scroll_container.set_scrollable_area_dimensions((content_width, y_pos))

    def handle_item_action(self, action, payload):
        """Unified Action Handler (Command Pattern)"""
        # Return values are passed back to builder_gui 'handle_event' loop
        # Usually tuple: (action_string, payload)
        
        if action == ACTION_TOGGLE_LAYER:
            self.expanded_layers[payload] = not self.expanded_layers.get(payload, True)
            self.rebuild()
            return ('refresh_ui', None)
            
        elif action == ACTION_TOGGLE_GROUP:
            self.expanded_groups[payload] = not self.expanded_groups.get(payload, False)
            self.rebuild()
            return ('refresh_ui', None)
            
        elif action == ACTION_SELECT_GROUP:
            self.selected_group_key = payload
            self.selected_component_id = None
            return ('select_group', payload)
            
        elif action == ACTION_SELECT_INDIVIDUAL:
            self.selected_group_key = None
            self.selected_component_id = payload
            return ('select_individual', payload)
            
        elif action == ACTION_ADD_GROUP:
            return ('add_group', payload)
        elif action == ACTION_ADD_INDIVIDUAL:
            return ('add_individual', payload)
        elif action == ACTION_REMOVE_GROUP:
            return ('remove_group', payload)
        elif action == ACTION_REMOVE_INDIVIDUAL:
            return ('remove_individual', payload)
            
        elif action == ACTION_START_DRAG:
            # Reorder Strategy: Pick up component (remove from ship) and attach to cursor
            comp = payload
            removed = False
            for l_type, layers in self.builder.ship.layers.items():
                if comp in layers['components']:
                    layers['components'].remove(comp)
                    removed = True
                    break
            
            if removed:
                self.builder.controller.dragged_item = comp
                self.builder.ship.recalculate_stats()
                # Clear selection if we picked up the selected item
                if self.builder.selected_components and any(x[2] is comp for x in self.builder.selected_components):
                     self.builder.selected_components = []
                     self.builder.on_selection_changed(None)
                
                return ('refresh_ui', None)
            
        return False

    def handle_event(self, event):
        # Local Event: Dropdown
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.view_dropdown:
            selected = event.text
            if selected in self.grouping_strategies:
                self.current_strategy_name = selected
                self.grouping_strategy = self.grouping_strategies[selected]
                # Invalidate cache because group keys might change completely
                for item in self.ui_cache.values():
                    item.kill()
                self.ui_cache = {}
                self.rebuild()
                return True
        
        for item in self.items:
            if hasattr(item, 'handle_event'):
                result = item.handle_event(event)
                if result:
                    return result
        return False

    def update(self, dt):
        if self.toggle_suppress_timer > 0:
            self.toggle_suppress_timer -= dt
            
        # Hide scroll container when dropdown is expanded to avoid z-order issues
        # This was requested by the user as the preferred solution/workaround
        if self.view_dropdown.current_state == self.view_dropdown.menu_states['expanded']:
            if self.scroll_container.visible:
                self.scroll_container.hide()
        else:
            if not self.scroll_container.visible:
                self.scroll_container.show()
            
    def suppress_toggle(self):
        """Suppress toggle events for a short duration."""
        self.toggle_suppress_timer = 0.2
        
    def draw(self, screen):
        # Draw selection highlight overlays for selected items
        container_rect = self.scroll_container.get_abs_rect()
        for item in self.items:
            if isinstance(item, (LayerComponentItem, IndividualComponentItem)):
                if getattr(item, 'is_selected', False):
                    # Get the absolute rect of the item
                    abs_rect = item.get_abs_rect()
                    # Check if it's visible in the scroll container
                    if container_rect.colliderect(abs_rect):
                        # Clip to container bounds
                        clipped = abs_rect.clip(container_rect)
                        # Draw semi-transparent highlight
                        highlight_surf = pygame.Surface((clipped.width, clipped.height), pygame.SRCALPHA)
                        # Use color from config
                        highlight_surf.fill(self.config.SELECTION_COLOR) 
                        screen.blit(highlight_surf, clipped.topleft)

    def can_accept_drop(self, pos):
        return self.get_target_layer_at(pos) is not None

    def accept_drop(self, pos, component, count=1):
        target_layer = self.get_target_layer_at(pos)
        if target_layer:
             # Validation
             # For bulk add, we trust add_components_bulk to handle loop validation or we should validate appropriately.
             # add_components_bulk performs validation internally per item or in batch.
             # Let's delegate to ship.add_components_bulk directly.
             
             added_count = self.builder.ship.add_components_bulk(component, target_layer, count)
             if added_count > 0:
                 self.builder.update_stats()
                 return True
             else:
                 # If 0 added, show error from validation of first attempt?
                 # ship.add_components_bulk prints errors to console, but builder.show_error might be needed.
                 # Let's re-run single validation to get the error message for UI if it failed completely.
                 validation = VALIDATOR.validate_addition(self.builder.ship, component, target_layer)
                 if not validation.is_valid:
                     self.builder.show_error(f"Cannot add: {', '.join(validation.errors)}")
                 return False
        return False

    def get_target_layer_at(self, pos):
        """
        Determines if the position is within a layer's drop zone.
        """
        if not self.rect.collidepoint(pos):
             return None
        
        mx, my = pos
        current_checking_layer = None
        
        # We need to account for scroll position!
        # The items are inside scroll_container. 
        # get_abs_rect on the items *should* handle this if pygame_gui is working normally.
        
        for item in self.items:
            abs_rect = item.panel.get_abs_rect()
            
            # Since header defines the start of a layer section, we track it.
            if isinstance(item, LayerHeaderItem):
                current_checking_layer = item.layer_type
            
            # If we are hovering THIS item, and we have established a current layer, return it.
            if abs_rect.collidepoint(mx, my):
                return current_checking_layer
                
        # If hovering empty space at bottom of list...
        if current_checking_layer:
            # Check if we are physically below the last item?
            # Or just assume if we are in the panel rect (checked at start) and last header was X...
            return current_checking_layer
            
        return None

    def get_range_selection(self, start_comp, end_comp):
        """
        Returns a list of components corresponding to the UI items between start_comp and end_comp (inclusive).
        Handles both individual items and collapsed groups in the range.
        
        Args:
            start_comp: The component object starting the range (or None).
            end_comp: The component object ending the range (from user click).
            
        Returns:
            List of Component objects.
        """
        if not start_comp or not end_comp:
            return [end_comp]
            
        start_idx = -1
        end_idx = -1
        
        # Locate indices in the UI list
        for idx, item in enumerate(self.items):
            # Check Individual Items
            if isinstance(item, IndividualComponentItem):
                if item.component is start_comp:
                    start_idx = idx
                if item.component is end_comp:
                    end_idx = idx
            
            # Check Group Items (if start/end comp is inside a collapsed group?)
            # Usually range selection starts from a visible selection. 
            # If the component is inside a group, it wouldn't be 'selected' in the single context 
            # unless the group was expanded. 
            # But let's check just in case.
            elif isinstance(item, LayerComponentItem):
                # If the group key matches the 'start_comp's group? 
                # Ideally we rely on the object identity match for individuals.
                pass
                
        if start_idx == -1 or end_idx == -1:
            # If we couldn't find one of the endpoints in the visible list (e.g. scrolled out? No, self.items has all),
            # Fallback to just the end item.
            return [end_comp]
            
        # Determine range
        low = min(start_idx, end_idx)
        high = max(start_idx, end_idx)
        
        subset = self.items[low : high + 1]
        result_components = []
        
        from ui.builder.grouping_strategies import get_component_group_key
        
        for item in subset:
            if isinstance(item, IndividualComponentItem):
                result_components.append(item.component)
            elif isinstance(item, LayerComponentItem):
                # Resolve group to components
                # We can't access 'ship' easily to find them all efficiently without strategy,
                # but we can iterate ship layers like BuilderSceneGUI does.
                g_key = item.group_key
                for layers in self.builder.ship.layers.values():
                    for c in layers['components']:
                        if get_component_group_key(c) == g_key:
                            result_components.append(c)
                            
        return result_components
