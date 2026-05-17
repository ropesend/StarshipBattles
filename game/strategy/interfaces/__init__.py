"""
Strategy layer interfaces for clean dependency management.

PROJ-11 Phase 4: Defines explicit interfaces between layers.
This allows the strategy layer to depend on abstractions rather than
concrete simulation implementations.

PROJ-43 Phase 4: Added engine interfaces for TurnEngine constructor DI.
PROJ-422 (TD-09): re-exports every engine ABC the `engines` package
exposes, closing the prior 5-name drift (IOrganicsConsumptionEngine,
IHappinessEngine, IQualityEngine, IAtmosphereEngine, IWaterEngine were
previously defined in the monolith but missing here).
"""

from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
from game.strategy.interfaces.engines import (
    IActionExecutionEngine,
    IAtmosphereEngine,
    IComponentActivationEngine,
    IConflictEngine,
    IConsumableEngine,
    IEnvironmentalHazardEngine,
    IHappinessEngine,
    IHarvestingEngine,
    IMovementEngine,
    IOrderProcessor,
    IOrganicsConsumptionEngine,
    IPlanetActionEngine,
    IPlanetEnergyEngine,
    IPopulationEngine,
    IProductionEngine,
    IQualityEngine,
    IResupplyEngine,
    IWaterEngine,
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
    'IOrganicsConsumptionEngine',
    'IHappinessEngine',
    'IQualityEngine',
    'IAtmosphereEngine',
    'IWaterEngine',
]
