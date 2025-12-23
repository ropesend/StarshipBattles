
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
        # Value might be float, round for stability? Or keep precise?
        # Assuming exact match required for "identical".
        mod_list.append((m.definition.id, m.value))
    mod_list.sort()
    return (component.id, tuple(mod_list))

class IndividualComponentItem:
    """Row for a single component inside an expanded group."""
    def __init__(self, manager, container, component, max_mass, y_pos, width, sprite_mgr):
        self.component = component
        self.height = 30
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#individual_component_item',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
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
            container=self.panel
        )
        
        UILabel(
            relative_rect=pygame.Rect(-160, 0, 80, self.height),
            text=f"{int(component.mass)}t",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
        pct_val = (component.mass / max_mass * 100) if max_mass > 0 else 0
        UILabel(
            relative_rect=pygame.Rect(-70, 0, 60, self.height),
            text=f"{pct_val:.1f}%",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
    def kill(self):
        self.panel.kill()

class LayerComponentItem:
    """
    Row representing a component group.
    """
    def __init__(self, manager, container, component, count, total_mass, total_pct, is_expanded, callback, group_key, y_pos, width, sprite_mgr):
        self.group_key = group_key
        self.callback = callback
        self.count = count
        self.height = 40
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#layer_component_item',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Helper to make row clickable
        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, width, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#layer_component_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Expansion Arrow (if count > 1)
        if count > 1:
            arrow = "▼" if is_expanded else "▶"
            UILabel(
                relative_rect=pygame.Rect(2, 0, 15, self.height),
                text=arrow,
                manager=manager,
                container=self.panel
            )
        
        # Icon
        icon_size = 32
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (icon_size, icon_size))
            UIImage(
                relative_rect=pygame.Rect(20, (self.height - icon_size)//2, icon_size, icon_size),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )
            
        # Name & Count
        name_text = f"{component.name}"
        if count > 1:
            name_text += f" x{count}"
            
        UILabel(
            relative_rect=pygame.Rect(60, 0, 160, self.height),
            text=name_text,
            manager=manager,
            container=self.panel
        )
        
        # Mass
        UILabel(
            relative_rect=pygame.Rect(-160, 0, 80, self.height),
            text=f"{int(total_mass)}t",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
        # Percent
        UILabel(
            relative_rect=pygame.Rect(-70, 0, 60, self.height),
            text=f"{total_pct:.1f}%",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.button:
            if self.count > 1:
                self.callback(self.group_key)
                return True
        return False

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
            return True
        return False
        
    def kill(self):
        self.panel.kill()

class LayerPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.items = [] 
        
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
        
    def rebuild(self):
        for item in self.items:
            item.kill()
        self.items = []
        
        y_pos = 0
        content_width = self.scroll_container.get_container().get_rect().width
        
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
                    is_expanded = self.expanded_groups.get(group_key, False)
                    
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
                        group_key,
                        y_pos,
                        content_width,
                        self.builder.sprite_mgr
                    )
                    self.items.append(item)
                    y_pos += item.height
                    
                    if is_expanded:
                        for comp in comp_list:
                             ind_item = IndividualComponentItem(
                                self.manager,
                                self.scroll_container,
                                comp,
                                max_mass,
                                y_pos,
                                content_width,
                                self.builder.sprite_mgr
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
                if item.handle_event(event):
                    return True
        return False

    def update(self, dt):
        pass
        
    def draw(self, screen):
        pass

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
