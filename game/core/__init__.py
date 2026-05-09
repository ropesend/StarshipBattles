"""
Core utilities package for Starship Battles.

Provides framework-agnostic utilities including math, logging, configuration,
validation, and registry management.

Public API
==========

Exceptions (game.core.exceptions):
    GameException, StateException, FrozenStateException, ValidationException,
    ResourceException, MissingResourceException, PersistenceException,
    SimulationException, ComponentException, FormulaException,
    LLMException, LLMConfigError, LLMNetworkError, LLMResponseError,
    LLMRateLimited, LLMTimeoutError, LLMCancelled,
    LLMUnexpectedError (PROJ-296 + PROJ-321..328 audit S1.1)

Error Codes (game.core.error_codes):
    ErrorCode

Math utilities (game.core.math):
    Vector2, clamp, lerp, angle_diff

Registry and DI (game.core.registry):
    GameRegistries, get_default_registry_provider, TestRegistryProvider,
    DefaultRegistryProvider, RegistryManager

Constants (game.core.constants):
    GameState, LayerType, AttackType, LayerDefaults, CombatConstants

Resources (game.core.resources):
    ResourceCatalog, ResourceDefinition

Event Logging (game.core.event_logging):
    EventBus  (PROJ-390 retired the module-level log_event shim)

Validation (game.core.validation):
    ValidationResult, IValidationRule

Configuration (game.core.config):
    DisplayConfig, AIConfig, PhysicsConfig, BattleTuning
    (UIConfig is in game.ui.config - PROJ-113)

Paths (game.core.paths):
    Paths

Protocols (game.core.protocols):
    IRegistryProvider, IFleet, IPlanet, ICombatant, IRaceRegistry,
    is_fleet, is_planet, is_combatant

Roles (game.core.roles, PROJ-278):
    Role, RoleRegistry, RoleRegistryReadOnlyError
"""

# Exceptions (PROJ-45, extended PROJ-296)
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
    # LLM Service (PROJ-296)
    LLMException,
    LLMConfigError,
    LLMNetworkError,
    LLMResponseError,
    LLMRateLimited,
    LLMTimeoutError,
    LLMCancelled,
    LLMUnexpectedError,
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
)

# Event Logging (PROJ-175). PROJ-390 retired the module-level
# log_event/set_event_handler/get_event_handler shim; only the
# session-scoped EventBus class remains and is re-exported here.
from game.core.event_logging import EventBus

# Validation
from game.core.validation import ValidationResult, IValidationRule

# Configuration
from game.core.config import (
    DisplayConfig,
    AIConfig,
    PhysicsConfig,
    BattleTuning,
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
    IRaceRegistry,
    is_fleet,
    is_planet,
    is_combatant,
)

# Roles (PROJ-278)
from game.core.roles import (
    Role,
    RoleRegistry,
    RoleRegistryReadOnlyError,
)


__all__ = [
    # Exceptions (PROJ-45)
    'GameException', 'StateException', 'FrozenStateException', 'ValidationException',
    'ResourceException', 'MissingResourceException', 'PersistenceException',
    'SimulationException', 'ComponentException', 'FormulaException',
    # LLM Service Exceptions (PROJ-296)
    'LLMException', 'LLMConfigError', 'LLMNetworkError', 'LLMResponseError',
    'LLMRateLimited', 'LLMTimeoutError', 'LLMCancelled',
    # PROJ-321..328 audit S1.1: wraps non-LLM provider exceptions in LLMBackgroundCall
    'LLMUnexpectedError',
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
    # PLANET_RESOURCES removed — use ResourceCatalog from game.core.resources
    # Event Logging (PROJ-390: only EventBus remains)
    'EventBus',
    # Validation
    'ValidationResult', 'IValidationRule',
    # Configuration (UIConfig moved to game.ui.config - PROJ-113)
    'DisplayConfig', 'AIConfig', 'PhysicsConfig', 'BattleTuning',
    # Paths
    'Paths',
    # Protocols
    'IRegistryProvider', 'IFleet', 'IPlanet', 'ICombatant', 'IRaceRegistry',
    'is_fleet', 'is_planet', 'is_combatant',
    # Roles (PROJ-278)
    'Role', 'RoleRegistry', 'RoleRegistryReadOnlyError',
]
