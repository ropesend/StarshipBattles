import json
import os
import copy
import threading
from typing import Dict, Any, Optional

class SessionRegistryCache:
    """
    Thread-safe Singleton cache for raw game data (components, modifiers, vehicle_classes).
    Loads data from disk EXACTLY ONCE per test session to prevent IO contention.
    """
    _instance: Optional['SessionRegistryCache'] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self):
        if SessionRegistryCache._instance is not None:
             raise Exception("SessionRegistryCache is a singleton. Use instance()")
        
        self.components_data: Dict[str, Any] = {}
        self.modifiers_data: Dict[str, Any] = {}
        self.vehicle_classes_data: Dict[str, Any] = {}
        self._is_loaded = False

    @classmethod
    def instance(cls) -> 'SessionRegistryCache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_all_data(self, base_path: str = "data"):
        """
        Loads all data using actual game loaders to ensure logic (e.g. layer resolution) is applied.
        Captures the resulting state from RegistryManager.
        """
        with self._lock:
            if self._is_loaded:
                return

            try:
                # 1. Import Loaders inside method to avoid circular imports at top level
                from game.simulation.components.component import load_components, load_modifiers
                from game.simulation.entities.ship import load_vehicle_classes
                from game.core.registry import RegistryManager

                # 2. Reset Registry to clean state for capture
                mgr = RegistryManager.instance()
                mgr.clear()

                # 3. Trigger Loaders (They populate Registry)
                # Ensure we use absolute paths from constants
                from game.core.constants import DATA_DIR
                
                comp_path = os.path.join(DATA_DIR, "components.json")
                mod_path = os.path.join(DATA_DIR, "modifiers.json")
                
                load_modifiers(mod_path) 
                load_components(comp_path)
                load_vehicle_classes()

                # 4. Capture State (Deep Copy)
                self.modifiers_data = copy.deepcopy(mgr.modifiers)
                self.components_data = copy.deepcopy(mgr.components)
                self.vehicle_classes_data = copy.deepcopy(mgr.vehicle_classes)

                self._is_loaded = True
                print(f"[SessionRegistryCache] Loaded {len(self.components_data)} components, {len(self.vehicle_classes_data)} classes.")

            except Exception as e:
                print(f"[SessionRegistryCache] CRITICAL ERROR loading data: {e}")
                import traceback
                traceback.print_exc()

    # _load_json helper no longer needed, removing...
    def _deprecated_load_json(self, filepath: str):
        pass

    def get_components(self) -> Dict[str, Any]:
        """Returns deep, safe copy of components data."""
        with self._lock:
             # Return deepcopy to ensure no one modifies the cache
             return copy.deepcopy(self.components_data)

    def get_modifiers(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self.modifiers_data)

    def get_vehicle_classes(self) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self.vehicle_classes_data)

    @classmethod
    def reset(cls):
        """For testing the cache itself."""
        cls._instance = None
