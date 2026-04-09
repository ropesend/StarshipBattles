"""
Strategy Manager - Manager for combat strategies, targeting policies, and movement policies.

Exception Handling
==================
- All policy lookups return defaults for missing keys (graceful degradation)
"""

import logging
import os
import threading
from typing import Any, Dict, Optional

from game.core.json_utils import load_json

logger = logging.getLogger(__name__)
from game.core.strategy_metadata import get_default_strategy_metadata_service

# Module-level reference (PROJ-258)
_default_strategy_manager: Optional['StrategyManager'] = None


def get_default_strategy_manager() -> 'StrategyManager':
    """Get the module-level StrategyManager reference.

    Auto-creates on first access if not yet set.

    Returns:
        The module-level StrategyManager instance.
    """
    global _default_strategy_manager
    if _default_strategy_manager is None:
        _default_strategy_manager = StrategyManager()
    return _default_strategy_manager


class StrategyManager:
    """Manager for combat strategies, targeting policies, and movement policies.

    PROJ-258: Migrated from SingletonMeta to DI via module-level accessor.

    Access patterns:
        - Production: get_default_strategy_manager()
        - Tests: StrategyManager() for direct construction

    Thread Safety:
        - Data loading (load_data/ensure_loaded) is thread-safe via locking
        - Once loaded, all read operations are safe without synchronization
    """
    _data_lock = threading.Lock()

    def __init__(self):
        """Initialize the StrategyManager."""
        self.targeting_policies = {}
        self.movement_policies = {}
        self.strategies = {}
        self._loaded = False
        self.defaults = {
            'targeting': {'name': 'Default', 'rules': [{'type': 'nearest', 'weight': 100}]},
            'movement': {'behavior': 'kite', 'engage_distance': 'max_range', 'retreat_hp_threshold': 0.1, 'avoid_collisions': True},
            'strategy': {'name': 'Default', 'targeting_policy': 'standard', 'movement_policy': 'kite_max'}
        }

    def clear(self):
        """
        Reset all policies. Used for test isolation.

        Preserves the instance but clears all data and resets the loaded flag.
        """
        self.targeting_policies = {}
        self.movement_policies = {}
        self.strategies = {}
        self._loaded = False
        # Also clear the metadata service for UI layer
        get_default_strategy_metadata_service().clear()

    def ensure_loaded(self, base_path: str = "data"):
        """
        Ensure data is loaded (lazy loading).

        Loads data from disk only on first call. Subsequent calls are no-ops.

        Args:
            base_path: Base directory containing strategy JSON files
        """
        if self._loaded:
            return
        with self._data_lock:
            if self._loaded:
                return
            self.load_data(base_path)
            self._loaded = True

    def load_data(
        self,
        base_path: str = "data",
        targeting_file: str = "targeting_policies.json",
        movement_file: str = "movement_policies.json",
        strategy_file: str = "combat_strategies.json"
    ) -> None:
        # Load Targeting Policies
        targeting_data = load_json(os.path.join(base_path, targeting_file), default={})
        self.targeting_policies = targeting_data.get('policies', {})

        # Load Movement Policies
        movement_data = load_json(os.path.join(base_path, movement_file), default={})
        self.movement_policies = movement_data.get('policies', {})

        # Load Strategies
        strategy_data = load_json(os.path.join(base_path, strategy_file), default={})
        self.strategies = strategy_data.get('strategies', {})

        # Populate metadata service for UI layer
        get_default_strategy_metadata_service().set_strategies(self.strategies)

        logger.info(f"StrategyManager loaded: {len(self.strategies)} strategies, {len(self.targeting_policies)} targeting, {len(self.movement_policies)} movement")

    def get_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Get a strategy definition by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.strategies.get(strategy_id, self.defaults['strategy'])

    def get_targeting_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get a targeting policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.targeting_policies.get(policy_id, self.defaults['targeting'])

    def get_movement_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get a movement policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.movement_policies.get(policy_id, self.defaults['movement'])

    def resolve_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Returns fully resolved strategy object with policy data embedded (helper)."""
        strat_def = self.get_strategy(strategy_id)

        t_pol = self.get_targeting_policy(strat_def.get('targeting_policy'))
        m_pol = self.get_movement_policy(strat_def.get('movement_policy'))

        return {
            'definition': strat_def,
            'targeting': t_pol,
            'movement': m_pol
        }
