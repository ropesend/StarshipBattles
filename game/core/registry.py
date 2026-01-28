"""
Registry Access Patterns
========================

TIER 1 - Utility Functions (Raw Access) [DEPRECATED]:
    from game.core.registry import get_component_registry
    components = get_component_registry()

TIER 2 - Domain Services (Computed Access):
    from game.strategy.services.ship_stats_service import ShipStatsService
    stats = ShipStatsService.calculate_ship_stats(design)

TIER 3 - Dependency Injection (PROJ-27) [RECOMMENDED]:
    from game.core.registry import get_default_registry_provider, TestRegistryProvider

    # Production code - uses the shared singleton-backed provider
    provider = get_default_registry_provider()
    components = provider.get_components()

    # Test code - uses isolated data
    provider = TestRegistryProvider(
        components={"test_laser": {"id": "test_laser"}},
        modifiers={}
    )
    service.calculate_stats(design, registry=provider)

AVOID - Direct Singleton Access:
    # DON'T DO THIS - harder to test
    RegistryManager.instance().components

PROJ-38: Deprecation
====================
The utility functions (get_component_registry, get_modifier_registry, etc.) are
deprecated. Use GameRegistries via dependency injection instead.
"""

__all__ = [
    # Core containers
    'GameRegistries',
    'RegistryManager',
    # DI providers (PROJ-27)
    'DefaultRegistryProvider',
    'TestRegistryProvider',
    'get_default_registry_provider',
    # Lifecycle functions
    'get_default_registries',
    'set_default_registries',
    'freeze_registry',
    'clear_registry',
    'set_validator',
    # Deprecated utility functions (use DI instead)
    'get_component_registry',
    'get_modifier_registry',
    'get_vehicle_classes',
    'get_validator',
    'get_resource_registry',
]
from dataclasses import dataclass
from typing import Dict, Any, Optional
import threading
import warnings


# =============================================================================
# GameRegistries Container (PROJ-38)
# =============================================================================

@dataclass(frozen=True)
class GameRegistries:
    """
    Immutable container for all game data registries.

    PROJ-38: This container enables Dependency Injection by bundling all
    registries together as an immutable package that can be passed to consumers.

    The container itself is frozen (immutable), but the dictionaries inside
    can still be modified. This ensures registry references cannot be swapped
    after initialization while still allowing data to be loaded.

    Attributes:
        components: Dict of component definitions keyed by ID
        modifiers: Dict of modifier definitions keyed by ID
        vehicle_classes: Dict of vehicle class definitions keyed by name
        resources: Dict of resource definitions keyed by ID
    """
    components: Dict[str, Any]
    modifiers: Dict[str, Any]
    vehicle_classes: Dict[str, Any]
    resources: Dict[str, Any]


# Module-level default registries for transitional fallback
_default_registries: Optional[GameRegistries] = None


def set_default_registries(registries: GameRegistries) -> None:
    """
    Set the default GameRegistries instance for transitional fallback.

    PROJ-38: During incremental migration, consumers that haven't been
    converted to DI can use get_default_registries() to access registries.

    Args:
        registries: The GameRegistries instance to use as default
    """
    global _default_registries
    _default_registries = registries


def get_default_registries() -> GameRegistries:
    """
    Get the default GameRegistries instance.

    PROJ-38: Returns the default GameRegistries instance set by the
    composition root. Raises RuntimeError if not set.

    Returns:
        The default GameRegistries instance

    Raises:
        RuntimeError: If set_default_registries() has not been called
    """
    if _default_registries is None:
        raise RuntimeError(
            "Default registries not set. Call set_default_registries() first."
        )
    return _default_registries

class RegistryManager:
    """
    Central singleton for managing global game state registries.
    
    Replaces module-level globals to allow for clean state resets in testing.
    
    Thread Safety:
        - Instance creation is thread-safe via double-checked locking
        - All dictionary operations use the same dict instances (no replacement)
        - Individual dict operations are atomic in CPython (GIL)
        - For cross-registry transactions, external synchronization is required
    
    Usage:
        # Preferred: Use utility functions (easier to mock)
        from game.core.registry import get_component_registry, get_modifier_registry
        
        components = get_component_registry()
        modifiers = get_modifier_registry()
        classes = get_vehicle_classes()
        
        # Alternative: Direct access (when needed for special operations)
        mgr = RegistryManager.instance()
        mgr.clear()  # For test isolation
        mgr.freeze() # For production initialization
    
    Testing:
        - Use conftest.py's reset_game_state fixture (auto-applied)
        - Fixture calls clear() before/after each test
        - Never call reset() in production code
    
    Attributes:
        components: Dict of component definitions keyed by ID
        modifiers: Dict of modifier definitions keyed by ID
        vehicle_classes: Dict of vehicle class definitions keyed by name
    """
    _instance: Optional['RegistryManager'] = None
    _lock = threading.Lock()

    def __init__(self):
        """
        Initialize the RegistryManager.
        
        Raises:
            RuntimeError: If called directly instead of via instance()
        """
        if RegistryManager._instance is not None:
             raise RuntimeError("RegistryManager is a singleton. Use RegistryManager.instance()")
        
        self.components: Dict[str, Any] = {}
        self.modifiers: Dict[str, Any] = {}
        self.vehicle_classes: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}
        self._validator: Any = None
        self._frozen: bool = False

    @classmethod
    def instance(cls) -> 'RegistryManager':
        """
        Get the singleton instance, creating it if necessary.
        
        Thread-safe via double-checked locking pattern.
        
        Returns:
            The singleton RegistryManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.
        
        WARNING: For testing only! This can cause stale reference hazards if
        any code is holding references to the old instance's dictionaries.
        
        Prefer clear() for test isolation - it preserves dict identity while
        emptying the contents.
        """
        cls._instance = None

    def freeze(self):
        """
        Prevent further modifications to the registry.
        
        Call this after game initialization to catch accidental mutations
        during gameplay. Useful for detecting bugs where code tries to
        modify registry data at runtime.
        """
        self._frozen = True

    def hydrate(self, components_data: Dict[str, Any], modifiers_data: Dict[str, Any], vehicle_classes_data: Dict[str, Any], resources_data: Optional[Dict[str, Any]] = None):
        """
        Fast hydration from pre-loaded dictionary data.

        Used by test fixtures to populate registries from SessionRegistryCache
        without disk I/O. Updates dictionaries in-place to preserve any
        existing references.

        Args:
            components_data: Pre-loaded component definitions
            modifiers_data: Pre-loaded modifier definitions
            vehicle_classes_data: Pre-loaded vehicle class definitions
            resources_data: Optional pre-loaded resource definitions

        Raises:
            RuntimeError: If the registry is frozen
        """
        if self._frozen:
            raise RuntimeError("Cannot hydrate a frozen RegistryManager")

        # NOTE: We update dictionaries in-place rather than replacing them.
        # This ensures any code holding references to these dicts sees the updates.
        self.components.clear()
        self.components.update(components_data)

        self.modifiers.clear()
        self.modifiers.update(modifiers_data)

        self.vehicle_classes.clear()
        self.vehicle_classes.update(vehicle_classes_data)

        self.resources.clear()
        if resources_data:
            self.resources.update(resources_data)

    def clear(self):
        """
        Clear all registries to empty state.
        
        Used by test fixtures to ensure clean state between tests.
        Preserves dict identity, only empties contents.
        
        Raises:
            RuntimeError: If the registry is frozen
        """
        if self._frozen:
             raise RuntimeError("Cannot clear a frozen RegistryManager (Tests must unfreeze or reset if absolutely necessary)")
        self.components.clear()
        self.modifiers.clear()
        self.vehicle_classes.clear()
        self.resources.clear()
        self._validator = None

    def get_validator(self):
        """Get the ship design validator (may be None if not initialized)."""
        return self._validator
    
    def set_validator(self, validator):
        """
        Set the ship design validator.
        
        Args:
            validator: ShipDesignValidator instance
            
        Raises:
            RuntimeError: If the registry is frozen
        """
        self._check_frozen()
        self._validator = validator

    def _check_frozen(self):
        """Helper to raise error if modifications are attempted while frozen."""
        if self._frozen:
            raise RuntimeError("RegistryManager is frozen and cannot be modified")

def get_component_registry() -> Dict[str, Any]:
    """Get the component registry dictionary.

    .. deprecated::
        Use GameRegistries via dependency injection instead.
        This function will be removed in a future version.

    Returns a reference to the live dictionary managed by RegistryManager.
    """
    warnings.warn(
        "get_component_registry() is deprecated. Use GameRegistries via dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return RegistryManager.instance().components

def get_modifier_registry() -> Dict[str, Any]:
    """Get the modifier registry dictionary.

    .. deprecated::
        Use GameRegistries via dependency injection instead.
    """
    warnings.warn(
        "get_modifier_registry() is deprecated. Use GameRegistries via dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return RegistryManager.instance().modifiers

def get_vehicle_classes() -> Dict[str, Any]:
    """Get the vehicle classes dictionary.

    .. deprecated::
        Use GameRegistries via dependency injection instead.
    """
    warnings.warn(
        "get_vehicle_classes() is deprecated. Use GameRegistries via dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return RegistryManager.instance().vehicle_classes

def get_validator():
    """Get the ship design validator (lazy-loaded).

    .. deprecated::
        Use GameRegistries via dependency injection instead.
    """
    warnings.warn(
        "get_validator() is deprecated. Use GameRegistries via dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return RegistryManager.instance().get_validator()

def get_resource_registry() -> Dict[str, Any]:
    """Get the resource registry dictionary.

    .. deprecated::
        Use GameRegistries via dependency injection instead.
    """
    warnings.warn(
        "get_resource_registry() is deprecated. Use GameRegistries via dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return RegistryManager.instance().resources

def freeze_registry() -> None:
    """
    Freeze the registry to prevent further modifications.

    Call this after game initialization to catch accidental mutations
    during gameplay. Thread-safe.

    Note: Use RegistryManager.reset() to unfreeze (destroys instance).
    """
    RegistryManager.instance().freeze()

def set_validator(validator) -> None:
    """
    Set the ship design validator.

    Args:
        validator: ShipDesignValidator instance

    Raises:
        RuntimeError: If the registry is frozen
    """
    RegistryManager.instance().set_validator(validator)

def clear_registry() -> None:
    """
    Clear all registries to empty state.

    Used by test fixtures to ensure clean state between tests.
    Preserves dict identity, only empties contents.

    Raises:
        RuntimeError: If the registry is frozen
    """
    RegistryManager.instance().clear()


# =============================================================================
# Registry Provider Implementations (PROJ-27)
# =============================================================================

class DefaultRegistryProvider:
    """
    Default IRegistryProvider implementation backed by the RegistryManager singleton.

    PROJ-27: This class provides the production implementation of IRegistryProvider.
    It delegates all registry access to the existing singleton, maintaining full
    backward compatibility while enabling dependency injection.

    Usage:
        provider = get_default_registry_provider()
        components = provider.get_components()
    """

    def get_components(self) -> Dict[str, Any]:
        """Get the component registry dictionary from singleton."""
        return RegistryManager.instance().components

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the modifier registry dictionary from singleton."""
        return RegistryManager.instance().modifiers

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the vehicle classes dictionary from singleton."""
        return RegistryManager.instance().vehicle_classes


class TestRegistryProvider:
    """
    Test-friendly IRegistryProvider implementation with isolated data.

    PROJ-27: This class provides an isolated registry for testing. Each instance
    has its own data dictionaries, completely independent of the global singleton.

    Usage:
        # Create isolated provider with custom test data
        provider = TestRegistryProvider(
            components={"test_laser": {"id": "test_laser", "damage": 10}},
            modifiers={"test_mod": {"id": "test_mod", "effect": 1.5}}
        )
        service.calculate_stats(design, registry=provider)
    """

    def __init__(
        self,
        components: Optional[Dict[str, Any]] = None,
        modifiers: Optional[Dict[str, Any]] = None,
        vehicle_classes: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with optional custom data.

        Args:
            components: Custom component definitions (default: empty dict)
            modifiers: Custom modifier definitions (default: empty dict)
            vehicle_classes: Custom vehicle class definitions (default: empty dict)
        """
        self._components = components if components is not None else {}
        self._modifiers = modifiers if modifiers is not None else {}
        self._vehicle_classes = vehicle_classes if vehicle_classes is not None else {}

    def get_components(self) -> Dict[str, Any]:
        """Get the isolated component registry dictionary."""
        return self._components

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the isolated modifier registry dictionary."""
        return self._modifiers

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the isolated vehicle classes dictionary."""
        return self._vehicle_classes


# Singleton instance of DefaultRegistryProvider
_default_provider: Optional[DefaultRegistryProvider] = None


def get_default_registry_provider() -> DefaultRegistryProvider:
    """
    Get the default registry provider (singleton instance).

    PROJ-27: Factory function that returns a shared DefaultRegistryProvider
    instance. This is the recommended way to get the production registry
    provider for dependency injection.

    Returns:
        DefaultRegistryProvider: The shared provider instance
    """
    global _default_provider
    if _default_provider is None:
        _default_provider = DefaultRegistryProvider()
    return _default_provider
