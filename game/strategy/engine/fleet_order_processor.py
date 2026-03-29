"""
Backward compatibility module.

PROJ-238: FleetOrderProcessor renamed to OrderProcessor in order_processor.py.
This module re-exports everything for backward compatibility.
"""
from game.strategy.engine.order_processor import *  # noqa: F401,F403
from game.strategy.engine.order_processor import OrderProcessor as FleetOrderProcessor  # noqa: F401
