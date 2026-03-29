"""
Planet order compatibility module.

PROJ-238: PlanetOrderType merged into OrderType, PlanetOrder merged into Order.
This module re-exports Order as PlanetOrder for backward compatibility.
Will be deleted once all references are updated.
"""

from game.strategy.data.order_types import Order as PlanetOrder, OrderType  # noqa: F401

__all__ = ['PlanetOrder', 'OrderType']
