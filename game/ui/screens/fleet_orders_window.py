"""
Backward compatibility module.

PROJ-238: FleetOrdersWindow renamed to OrdersWindow in orders_window.py.
This module re-exports for backward compatibility.
"""
from game.ui.screens.orders_window import *  # noqa: F401,F403
from game.ui.screens.orders_window import OrdersWindow as FleetOrdersWindow  # noqa: F401
