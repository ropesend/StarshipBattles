"""Package entry point for the strategy engine ABC contracts.

Re-exports every leaf-module ABC under one namespace. This is the public
seam, not a backward-compat shim — delete only when all 30 consumers are
rewritten to use leaf module paths.

PROJ-43 Phase 4: original interface contracts for TurnEngine sub-engines.
PROJ-161: Harvesting interface is per-tick only.
PROJ-422 (TD-09): the former 778-LOC `engines.py` monolith was split into
nine domain-scoped leaf modules. The 30 existing
`from game.strategy.interfaces.engines import I<Name>` import sites
continue to work unchanged via this package's explicit re-exports.

Layout:
- movement.py      - IMovementEngine
- orders.py        - IOrderProcessor, IActionExecutionEngine
- combat.py        - IConflictEngine, IEnvironmentalHazardEngine
- production.py    - IProductionEngine
- logistics.py     - IConsumableEngine, IResupplyEngine, IHarvestingEngine
- population.py    - IPopulationEngine, IOrganicsConsumptionEngine,
                     IHappinessEngine
- planet_ops.py    - IPlanetEnergyEngine, IPlanetActionEngine
- terraforming.py  - IQualityEngine, IAtmosphereEngine, IWaterEngine
- components.py    - IComponentActivationEngine

Hard rule (architectural invariant): leaf modules under this package are
private. Consumers MUST import via `game.strategy.interfaces.engines`
(this package path), never via `game.strategy.interfaces.engines.movement`
etc. This keeps the public API surface narrow and lets future domain
regrouping happen inside the package without churning consumers.
"""

from game.strategy.interfaces.engines.combat import (
    IConflictEngine,
    IEnvironmentalHazardEngine,
)
from game.strategy.interfaces.engines.components import IComponentActivationEngine
from game.strategy.interfaces.engines.logistics import (
    IConsumableEngine,
    IHarvestingEngine,
    IResupplyEngine,
)
from game.strategy.interfaces.engines.movement import IMovementEngine
from game.strategy.interfaces.engines.orders import (
    IActionExecutionEngine,
    IOrderProcessor,
)
from game.strategy.interfaces.engines.planet_ops import (
    IPlanetActionEngine,
    IPlanetEnergyEngine,
)
from game.strategy.interfaces.engines.population import (
    IHappinessEngine,
    IOrganicsConsumptionEngine,
    IPopulationEngine,
)
from game.strategy.interfaces.engines.production import IProductionEngine
from game.strategy.interfaces.engines.terraforming import (
    IAtmosphereEngine,
    IQualityEngine,
    IWaterEngine,
)


# Sorted by domain (matches the layout table in this docstring and in the
# PROJ-422 manifest). PROJ-422 closes the prior drift where
# IComponentActivationEngine was defined but missing from __all__.
__all__ = [
    # movement
    'IMovementEngine',
    # orders
    'IOrderProcessor',
    'IActionExecutionEngine',
    # combat
    'IConflictEngine',
    'IEnvironmentalHazardEngine',
    # production
    'IProductionEngine',
    # logistics
    'IConsumableEngine',
    'IResupplyEngine',
    'IHarvestingEngine',
    # population
    'IPopulationEngine',
    'IOrganicsConsumptionEngine',
    'IHappinessEngine',
    # planet ops
    'IPlanetEnergyEngine',
    'IPlanetActionEngine',
    # terraforming
    'IQualityEngine',
    'IAtmosphereEngine',
    'IWaterEngine',
    # components
    'IComponentActivationEngine',
]
