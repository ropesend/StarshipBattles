import pytest
import pygame
import pygame_gui
from game.ui.screens.fleet_orders_window import FleetOrdersWindow
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
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
    assert window.rows[0]['desc'].text == "MOVE HexCoord(1, 1)"
    
    # Remove order externally
    fleet.orders.pop()
    window.update(0.1)
    assert len(window.rows) == 0

if __name__ == "__main__":
    pytest.main([__file__])
