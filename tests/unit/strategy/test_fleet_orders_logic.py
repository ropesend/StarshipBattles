from unittest.mock import MagicMock, patch
import pygame
import pygame_gui
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType


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


class TestFleetOrdersLogic:
    def test_reorder_down(self):
        fleet = Fleet(1, 0, (0, 0))
        fleet.orders = [
            Order(OrderType.MOVE, target=(10, 10)),
            Order(OrderType.COLONIZE, target="PlanetA"),
            Order(OrderType.MOVE, target=(20, 20))
        ]
        window = MockFleetOrdersWindow(fleet)

        # Move first order down
        original_first = fleet.orders[0]
        window.move_order(0, 1)

        # Verify swap
        assert fleet.orders[1] == original_first
        assert fleet.orders[0].type == OrderType.COLONIZE

    def test_reorder_up(self):
        fleet = Fleet(1, 0, (0, 0))
        fleet.orders = [
            Order(OrderType.MOVE, target=(10, 10)),
            Order(OrderType.COLONIZE, target="PlanetA"),
            Order(OrderType.MOVE, target=(20, 20))
        ]
        window = MockFleetOrdersWindow(fleet)

        # Move second order up
        original_second = fleet.orders[1]
        window.move_order(1, -1)

        # Verify swap
        assert fleet.orders[0] == original_second

    def test_delete_and_undo(self):
        fleet = Fleet(1, 0, (0, 0))
        fleet.orders = [
            Order(OrderType.MOVE, target=(10, 10)),
            Order(OrderType.COLONIZE, target="PlanetA"),
            Order(OrderType.MOVE, target=(20, 20))
        ]
        window = MockFleetOrdersWindow(fleet)

        original_len = len(fleet.orders)
        to_delete = fleet.orders[1]

        # Delete middle order
        window.delete_order(1)

        assert len(fleet.orders) == original_len - 1
        assert to_delete not in fleet.orders
        assert len(window.deleted_history) == 1

        # Undo
        window.undo_delete()

        assert len(fleet.orders) == original_len
        assert fleet.orders[1] == to_delete
        assert len(window.deleted_history) == 0

    def test_undo_index_handling(self):
        fleet = Fleet(1, 0, (0, 0))
        fleet.orders = [
            Order(OrderType.MOVE, target=(10, 10)),
            Order(OrderType.COLONIZE, target="PlanetA"),
            Order(OrderType.MOVE, target=(20, 20))
        ]
        window = MockFleetOrdersWindow(fleet)

        # Test undoing into a list that changed size (simulating other deletion)
        # 1. Delete index 0
        o0 = fleet.orders[0]
        window.delete_order(0)

        # 2. Delete index 0 again (what was index 1)
        o1 = fleet.orders[0]
        window.delete_order(0)

        # History Stack: [(0, o0), (0, o1)]

        # Undo last delete (o1) -> Should go to index 0
        window.undo_delete()
        assert fleet.orders[0] == o1

        # Undo first delete (o0) -> Should go to index 0, pushing o1 to 1
        window.undo_delete()
        assert fleet.orders[0] == o0
        assert fleet.orders[1] == o1
