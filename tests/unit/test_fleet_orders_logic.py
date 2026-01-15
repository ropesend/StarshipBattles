
import unittest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType

# Mock the window to avoid full pygame init
class MockFleetOrdersWindow:
    def __init__(self, fleet):
        self.fleet = fleet
        self.deleted_history = []
        self.rows = []
        self.btn_undo = MagicMock()
        
    def rebuild_list(self):
        pass
        
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
            # Store (index, order)
            self.deleted_history.append((index, order))
            self.btn_undo.enable()
            self.rebuild_list()

    def undo_delete(self):
        """Restore last deleted order."""
        if self.deleted_history:
            original_index, order = self.deleted_history.pop()
            
            if original_index > len(self.fleet.orders):
                original_index = len(self.fleet.orders)
                
            self.fleet.orders.insert(original_index, order)
            
            if not self.deleted_history:
                self.btn_undo.disable()
                
            self.rebuild_list()

class TestFleetOrdersLogic(unittest.TestCase):
    def setUp(self):
        self.fleet = Fleet(1, 0, (0,0))
        self.fleet.orders = [
            FleetOrder(OrderType.MOVE, target=(10, 10)),
            FleetOrder(OrderType.COLONIZE, target="PlanetA"),
            FleetOrder(OrderType.MOVE, target=(20, 20))
        ]
        self.window = MockFleetOrdersWindow(self.fleet)
        
    def test_reorder_down(self):
        # Move first order down
        original_first = self.fleet.orders[0]
        self.window.move_order(0, 1)
        
        # Verify swap
        self.assertEqual(self.fleet.orders[1], original_first)
        self.assertEqual(self.fleet.orders[0].type, OrderType.COLONIZE)
        
    def test_reorder_up(self):
        # Move second order up
        original_second = self.fleet.orders[1]
        self.window.move_order(1, -1)
        
        # Verify swap
        self.assertEqual(self.fleet.orders[0], original_second)
        
    def test_delete_and_undo(self):
        original_len = len(self.fleet.orders)
        to_delete = self.fleet.orders[1]
        
        # Delete middle order
        self.window.delete_order(1)
        
        self.assertEqual(len(self.fleet.orders), original_len - 1)
        self.assertNotIn(to_delete, self.fleet.orders)
        self.assertEqual(len(self.window.deleted_history), 1)
        
        # Undo
        self.window.undo_delete()
        
        self.assertEqual(len(self.fleet.orders), original_len)
        self.assertEqual(self.fleet.orders[1], to_delete)
        self.assertEqual(len(self.window.deleted_history), 0)

    def test_undo_index_handling(self):
        # Test undoing into a list that changed size (simulating other deletion)
        # 1. Delete index 0
        o0 = self.fleet.orders[0]
        self.window.delete_order(0)
        
        # 2. Delete index 0 again (what was index 1)
        o1 = self.fleet.orders[0]
        self.window.delete_order(0)
        
        # History Stack: [(0, o0), (0, o1)]
        
        # Undo last delete (o1) -> Should go to index 0
        self.window.undo_delete()
        self.assertEqual(self.fleet.orders[0], o1)
        
        # Undo first delete (o0) -> Should go to index 0, pushing o1 to 1
        self.window.undo_delete()
        self.assertEqual(self.fleet.orders[0], o0)
        self.assertEqual(self.fleet.orders[1], o1)

if __name__ == '__main__':
    unittest.main()
