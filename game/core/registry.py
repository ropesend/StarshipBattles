"""
Registry Access Patterns
========================

TIER 1 - Domain Services (Computed Access):
    from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
    stats = ShipStatsCalculator.calculate_ship_stats(design)

TIER 2 - Dependency Injection (PROJ-27) [RECOMMENDED]:
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

TIER 3 - Direct Singleton Access (for internal/low-level code):
    # Use sparingly - prefer DI for better testability
    RegistryManager.instance().components

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
]
from dataclasses import dataclass
from typing import Dict, Any, Optional

from game.core.exceptions import StateException, FrozenStateException
from game.core.error_codes import ErrorCode
from game.core.singleton import SingletonMeta


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


# Module-level default registries (set by composition root at startup)
_default_registries: Optional[GameRegistries] = None


def set_default_registries(registries: GameRegistries) -> None:
    """
    Set the default GameRegistries instance.

    Called by composition roots (app.py at startup, conftest.py in tests)
    to make registries available via get_default_registries().

    Args:
        registries: The GameRegistries instance to use as default
    """
    global _default_registries
    _default_registries = registries


def get_default_registries() -> GameRegistries:
    """
    Get the default GameRegistries instance.

    Service locator for callers that cannot receive registries via
    constructor injection (e.g., dataclass methods, lazy init).
    Prefer constructor injection where possible.

    Set by: app.py (production), conftest.py (tests)

    Returns:
        The default GameRegistries instance

    Raises:
        StateException: If set_default_registries() has not been called
    """
    if _default_registries is None:
        raise StateException(
            "Default registries not set. Call set_default_registries() first.",
            code=ErrorCode.NOT_INITIALIZED.value,
            context={"operation": "get_default_registries"}
        )
    return _default_registries

class RegistryManager(metaclass=SingletonMeta):
    """
    Central singleton for managing global game state registries.

    Replaces module-level globals to allow for clean state resets in testing.

    Thread Safety:
        - Instance creation is thread-safe via SingletonMeta
        - All dictionary operations use the same dict instances (no replacement)
        - Individual dict operations are atomic in CPython (GIL)
        - For cross-registry transactions, external synchronization is required

    Usage:
        # Preferred: Use GameRegistries via DI (PROJ-38)
        from game.core.registry import get_default_registries

        registries = get_default_registries()
        components = registries.components
        modifiers = registries.modifiers
        classes = registries.vehicle_classes

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
        FrozenStateException: If the registry is frozen
    """
    RegistryManager.instance().set_validator(validator)

def clear_registry() -> None:
    """
    Clear all registries to empty state.

    Used by test fixtures to ensure clean state between tests.
    Preserves dict identity, only empties contents.

    Raises:
        FrozenStateException: If the registry is frozen
    """
    RegistryManager.instance().clear()


# =============================================================================
# Registry Provider Implementations (PROJ-27)
# =============================================================================

class DefaultRegistryProvider:
    """
    Default IRegistryProvider implementation backed by the RegistryManager singleton.

    PROJ-27: This class provides the production implementation of IRegistryProvider.
    It delegates all registry access to the existing singleton while enabling
    dependency injection.

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
