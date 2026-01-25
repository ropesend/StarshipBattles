"""
AI Interfaces package.

PROJ-12 Phase 5: Contains interface abstractions for AI system.
Decouples AI from specific entity implementations.
"""

from game.ai.interfaces.controllable import IControllable, ShipControllableAdapter

__all__ = ['IControllable', 'ShipControllableAdapter']
