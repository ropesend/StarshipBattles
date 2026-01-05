from typing import Dict, Any, Optional

class RegistryManager:
    """
    Central singleton for managing global game state registries.
    Replaces module-level globals to allow for clean state resets in testing.
    """
    _instance: Optional['RegistryManager'] = None

    def __init__(self):
        if RegistryManager._instance is not None:
             raise Exception("RegistryManager is a singleton. Use RegistryManager.instance()")
        
        self.components: Dict[str, Any] = {}
        self.modifiers: Dict[str, Any] = {}
        self.vehicle_classes: Dict[str, Any] = {}
        self._validator: Any = None 
        self._frozen: bool = False

    @classmethod
    def instance(cls) -> 'RegistryManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """
        [WARNING] For testing only: completely destroys the singleton instance.
        Prefer clear() for test isolation to avoid stale reference hazards.
        """
        cls._instance = None

    def freeze(self):
        """Prevents further modifications to the registry."""
        self._frozen = True

    def hydrate(self, components_data: Dict[str, Any], modifiers_data: Dict[str, Any], vehicle_classes_data: Dict[str, Any]):
        """
        Fast hydration from pre-loaded dictionary data (e.g. Session Cache).
        Bypasses disk I/O.
        """
        if self._frozen:
            raise RuntimeError("Cannot hydrate a frozen RegistryManager")
            
        # CRITICAL: Do NOT replace the dictionary instances (e.g. self.components = ...).
        # Global aliases in other modules (like COMPONENT_REGISTRY) hold references to the original dicts.
        # We must update them in place.
        self.components.clear()
        self.components.update(components_data)
        
        self.modifiers.clear()
        self.modifiers.update(modifiers_data)
        
        self.vehicle_classes.clear()
        self.vehicle_classes.update(vehicle_classes_data)

    def clear(self):
        """Clears all registries to empty state."""
        if self._frozen:
             raise RuntimeError("Cannot clear a frozen RegistryManager (Tests must unfreeze or reset if absolutely necessary)")
        self.components.clear()
        self.modifiers.clear()
        self.vehicle_classes.clear()
        self._validator = None

    def get_validator(self):
        return self._validator
    
    def set_validator(self, validator):
        self._validator = validator
