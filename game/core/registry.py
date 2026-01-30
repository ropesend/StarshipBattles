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
import threading

from game.core.exceptions import StateException, FrozenStateException
from game.core.error_codes import ErrorCode


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
    composition root. Raises StateException if not set.

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
    _instance: Optional['RegistryManager'] = None
    _lock = threading.Lock()

    def __init__(self):
        """
        Initialize the RegistryManager.

        Raises:
            StateException: If called directly instead of via instance()
        """
        if RegistryManager._instance is not None:
             raise StateException(
                 "RegistryManager is a singleton. Use RegistryManager.instance()",
                 code=ErrorCode.INVALID_STATE.value,
                 context={"class": "RegistryManager"}
             )
        
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

    def get_validator(self):
        """Get the ship design validator (may be None if not initialized)."""
        return self._validator
    
    def set_validator(self, validator):
        """
        Set the ship design validator.

        Args:
            validator: ShipDesignValidator instance

        Raises:
            FrozenStateException: If the registry is frozen
        """
        self._check_frozen()
        self._validator = validator

    def _check_frozen(self):
        """Helper to raise error if modifications are attempted while frozen."""
        if self._frozen:
            raise FrozenStateException(
                "RegistryManager is frozen and cannot be modified",
                code=ErrorCode.STATE_FROZEN.value,
                context={"operation": "modify"}
            )

    def reload_all_from_directory(self, data_dir) -> bool:
        """
        Reload all registry data from a directory.

        Clears all existing registry data and reloads components, modifiers,
        and vehicle classes from JSON files in the specified directory.

        PROJ-44: Centralizes registry reload logic previously scattered across
        BuilderScreen and other locations.

        Args:
            data_dir: Path to directory containing data files (string or Path).
                     Looks for: components.json, modifiers.json, vehicleclasses.json
                     Also checks for test_* prefixed versions.

        Returns:
            True if directory exists (even if some files missing), False if directory invalid.

        Raises:
            FrozenStateException: If the registry is frozen.
        """
        import os
        import logging
        from pathlib import Path

        self._check_frozen()

        logger = logging.getLogger("StarshipBattles")

        # Normalize path
        if isinstance(data_dir, str):
            data_dir = Path(data_dir)

        if not data_dir.exists() or not data_dir.is_dir():
            logger.warning(f"RegistryManager: Directory does not exist: {data_dir}")
            return False

        # Clear all registries first (preserves dict identity)
        self.components.clear()
        self.modifiers.clear()
        self.vehicle_classes.clear()
        self.resources.clear()
        self._validator = None

        # Helper to find file with test_ prefix fallback
        def find_file(*names):
            """Find first existing file from names, checking test_ prefix first."""
            for name in names:
                # Check test_ prefix first (for test data directories)
                test_path = data_dir / f"test_{name}"
                if test_path.exists():
                    return test_path
                # Then standard name
                std_path = data_dir / name
                if std_path.exists():
                    return std_path
            return None

        # Load modifiers first (components may depend on them)
        mod_path = find_file("modifiers.json")
        if mod_path:
            try:
                from game.simulation.components.component import load_modifiers
                load_modifiers(str(mod_path))
                logger.info(f"RegistryManager: Loaded modifiers from {mod_path}")
            except Exception as e:
                logger.error(f"RegistryManager: Failed to load modifiers: {e}")

        # Load components
        comp_path = find_file("components.json")
        if comp_path:
            try:
                from game.simulation.components.component import load_components
                load_components(str(comp_path))
                logger.info(f"RegistryManager: Loaded components from {comp_path}")
            except Exception as e:
                logger.error(f"RegistryManager: Failed to load components: {e}")

        # Load vehicle classes (check multiple possible names)
        vclass_path = find_file("vehicleclasses.json", "classes.json")
        vlayer_path = find_file("vehiclelayers.json", "layers.json")
        if vclass_path:
            try:
                from game.simulation.entities.ship_loader import load_vehicle_classes
                if vlayer_path:
                    load_vehicle_classes(str(vclass_path), layers_file_path=str(vlayer_path))
                    logger.info(f"RegistryManager: Loaded classes from {vclass_path} with layers from {vlayer_path}")
                else:
                    load_vehicle_classes(str(vclass_path))
                    logger.info(f"RegistryManager: Loaded classes from {vclass_path}")
            except Exception as e:
                logger.error(f"RegistryManager: Failed to load vehicle classes: {e}")

        return True


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
