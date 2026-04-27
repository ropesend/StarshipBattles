from __future__ import annotations

from typing import Any
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIImage
from .panel_layout_config import StructurePanelLayoutConfig, ComponentItemContext

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
ACTION_MOVE_UP_INDIVIDUAL = 'move_up_individual'
ACTION_MOVE_DOWN_INDIVIDUAL = 'move_down_individual'
ACTION_MOVE_UP_GROUP = 'move_up_group'
ACTION_MOVE_DOWN_GROUP = 'move_down_group'

class IndividualComponentItem:
    """Row for a single component inside an expanded group."""
    def __init__(self, ctx: ComponentItemContext, component, max_mass, y_pos, is_selected, is_last=False, layer_type=None):
        """
        Create an individual component row item.

        Args:
            ctx: ComponentItemContext with manager, container, width, sprite_mgr, event_handler, config
            component: The component to display
            max_mass: Maximum mass for percentage calculation
            y_pos: Vertical position
            is_selected: Whether this item is selected
            is_last: Whether this is the last item in the group (affects tree line)
            layer_type: The LayerType this component belongs to
        """
        self.component = component
        self.layer_type = layer_type
        self.event_handler = ctx.event_handler
        self.is_selected = is_selected
        self.is_last = is_last
        self.config = ctx.config
        self.ctx = ctx
        self.height = ctx.config.ROW_HEIGHT
        self.rect = pygame.Rect(0, y_pos, ctx.width, self.height)

        self.modifier_icons = []

        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=ctx.manager,
            container=ctx.container,
            object_id='#individual_component_item',
            anchors=ctx.config.ANCHOR_TOP_LEFT
        )
        self.panel.background_colour = pygame.Color(ctx.config.BG_COLOR_INDIVIDUAL)

        # Clickable Area (Button covering text/icon)
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, ctx.width - 35, self.height),
            text="",
            manager=ctx.manager,
            container=self.panel,
            object_id='#transparent_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Tree Connector
        self.line_surface = self._create_tree_line(is_last, ctx.config)
        self.line_image = UIImage(
            relative_rect=pygame.Rect(5, 0, 20, self.height),
            image_surface=self.line_surface,
            manager=ctx.manager,
            container=self.panel
        )

        # Icon
        sprite = ctx.sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (ctx.config.ICON_SIZE, ctx.config.ICON_SIZE))
            UIImage(
                relative_rect=pygame.Rect(ctx.config.INDENT_STEP, (self.height - ctx.config.ICON_SIZE)//2, ctx.config.ICON_SIZE, ctx.config.ICON_SIZE),
                image_surface=scaled,
                manager=ctx.manager,
                container=self.panel
            )

        UILabel(
            relative_rect=pygame.Rect(ctx.config.LABEL_OFFSET_X, 0, ctx.config.NAME_WIDTH, self.height),
            text=f"{component.name}",
            manager=ctx.manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )

        self._rebuild_modifier_icons()


        # Mass (positioned left of button zone)
        self.mass_label = UILabel(
            relative_rect=pygame.Rect(-220, 0, ctx.config.MASS_WIDTH, self.height),
            text=f"{int(component.mass)}t",
            manager=ctx.manager,
            container=self.panel,
            anchors=ctx.config.ANCHOR_TOP_RIGHT.copy()
        )

        pct_val = (component.mass / max_mass * 100) if max_mass > 0 else 0
        self.pct_label = UILabel(
            relative_rect=pygame.Rect(-170, 0, 50, self.height),
            text=f"{pct_val:.1f}%",
            manager=ctx.manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

        # Buttons (right-aligned): ↑ ↓ ≡ + -
        btn_w = 28
        btn_h = 20
        gap = 2
        # Position from right edge: - at -32, + at -62, ≡ at -92, ↓ at -122, ↑ at -152
        r = -(btn_w + gap)  # starting offset for rightmost button

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="-",
            manager=ctx.manager,
            container=self.panel,
            object_id='#delete_button',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Add Button
        self.add_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="+",
            manager=ctx.manager,
            container=self.panel,
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Drag Handle
        self.drag_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="≡",
            manager=ctx.manager,
            container=self.panel,
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Move Down Button
        self.move_down_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="↓",
            manager=ctx.manager,
            container=self.panel,
            object_id='#mini_arrow_btn',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Move Up Button
        self.move_up_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="↑",
            manager=ctx.manager,
            container=self.panel,
            object_id='#mini_arrow_btn',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        
    def update(self, component, max_mass, is_selected, is_last=False) -> None:
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

        self._rebuild_modifier_icons()

    def _rebuild_modifier_icons(self) -> None:
        """Build modifier icons for non-default values."""
        # Clear existing
        for icon in self.modifier_icons:
            icon.kill()
        self.modifier_icons = []

        if not self.ctx.modifier_icon_service:
            return

        component = self.component
        modified_ids = []
        for mod in component.modifiers:
            if mod.value != mod.definition.default_val:
                modified_ids.append((mod.definition.id, mod.definition.name, mod.value))

        if not modified_ids:
            return

        icon_size = self.ctx.config.MODIFIER_ICON_SIZE
        icon_y = (self.height - icon_size) // 2

        # Anchor from the right side, starting left of the mass label (-220)
        total_width = len(modified_ids) * (icon_size + self.ctx.config.MODIFIER_ICON_SPACING)
        start_x_from_right = -220 - total_width
        current_x = start_x_from_right

        for mod_id, mod_name, mod_value in modified_ids:
            surf = self.ctx.modifier_icon_service.get_icon(mod_id)
            if surf:
                # Format value for tooltip
                val_str = f"{mod_value:.2f}" if isinstance(mod_value, float) else str(mod_value)
                icon_image = UIImage(
                    relative_rect=pygame.Rect(current_x, icon_y, icon_size, icon_size),
                    image_surface=surf,
                    manager=self.ctx.manager,
                    container=self.panel,
                    tool_tip_text=f"{mod_name}: {val_str}",
                    anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
                )
                self.modifier_icons.append(icon_image)
                current_x += icon_size + self.ctx.config.MODIFIER_ICON_SPACING

    def _create_tree_line(self, is_last, config) -> Any:
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

    def get_abs_rect(self) -> Any:
        """Get the absolute screen rect of this item's panel."""
        return self.panel.get_abs_rect()
        
    def handle_event(self, event) -> Any:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.remove_button:
                return self.event_handler.handle_item_action(ACTION_REMOVE_INDIVIDUAL, (self.component, self.layer_type))
            elif event.ui_element == self.add_button:
                return self.event_handler.handle_item_action(ACTION_ADD_INDIVIDUAL, (self.component, self.layer_type))
            elif event.ui_element == self.drag_button:
                return self.event_handler.handle_item_action(ACTION_START_DRAG, self.component)
            elif event.ui_element == self.move_up_button:
                return self.event_handler.handle_item_action(ACTION_MOVE_UP_INDIVIDUAL, (self.component, self.layer_type))
            elif event.ui_element == self.move_down_button:
                return self.event_handler.handle_item_action(ACTION_MOVE_DOWN_INDIVIDUAL, (self.component, self.layer_type))
            elif event.ui_element == self.select_button:
                return self.event_handler.handle_item_action(ACTION_SELECT_INDIVIDUAL, self.component)
        return False

    def set_move_buttons_enabled(self, can_move_up: bool, can_move_down: bool) -> None:
        """Enable/disable move buttons based on layer availability."""
        if can_move_up:
            self.move_up_button.enable()
        else:
            self.move_up_button.disable()
        if can_move_down:
            self.move_down_button.enable()
        else:
            self.move_down_button.disable()

    def kill(self) -> None:
        self.panel.kill()

class LayerComponentItem:
    """Row representing a component group."""
    def __init__(self, ctx: ComponentItemContext, component, count, total_mass, total_pct, is_expanded,
                 group_key, is_selected, y_pos, layer_type=None):
        """
        Create a component group row item.

        Args:
            ctx: ComponentItemContext with manager, container, width, sprite_mgr, event_handler, config
            component: Representative component for this group
            count: Number of components in the group
            total_mass: Total mass of all components in the group
            total_pct: Percentage of layer mass this group represents
            is_expanded: Whether the group is expanded to show individuals
            group_key: Unique key for this component group
            is_selected: Whether this group is selected
            y_pos: Vertical position
            layer_type: The LayerType this group belongs to
        """
        self.group_key = group_key
        self.layer_type = layer_type
        self.event_handler = ctx.event_handler
        self.count = count
        self.is_selected = is_selected
        self.config = ctx.config
        self.ctx = ctx
        self.height = ctx.config.LAYER_ROW_HEIGHT
        self.rect = pygame.Rect(0, y_pos, ctx.width, self.height)

        self.modifier_icons = []

        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=ctx.manager,
            container=ctx.container,
            object_id='#layer_component_item',
            anchors=ctx.config.ANCHOR_TOP_LEFT
        )
        self.panel.background_colour = pygame.Color(ctx.config.BG_COLOR_GROUP)

        # Selection Button
        self.select_button = UIButton(
            relative_rect=pygame.Rect(0, 0, ctx.width - 35, self.height),
            text="",
            manager=ctx.manager,
            container=self.panel,
            object_id='#transparent_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Expand Button
        self.expand_button = UIButton(
            relative_rect=pygame.Rect(2, 5, 20, 30),
            text="▲" if is_expanded else "▼",
            manager=ctx.manager,
            container=self.panel,
            object_id='#expand_button'
        )
        if count <= 1:
            self.expand_button.hide()

        # Icon
        sprite = ctx.sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (ctx.config.LAYER_ICON_SIZE, ctx.config.LAYER_ICON_SIZE))
            UIImage(
                relative_rect=pygame.Rect(ctx.config.INDENT_STEP, (self.height - ctx.config.LAYER_ICON_SIZE)//2, ctx.config.LAYER_ICON_SIZE, ctx.config.LAYER_ICON_SIZE),
                image_surface=scaled,
                manager=ctx.manager,
                container=self.panel
            )

        # Name & Count
        name_text = f"{component.name}"
        if count > 1:
            name_text += f" x{count}"

        self.name_label = UILabel(
            relative_rect=pygame.Rect(ctx.config.LAYER_NAME_OFFSET_X, 0, ctx.config.NAME_WIDTH, self.height),
            text=name_text,
            manager=ctx.manager,
            container=self.panel,
            object_id='#left_aligned_label'
        )

        self.component = component
        self._rebuild_modifier_icons()

        # Mass (positioned left of button zone)
        self.mass_label = UILabel(
            relative_rect=pygame.Rect(-220, 0, ctx.config.MASS_WIDTH, self.height),
            text=f"{int(total_mass)}t",
            manager=ctx.manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

        # Percent
        self.pct_label = UILabel(
            relative_rect=pygame.Rect(-170, 0, ctx.config.PCT_WIDTH, self.height),
            text=f"{total_pct:.1f}%",
            manager=ctx.manager,
            container=self.panel,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )

        # Buttons (right-aligned): ↑ ↓ + -
        btn_w = 28
        btn_h = 30
        gap = 2
        r = -(btn_w + gap)

        # Remove Button
        self.remove_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="-",
            manager=ctx.manager,
            container=self.panel,
            object_id='#delete_button',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Add Button
        self.add_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="+",
            manager=ctx.manager,
            container=self.panel,
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Move Down Button
        self.move_down_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="↓",
            manager=ctx.manager,
            container=self.panel,
            object_id='#mini_arrow_btn',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )
        r -= (btn_w + gap)

        # Move Up Button
        self.move_up_button = UIButton(
            relative_rect=pygame.Rect(r - 1, 5, btn_w, btn_h),
            text="↑",
            manager=ctx.manager,
            container=self.panel,
            object_id='#mini_arrow_btn',
            anchors=ctx.config.ANCHOR_TOP_RIGHT
        )

    def update(self, count, total_mass, total_pct, is_expanded, is_selected, component_name) -> None:
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
        if count <= 1:
            self.expand_button.hide()
        else:
            self.expand_button.show()
            arrow = "▲" if is_expanded else "▼"
            self.expand_button.set_text(arrow)

        self._rebuild_modifier_icons()

    def _rebuild_modifier_icons(self) -> None:
        """Build modifier icons for non-default values."""
        # Clear existing
        for icon in self.modifier_icons:
            icon.kill()
        self.modifier_icons = []

        if not self.ctx.modifier_icon_service:
            return

        component = self.component
        modified_ids = []
        # Group items always have identical modifiers for all members
        for mod in component.modifiers:
            if mod.value != mod.definition.default_val:
                modified_ids.append((mod.definition.id, mod.definition.name, mod.value))

        if not modified_ids:
            return

        icon_size = self.ctx.config.MODIFIER_ICON_SIZE
        icon_y = (self.height - icon_size) // 2

        # Anchor from the right side, starting left of the mass label (-220)
        total_width = len(modified_ids) * (icon_size + self.ctx.config.MODIFIER_ICON_SPACING)
        start_x_from_right = -220 - total_width
        current_x = start_x_from_right

        for mod_id, mod_name, mod_value in modified_ids:
            surf = self.ctx.modifier_icon_service.get_icon(mod_id)
            if surf:
                # Format value for tooltip
                val_str = f"{mod_value:.2f}" if isinstance(mod_value, float) else str(mod_value)
                icon_image = UIImage(
                    relative_rect=pygame.Rect(current_x, icon_y, icon_size, icon_size),
                    image_surface=surf,
                    manager=self.ctx.manager,
                    container=self.panel,
                    tool_tip_text=f"{mod_name}: {val_str}",
                    anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
                )
                self.modifier_icons.append(icon_image)
                current_x += icon_size + self.ctx.config.MODIFIER_ICON_SPACING

    def handle_event(self, event) -> Any:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.expand_button:
                self.event_handler.handle_item_action(ACTION_TOGGLE_GROUP, self.group_key)
                return ('refresh_ui', None)
            elif event.ui_element == self.remove_button:
                return self.event_handler.handle_item_action(ACTION_REMOVE_GROUP, (self.group_key, self.layer_type))
            elif event.ui_element == self.add_button:
                return self.event_handler.handle_item_action(ACTION_ADD_GROUP, (self.group_key, self.layer_type))
            elif event.ui_element == self.move_up_button:
                return self.event_handler.handle_item_action(ACTION_MOVE_UP_GROUP, (self.group_key, self.layer_type))
            elif event.ui_element == self.move_down_button:
                return self.event_handler.handle_item_action(ACTION_MOVE_DOWN_GROUP, (self.group_key, self.layer_type))
            elif event.ui_element == self.select_button:
                return self.event_handler.handle_item_action(ACTION_SELECT_GROUP, self.group_key)
        return False

    def set_move_buttons_enabled(self, can_move_up: bool, can_move_down: bool) -> None:
        """Enable/disable move buttons based on layer availability."""
        if can_move_up:
            self.move_up_button.enable()
        else:
            self.move_up_button.disable()
        if can_move_down:
            self.move_down_button.enable()
        else:
            self.move_down_button.disable()

    def get_abs_rect(self) -> Any:
        return self.panel.get_abs_rect()

    def kill(self) -> None:
        self.panel.kill()

class LayerHeaderItem:
    """Header row for a Layer."""
    def __init__(self, ctx: ComponentItemContext, layer_type, current_mass, max_mass, is_expanded, y_pos):
        """
        Create a layer header row item.

        Args:
            ctx: ComponentItemContext with manager, container, width, event_handler, config
            layer_type: The layer type enum value
            current_mass: Current mass used in this layer
            max_mass: Maximum allowed mass for this layer
            is_expanded: Whether the layer is expanded
            y_pos: Vertical position
        """
        self.layer_type = layer_type
        self.event_handler = ctx.event_handler
        self.config = ctx.config
        self.height = ctx.config.HEADER_HEIGHT
        self.rect = pygame.Rect(0, y_pos, ctx.width, self.height)
        self.panel = UIPanel(
             relative_rect=self.rect,
             manager=ctx.manager,
             container=ctx.container,
             object_id='#layer_header_panel',
             anchors=ctx.config.ANCHOR_TOP_LEFT
        )

        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, ctx.width, self.height),
            text="",
            manager=ctx.manager,
            container=self.panel,
            object_id='#layer_header_button',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        arrow = "▲" if is_expanded else "▼"
        self.arrow_label = UILabel(
            relative_rect=pygame.Rect(5, 0, 20, self.height),
            text=arrow,
            manager=ctx.manager,
            container=self.panel
        )

        UILabel(
            relative_rect=pygame.Rect(30, 0, 100, self.height),
            text=layer_type.name,
            manager=ctx.manager,
            container=self.panel
        )

        pct_filled = (current_mass / max_mass * 100) if max_mass > 0 else 0
        stats_text = f"{int(current_mass)}/{int(max_mass)}t ({pct_filled:.1f}%)"

        obj_id = '#layer_stats_text'
        if current_mass > max_mass:
            obj_id = '#layer_stats_text_overflow'

        self.stats_label = UILabel(
            relative_rect=pygame.Rect(-210, 0, ctx.config.STATS_WIDTH, self.height),
            text=stats_text,
            manager=ctx.manager,
            container=self.panel,
            object_id=obj_id,
            anchors={'left': 'right', 'right': 'right', 'centerY': 'center'}
        )
        
    def update(self, current_mass, max_mass, is_expanded) -> None:
        arrow = "▲" if is_expanded else "▼"
        self.arrow_label.set_text(arrow)
        
        pct_filled = (current_mass / max_mass * 100) if max_mass > 0 else 0
        stats_text = f"{int(current_mass)}/{int(max_mass)}t ({pct_filled:.1f}%)"
        self.stats_label.set_text(stats_text)
        
        # Optional: Update Object ID for overflow color?
        # PygameGUI doesn't support changing object_id easily at runtime without rebuild. 
        # But we can change text color if we track the labels. For now, text update is good.
        
    def handle_event(self, event) -> bool | tuple:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.button:
            # Check for toggle suppression (e.g. from drop event)
            if self.event_handler.toggle_suppress_timer > 0:
                return False

            self.event_handler.handle_item_action(ACTION_TOGGLE_LAYER, self.layer_type)
            return ('refresh_ui', None)
        return False
        
    def kill(self) -> None:
        self.panel.kill()
