"""Configuration dataclass for TurnEngine optional engine parameters.

Bundles the 13 optional engine dependencies into a single frozen dataclass,
reducing TurnEngine.__init__() from 20 parameters to 5.

Fields default to None, meaning "use the default engine implementation."

PROJ-259: Created to simplify TurnEngine constructor.

Usage:
    # All defaults (same as current TurnEngine() with no engine kwargs)
    config = TurnEngineConfig()

    # Override specific engines for testing
    config = TurnEngineConfig(
        movement_engine=mock_movement,
        production_engine=mock_production,
    )

    # Pass to TurnEngine
    engine = TurnEngine(registries=registries, config=config)
"""
from dataclasses import dataclass
from typing import Any, Optional

__all__ = ['TurnEngineConfig']


@dataclass(frozen=True)
class TurnEngineConfig:
    """Frozen configuration bundling optional engine dependencies for TurnEngine.

    All fields default to None, meaning the TurnEngine will create default
    implementations via lazy initialization.
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
