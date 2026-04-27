from unittest.mock import MagicMock
import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
from game.ui.screens.strategy_detail_fmt import _format_orders

def test_repro_warp_point_creation_failure():
    """Reproduce the bug where warp point creation fails if fleet is not at system center."""
    galaxy = Galaxy(radius=100)
    
    # Create two systems
    sys_a = StarSystem("Alpha", HexCoord(0, 0))
    sys_b = StarSystem("Beta", HexCoord(20, 20))
    
    galaxy.add_system(sys_a)
    galaxy.add_system(sys_b)
    
    # Create a fleet at Alpha but NOT at its center
    # Alpha is at (0,0). Let's put fleet at (1,0).
    fleet = Fleet(1, 1, HexCoord(1, 0))
    fleet.ships = [MagicMock()] # Just need something in ships
    
    # Add OPEN_WARP_POINT order
    order_target = {
        'target_hex': HexCoord(1, 0),
        'target_system_name': 'Beta'
    }
    order = Order(OrderType.OPEN_WARP_POINT, target=order_target)
    fleet.add_order(order)
    
    processor = SuperweaponOrderProcessor()
    empire = MagicMock() # Not needed for this check
    
    # Act
    result = processor.process_open_warp_point(fleet, empire, galaxy)
    
    # Assert
    # After the fix, this should SUCCEED
    if result.success:
        print(f"Test passed: {result.message}")
    else:
        print(f"Test failed: {result.message}")
    
    assert result.success
    assert len(sys_a.warp_points) == 1
    assert sys_a.warp_points[0].destination_id == "Beta"

def test_repro_warp_point_ui_order_display():
    """Reproduce the bug where the target system name is not shown in orders."""
    fleet = Fleet(1, 1, HexCoord(0, 0))
    
    order_target = {
        'target_hex': HexCoord(1, 0),
        'target_system_name': 'Beta'
    }
    order = Order(OrderType.OPEN_WARP_POINT, target=order_target)
    fleet.add_order(order)
    
    # Act
    formatted_orders = _format_orders(fleet)
    
    # Assert
    print(f"Formatted orders: {formatted_orders}")
    # After the fix, it should include "Beta"
    assert "OPEN WARP POINT" in formatted_orders
    assert "Beta" in formatted_orders

if __name__ == "__main__":
    # Run tests manually if needed
    try:
        test_repro_warp_point_creation_failure()
        test_repro_warp_point_ui_order_display()
    except AssertionError as e:
        print(f"Test failed as expected: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
