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

    @classmethod
    def instance(cls) -> 'RegistryManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """For testing only: completely destroys the singleton instance."""
        cls._instance = None

    def clear(self):
        """Clears all registries to empty state."""
        self.components.clear()
        self.modifiers.clear()
        self.vehicle_classes.clear()
        self._validator = None

    def get_validator(self):
        return self._validator
    
    def set_validator(self, validator):
        self._validator = validator
