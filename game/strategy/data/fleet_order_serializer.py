"""
Backward compatibility module.

PROJ-238: FleetOrderSerializer renamed to OrderSerializer in order_serializer.py.
This module re-exports everything for backward compatibility.
"""
from game.strategy.data.order_serializer import *  # noqa: F401,F403
from game.strategy.data.order_serializer import OrderSerializer as FleetOrderSerializer  # noqa: F401
