import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIImage
from ui.builder.panel_layout_config import StructurePanelLayoutConfig

# Action Constants for Command Pattern
ACTION_SELECT_INDIVIDUAL = 'select_individual'
ACTION_SELECT_GROUP = 'select_group'
ACTION_ADD_INDIVIDUAL = 'add_individual'
ACTION_ADD_GROUP = 'add_group'
ACTION_REMOVE_INDIVIDUAL = 'remove_individual'
ACTION_REMOVE_GROUP = 'remove_group'
ACTION_TOGGLE_GROUP = 'toggle_group'
ACTION_TOGGLE_LAYER = 'toggle_layer'
ACTION_START_DRAG = 'start_drag'

class IndividualComponentItem:
    """Row for a single component inside an expanded group."""
    def __init__(self, manager, container, component, max_mass, y_pos, width, sprite_mgr, event_handler, is_selected, is_last=False, config=StructurePanelLayoutConfig()):
        self.component = component
        self.event_handler = event_handler
        self.is_selected = is_selected
        self.is_last = is_last
        self.config = config
        self.height = config.ROW_HEIGHT
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#individual_component_item',
            anchors=config.ANCHOR_TOP_LEFT
        )
        self.panel.background_colour = pygame.Color(config.BG_COLOR_INDIVIDUAL) 
        
        # Clickable Area (Button covering text/icon)
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, width - 35, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#transparent_button', 
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Tree Connector
        self.line_surface = self._create_tree_line(is_last, config)
        self.line_image = UIImage(
            relative_rect=pygame.Rect(5, 0, 20, self.height),
            image_surface=self.line_surface,
            manager=manager,
            container=self.panel
        )
        
        # Icon
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (config.ICON_SIZE, config.ICON_SIZE))
            UIImage(
                relative_rect=pygame.Rect(config.INDENT_STEP, (self.height - config.ICON_SIZE)//2, config.ICON_SIZE, config.ICON_SIZE),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )
            
        UILabel(
            relative_rect=pygame.Rect(config.LABEL_OFFSET_X, 0, config.NAME_WIDTH, self.height),
            text=f"{component.name}",
            manager=manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )
        
        
        # Mass shifted right
        self.mass_label = UILabel(
            relative_rect=pygame.Rect(-160, 0, config.MASS_WIDTH, self.height),
            text=f"{int(component.mass)}t",
            manager=manager,
            container=self.panel,
            anchors=config.ANCHOR_TOP_RIGHT.copy()
        )
        self.mass_label.set_dimensions((config.MASS_WIDTH, self.height)) # Fix anchor adjustment if needed? pygame_gui usually handles it
        
        pct_val = (component.mass / max_mass * 100) if max_mass > 0 else 0
        self.pct_label = UILabel(
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
            anchors=config.ANCHOR_TOP_RIGHT
        )

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(-32, 5, 28, 20),
            text="-",
            manager=manager,
            container=self.panel,
            object_id='#delete_button',
            anchors=config.ANCHOR_TOP_RIGHT
        )

        # Drag Handle
        self.drag_button = UIButton(
            relative_rect=pygame.Rect(-92, 5, 28, 20),
            text="≡",
            manager=manager,
            container=self.panel,
            anchors=config.ANCHOR_TOP_RIGHT
        )
        
    def update(self, component, max_mass, is_selected, is_last=False):
        """Update relevant data in-place."""
        self.component = component
        self.is_selected = is_selected
        
        # Update Tree Line if changed
        if is_last != self.is_last:
            self.is_last = is_last
            self.line_image.set_image(self._create_tree_line(is_last, self.config))
        
        self.mass_label.set_text(f"{int(component.mass)}t")
        
        pct_val = (component.mass / max_mass * 100) if max_mass > 0 else 0
        self.pct_label.set_text(f"{pct_val:.1f}%")

    def _create_tree_line(self, is_last, config):
        surf = pygame.Surface((20, self.height), pygame.SRCALPHA)
        color = pygame.Color(config.TREE_LINE_COLOR)
        
        # Vertical Line
        # Center X = 10
        # If not last: Line goes top to bottom
        # If last: Line goes top to center
        # Also need horizontal line to item
        
        center_x = 10
        center_y = self.height // 2
        
        end_y = self.height if not is_last else center_y
        
        # Vertical
        pygame.draw.line(surf, color, (center_x, 0), (center_x, end_y), 1)
        
        # Horizontal (Connect to item)
        pygame.draw.line(surf, color, (center_x, center_y), (20, center_y), 1)
        
        return surf

    def get_abs_rect(self):
        """Get the absolute screen rect of this item's panel."""
        return self.panel.get_abs_rect()
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.remove_button:
                return self.event_handler.handle_item_action(ACTION_REMOVE_INDIVIDUAL, self.component)
            elif event.ui_element == self.add_button:
                return self.event_handler.handle_item_action(ACTION_ADD_INDIVIDUAL, self.component)
            elif event.ui_element == self.drag_button:
                return self.event_handler.handle_item_action(ACTION_START_DRAG, self.component)
            elif event.ui_element == self.select_button:
                return self.event_handler.handle_item_action(ACTION_SELECT_INDIVIDUAL, self.component)
        return False

    def kill(self):
        self.panel.kill()

class LayerComponentItem:
    """Row representing a component group."""
    def __init__(self, manager, container, component, count, total_mass, total_pct, is_expanded, 
                 group_key, is_selected, y_pos, width, sprite_mgr, event_handler, config=StructurePanelLayoutConfig()):
        self.group_key = group_key
        self.event_handler = event_handler
        self.count = count
        self.is_selected = is_selected
        self.config = config
        self.height = config.LAYER_ROW_HEIGHT
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#layer_component_item',
            anchors=config.ANCHOR_TOP_LEFT
        )
        self.panel.background_colour = pygame.Color(config.BG_COLOR_GROUP)
        
        # Selection Button
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, width - 35, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#transparent_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Expand Button
        self.expand_button = None
        if count > 1:
            arrow = "▼" if is_expanded else "▶"
            self.expand_button = UIButton(
                relative_rect=pygame.Rect(2, 5, 20, 30),
                text=arrow,
                manager=manager,
                container=self.panel,
                object_id='#expand_button'
            )
        
        # Icon
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (config.LAYER_ICON_SIZE, config.LAYER_ICON_SIZE))
            UIImage(
                relative_rect=pygame.Rect(config.INDENT_STEP, (self.height - config.LAYER_ICON_SIZE)//2, config.LAYER_ICON_SIZE, config.LAYER_ICON_SIZE),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )
            
        # Name & Count
        name_text = f"{component.name}"
        if count > 1:
            name_text += f" x{count}"
            
        self.name_label = UILabel(
            relative_rect=pygame.Rect(config.LAYER_NAME_OFFSET_X, 0, config.NAME_WIDTH, self.height),
            text=name_text,
            manager=manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )
        
        # Mass
        self.mass_label = UILabel(
            relative_rect=pygame.Rect(-160, 0, config.MASS_WIDTH, self.height),
            text=f"{int(total_mass)}t",
            manager=manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
        # Percent
        self.pct_label = UILabel(
            relative_rect=pygame.Rect(-100, 0, config.PCT_WIDTH, self.height),
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
            anchors=config.ANCHOR_TOP_RIGHT
        )

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(-32, 5, 28, 30),
            text="-",
            manager=manager,
            container=self.panel,
            object_id='#delete_button',
            anchors=config.ANCHOR_TOP_RIGHT
        )

    def update(self, count, total_mass, total_pct, is_expanded, is_selected, component_name):
        self.count = count
        self.is_selected = is_selected
        
        # Update labels
        name_text = f"{component_name}"
        if count > 1:
            name_text += f" x{count}"
        self.name_label.set_text(name_text)
        
        self.mass_label.set_text(f"{int(total_mass)}t")
        self.pct_label.set_text(f"{total_pct:.1f}%")
        
        # Update expand arrow
        if self.expand_button:
            if count <= 1:
                self.expand_button.hide()
            else:
                self.expand_button.show()
                arrow = "▼" if is_expanded else "▶"
                self.expand_button.set_text(arrow)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.expand_button and event.ui_element == self.expand_button:
                self.event_handler.handle_item_action(ACTION_TOGGLE_GROUP, self.group_key)
                return ('refresh_ui', None)
            elif event.ui_element == self.remove_button:
                return self.event_handler.handle_item_action(ACTION_REMOVE_GROUP, self.group_key)
            elif event.ui_element == self.add_button:
                return self.event_handler.handle_item_action(ACTION_ADD_GROUP, self.group_key)
            elif event.ui_element == self.select_button:
                return self.event_handler.handle_item_action(ACTION_SELECT_GROUP, self.group_key)
        return False
    
    def get_abs_rect(self):
        return self.panel.get_abs_rect()

    def kill(self):
        self.panel.kill()

class LayerHeaderItem:
    """Header row for a Layer."""
    def __init__(self, manager, container, layer_type, current_mass, max_mass, is_expanded, event_handler, y_pos, width, config=StructurePanelLayoutConfig()):
        self.layer_type = layer_type
        self.event_handler = event_handler
        self.config = config
        self.height = config.HEADER_HEIGHT
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        self.panel = UIPanel(
             relative_rect=self.rect,
             manager=manager,
             container=container,
             object_id='#layer_header_panel',
             anchors=config.ANCHOR_TOP_LEFT
        )
        
        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, width, self.height),
            text="",
            manager=manager,
            container=self.panel,
            object_id='#layer_header_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        arrow = "▼" if is_expanded else "▶"
        self.arrow_label = UILabel(
            relative_rect=pygame.Rect(5, 0, 20, self.height),
            text=arrow,
            manager=manager,
            container=self.panel
        )
        
        UILabel(
            relative_rect=pygame.Rect(30, 0, 100, self.height),
            text=layer_type.name,
            manager=manager,
            container=self.panel
        )
        
        pct_filled = (current_mass / max_mass * 100) if max_mass > 0 else 0
        stats_text = f"{int(current_mass)}/{int(max_mass)}t ({pct_filled:.1f}%)"
        
        obj_id = '#layer_stats_text'
        if current_mass > max_mass:
            obj_id = '#layer_stats_text_overflow'
            
        self.stats_label = UILabel(
            relative_rect=pygame.Rect(-210, 0, config.STATS_WIDTH, self.height),
            text=stats_text,
            manager=manager,
            container=self.panel,
            object_id=obj_id,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
    def update(self, current_mass, max_mass, is_expanded):
        arrow = "▼" if is_expanded else "▶"
        self.arrow_label.set_text(arrow)
        
        pct_filled = (current_mass / max_mass * 100) if max_mass > 0 else 0
        stats_text = f"{int(current_mass)}/{int(max_mass)}t ({pct_filled:.1f}%)"
        self.stats_label.set_text(stats_text)
        
        # Optional: Update Object ID for overflow color?
        # PygameGUI doesn't support changing object_id easily at runtime without rebuild. 
        # But we can change text color if we track the labels. For now, text update is good.
        
    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.button:
            self.event_handler.handle_item_action(ACTION_TOGGLE_LAYER, self.layer_type)
            return ('refresh_ui', None)
        return False
        
    def kill(self):
        self.panel.kill()
