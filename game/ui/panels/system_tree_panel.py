import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UIImage, UILabel, UIScrollingContainer

class SystemTreeItem:
    """Base class for items in the tree."""
    def __init__(self, obj, label, icon_surface=None, container=None, manager=None, 
                 width=200, height=30, y_pos=0, indent=0, parent_panel=None):
        self.obj = obj
        self.label_text = label
        self.icon_surface = icon_surface
        self.container = container
        self.manager = manager
        self.width = width
        self.height = height
        self.y_pos = y_pos
        self.indent = indent
        self.parent_panel = parent_panel
        
        self.expanded = False
        self.children = [] # List of SystemTreeItem
        
        # UI Elements
        self.rect = pygame.Rect(0, y_pos, width, height)
        
        # Panel for row (clickable)
        # We simulate a button covering the row? Or just a transparent panel + label?
        # A Button is easiest for click handling.
        
        # Indent logic
        x_offset = indent * 20
        
        self.button = UIButton(
            relative_rect=pygame.Rect(x_offset, y_pos, width - x_offset, height),
            text="", # Custom drawing or use label separately?
            manager=manager,
            container=container,
            object_id='#tree_item_bg' # For theming?
        )
        # We want left aligned text and icon.
        # UIButton centers text by default. 
        # So we add a Label and Icon on top (passthrough False? No, need clicks).
        # We can disable the button textual part and just use it for bg/clicks.
        
        # Icon
        icon_x = x_offset + 5
        self.icon_image = None
        if icon_surface:
            # Scale icon
            scaled = pygame.transform.smoothscale(icon_surface, (20, 20))
            self.icon_image = UIImage(
                relative_rect=pygame.Rect(icon_x, y_pos + 5, 20, 20),
                image_surface=scaled,
                manager=manager,
                container=container
            )
            icon_x += 25
            
        # Arrow for folders
        self.arrow_button = None
        text_x = icon_x
        
        # Label
        # Left Justified Text
        self.label = UILabel(
            relative_rect=pygame.Rect(text_x, y_pos, width - text_x - 10, height),
            text=label,
            manager=manager,
            container=container,
            object_id='#tree_item_label' # Custom alignment in theme?
        )
        # By default UILabel is centered? 
        # Theme can contextually set "text_horiz_alignment": "left"?
        # Or we can subclass?
        
    def add_child(self, item):
        self.children.append(item)
        
    def set_expanded(self, expanded):
        self.expanded = expanded
        # Update arrow icon?

    def set_position(self, y):
        self.y_pos = y
        # Move elements
        self.rect.y = y
        self.button.set_relative_position((self.rect.x + (self.indent*20), y))
        
        if self.icon_image:
            self.icon_image.set_relative_position((self.rect.x + (self.indent*20) + 5, y + 5))
            
        text_x = (self.indent*20) + 5 + (25 if self.icon_image else 0)
        self.label.set_relative_position((text_x, y))
        
        if self.arrow_button:
            # Arrow pos logic
            pass

    def show(self):
        self.button.show()
        self.label.show()
        if self.icon_image: self.icon_image.show()
        
    def hide(self):
        self.button.hide()
        self.label.hide()
        if self.icon_image: self.icon_image.hide()
        
    def kill(self):
        self.button.kill()
        self.label.kill()
        if self.icon_image: self.icon_image.kill()


class SystemTreePanel:
    """
    Manages a collapsible tree view of system objects.
    Replaces UISelectionList.
    """
    def __init__(self, relative_rect, manager, container):
        self.manager = manager
        self.container = container
        self.rect = relative_rect
        
        self.scrolling_container = UIScrollingContainer(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        self.items = [] # Linear list of ALL items (for lookup)
        self.root_items = [] # Top level items
        self.expanded_groups = set() # Keys
        
        self.on_selection_callback = None
        
    def set_items(self, contents, scene_interface, flat_view=False):
        """
        Rebuild tree from content list.
        scene_interface used to fetch assets logic (dependency injection).
        flat_view: If True, do not use top-level "Planetary System" grouping (for Sector View).
        """
        # Clear old
        for item in self.items:
            item.kill()
        self.items = []
        self.root_items = []
        
        if not contents:
            return
            
        # Group detection
        planets = [x for x in contents if hasattr(x, 'planet_type')]
        stars = [x for x in contents if hasattr(x, 'color') and hasattr(x, 'mass')]
        warp_points = [x for x in contents if hasattr(x, 'destination_id')]
        
        others = [x for x in contents if 
                  not hasattr(x, 'planet_type') and
                  not (hasattr(x, 'color') and hasattr(x, 'mass')) and
                  not hasattr(x, 'destination_id')]
        
        # 1. Add Others (Systems, Fleets, etc.)
        for obj in others:
            if hasattr(obj, 'stars'): continue # Skip System object itself if present
            
            label = scene_interface._get_label_for_obj(obj)
            icon = scene_interface._get_object_asset(obj) # Resolve asset
            
            item = SystemTreeItem(obj, label, icon, 
                                  container=self.scrolling_container, 
                                  manager=self.manager,
                                  width=self.rect.width - 20,
                                  parent_panel=self)
            self.root_items.append(item)
            self.items.append(item)
            
        # 2. Stars Grouping
        if len(stars) > 1:
            group_label = f"Stars ({len(stars)})"
            # Use first star icon if available
            group_icon = scene_interface._get_object_asset(stars[0])
            
            stars_header = SystemTreeItem(None, group_label, group_icon,
                                    container=self.scrolling_container,
                                    manager=self.manager,
                                    width=self.rect.width - 20,
                                    parent_panel=self)
            stars_header.is_group = True
            stars_header.group_key = "stars_group"
            stars_header.expanded = "stars_group" in self.expanded_groups
            
            self.root_items.append(stars_header)
            self.items.append(stars_header)
            
            for star in stars:
                label = star.name
                icon = scene_interface._get_object_asset(star)
                leaf = SystemTreeItem(star, label, icon,
                                      container=self.scrolling_container,
                                      manager=self.manager,
                                      width=self.rect.width - 20,
                                      indent=1,
                                      parent_panel=self)
                stars_header.add_child(leaf)
                self.items.append(leaf)
        elif len(stars) == 1:
             # Single Star - Add directly
             star = stars[0]
             label = star.name # Or "Star: Name"?
             icon = scene_interface._get_object_asset(star)
             item = SystemTreeItem(star, label, icon,
                                   container=self.scrolling_container,
                                   manager=self.manager,
                                   width=self.rect.width - 20,
                                   parent_panel=self)
             self.root_items.append(item)
             self.items.append(item)

        # 3. Warp Points
        if len(warp_points) > 1:
            group_label = f"Warp Points ({len(warp_points)})"
            group_icon = scene_interface._get_object_asset(warp_points[0]) if warp_points else None
            
            wp_header = SystemTreeItem(None, group_label, group_icon,
                                    container=self.scrolling_container,
                                    manager=self.manager,
                                    width=self.rect.width - 20,
                                    parent_panel=self)
            wp_header.is_group = True
            wp_header.group_key = "wp_group"
            wp_header.expanded = "wp_group" in self.expanded_groups
            
            self.root_items.append(wp_header)
            self.items.append(wp_header)
            
            for wp in warp_points:
                label = f"To {wp.destination_id}"
                icon = scene_interface._get_object_asset(wp)
                leaf = SystemTreeItem(wp, label, icon,
                                      container=self.scrolling_container,
                                      manager=self.manager,
                                      width=self.rect.width - 20,
                                      indent=1,
                                      parent_panel=self)
                wp_header.add_child(leaf)
                self.items.append(leaf)
        elif len(warp_points) == 1:
             wp = warp_points[0]
             label = f"Warp to {wp.destination_id}"
             icon = scene_interface._get_object_asset(wp)
             item = SystemTreeItem(wp, label, icon,
                                   container=self.scrolling_container,
                                   manager=self.manager,
                                   width=self.rect.width - 20,
                                   parent_panel=self)
             self.root_items.append(item)
             self.items.append(item)

        # 4. Planets
        if planets:
            # Helper to create planet nodes
            def create_planet_nodes(parent_item, indent_level):
                # Group by Hex
                hex_groups = {}
                for p in planets:
                    h = p.location
                    key = (h.q, h.r)
                    if key not in hex_groups: hex_groups[key] = []
                    hex_groups[key].append(p)
                
                for key, p_list in hex_groups.items():
                    # Sort stack by size
                    p_list.sort(key=lambda x: x.mass, reverse=True)
                    
                    if len(p_list) > 1:
                        # Stack Group
                        top_p = p_list[0]
                        stack_label = f"Sector [{key[0]},{key[1]}] (x{len(p_list)})"
                        stack_icon = scene_interface._get_object_asset(top_p)
                        
                        stack_item = SystemTreeItem(None, stack_label, stack_icon,
                                                    container=self.scrolling_container,
                                                    manager=self.manager,
                                                    width=self.rect.width - 20,
                                                    indent=indent_level,
                                                    parent_panel=self)
                        
                        stack_item.is_group = True
                        stack_item.group_key = f"stack_{key}"
                        stack_item.expanded = f"stack_{key}" in self.expanded_groups
                        
                        parent_item.add_child(stack_item) if parent_item else self.root_items.append(stack_item)
                        self.items.append(stack_item)
                        
                        for p in p_list:
                            p_label = p.name
                            p_icon = scene_interface._get_object_asset(p)
                            leaf = SystemTreeItem(p, p_label, p_icon,
                                                  container=self.scrolling_container,
                                                  manager=self.manager,
                                                  width=self.rect.width - 20,
                                                  indent=indent_level + 1,
                                                  parent_panel=self)
                            stack_item.add_child(leaf)
                            self.items.append(leaf)
                            
                    else:
                        # Single planet
                        p = p_list[0]
                        p_label = p.name
                        p_icon = scene_interface._get_object_asset(p)
                        leaf = SystemTreeItem(p, p_label, p_icon,
                                              container=self.scrolling_container,
                                              manager=self.manager,
                                              width=self.rect.width - 20,
                                              indent=indent_level,
                                              parent_panel=self)
                        parent_item.add_child(leaf) if parent_item else self.root_items.append(leaf)
                        self.items.append(leaf)

            if flat_view:
                create_planet_nodes(None, 0)
            else:
                if len(planets) > 1:
                    largest = max(planets, key=lambda p: p.mass)
                    group_label = f"Planetary System ({largest.name}) ({len(planets)})"
                    group_icon = scene_interface._get_object_asset(largest)
                    
                    header = SystemTreeItem(None, group_label, group_icon,
                                            container=self.scrolling_container,
                                            manager=self.manager,
                                            width=self.rect.width - 20,
                                            parent_panel=self)
                    
                    header.is_group = True
                    header.group_key = "planets_root"
                    header.expanded = "planets_root" in self.expanded_groups
                    
                    self.root_items.append(header)
                    self.items.append(header)
                    create_planet_nodes(header, 1)
                else:
                    # Single Planet -> No Root Group
                    create_planet_nodes(None, 0)

        self.layout()
        
    def layout(self):
        """Reposition visible items (recursive)."""
        self.y_cursor = 5
        
        def process_item(item):
            item.set_position(self.y_cursor)
            item.show()
            self.y_cursor += item.height + 2
            
            if hasattr(item, 'is_group'):
                if item.expanded:
                    for child in item.children:
                        process_item(child)
                else:
                    # Hide children recursively
                    self._hide_recursive(item)
                    
        for item in self.root_items:
            process_item(item)
            
        # Update Scroll container content size
        self.scrolling_container.set_scrollable_area_dimensions((self.rect.width - 20, self.y_cursor))
        
    def _hide_recursive(self, item):
        for child in item.children:
            child.hide()
            if hasattr(child, 'is_group'):
                self._hide_recursive(child)
        
    def process_event(self, event):
        """Handle clicks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check if one of our items
            for item in self.items:
                if event.ui_element == item.button:
                    self.on_click(item)
                    return True
        return False
        
    def on_click(self, item):
        if hasattr(item, 'is_group'):
            # Toggle
            item.expanded = not item.expanded
            if item.expanded:
                self.expanded_groups.add(item.group_key)
                
                # Recursive Expand Children (Expand All)
                # Mainly for System View to expand Sector Stacks automatically
                for child in item.children:
                    if hasattr(child, 'is_group'):
                        child.expanded = True
                        if hasattr(child, 'group_key'):
                            self.expanded_groups.add(child.group_key)
            else:
                if item.group_key in self.expanded_groups:
                    self.expanded_groups.remove(item.group_key)
            self.layout()
            
        elif item.obj:
            # Select
            if self.on_selection_callback:
                self.on_selection_callback(item.obj)
                
    def set_selection_callback(self, callback):
        self.on_selection_callback = callback
        
    def set_dimensions(self, dimensions):
        self.rect.size = dimensions
        self.scrolling_container.set_dimensions(dimensions)
        self.layout()
