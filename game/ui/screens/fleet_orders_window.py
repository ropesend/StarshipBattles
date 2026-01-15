
import pygame
import pygame_gui
from pygame_gui.windows import UIConfirmationDialog

from game.strategy.data.fleet import OrderType

class FleetOrdersWindow(pygame_gui.elements.UIWindow):
    """
    Window to manage a Fleet's orders.
    Allows re-ordering, deletion, undeletion, and clearing.
    """
    def __init__(self, rect, manager, fleet):
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=f"Orders: Fleet {fleet.id}",
            element_id='fleet_orders_window',
            resizable=True
        )
        self.fleet = fleet
        
        # Undo History: Stores (index, order_object) tuples
        self.deleted_history = [] 
        
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
        
        self.btn_undo = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, -40, 100, 30),
            text="Undo Delete",
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'left', 'top': 'bottom', 'bottom': 'bottom'}
        )
        self.btn_undo.disable()
        
        self.rows = [] # Keep track of row UI elements
        self.rebuild_list()
        
    def rebuild_list(self):
        """Clear and rebuild the order list rows."""
        # Clear existing rows
        for row in self.rows:
            for element in row.values():
                if hasattr(element, 'kill'):
                    element.kill()
        self.rows.clear()
        
        # Re-populate
        orders = self.fleet.orders
        gap = 5
        row_height = 40
        y_offset = 5
        
        # Calculate total content height for scrolling
        total_h = len(orders) * (row_height + gap) + 10
        self.list_container.set_scrollable_area_dimensions((self.list_container.rect.width - 20, total_h))
        
        for i, order in enumerate(orders):
            row_y = y_offset + i * (row_height + gap)
            
            # Row Container (Virtual or just positioning)
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
                relative_rect=pygame.Rect(40, row_y, 180, row_height),
                text=desc,
                manager=self.ui_manager,
                container=self.list_container
            )
            
            # 3. Controls (Up, Down, Delete)
            btn_up = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(230, row_y, 30, row_height),
                text="^",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#up_{i}" # Tag for event handling
            )
            if i == 0: btn_up.disable()
            
            btn_down = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(265, row_y, 30, row_height),
                text="v",
                manager=self.ui_manager,
                container=self.list_container,
                object_id=f"#down_{i}"
            )
            if i == len(orders) - 1: btn_down.disable()
            
            btn_del = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, row_y, 30, row_height),
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
             return f"MOVE {t}"
        elif order.type == OrderType.COLONIZE:
             # target is Planet object
             p_name = order.target.name if hasattr(order.target, 'name') else "Unknown"
             return f"COLONIZE {p_name}"
        elif order.type == OrderType.MOVE_TO_FLEET:
             f_id = order.target.id if hasattr(order.target, 'id') else "?"
             return f"INTERCEPT Fleet {f_id}"
        elif order.type == OrderType.JOIN_FLEET:
             f_id = order.target.id if hasattr(order.target, 'id') else "?"
             return f"JOIN Fleet {f_id}"
        else:
             return f"{order.type.name}"

    def process_event(self, event):
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_clear:
                self.show_clear_confirmation()
                handled = True
            
            elif event.ui_element == self.btn_undo:
                self.undo_delete()
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
        """Swap order at index with index + direction."""
        new_index = index + direction
        orders = self.fleet.orders
        
        if 0 <= new_index < len(orders):
            orders[index], orders[new_index] = orders[new_index], orders[index]
            self.rebuild_list()
            
    def delete_order(self, index):
        """Remove order and add to undo stack."""
        if 0 <= index < len(self.fleet.orders):
            order = self.fleet.orders.pop(index)
            # Store (original_index, order)
            self.deleted_history.append((index, order))
            self.btn_undo.enable()
            self.rebuild_list()
            
    def undo_delete(self):
        """Restore last deleted order."""
        if self.deleted_history:
            original_index, order = self.deleted_history.pop()
            
            # Clamp index to bounds (it might be out of range if other items were deleted/moved)
            # Actually, insert handles out-of-bounds by appending, which is fine.
            if original_index > len(self.fleet.orders):
                original_index = len(self.fleet.orders)
                
            self.fleet.orders.insert(original_index, order)
            
            if not self.deleted_history:
                self.btn_undo.disable()
                
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
        """Handle events from the wider application (like dialog confirmations)."""
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element.object_ids[-1] == '#confirm_clear_orders':
                self.fleet.clear_orders()
                self.deleted_history.clear()
                self.btn_undo.disable()
                self.rebuild_list()
                return True
        return False
