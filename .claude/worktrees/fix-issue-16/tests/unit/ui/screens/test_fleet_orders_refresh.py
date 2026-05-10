import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.ui.screens.orders_window import OrdersWindow
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord

@pytest.fixture
def manager():
    pygame.init()
    return pygame_gui.UIManager((800, 600))

@pytest.fixture
def fleet():
    return Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))


@pytest.fixture
def window_manager():
    """Stub StrategyWindowManager for OrdersWindow construction (PROJ-313)."""
    wm = MagicMock()
    wm._modals = []
    wm.register_modal = lambda w: wm._modals.append(w)
    wm.unregister_modal = lambda w: wm._modals.remove(w) if w in wm._modals else None
    return wm

def test_order_descriptions(manager, fleet, window_manager):
    window = OrdersWindow(pygame.Rect(0, 0, 400, 500), manager, fleet, window_manager=window_manager)
    
    # Test TRANSFER load
    order_load = Order(OrderType.TRANSFER, target={'direction': 'load', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_load) == "load cargo"
    
    # Test TRANSFER unload
    order_unload = Order(OrderType.TRANSFER, target={'direction': 'unload', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_unload) == "drop cargo"
    
    # Test LOAD_POPULATION
    order_pop_load = Order(OrderType.LOAD_POPULATION, target={'direction': 'load', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_pop_load) == "load cargo"
    
    # Test UNLOAD_POPULATION
    order_pop_unload = Order(OrderType.UNLOAD_POPULATION, target={'direction': 'unload', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_pop_unload) == "drop cargo"

def test_auto_refresh(manager, fleet, window_manager):
    window = OrdersWindow(pygame.Rect(0, 0, 400, 500), manager, fleet, window_manager=window_manager)
    assert len(window.rows) == 0
    
    # Add order externally
    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 1)))
    
    # Before update, row count is still 0 in UI elements (though fleet has 1)
    assert len(window.rows) == 0
    
    # Update window
    window.update(0.1)
    
    # Now rows should be 1
    assert len(window.rows) == 1
    assert window.rows[0]['desc'].text == "MOVE (1, 1)"
    
    # Remove order externally
    fleet.orders.pop()
    window.update(0.1)
    assert len(window.rows) == 0

def test_clear_orders_uses_callback(manager, fleet, window_manager):
    """PROJ-207 Phase 4: Clear All should dispatch via callback when provided."""
    # Track callback invocations
    callback_calls = []

    def mock_callback(fleet_id):
        callback_calls.append(fleet_id)

    window = OrdersWindow(
        pygame.Rect(0, 0, 400, 500), manager, fleet,
        window_manager=window_manager,
        clear_orders_callback=mock_callback
    )

    # Add an order so we have something to clear
    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 1)))
    window.update(0.1)
    assert len(window.rows) == 1

    # Simulate the confirmation dialog confirmed event
    mock_event = pygame.event.Event(
        pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
        {'ui_element': type('MockElement', (), {'object_ids': ['#confirm_clear_orders']})()}
    )

    result = window.handle_global_event(mock_event)

    assert result is True
    assert len(callback_calls) == 1
    assert callback_calls[0] == 1  # fleet.id


def test_clear_orders_requires_callback(manager, fleet, window_manager):
    """Without callback, clear orders does nothing (PROJ-208: fallback removed)."""
    window = OrdersWindow(
        pygame.Rect(0, 0, 400, 500), manager, fleet,
        window_manager=window_manager,
        # No callback provided
    )

    # Add an order
    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 1)))
    window.update(0.1)
    assert len(fleet.orders) == 1

    # Simulate the confirmation dialog confirmed event
    mock_event = pygame.event.Event(
        pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED,
        {'ui_element': type('MockElement', (), {'object_ids': ['#confirm_clear_orders']})()}
    )

    result = window.handle_global_event(mock_event)

    # Without callback, event is not handled and orders remain
    assert result is False
    assert len(fleet.orders) == 1  # Orders NOT cleared - callback required


def test_buttons_fit_within_container(manager, fleet, window_manager):
    """BUG-105: All row buttons (up, down, delete) must fit within the container width."""
    # Use the default window width from strategy_window_manager (480px)
    window = OrdersWindow(pygame.Rect(0, 0, 480, 500), manager, fleet, window_manager=window_manager)

    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 1)))
    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(2, 2)))
    window.update(0.1)

    assert len(window.rows) == 2

    # Get the container's usable width (the scrollable area width)
    container_width = window.list_container.get_container().get_rect().width

    for row in window.rows:
        # The delete button is the rightmost element — its right edge must fit
        del_rect = row['del'].relative_rect
        assert del_rect.right <= container_width, (
            f"Delete button right edge ({del_rect.right}) exceeds "
            f"container width ({container_width})"
        )
        # Down button must also fit
        down_rect = row['down'].relative_rect
        assert down_rect.right <= container_width, (
            f"Down button right edge ({down_rect.right}) exceeds "
            f"container width ({container_width})"
        )


def test_buttons_use_relative_positioning(manager, fleet, window_manager):
    """BUG-105: Button positions should adapt to different window widths."""
    # Create two windows with different widths
    narrow = OrdersWindow(pygame.Rect(0, 0, 480, 500), manager, fleet, window_manager=window_manager)
    wide = OrdersWindow(pygame.Rect(0, 0, 600, 500), manager, fleet, window_manager=window_manager)

    fleet.add_order(Order(OrderType.MOVE, target=HexCoord(1, 1)))
    narrow.update(0.1)
    wide.update(0.1)

    # Delete button X position should differ between narrow and wide windows
    narrow_del_x = narrow.rows[0]['del'].relative_rect.x
    wide_del_x = wide.rows[0]['del'].relative_rect.x

    assert wide_del_x > narrow_del_x, (
        f"Button positions should be relative to container width. "
        f"Narrow delete X={narrow_del_x}, Wide delete X={wide_del_x}"
    )


if __name__ == "__main__":
    pytest.main([__file__])
