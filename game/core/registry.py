"""
Registry Access
===============

Dependency Injection [RECOMMENDED]:
    from game.core.registry import get_default_registry_provider

    # Production - uses the shared singleton-backed provider
    provider = get_default_registry_provider()
    components = provider.get_components()

    # Or receive via constructor (best):
    def __init__(self, registry: IRegistryProvider):
        self._registry = registry

    # Test - uses isolated data
    from game.core.registry import TestRegistryProvider
    provider = TestRegistryProvider(
        components={"test_laser": {...}},
        modifiers={},
        resources={}
    )

Lifecycle (composition roots only):
    from game.core.registry import freeze_registry, clear_registry
    freeze_registry()   # After initialization
    clear_registry()    # Test cleanup
"""

__all__ = [
    # Core containers
    'GameRegistries',
    # DI providers (PROJ-27)
    'DefaultRegistryProvider',
    'TestRegistryProvider',
    'get_default_registry_provider',
    # Lifecycle functions
    'freeze_registry',
    'clear_registry',
    'set_validator',
]
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

from game.core.exceptions import StateException, FrozenStateException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from game.core.resources import ResourceCatalog


# =============================================================================
# GameRegistries Container (PROJ-38)
# =============================================================================

@dataclass(frozen=True)
class GameRegistries:
    """
    Immutable container for all game data registries.

    PROJ-38: This container enables Dependency Injection by bundling all
    registries together as an immutable package that can be passed to consumers.

    PROJ-211: Added IRegistryProvider methods so GameRegistries can be passed
    directly to services expecting a registry provider.

    The container itself is frozen (immutable), but the dictionaries inside
    can still be modified. This ensures registry references cannot be swapped
    after initialization while still allowing data to be loaded.

    Attributes:
        components: Dict of component definitions keyed by ID
        modifiers: Dict of modifier definitions keyed by ID
        vehicle_classes: Dict of vehicle class definitions keyed by name
        resources: Dict of resource definitions keyed by ID
        resource_catalog: Unified ResourceCatalog for all resource definitions
    """
    components: Dict[str, Any]
    modifiers: Dict[str, Any]
    vehicle_classes: Dict[str, Any]
    resources: Dict[str, Any]
    resource_catalog: Optional['ResourceCatalog'] = field(default=None)

    def __post_init__(self):
        """Ensure resource_catalog is never None — default to empty catalog."""
        if self.resource_catalog is None:
            from game.core.resources import ResourceCatalog
            object.__setattr__(self, 'resource_catalog', ResourceCatalog.from_data([]))

    # PROJ-211: IRegistryProvider interface methods
    def get_components(self) -> Dict[str, Any]:
        """Get the component registry dictionary."""
        return self.components

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the modifier registry dictionary."""
        return self.modifiers

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the vehicle classes dictionary."""
        return self.vehicle_classes

    def get_resources(self) -> Dict[str, Any]:
        """Get the resources registry dictionary."""
        return self.resources

    def get_resource_catalog(self) -> Optional['ResourceCatalog']:
        """Get the unified ResourceCatalog, or None if not loaded."""
        return self.resource_catalog


class RegistryManager:
    """Central manager for global game state registries.

    PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext.
    Create instances directly or via ApplicationContext.create_production().

    Thread Safety:
        - All dictionary operations use the same dict instances (no replacement)
        - Individual dict operations are atomic in CPython (GIL)
        - For cross-registry transactions, external synchronization is required

    Usage:
        # Preferred: Use IRegistryProvider via DI (PROJ-27)
        from game.core.registry import get_default_registry_provider

        provider = get_default_registry_provider()
        components = provider.get_components()

        # Direct access via ApplicationContext:
        mgr = ctx.registry_manager
        mgr.clear()  # For test isolation
        mgr.freeze() # For production initialization

    Attributes:
        components: Dict of component definitions keyed by ID
        modifiers: Dict of modifier definitions keyed by ID
        vehicle_classes: Dict of vehicle class definitions keyed by name
    """

    def __init__(self):
        """Initialize the RegistryManager."""
        self.components: Dict[str, Any] = {}
        self.modifiers: Dict[str, Any] = {}
        self.vehicle_classes: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}
        self._validator: Any = None
        self._frozen: bool = False

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
            FrozenStateException: If the registry is frozen
        """
        if self._frozen:
            raise FrozenStateException(
                "Cannot hydrate a frozen RegistryManager",
                code=ErrorCode.STATE_FROZEN.value,
                context={"operation": "hydrate"}
            )

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
            FrozenStateException: If the registry is frozen
        """
        if self._frozen:
             raise FrozenStateException(
                 "Cannot clear a frozen RegistryManager (Tests must unfreeze or reset if absolutely necessary)",
                 code=ErrorCode.STATE_FROZEN.value,
                 context={"operation": "clear"}
             )
        self.components.clear()
        self.modifiers.clear()
        self.vehicle_classes.clear()
        self.resources.clear()
        self._validator = None

    def get_validator(self) -> Any:
        """Get the ship design validator (may be None if not initialized)."""
        return self._validator

    def set_validator(self, validator: Any) -> None:
        """
        Set the ship design validator.

        Args:
            validator: ShipDesignValidator instance

        Raises:
            FrozenStateException: If the registry is frozen
        """
        self._check_frozen()
        self._validator = validator

    def _check_frozen(self) -> None:
        """Helper to raise error if modifications are attempted while frozen."""
        if self._frozen:
            raise FrozenStateException(
                "RegistryManager is frozen and cannot be modified",
                code=ErrorCode.STATE_FROZEN.value,
                context={"operation": "modify"}
            )


# =============================================================================
# Module-level RegistryManager reference (PROJ-258)
# =============================================================================

_default_manager: Optional[RegistryManager] = None


def set_default_registry_manager(manager: RegistryManager) -> None:
    """Set the module-level RegistryManager reference.

    Called from ApplicationContext or app.py during startup.
    Module-level wrapper functions (freeze_registry, etc.) use this reference.
    """
    global _default_manager
    _default_manager = manager


def get_default_registry_manager() -> RegistryManager:
    """Get the module-level RegistryManager reference.

    Returns:
        The RegistryManager instance set via set_default_registry_manager().

    Raises:
        StateException: If no RegistryManager has been set.
    """
    if _default_manager is None:
        raise StateException(
            "No RegistryManager configured. Call set_default_registry_manager() "
            "or use ApplicationContext.create_production() first.",
            code=ErrorCode.STATE_FROZEN.value,
        )
    return _default_manager


def freeze_registry() -> None:
    """Freeze the registry to prevent further modifications.

    Call this after game initialization to catch accidental mutations
    during gameplay.
    """
    get_default_registry_manager().freeze()


def set_validator(validator) -> None:
    """Set the ship design validator.

    Args:
        validator: ShipDesignValidator instance

    Raises:
        FrozenStateException: If the registry is frozen
    """
    get_default_registry_manager().set_validator(validator)


def get_validator():
    """Get the ship design validator.

    Returns:
        ShipDesignValidator instance or None if not set
    """
    return get_default_registry_manager().get_validator()


def clear_registry() -> None:
    """Clear all registries to empty state.

    Used by test fixtures to ensure clean state between tests.

    Raises:
        FrozenStateException: If the registry is frozen
    """
    get_default_registry_manager().clear()


# =============================================================================
# Registry Provider Implementations (PROJ-27)
# =============================================================================

class DefaultRegistryProvider:
    """Default IRegistryProvider backed by the module-level RegistryManager.

    PROJ-27: Production implementation of IRegistryProvider.
    PROJ-258: Uses get_default_registry_manager() instead of singleton.

    Usage:
        provider = get_default_registry_provider()
        components = provider.get_components()
    """

    def get_components(self) -> Dict[str, Any]:
        """Get the component registry dictionary."""
        return get_default_registry_manager().components

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the modifier registry dictionary."""
        return get_default_registry_manager().modifiers

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the vehicle classes dictionary."""
        return get_default_registry_manager().vehicle_classes

    def get_resources(self) -> Dict[str, Any]:
        """Get the resources registry dictionary."""
        return get_default_registry_manager().resources

    def get_resource_catalog(self) -> Optional['ResourceCatalog']:
        """Get the unified ResourceCatalog.

        Lazily loads from data/resources.json on first access.
        """
        if not hasattr(self, '_resource_catalog'):
            from game.core.resources import ResourceCatalog
            self._resource_catalog = ResourceCatalog.from_json()
        return self._resource_catalog


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
        vehicle_classes: Optional[Dict[str, Any]] = None,
        resources: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize with optional custom data.

        Args:
            components: Custom component definitions (default: empty dict)
            modifiers: Custom modifier definitions (default: empty dict)
            vehicle_classes: Custom vehicle class definitions (default: empty dict)
            resources: Custom resource definitions (default: empty dict)
        """
        self._components = components if components is not None else {}
        self._modifiers = modifiers if modifiers is not None else {}
        self._vehicle_classes = vehicle_classes if vehicle_classes is not None else {}
        self._resources = resources if resources is not None else {}

    def get_components(self) -> Dict[str, Any]:
        """Get the isolated component registry dictionary."""
        return self._components

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the isolated modifier registry dictionary."""
        return self._modifiers

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the isolated vehicle classes dictionary."""
        return self._vehicle_classes

    def get_resources(self) -> Dict[str, Any]:
        """Get the isolated resources registry dictionary."""
        return self._resources

    def get_resource_catalog(self) -> Optional['ResourceCatalog']:
        """Get resource catalog. Returns None for test providers."""
        return None


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
