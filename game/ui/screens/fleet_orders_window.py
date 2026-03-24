"""Fleet orders management window.

Cross-layer imports (acceptable for UI):
- OrderType: Runtime - displays and filters order types

PROJ-208 Phase 1: Refactored to use DeleteFleetOrderCommand and ReorderFleetOrderCommand
via command pipeline callbacks. Undo feature removed (command-level undo is future work).
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

class FleetOrdersWindow(pygame_gui.elements.UIWindow):
    """
    Window to manage a Fleet's orders.
    Allows re-ordering, deletion, and clearing.

    PROJ-208: Operations route through command callbacks instead of direct mutation.
    """
    def __init__(
        self,
        rect,
        manager,
        fleet,
        input_mapper: Optional['InputMapper'] = None,
        clear_orders_callback: Optional['Callable[[int], None]'] = None,
        delete_order_callback: Optional['Callable[[int, int], None]'] = None,
        reorder_order_callback: Optional['Callable[[int, int, int], None]'] = None
    ):
        """Initialize the Fleet Orders Window.

        Args:
            rect: Window position and size.
            manager: pygame_gui UIManager.
            fleet: Fleet object to display orders for.
            input_mapper: Optional InputMapper for hotkey tooltips.
            clear_orders_callback: Callback(fleet_id) to clear all orders.
            delete_order_callback: Callback(fleet_id, order_index) to delete an order.
            reorder_order_callback: Callback(fleet_id, order_index, direction: int) to reorder (-1=up, +1=down).
        """
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=f"Orders: Fleet {fleet.id}",
            element_id='fleet_orders_window',
            resizable=True
        )
        self.fleet = fleet
        self._mapper = input_mapper
        # PROJ-207 Phase 4: Callback to dispatch clear orders through command pipeline
        self._clear_orders_callback = clear_orders_callback
        # PROJ-208 Phase 1: Callbacks for delete/reorder operations
        self._delete_order_callback = delete_order_callback
        self._reorder_order_callback = reorder_order_callback
        
        # --- UI Layout ---
        
        # 1. Top Control Bar (Maybe just header is enough?)
        
        # 2. Main List Area
        # Use a Scrolling Container for rows
        container_rect = pygame.Rect(0, 0, rect.width - 32, rect.height - 100)
        self.list_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=container_rect,
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # 3. Footer Area
        self.btn_clear = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-110, -40, 100, 30),
            text="Clear All",
            manager=manager,
            container=self,
            anchors={'left': 'right', 'right': 'right', 'top': 'bottom', 'bottom': 'bottom'}
        )

        self.rows = []  # Keep track of row UI elements
        self._last_order_count = len(fleet.orders)
        self.rebuild_list()
        self._apply_tooltips()
        
    def update(self, dt):
        """Standard pygame-gui update. Checks for order changes."""
        super().update(dt)
        
        # Performance: Only rebuild if order count changed
        # Note: If we need to detect order content changes (like direction swap at same index),
        # we would need a deeper check, but for this task, adding/removing is the key.
        if len(self.fleet.orders) != self._last_order_count:
            self._last_order_count = len(self.fleet.orders)
            self.rebuild_list()
    def rebuild_list(self):
        """Clear and rebuild the order list rows."""
        # Clear existing rows
        for row in self.rows:
            for key, element in row.items():
                if key != 'order_ref':  # order_ref is the Order object, not a UI element
                    element.kill()
        self.rows.clear()
        
        # Re-populate
        orders = self.fleet.orders
        gap = 5
        row_height = UIConfig.ROW_HEIGHT_STANDARD
        y_offset = 5
        
        # Calculate total content height for scrolling
        total_h = len(orders) * (row_height + gap) + 10
        self.list_container.set_scrollable_area_dimensions((self.list_container.rect.width - 20, total_h))
        
        # Calculate button positions relative to container width
        content_width = self.list_container.get_container().get_rect().width
        btn_size = 30
        btn_gap = 5
        # Buttons anchored to right edge: [up] [down] [del]
        btn_del_x = content_width - btn_size - btn_gap
        btn_down_x = btn_del_x - btn_size - btn_gap
        btn_up_x = btn_down_x - btn_size - btn_gap
        # Description fills space between index label and first button
        desc_x = 40
        desc_width = btn_up_x - desc_x - btn_gap

        for i, order in enumerate(orders):
            row_y = y_offset + i * (row_height + gap)

            # 1. Index Label
            lbl_idx = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, row_y, 30, row_height),
                text=str(i + 1),
                manager=self.ui_manager,
                container=self.list_container
            )

            # 2. Description
            desc = self._get_order_description(order)
            lbl_desc = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(desc_x, row_y, desc_width, row_height),
                text=desc,
                manager=self.ui_manager,
                container=self.list_container
            )

            # 3. Controls (Up, Down, Delete) — positioned relative to container width
            btn_up = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_up_x, row_y, btn_size, row_height),
                text="^",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#up_{i}"
            )
            if i == 0: btn_up.disable()

            btn_down = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_down_x, row_y, btn_size, row_height),
                text="v",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#down_{i}"
            )
            if i == len(orders) - 1: btn_down.disable()

            btn_del = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_del_x, row_y, btn_size, row_height),
                text="X",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#del_{i}"
            )
            
            # Store refs
            self.rows.append({
                'idx': lbl_idx,
                'desc': lbl_desc,
                'up': btn_up,
                'down': btn_down,
                'del': btn_del,
                'order_ref': order
            })
            
    def _get_order_description(self, order):
        if order.type == OrderType.MOVE:
             t = order.target
             if isinstance(t, HexCoord):
                 return f"MOVE ({t.q}, {t.r})"
             return f"MOVE {t}"
        elif order.type == OrderType.COLONIZE:
             # target is Planet object
             p_name = order.target.name if is_planet(order.target) else "Unknown"
             return f"COLONIZE {p_name}"
        elif order.type == OrderType.MOVE_TO_FLEET:
             f_id = order.target.id if is_fleet(order.target) else "?"
             return f"INTERCEPT Fleet {f_id}"
        elif order.type == OrderType.JOIN_FLEET:
             f_id = order.target.id if is_fleet(order.target) else "?"
             return f"JOIN Fleet {f_id}"
        elif order.type == OrderType.BUILD:
             # PROJ-67: Show queue size for BUILD orders
             queue_size = len(self.fleet.construction_queue)
             return f"BUILDING ({queue_size} items)"
        elif order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
             # PROJ-68: Show TRANSFER/POPULATION order details
             if isinstance(order.target, dict):
                 direction = order.target.get('direction', '?')
                 
                 # Set description based on direction param
                 if order.type == OrderType.LOAD_POPULATION:
                     return "load cargo"
                 elif order.type == OrderType.UNLOAD_POPULATION:
                     return "drop cargo"
                 else:
                     return "load cargo" if direction == "load" else "drop cargo"
                     
             return "TRANSFER"
        else:
             return f"{order.type.name}"

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        clear_hint = self._mapper.get_display_text(InputAction.FLEET_ORDERS_CLEAR)
        if clear_hint:
            self.btn_clear.set_tooltip(f"Clear All ({clear_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper.

        Args:
            event: A pygame KEYDOWN event.

        Returns:
            True if the event was handled.
        """
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["fleet_orders"])
        if action == InputAction.FLEET_ORDERS_CLEAR:
            self.show_clear_confirmation()
            return True
        return False

    def process_event(self, event):
        handled = super().process_event(event)

        # Keyboard hotkeys via InputMapper
        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_clear:
                self.show_clear_confirmation()
                handled = True
            else:
                # Check row buttons
                # IDs are #up_0, #down_1, #del_2 etc.
                obj_id = event.ui_element.object_ids[-1] # Get most specific ID
                if obj_id:
                     if obj_id.startswith("#up_"):
                         idx = int(obj_id.split("_")[1])
                         self.move_order(idx, -1)
                         handled = True
                     elif obj_id.startswith("#down_"):
                         idx = int(obj_id.split("_")[1])
                         self.move_order(idx, 1)
                         handled = True
                     elif obj_id.startswith("#del_"):
                         idx = int(obj_id.split("_")[1])
                         self.delete_order(idx)
                         handled = True
                         
        return handled
        
    def move_order(self, index, direction):
        """Swap order at index with index + direction.

        PROJ-208: Routes through ReorderFleetOrderCommand via callback.
        """
        if not self._reorder_order_callback:
            return

        new_index = index + direction
        if 0 <= new_index < len(self.fleet.orders):
            # PROJ-208: Pass int direction (-1 for up, +1 for down) to command handler
            self._reorder_order_callback(self.fleet.id, index, direction)
            self.rebuild_list()

    def delete_order(self, index):
        """Remove order at index.

        PROJ-208: Routes through DeleteFleetOrderCommand via callback.
        """
        if not self._delete_order_callback:
            return

        if 0 <= index < len(self.fleet.orders):
            self._delete_order_callback(self.fleet.id, index)
            self.rebuild_list()
            
    def show_clear_confirmation(self):
        """Show confirmation dialog."""
        UIConfirmationDialog(
            rect=pygame.Rect(0, 0, 300, 200),
            manager=self.ui_manager, # Use window's manager
            action_long_desc="Are you sure you want to clear ALL orders for this fleet?",
            window_title="Confirm Clear",
            action_short_name="Clear",
            blocking=True,
            object_id='#confirm_clear_orders'
        )
        
        # Note: Handling the confirmation require listening for the confirmation event
        # The StrategyScreen usually handles `UI_CONFIRMATION_DIALOG_CONFIRMED`
        # But since we are a window, we can also bind a listener if we were the manager?
        # Actually standard practice in pygame_gui is events bubble up.
        # We need to catch the event in `StrategyScreen` or here if we have access.
        # StrategyScreen delegates via manager.process_events. 
        # But `FleetOrdersWindow.process_event` is called manually or by manager?
        # Manager calls process_event on windows.
        
    # We need to hook into the Confirmation Dialog result.
    # The confirmation dialog emits an event.
    # Since this class receives events via `process_event`, we should check for it here?
    # NO, standard UIWindow `process_event` only gets events FOR ITSELF (clicks inside).
    # Global events like CONFIRMED from a dialog MIGHT not reach here unless we listen globally.
    
    # Wait, `UIWindow` typically doesn't receive `UI_CONFIRMATION_DIALOG_CONFIRMED` unless it's the `ui_element` that fired it?
    # No, the dialog is the element.
    # So `StrategyScreen` (the scene) needs to forward events, or we need to handle it.
    
    # Let's check `StrategyScreen.handle_event`. It calls `self.manager.process_events(event)`.
    # And then handles specific things.
    # If we want `FleetOrdersWindow` to handle its own popups, we might need a custom event handler loop or
    # rely on `StrategyScreen` passing valid events to us?
    # But `manager.process_events` is internal.
    
    # BETTER APPROACH:
    # `process_event` in `UIWindow` is usually for input events.
    # We need to capture the `UI_CONFIRMATION_DIALOG_CONFIRMED` event in the main loop or `StrategyScreen` and route it.
    
    # HOWEVER, `FleetOrdersWindow` is just a UI element.
    # The event loop in `StrategyScreen` sees all.
    # If I rename the object_id of the dialog to something unique like `#fleet_clear_confirm`,
    # then `StrategyScreen` can detect it?
    # OR, we can attach the handling logic to the window and ask `StrategyScreen` to route it?
    
    # EASIEST:
    # Add logic in `FleetOrdersWindow` to check for the event if passed to it?
    # `pygame_gui` doesn't automatically route "other" events to windows.
    
    # Let's make `StrategyScreen` forward events to open windows?
    # Or just handle the logic in `StrategyScreen.handle_event`?
    # But that breaks encapsulation.
    
    # Alternative: Use a callback-based tailored dialog or modify `handle_event` in `StrategyScreen` to specificallly look for this dialog ID.
    
    # I will stick to checking for the event in the `StrategyScreen` for now, 
    # OR I can implement a check in `FleetOrdersWindow` if I manually pass the event to it from `StrategyScreen`.
    
    # Let's assume for this task, I will implement a `handle_global_event` method on `FleetOrdersWindow` and call it from `StrategyScreen`.
    
    def handle_global_event(self, event):
        """Handle events from the wider application (like dialog confirmations).

        PROJ-207 Phase 4: Clear orders routes through command pipeline via callback.
        PROJ-208 Phase 1: Removed fallback - callback is now required.
        """
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element.object_ids[-1] == '#confirm_clear_orders':
                if self._clear_orders_callback:
                    self._clear_orders_callback(self.fleet.id)
                    self.rebuild_list()
                    return True
        return False
