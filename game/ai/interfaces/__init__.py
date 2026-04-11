"""
AI Interfaces package.

PROJ-12 Phase 5: Contains interface abstractions for AI system.
Decouples AI from specific entity implementations.

PROJ-192: Added AI-layer protocols for type-safe duck typing replacement.
"""

from game.ai.interfaces.controllable import IControllable, ShipControllableAdapter
from game.ai.protocols import (
    IGridEntity,
    IProjectile,
    IComponentHealth,
    is_grid_entity,
    is_projectile,
    is_component_health,
)

__all__ = [
    'IControllable',
    'ShipControllableAdapter',
    # PROJ-192 Protocols
    'IGridEntity',
    'IProjectile',
    'IComponentHealth',
    'is_grid_entity',
    'is_projectile',
    'is_component_health',
]
