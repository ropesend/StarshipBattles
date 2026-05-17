"""
Tests that all strategy sub-engines inherit from their interface ABCs.

PROJ-239 Task 2.3: AR-005 - All sub-engines should formally inherit
from their interfaces defined in the ``game/strategy/interfaces/engines/``
package (split from the former 778-LOC ``engines.py`` monolith by PROJ-422).
Consumers must continue to import via the package root path
``game.strategy.interfaces.engines``; leaf modules under that package are
private.
"""
import pytest


ENGINE_INTERFACE_PAIRS = [
    ("game.strategy.engine.fleet_movement_engine", "FleetMovementEngine",
     "game.strategy.interfaces.engines", "IMovementEngine"),
    ("game.strategy.engine.production_engine", "ProductionEngine",
     "game.strategy.interfaces.engines", "IProductionEngine"),
    ("game.strategy.engine.order_processor", "OrderProcessor",
     "game.strategy.interfaces.engines", "IOrderProcessor"),
    ("game.strategy.engine.conflict_resolution_engine", "ConflictResolutionEngine",
     "game.strategy.interfaces.engines", "IConflictEngine"),
    ("game.strategy.engine.consumable_management_engine", "ConsumableManagementEngine",
     "game.strategy.interfaces.engines", "IConsumableEngine"),
    ("game.strategy.engine.environmental_hazard_engine", "EnvironmentalHazardEngine",
     "game.strategy.interfaces.engines", "IEnvironmentalHazardEngine"),
    ("game.strategy.engine.planet_energy_engine", "PlanetEnergyEngine",
     "game.strategy.interfaces.engines", "IPlanetEnergyEngine"),
    ("game.strategy.engine.planet_action_engine", "PlanetActionEngine",
     "game.strategy.interfaces.engines", "IPlanetActionEngine"),
    # These 4 already inherit — included to prevent regression
    ("game.strategy.engine.action_execution_engine", "ActionExecutionEngine",
     "game.strategy.interfaces.engines", "IActionExecutionEngine"),
    ("game.strategy.engine.harvesting_engine", "HarvestingEngine",
     "game.strategy.interfaces.engines", "IHarvestingEngine"),
    ("game.strategy.engine.population_engine", "PopulationEngine",
     "game.strategy.interfaces.engines", "IPopulationEngine"),
    ("game.strategy.engine.resupply_engine", "ResupplyEngine",
     "game.strategy.interfaces.engines", "IResupplyEngine"),
]


@pytest.mark.parametrize(
    "engine_module,engine_class,iface_module,iface_class",
    ENGINE_INTERFACE_PAIRS,
    ids=[f"{e[1]}->{e[3]}" for e in ENGINE_INTERFACE_PAIRS],
)
class TestEngineInheritsInterface:
    """Each sub-engine must inherit from its interface ABC."""

    def test_engine_is_subclass_of_interface(
        self, engine_module, engine_class, iface_module, iface_class
    ):
        import importlib
        eng_mod = importlib.import_module(engine_module)
        ifc_mod = importlib.import_module(iface_module)
        EngClass = getattr(eng_mod, engine_class)
        IfcClass = getattr(ifc_mod, iface_class)
        assert issubclass(EngClass, IfcClass), (
            f"{engine_class} does not inherit from {iface_class}"
        )
