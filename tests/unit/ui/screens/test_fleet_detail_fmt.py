import pytest
from unittest.mock import MagicMock
from game.ui.screens.strategy_detail_fmt import format_fleet_info
from game.strategy.data.fleet import OrderType

def test_format_fleet_info_with_transfer_order():
    """Verify that TRANSFER orders are formatted correctly in fleet info."""
    # Arrange
    fleet = MagicMock()
    fleet.id = 5
    fleet.owner_id = 1
    fleet.ships = [MagicMock(), MagicMock()]
    fleet.location = MagicMock()
    fleet.location.__str__.return_value = "(10, 20)"
    
    # Mock a TRANSFER order
    order = MagicMock()
    order.type = OrderType.TRANSFER
    order.target = {
        'direction': 'load',
        'cargo_type': 'passengers',
        'amount': 50
    }
    fleet.orders = [order]
    
    # Act
    html = format_fleet_info(fleet)
    
    # Assert
    assert "LOAD 50 passengers" in html

def test_format_fleet_info_with_transfer_all():
    """Verify that TRANSFER orders with amount 0 are formatted as 'All'."""
    # Arrange
    fleet = MagicMock()
    fleet.id = 5
    fleet.owner_id = 1
    fleet.ships = []
    fleet.location = MagicMock()
    fleet.location.__str__.return_value = "(0, 0)"
    
    order = MagicMock()
    order.type = OrderType.TRANSFER
    order.target = {
        'direction': 'unload',
        'cargo_type': 'passengers',
        'amount': 0
    }
    fleet.orders = [order]
    
    # Act
    html = format_fleet_info(fleet)
    
    # Assert
    assert "UNLOAD All passengers" in html
