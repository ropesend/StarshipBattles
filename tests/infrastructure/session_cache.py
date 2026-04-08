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
        self.strategies_data: Dict[str, Any] = {}
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
                from game.simulation.entities.ship_loader import load_vehicle_classes
                from game.core.registry import RegistryManager, set_default_registry_manager

                # 2. Create fresh Registry for data capture (PROJ-258)
                mgr = RegistryManager()
                set_default_registry_manager(mgr)

                # 3. Trigger Loaders (They populate Registry)
                # Ensure we use absolute paths from constants
                from game.core.paths import Paths
                from game.core.registry import get_default_registry_provider

                comp_path = os.path.join(Paths.DATA_DIR, "components.json")
                mod_path = os.path.join(Paths.DATA_DIR, "modifiers.json")

                # PROJ-211: Pass registry_provider explicitly (no fallback)
                provider = get_default_registry_provider()
                load_modifiers(mod_path, registry_provider=provider)
                load_components(comp_path, registry_provider=provider)
                load_vehicle_classes(registry_provider=provider)

                # 4. Load combat strategies
                from game.ai.strategy_manager import StrategyManager
                strategy_mgr = StrategyManager.instance()
                strategy_mgr.clear()
                strategy_mgr.load_data(str(Paths.DATA_DIR))
                strategy_mgr._loaded = True

                # 5. Capture State (Deep Copy for initial load, shallow copies on retrieval)
                self.modifiers_data = copy.deepcopy(mgr.modifiers)
                self.components_data = copy.deepcopy(mgr.components)
                self.vehicle_classes_data = copy.deepcopy(mgr.vehicle_classes)
                self.strategies_data = copy.deepcopy(StrategyManager.instance().strategies)

                self._is_loaded = True

                if os.environ.get("PYTEST_XDIST_WORKER") is None:
                    print(f"[SessionRegistryCache] Loaded {len(self.components_data)} components, {len(self.vehicle_classes_data)} classes, {len(self.strategies_data)} strategies.")

            except Exception as e:
                # Always print critical errors
                print(f"[SessionRegistryCache] CRITICAL ERROR loading data: {e}")
                import traceback
                traceback.print_exc()

    # _load_json helper no longer needed, removing...
    def _deprecated_load_json(self, filepath: str):
        pass

    def get_components(self) -> Dict[str, Any]:
        """Returns deep copy of components data.

        Deep copy is required because Component objects are mutable and tests
        may modify their abilities dict during recalculate_stats(). Without
        deep copy, these mutations would pollute the session cache and cause
        test isolation failures.
        """
        with self._lock:
            return copy.deepcopy(self.components_data)

    def get_modifiers(self) -> Dict[str, Any]:
        """Returns deep copy of modifiers data.

        Deep copy is required to prevent test mutations from polluting
        the session cache.
        """
        with self._lock:
            return copy.deepcopy(self.modifiers_data)

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Returns deep copy of vehicle classes data.

        Deep copy is required because tests may mutate vehicle class
        definitions (e.g., test_planetary_complex.py modifies max_mass).
        Without deep copy, these mutations would pollute the session cache.
        """
        with self._lock:
            return copy.deepcopy(self.vehicle_classes_data)

    def get_strategies(self) -> Dict[str, Any]:
        """Returns deep copy of combat strategies data.

        Deep copy is required to prevent test mutations from polluting
        the session cache.
        """
        with self._lock:
            return copy.deepcopy(self.strategies_data)

    @classmethod
    def reset(cls):
        """For testing the cache itself."""
        cls._instance = None
