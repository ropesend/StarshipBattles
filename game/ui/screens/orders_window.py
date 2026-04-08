"""Orders management window for fleets and planets.

PROJ-238: Generalized from FleetOrdersWindow to work with any IOrderable entity.

Cross-layer imports (acceptable for UI):
- OrderType: Runtime - displays and filters order types
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.windows import UIConfirmationDialog

from game.ui.config import UIConfig
from game.core.hex_math import HexCoord
from game.core.input_actions import InputAction
from game.core.protocols import is_planet, is_fleet
from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from typing import Callable

EDITABLE_ORDER_TYPES = frozenset({
    OrderType.MOVE,
    OrderType.TRANSFER,
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
})


class OrdersWindow(pygame_gui.elements.UIWindow):
    """
    Window to manage an entity's order queue (fleet or planet).
    Allows re-ordering, deletion, editing, and clearing.

    PROJ-238: Generalized from FleetOrdersWindow.
    """
    def __init__(
        self,
        rect,
        manager,
        entity,
        entity_type: str = "fleet",
        input_mapper: Optional['InputMapper'] = None,
        clear_orders_callback: Optional['Callable[[int], None]'] = None,
        delete_order_callback: Optional['Callable[[int, int], None]'] = None,
        reorder_order_callback: Optional['Callable[[int, int, int], None]'] = None,
        edit_order_callback: Optional['Callable[[int, int, object], None]'] = None,
    ):
        """Initialize the Orders Window.

        Args:
            rect: Window position and size.
            manager: pygame_gui UIManager.
            entity: IOrderable entity (Fleet or Planet) to display orders for.
            entity_type: "fleet" or "planet" — affects title and descriptions.
            input_mapper: Optional InputMapper for hotkey tooltips.
            clear_orders_callback: Callback(entity_id) to clear all orders.
            delete_order_callback: Callback(entity_id, order_index) to delete an order.
            reorder_order_callback: Callback(entity_id, order_index, direction) to reorder.
        """
        # Determine display title
        if entity_type == "planet":
            title = f"Orders: {entity.name}"
        else:
            title = f"Orders: Fleet {entity.id}"

        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=title,
            element_id='orders_window',
            resizable=True
        )
        self.entity = entity
        self.entity_type = entity_type
        self._mapper = input_mapper
        self._clear_orders_callback = clear_orders_callback
        self._delete_order_callback = delete_order_callback
        self._reorder_order_callback = reorder_order_callback
        self._edit_order_callback = edit_order_callback

        # --- UI Layout ---
        container_rect = pygame.Rect(0, 0, rect.width - 32, rect.height - 100)
        self.list_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=container_rect,
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        self.btn_clear = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-110, -40, 100, 30),
            text="Clear All",
            manager=manager,
            container=self,
            anchors={'left': 'right', 'right': 'right', 'top': 'bottom', 'bottom': 'bottom'}
        )

        self.rows = []
        self._last_order_count = len(entity.orders)
        self.rebuild_list()
        self._apply_tooltips()

    def update(self, dt):
        super().update(dt)
        if len(self.entity.orders) != self._last_order_count:
            self._last_order_count = len(self.entity.orders)
            self.rebuild_list()

    def rebuild_list(self):
        """Clear and rebuild the order list rows."""
        for row in self.rows:
            for key, element in row.items():
                if key != 'order_ref':
                    element.kill()
        self.rows.clear()

        orders = self.entity.orders
        gap = 5
        row_height = UIConfig.ROW_HEIGHT_STANDARD
        y_offset = 5

        total_h = len(orders) * (row_height + gap) + 10
        self.list_container.set_scrollable_area_dimensions((self.list_container.rect.width - 20, total_h))

        content_width = self.list_container.get_container().get_rect().width
        btn_size = 30
        btn_gap = 5
        # Layout: [desc] [E] [^] [v] [X]  — E only shown for editable orders
        btn_del_x = content_width - btn_size - btn_gap
        btn_down_x = btn_del_x - btn_size - btn_gap
        btn_up_x = btn_down_x - btn_size - btn_gap
        btn_edit_x = btn_up_x - btn_size - btn_gap
        desc_x = 40
        desc_width = btn_edit_x - desc_x - btn_gap

        for i, order in enumerate(orders):
            row_y = y_offset + i * (row_height + gap)
            is_editable = order.type in EDITABLE_ORDER_TYPES

            lbl_idx = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, row_y, 30, row_height),
                text=str(i + 1),
                manager=self.ui_manager,
                container=self.list_container
            )

            desc = self._get_order_description(order)
            lbl_desc = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(desc_x, row_y, desc_width, row_height),
                text=desc,
                manager=self.ui_manager,
                container=self.list_container
            )

            row_dict = {
                'idx': lbl_idx,
                'desc': lbl_desc,
                'order_ref': order,
            }

            # Edit button (only for editable order types)
            if is_editable:
                btn_edit = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(btn_edit_x, row_y, btn_size, row_height),
                    text="E",
                    manager=self.ui_manager,
                    container=self.list_container,
                    object_id=f"#edit_{i}"
                )
                row_dict['edit'] = btn_edit

            btn_up = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_up_x, row_y, btn_size, row_height),
                text="^",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#up_{i}"
            )
            if i == 0:
                btn_up.disable()
            row_dict['up'] = btn_up

            btn_down = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_down_x, row_y, btn_size, row_height),
                text="v",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#down_{i}"
            )
            if i == len(orders) - 1:
                btn_down.disable()
            row_dict['down'] = btn_down

            btn_del = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_del_x, row_y, btn_size, row_height),
                text="X",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#del_{i}"
            )
            row_dict['del'] = btn_del

            self.rows.append(row_dict)

    def _get_order_description(self, order):
        """Get human-readable description for an order."""
        if order.type == OrderType.MOVE:
            t = order.target
            if isinstance(t, HexCoord):
                return f"MOVE ({t.q}, {t.r})"
            return f"MOVE {t}"
        elif order.type == OrderType.COLONIZE:
            t = order.target
            if isinstance(t, dict):
                planet_obj = t.get('planet')
                p_name = planet_obj.name if planet_obj else 'Any Planet'
            elif is_planet(t):
                p_name = t.name
            else:
                p_name = 'Unknown'
            return f"COLONIZE {p_name}"
        elif order.type == OrderType.MOVE_TO_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            return f"INTERCEPT Fleet {f_id}"
        elif order.type == OrderType.JOIN_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            return f"JOIN Fleet {f_id}"
        elif order.type == OrderType.BUILD:
            if hasattr(self.entity, 'construction_queue'):
                queue_size = len(self.entity.construction_queue)
                return f"BUILDING ({queue_size} items)"
            return "BUILDING"
        elif order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
            if isinstance(order.target, dict):
                direction = order.target.get('direction', '?')
                if order.type == OrderType.LOAD_POPULATION:
                    return "load cargo"
                elif order.type == OrderType.UNLOAD_POPULATION:
                    return "drop cargo"
                else:
                    return "load cargo" if direction == "load" else "drop cargo"
            return "TRANSFER"
        # PROJ-238: Planet order descriptions
        elif order.type == OrderType.ACTIVATE_ABILITY:
            ability = order.target.get('ability_name', 'ability') if isinstance(order.target, dict) else 'ability'
            return f"ACTIVATE {ability.upper()}"
        elif order.type == OrderType.DEACTIVATE_ABILITY:
            ability = order.target.get('ability_name', 'ability') if isinstance(order.target, dict) else 'ability'
            return f"DEACTIVATE {ability.upper()}"
        else:
            return f"{order.type.name}"

    def _apply_tooltips(self) -> None:
        if not self._mapper:
            return
        clear_hint = self._mapper.get_display_text(InputAction.FLEET_ORDERS_CLEAR)
        if clear_hint:
            self.btn_clear.set_tooltip(f"Clear All ({clear_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["fleet_orders"])
        if action == InputAction.FLEET_ORDERS_CLEAR:
            self.show_clear_confirmation()
            return True
        return False

    def process_event(self, event):
        handled = super().process_event(event)

        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_clear:
                self.show_clear_confirmation()
                handled = True
            else:
                obj_id = event.ui_element.object_ids[-1]
                if obj_id:
                    if obj_id.startswith("#up_"):
                        idx = int(obj_id.split("_")[1])
                        self.move_order(idx, -1)
                        handled = True
                    elif obj_id.startswith("#down_"):
                        idx = int(obj_id.split("_")[1])
                        self.move_order(idx, 1)
                        handled = True
                    elif obj_id.startswith("#edit_"):
                        idx = int(obj_id.split("_")[1])
                        self.edit_order(idx)
                        handled = True
                    elif obj_id.startswith("#del_"):
                        idx = int(obj_id.split("_")[1])
                        self.delete_order(idx)
                        handled = True

        return handled

    def move_order(self, index, direction):
        if not self._reorder_order_callback:
            return
        new_index = index + direction
        if 0 <= new_index < len(self.entity.orders):
            self._reorder_order_callback(self.entity.id, index, direction)
            self.rebuild_list()

    def edit_order(self, index):
        if not self._edit_order_callback:
            return
        if 0 <= index < len(self.entity.orders):
            order = self.entity.orders[index]
            self._edit_order_callback(self.entity.id, index, order)

    def delete_order(self, index):
        if not self._delete_order_callback:
            return
        if 0 <= index < len(self.entity.orders):
            self._delete_order_callback(self.entity.id, index)
            self.rebuild_list()

    def show_clear_confirmation(self):
        entity_label = self.entity.name if self.entity_type == "planet" else f"fleet {self.entity.id}"
        UIConfirmationDialog(
            rect=pygame.Rect(0, 0, 300, 200),
            manager=self.ui_manager,
            action_long_desc=f"Are you sure you want to clear ALL orders for {entity_label}?",
            window_title="Confirm Clear",
            action_short_name="Clear",
            blocking=True,
            object_id='#confirm_clear_orders'
        )

    def handle_global_event(self, event):
        """Handle events from the wider application (like dialog confirmations)."""
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element.object_ids[-1] == '#confirm_clear_orders':
                if self._clear_orders_callback:
                    self._clear_orders_callback(self.entity.id)
                    self.rebuild_list()
                    return True
        return False


# PROJ-238: Backward compatibility alias
FleetOrdersWindow = OrdersWindow
