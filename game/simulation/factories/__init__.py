"""
Simulation layer factories.

This package contains factory classes that create objects with dependencies
from other layers, isolating cross-layer imports to a single location.
"""

from game.simulation.factories.ai_factory import AIControllerFactory

__all__ = ['AIControllerFactory']
