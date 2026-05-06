"""Configuration dataclass for TurnEngine engine dependencies.

Bundles the 18 engine dependencies into a single frozen dataclass.

PROJ-259: Created to simplify TurnEngine constructor.
PROJ-369 Phase 3: Adds ``create_default(registries, ...)`` classmethod
as the canonical injection entry point. Eager construction means tests
can tell which default got used (no silent lazy fallback init).

Usage:
    # Production: build defaults eagerly via the factory.
    cfg = TurnEngineConfig.create_default(
        registries,
        ai_factory=ai_factory,
        race_registry=race_registry,
        event_bus=event_bus,
    )
    engine = TurnEngine(registries=registries, config=cfg)

    # Testing: replace specific engines via dataclasses.replace.
    import dataclasses
    cfg = dataclasses.replace(
        TurnEngineConfig.create_default(registries),
        movement_engine=mock_movement,
        production_engine=mock_production,
    )
    engine = TurnEngine(registries=registries, config=cfg)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

from game.core.registry import GameRegistries

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry

__all__ = ['TurnEngineConfig']


@dataclass(frozen=True)
class TurnEngineConfig:
    """Frozen configuration bundling 18 engine dependencies for TurnEngine.

    Fields default to None for the convenience of test paths that build
    a config via ``dataclasses.replace`` from the eager
    ``create_default()`` baseline. Production code MUST go through
    ``create_default()`` so every engine is bound; passing a partially
    populated config will surface as ``AttributeError`` at first use.
    """
    movement_engine: Optional[Any] = None
    production_engine: Optional[Any] = None
    order_processor: Optional[Any] = None
    conflict_engine: Optional[Any] = None
    resource_engine: Optional[Any] = None
    population_engine: Optional[Any] = None
    resupply_engine: Optional[Any] = None
    harvesting_engine: Optional[Any] = None
    action_engine: Optional[Any] = None
    environmental_engine: Optional[Any] = None
    planet_energy_engine: Optional[Any] = None
    planet_action_engine: Optional[Any] = None
    component_activation_engine: Optional[Any] = None
    # PROJ-284: Per-colony per-species food consumption (drains the
    # configured food resource after the tick loop, before pop growth).
    organics_consumption_engine: Optional[Any] = None
    # PROJ-284 Phase 3: Derives happiness between consumption and pop growth.
    happiness_engine: Optional[Any] = None
    # PROJ-369 Phase 2: per-turn terraforming engines now injectable.
    # Previously constructed inline inside `TurnEngine.process_turn`
    # (function-local imports — non-injectable).
    quality_engine: Optional[Any] = None
    atmosphere_engine: Optional[Any] = None
    water_engine: Optional[Any] = None

    @classmethod
    def create_default(
        cls,
        registries: GameRegistries,
        *,
        ai_factory: Any = None,
        race_registry: 'IRaceRegistry | None' = None,
        event_bus: Any = None,
    ) -> 'TurnEngineConfig':
        """Eagerly construct all 18 default engines and bundle them.

        This is the canonical injection entry point for production
        callers. Tests that need to override specific engines should
        construct a base config via ``create_default()`` and then use
        ``dataclasses.replace(cfg, foo_engine=mock_foo)`` to swap.

        Imports are function-local to avoid circular-import problems at
        module load time. This is the ONLY allow-listed location for
        function-local engine imports in the strategy turn-engine
        layer; the AST guard test
        ``test_no_lazy_fallback_init.py::test_no_function_local_engine_imports_in_TurnEngine_methods``
        enforces that.

        PROJ-369 Phase 3: replaces the per-property lazy fallback init
        that previously lived in ``TurnEngine.{movement_engine, ...}``.

        Args:
            registries: GameRegistries threaded into engines that need
                them for component / resource / vehicle-class lookups.
            ai_factory: Optional AI controller factory. When provided,
                a ``SimulationBattleResolver`` is constructed and wired
                to the conflict engine. When ``None``, the conflict
                engine receives ``battle_resolver=None`` and raises
                clearly at first combat.
            race_registry: Optional race registry threaded through
                Population + Happiness engines for multi-species
                colonies (PROJ-291 C3).
            event_bus: Optional event bus for structured logging,
                threaded through Production / OrderProcessor /
                ConflictResolution / PlanetEnergy / PlanetAction engines.

        Returns:
            Fully populated ``TurnEngineConfig`` with eagerly
            constructed default engines.
        """
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.engine.conflict_resolution_engine import (
            ConflictResolutionEngine,
        )
        from game.strategy.engine.consumable_management_engine import (
            ConsumableManagementEngine,
        )
        from game.strategy.engine.population_engine import PopulationEngine
        from game.strategy.engine.resupply_engine import ResupplyEngine
        from game.strategy.engine.harvesting_engine import HarvestingEngine
        from game.strategy.engine.action_execution_engine import (
            ActionExecutionEngine,
        )
        from game.strategy.engine.environmental_hazard_engine import (
            EnvironmentalHazardEngine,
        )
        from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
        from game.strategy.engine.planet_action_engine import PlanetActionEngine
        from game.strategy.engine.component_activation_engine import (
            ComponentActivationEngine,
        )
        from game.strategy.engine.organics_consumption_engine import (
            OrganicsConsumptionEngine,
        )
        from game.strategy.engine.happiness_engine import HappinessEngine
        from game.strategy.engine.quality_engine import QualityEngine
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine
        from game.strategy.engine.water_engine import WaterEngine
        from game.strategy.services.action_time_resolver import ActionTimeResolver

        # Battle resolver: only constructed when ai_factory is provided.
        # battle_resolver=None reaches conflict_engine, which raises
        # clearly at first combat. _NullBattleResolver was deleted in
        # PROJ-369 Phase 3.
        battle_resolver = None
        if ai_factory is not None:
            from game.strategy.adapters.simulation_adapter import (
                SimulationBattleResolver,
            )
            battle_resolver = SimulationBattleResolver(ai_factory=ai_factory)

        order_processor = OrderProcessor(event_bus=event_bus)

        return cls(
            movement_engine=FleetMovementEngine(),
            production_engine=ProductionEngine(
                registries=registries, event_bus=event_bus,
            ),
            order_processor=order_processor,
            conflict_engine=ConflictResolutionEngine(
                battle_resolver,
                registries=registries,
                event_bus=event_bus,
            ),
            resource_engine=ConsumableManagementEngine(registries=registries),
            population_engine=PopulationEngine(race_registry=race_registry),
            resupply_engine=ResupplyEngine(registries=registries),
            harvesting_engine=HarvestingEngine(registries=registries),
            action_engine=ActionExecutionEngine(
                order_processor=order_processor,
                action_time_resolver=ActionTimeResolver(),
            ),
            environmental_engine=EnvironmentalHazardEngine(),
            planet_energy_engine=PlanetEnergyEngine(
                registries=registries, event_bus=event_bus,
            ),
            planet_action_engine=PlanetActionEngine(
                registries=registries,
                action_time_resolver=ActionTimeResolver(),
                event_bus=event_bus,
            ),
            component_activation_engine=ComponentActivationEngine(),
            organics_consumption_engine=OrganicsConsumptionEngine(),
            happiness_engine=HappinessEngine(race_registry=race_registry),
            quality_engine=QualityEngine(registries=registries),
            atmosphere_engine=AtmosphereEngine(registries=registries),
            water_engine=WaterEngine(registries=registries),
        )
