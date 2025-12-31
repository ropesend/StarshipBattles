
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIScrollingContainer, UIImage
from ship import LayerType


def get_component_group_key(component):
    """
    Returns a hashable key for grouping identical components.
    Key: (component_id, tuple(sorted((mod_id, mod_value))))
    """
    mod_list = []
    for m in component.modifiers:
        # Ignore readonly modifiers (like Mass Scaling) for grouping keys
        # This prevents stable application of modifiers from auto-ungrouping components
        # or causing key mismatch errors if values float slightly.
        if getattr(m.definition, 'readonly', False):
            continue
            
        # Value might be float, round for stability? Or keep precise?
        # Assuming exact match required for "identical".
        mod_list.append((m.definition.id, m.value))
    mod_list.sort()
    return (component.id, tuple(mod_list))

class IndividualComponentItem:
    """Row for a single component inside an expanded group."""
    def __init__(self, manager, container, component, max_mass, y_pos, width, sprite_mgr, callback_remove, callback_add, callback_select, is_selected):
        self.component = component
        self.callback_remove = callback_remove
        self.callback_add = callback_add
        self.callback_select = callback_select
        self.is_selected = is_selected  # Track selection state
        self.height = 30
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        # Use default color - highlight drawn as overlay
        bg_color = "#151515"
        
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#individual_component_item',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        self.panel.background_colour = pygame.Color(bg_color) 
        
        # Clickable Area (Button covering text/icon)
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, width - 35, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#transparent_button', 
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Indent Icon
        icon_size = 20
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (icon_size, icon_size))
            UIImage(
                relative_rect=pygame.Rect(25, (self.height - icon_size)//2, icon_size, icon_size),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )
            
        UILabel(
            relative_rect=pygame.Rect(50, 0, 150, self.height),
            text=f"{component.name}",
            manager=manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )
        
        # Mass shifted right
        UILabel(
            relative_rect=pygame.Rect(-160, 0, 60, self.height),
            text=f"{int(component.mass)}t",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
        pct_val = (component.mass / max_mass * 100) if max_mass > 0 else 0
        UILabel(
            relative_rect=pygame.Rect(-100, 0, 50, self.height),
            text=f"{pct_val:.1f}%",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

        # Add Button
        self.add_button = UIButton(
            relative_rect=pygame.Rect(-62, 5, 28, 20),
            text="+",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(-32, 5, 28, 20),
            text="-",
            manager=manager,
            container=self.panel,
            object_id='#delete_button',
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
    def get_abs_rect(self):
        """Get the absolute screen rect of this item's panel."""
        return self.panel.get_abs_rect()
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.remove_button:
                return self.callback_remove(self.component)
            elif event.ui_element == self.add_button:
                return self.callback_add(self.component)
            elif event.ui_element == self.select_button:
                return self.callback_select(self.component)
        return False

    def kill(self):
        self.panel.kill()

class LayerComponentItem:
    """
    Row representing a component group.
    """
    def __init__(self, manager, container, component, count, total_mass, total_pct, is_expanded, callback_expand, callback_select, callback_add, callback_remove, group_key, is_selected, y_pos, width, sprite_mgr):
        self.group_key = group_key
        self.callback_expand = callback_expand
        self.callback_select = callback_select
        self.callback_add = callback_add
        self.callback_remove = callback_remove
        self.count = count
        self.is_selected = is_selected  # Track selection state
        self.height = 40
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        bg_color = "#202020"  # Always use default - highlight drawn as overlay

        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#layer_component_item',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        self.panel.background_colour = pygame.Color(bg_color)
        
        # Selection Button (Covers most area)
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, width - 35, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#transparent_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Expand Button
        if count > 1:
            arrow = "▼" if is_expanded else "▶"
            self.expand_button = UIButton(
                relative_rect=pygame.Rect(2, 5, 20, 30),
                text=arrow,
                manager=manager,
                container=self.panel,
                object_id='#expand_button'
            )
        else:
            self.expand_button = None
        
        # Icon
        icon_size = 32
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (icon_size, icon_size))
            UIImage(
                relative_rect=pygame.Rect(25, (self.height - icon_size)//2, icon_size, icon_size),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )
            
        # Name & Count
        name_text = f"{component.name}"
        if count > 1:
            name_text += f" x{count}"
            
        UILabel(
            relative_rect=pygame.Rect(65, 0, 160, self.height),
            text=name_text,
            manager=manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )
        
        # Mass
        UILabel(
            relative_rect=pygame.Rect(-160, 0, 60, self.height),
            text=f"{int(total_mass)}t",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
        # Percent
        UILabel(
            relative_rect=pygame.Rect(-100, 0, 50, self.height),
            text=f"{total_pct:.1f}%",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

        # Add Button
        self.add_button = UIButton(
            relative_rect=pygame.Rect(-62, 5, 28, 30),
            text="+",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(-32, 5, 28, 30),
            text="-",
            manager=manager,
            container=self.panel,
            object_id='#delete_button',
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.expand_button and event.ui_element == self.expand_button:
                self.callback_expand(self.group_key)
                return ('refresh_ui', None)
            elif event.ui_element == self.remove_button:
                return self.callback_remove(self.group_key)
            elif event.ui_element == self.add_button:
                return self.callback_add(self.group_key)
            elif event.ui_element == self.select_button:
                return self.callback_select(self.group_key)
        return False
    
    def get_abs_rect(self):
        """Get the absolute screen rect of this item's panel."""
        return self.panel.get_abs_rect()

    def kill(self):
        self.panel.kill()

class LayerHeaderItem:
    """
    Header row for a Layer (Core, Inner, etc.).
    Acts as a drop target and expand/collapse toggle.
    """
    def __init__(self, manager, container, layer_type, current_mass, max_mass, is_expanded, callback, y_pos, width):
        self.layer_type = layer_type
        self.callback = callback
        self.height = 30
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        self.panel = UIPanel(
             relative_rect=self.rect,
             manager=manager,
             container=container,
             object_id='#layer_header_panel',
             anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        self.width = width
        
        # Toggle Button (covers whole header for easy clicking)
        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, width, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#layer_header_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Icon / Arrow based on state
        arrow = "▼" if is_expanded else "▶"
        UILabel(
            relative_rect=pygame.Rect(5, 0, 20, self.height),
            text=arrow,
            manager=manager,
            container=self.panel
        )
        
        # Layer Name
        UILabel(
            relative_rect=pygame.Rect(30, 0, 100, self.height),
            text=layer_type.name,
            manager=manager,
            container=self.panel
        )
        
        # Mass Stats
        pct_filled = (current_mass / max_mass * 100) if max_mass > 0 else 0
        stats_text = f"{int(current_mass)}/{int(max_mass)}t ({pct_filled:.1f}%)"
        
        # Color based on fullness?
        obj_id = '#layer_stats_text'
        if current_mass > max_mass:
            obj_id = '#layer_stats_text_overflow'
            
        label = UILabel(
            relative_rect=pygame.Rect(-150, 0, 140, self.height),
            text=stats_text,
            manager=manager,
            container=self.panel,
            object_id=obj_id,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.button:
            self.callback(self.layer_type)
            return ('refresh_ui', None)
        return False
        
    def kill(self):
        self.panel.kill()

class LayerPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.items = [] 
        
        # State
        self.selected_group_key = None
        self.selected_component_id = None # Check by instance match?
        
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
        
        self.list_y = 40
        self.scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, self.list_y, rect.width, rect.height - self.list_y),
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        self.expanded_layers = {
            LayerType.CORE: True,
            LayerType.INNER: True,
            LayerType.OUTER: True,
            LayerType.ARMOR: True
        }
        self.expanded_groups = {} # Map group_key -> bool
        
        self.rebuild()
        
    def toggle_layer(self, layer_type):
        self.expanded_layers[layer_type] = not self.expanded_layers.get(layer_type, True)
        self.rebuild()
        
    def toggle_group(self, group_key):
        self.expanded_groups[group_key] = not self.expanded_groups.get(group_key, False)
        self.rebuild()
        
    def on_select_group(self, group_key):
        self.selected_group_key = group_key
        self.selected_component_id = None
        # self.rebuild() # Defer to builder_gui after state update
        return ('select_group', group_key)
        
    def on_select_individual(self, component):
        self.selected_group_key = None
        self.selected_component_id = component
        # self.rebuild() # Defer to builder_gui after state update
        return ('select_individual', component)
        
    def on_add_group(self, group_key):
        return ('add_group', group_key)

    def on_add_individual(self, component):
        return ('add_individual', component)

    def on_remove_group(self, group_key):
        return ('remove_group', group_key)
        
    def on_remove_individual(self, component):
        return ('remove_individual', component)
        
    def rebuild(self):
        for item in self.items:
            item.kill()
        self.items = []
        
        y_pos = 0
        container_rect = self.scroll_container.get_container().get_rect()
        content_width = container_rect.width
        
        layer_order = [LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        ship = self.builder.ship
        
        for l_type in layer_order:
            if l_type not in ship.layers: continue
            
            data = ship.layers[l_type]
            components = data['components']
            
            current_mass = sum(c.mass for c in components)
            max_mass = ship.max_mass_budget * data.get('max_mass_pct', 1.0)
            
            header = LayerHeaderItem(
                self.manager,
                self.scroll_container,
                l_type,
                current_mass,
                max_mass,
                self.expanded_layers.get(l_type, True),
                self.toggle_layer,
                y_pos,
                content_width
            )
            self.items.append(header)
            y_pos += header.height
            
            if self.expanded_layers.get(l_type, True):
                groups = self._group_components(components)
                for comp_list, count, mass_total, group_key in groups:
                    pct_val = (mass_total / max_mass * 100) if max_mass > 0 else 0
                    
                    # Force collapse if not a stack (prevent single item expanding)
                    if count <= 1:
                        is_expanded = False
                    else:
                        is_expanded = self.expanded_groups.get(group_key, False)
                    
                    # Use builder state for selection source of truth
                    # Use builder state for selection source of truth
                    is_selected_group = False
                    if self.builder.selected_components:
                        # Check if ANY component in this group is selected
                        # This highlights the group if any memeber is selected.
                        # OR we could require ALL. 
                        # Usually for "Group Selection" we want to know if the group CONCEPT is selected.
                        # But with multi-select, we might just have 1 item.
                        
                        # Let's say if ANY item in comp_list is in selected_components, we highlight group?
                        # Or maybe we only highlight if ALL are selected?
                        
                        # The 'select_group' action selects ALL components.
                        # So let's check if the first component is selected, that's a good proxy if we assume consistent group selection.
                        # But with multi-select across groups, checking just existence is safer.
                        
                        selected_objs = [x[2] for x in self.builder.selected_components]
                        # If first item is selected, treat group as having some selection focus
                        if comp_list[0] in selected_objs:
                            is_selected_group = True

                    # Use first component as template
                    comp_template = comp_list[0]
                    
                    item = LayerComponentItem(
                        self.manager,
                        self.scroll_container,
                        comp_template,
                        count,
                        mass_total,
                        pct_val,
                        is_expanded,
                        self.toggle_group,
                        self.on_select_group,
                        self.on_add_group,
                        self.on_remove_group,
                        group_key,
                        is_selected_group,
                        y_pos,
                        content_width,
                        self.builder.sprite_mgr
                    )
                    self.items.append(item)
                    y_pos += item.height
                    
                    if is_expanded:
                        for comp in comp_list:
                             # Highlight if: 1) this specific individual is selected, OR
                             # 2) the parent group is selected (and no specific individual override)
                             is_sel_ind = False
                             if self.builder.selected_component and self.builder.selected_component[2] is comp:
                                 is_sel_ind = True
                             elif is_selected_group:
                                 # Parent group is selected, so highlight all children
                                 is_sel_ind = True
                                 
                             ind_item = IndividualComponentItem(
                                self.manager,
                                self.scroll_container,
                                comp,
                                max_mass,
                                y_pos,
                                content_width,
                                self.builder.sprite_mgr,
                                self.on_remove_individual,
                                self.on_add_individual,
                                self.on_select_individual,
                                is_sel_ind
                             )
                             self.items.append(ind_item)
                             y_pos += ind_item.height
            
        self.scroll_container.set_scrollable_area_dimensions((content_width, y_pos))
        
    def _group_components(self, components):
        """
        Groups identical components.
        Returns list of tuples: (list_of_components, count, total_mass, group_key)
        """
        groups = {} # Map key -> list of components
        
        for c in components:
            key = get_component_group_key(c)
            if key not in groups:
                groups[key] = []
            groups[key].append(c)
            
        result = []
        # Sort groups by name of first component for stability
        sorted_keys = sorted(groups.keys(), key=lambda k: groups[k][0].name)
        
        for key in sorted_keys:
            comps = groups[key]
            total_mass = sum(c.mass for c in comps)
            result.append((comps, len(comps), total_mass, key))
            
        return result

    def handle_event(self, event):
        for item in self.items:
            if hasattr(item, 'handle_event'):
                result = item.handle_event(event)
                if result:
                    return result
        return False

    def update(self, dt):
        pass
        
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
                        highlight_surf.fill((80, 100, 130, 120))  # Semi-transparent blue selection
                        screen.blit(highlight_surf, clipped.topleft)

    def get_target_layer_at(self, pos):
        """
        Determines if the position is within a layer's drop zone.
        Returns LayerType if valid drop target found, else None.
        """
        # Mouse is absolute. Container is absolute.
        # But items inside container are relative to container scroll.
        # So check items' absolute rects.
        
        if not self.rect.collidepoint(pos):
             return None
             
        # Find which item (header or component) we are over
        # And map it to a layer
        
        # We need to iterate items and their absolute rects
        mx, my = pos
        
        # Check specific items first
        clicked_layer = None
        
        # Optimization: We know items are in self.items list.
        # Headers identify the start of a layer section.
        # Components following a header belong to that layer.
        
        current_checking_layer = None
        
        # Iterate top to bottom
        for item in self.items:
            # Get Item Rect Absolute
            # panel.get_abs_rect() handles container offset
            abs_rect = item.panel.get_abs_rect()
            
            # Track which layer section we are in
            if isinstance(item, LayerHeaderItem):
                current_checking_layer = item.layer_type
                
            if abs_rect.collidepoint(mx, my):
                return current_checking_layer
                
        # If we are in the panel but "below" the last item?
        # Maybe return the last layer? Or None?
        # User said "drop onto this new list".
        # If I drop in empty space at bottom, what happens?
        # Maybe nothing. Safer.
        
        return None
