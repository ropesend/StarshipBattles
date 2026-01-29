"""
Simulation layer interfaces and protocols.

This package defines interfaces (protocols) that the simulation layer uses
for dependency injection and loose coupling with other layers.
"""

from game.simulation.interfaces.ai_controller import IAIController

__all__ = ['IAIController']
