"""
Strategy layer interfaces for clean dependency management.

PROJ-11 Phase 4: Defines explicit interfaces between layers.
This allows the strategy layer to depend on abstractions rather than
concrete simulation implementations.

PROJ-43 Phase 4: Added engine interfaces for TurnEngine constructor DI.
"""

from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
from game.strategy.interfaces.engines import (
    IMovementEngine,
    IProductionEngine,
    IOrderProcessor,
    IConflictEngine,
    IConsumableEngine,
    IResupplyEngine,
    IHarvestingEngine,
    IPopulationEngine,
    IActionExecutionEngine,
    IEnvironmentalHazardEngine,
    IPlanetEnergyEngine,
    IPlanetActionEngine,
    IComponentActivationEngine,
)

__all__ = [
    'IBattleResolver',
    'BattleResult',
    'IMovementEngine',
    'IProductionEngine',
    'IOrderProcessor',
    'IConflictEngine',
    'IConsumableEngine',
    'IResupplyEngine',
    'IHarvestingEngine',
    'IPopulationEngine',
    'IActionExecutionEngine',
    'IEnvironmentalHazardEngine',
    'IPlanetEnergyEngine',
    'IPlanetActionEngine',
    'IComponentActivationEngine',
]
