"""
Core utilities package for Starship Battles.

Provides framework-agnostic utilities including math, logging, configuration,
validation, and registry management.

Public API
==========

Exceptions (game.core.exceptions):
    GameException, StateException, FrozenStateException, ValidationException,
    ResourceException, MissingResourceException, PersistenceException,
    SimulationException, ComponentException, FormulaException

Error Codes (game.core.error_codes):
    ErrorCode

Math utilities (game.core.math):
    Vector2, clamp, lerp, angle_diff

Registry and DI (game.core.registry):
    GameRegistries, get_default_registry_provider, TestRegistryProvider,
    DefaultRegistryProvider, RegistryManager

Constants (game.core.constants):
    GameState, LayerType, AttackType, LayerDefaults, CombatConstants,
    PLANET_RESOURCES

Event Logging (game.core.event_logging):
    log_event, set_event_handler, get_event_handler

Validation (game.core.validation):
    ValidationResult, IValidationRule

Configuration (game.core.config):
    DisplayConfig, AIConfig, PhysicsConfig, BattleConfig
    (UIConfig is in game.ui.config - PROJ-113)

Paths (game.core.paths):
    Paths

Protocols (game.core.protocols):
    IRegistryProvider, IFleet, IPlanet, ICombatant,
    is_fleet, is_planet, is_combatant
"""

# Exceptions (PROJ-45)
from game.core.exceptions import (
    GameException,
    StateException,
    FrozenStateException,
    ValidationException,
    ResourceException,
    MissingResourceException,
    PersistenceException,
    SimulationException,
    ComponentException,
    FormulaException,
)

# Error Codes (PROJ-45)
from game.core.error_codes import ErrorCode

# Math utilities
from game.core.math import Vector2, clamp, lerp, angle_diff

# Registry and DI (PROJ-27, PROJ-38)
from game.core.registry import (
    GameRegistries,
    RegistryManager,
    DefaultRegistryProvider,
    TestRegistryProvider,
    get_default_registry_provider,
)

# Constants
from game.core.constants import (
    GameState,
    LayerType,
    AttackType,
    LayerDefaults,
    CombatConstants,
    PLANET_RESOURCES,
)

# Event Logging (PROJ-175)
from game.core.event_logging import (
    log_event,
    set_event_handler,
    get_event_handler,
)

# Validation
from game.core.validation import ValidationResult, IValidationRule

# Configuration
from game.core.config import (
    DisplayConfig,
    AIConfig,
    PhysicsConfig,
    BattleConfig,
)
# PROJ-113: UIConfig moved to game.ui.config

# Paths
from game.core.paths import Paths

# Protocols (type-safe duck typing)
from game.core.protocols import (
    IRegistryProvider,
    IFleet,
    IPlanet,
    ICombatant,
    is_fleet,
    is_planet,
    is_combatant,
)


__all__ = [
    # Exceptions (PROJ-45)
    'GameException', 'StateException', 'FrozenStateException', 'ValidationException',
    'ResourceException', 'MissingResourceException', 'PersistenceException',
    'SimulationException', 'ComponentException', 'FormulaException',
    # Error Codes (PROJ-45)
    'ErrorCode',
    # Math
    'Vector2', 'clamp', 'lerp', 'angle_diff',
    # Registry and DI
    'GameRegistries', 'RegistryManager',
    'DefaultRegistryProvider', 'TestRegistryProvider',
    'get_default_registry_provider',
    # Constants
    'GameState', 'LayerType', 'AttackType', 'LayerDefaults', 'CombatConstants',
    'PLANET_RESOURCES',
    # Event Logging
    'log_event', 'set_event_handler', 'get_event_handler',
    # Validation
    'ValidationResult', 'IValidationRule',
    # Configuration (UIConfig moved to game.ui.config - PROJ-113)
    'DisplayConfig', 'AIConfig', 'PhysicsConfig', 'BattleConfig',
    # Paths
    'Paths',
    # Protocols
    'IRegistryProvider', 'IFleet', 'IPlanet', 'ICombatant',
    'is_fleet', 'is_planet', 'is_combatant',
]
