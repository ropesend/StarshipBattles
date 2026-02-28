import pytest
import pygame
import pygame_gui
from game.ui.screens.fleet_orders_window import FleetOrdersWindow
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord

@pytest.fixture
def manager():
    pygame.init()
    return pygame_gui.UIManager((800, 600))

@pytest.fixture
def fleet():
    return Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))

def test_order_descriptions(manager, fleet):
    window = FleetOrdersWindow(pygame.Rect(0, 0, 400, 500), manager, fleet)
    
    # Test TRANSFER load
    order_load = FleetOrder(OrderType.TRANSFER, target={'direction': 'load', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_load) == "load cargo"
    
    # Test TRANSFER unload
    order_unload = FleetOrder(OrderType.TRANSFER, target={'direction': 'unload', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_unload) == "drop cargo"
    
    # Test LOAD_POPULATION
    order_pop_load = FleetOrder(OrderType.LOAD_POPULATION, target={'direction': 'load', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_pop_load) == "load cargo"
    
    # Test UNLOAD_POPULATION
    order_pop_unload = FleetOrder(OrderType.UNLOAD_POPULATION, target={'direction': 'unload', 'cargo_type': 'passengers', 'amount': 10})
    assert window._get_order_description(order_pop_unload) == "drop cargo"

def test_auto_refresh(manager, fleet):
    window = FleetOrdersWindow(pygame.Rect(0, 0, 400, 500), manager, fleet)
    assert len(window.rows) == 0
    
    # Add order externally
    fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 1)))
    
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

def test_clear_orders_uses_callback(manager, fleet):
    """PROJ-207 Phase 4: Clear All should dispatch via callback when provided."""
    # Track callback invocations
    callback_calls = []

    def mock_callback(fleet_id):
        callback_calls.append(fleet_id)

    window = FleetOrdersWindow(
        pygame.Rect(0, 0, 400, 500), manager, fleet,
        clear_orders_callback=mock_callback
    )

    # Add an order so we have something to clear
    fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 1)))
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


def test_clear_orders_requires_callback(manager, fleet):
    """Without callback, clear orders does nothing (PROJ-208: fallback removed)."""
    window = FleetOrdersWindow(
        pygame.Rect(0, 0, 400, 500), manager, fleet
        # No callback provided
    )

    # Add an order
    fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 1)))
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


if __name__ == "__main__":
    pytest.main([__file__])
