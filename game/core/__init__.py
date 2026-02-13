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

Logging (game.core.logger):
    log_debug, log_info, log_warning, log_error, set_logging

Validation (game.core.validation):
    ValidationResult, IValidationRule

Configuration (game.core.config):
    DisplayConfig, AIConfig, PhysicsConfig, BattleConfig, UIConfig

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
    get_default_registries,
    set_default_registries,
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

# Logging
from game.core.logger import (
    log_debug,
    log_info,
    log_warning,
    log_error,
    set_logging,
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
    'get_default_registry_provider', 'get_default_registries', 'set_default_registries',
    # Constants
    'GameState', 'LayerType', 'AttackType', 'LayerDefaults', 'CombatConstants',
    'PLANET_RESOURCES',
    # Logging
    'log_debug', 'log_info', 'log_warning', 'log_error', 'set_logging',
    # Validation
    'ValidationResult', 'IValidationRule',
    # Configuration
    'DisplayConfig', 'AIConfig', 'PhysicsConfig', 'BattleConfig', 'UIConfig',
    # Paths
    'Paths',
    # Protocols
    'IRegistryProvider', 'IFleet', 'IPlanet', 'ICombatant',
    'is_fleet', 'is_planet', 'is_combatant',
]
