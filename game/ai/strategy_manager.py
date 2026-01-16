"""
Strategy Manager - Singleton manager for combat strategies, targeting policies, and movement policies.
"""

import os
import threading
from typing import Optional

from game.core.logger import log_info
from game.core.json_utils import load_json


class StrategyManager:
    """
    Singleton manager for combat strategies, targeting policies, and movement policies.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking
        - Data loading is lazy (on first access) to avoid import-time side effects

    Usage:
        manager = StrategyManager.instance()
        strategy = manager.get_strategy('aggressive_ranged')

    Testing:
        - Use reset() to destroy instance completely
        - Use clear() to reset data but preserve instance
    """
    _instance: Optional['StrategyManager'] = None
    _lock = threading.Lock()

    def __init__(self):
        """
        Initialize the StrategyManager.

        Raises:
            Exception: If called directly instead of via instance()
        """
        if StrategyManager._instance is not None:
            raise Exception("StrategyManager is a singleton. Use StrategyManager.instance()")

        self.targeting_policies = {}
        self.movement_policies = {}
        self.strategies = {}
        self._loaded = False
        self.defaults = {
            'targeting': {'name': 'Default', 'rules': [{'type': 'nearest', 'weight': 100}]},
            'movement': {'behavior': 'kite', 'engage_distance': 'max_range', 'retreat_hp_threshold': 0.1, 'avoid_collisions': True},
            'strategy': {'name': 'Default', 'targeting_policy': 'standard', 'movement_policy': 'kite_max'}
        }

    @classmethod
    def instance(cls) -> 'StrategyManager':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton StrategyManager instance
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

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def clear(self):
        """
        Reset all policies. Used for test isolation.

        Preserves the instance but clears all data and resets the loaded flag.
        """
        self.targeting_policies = {}
        self.movement_policies = {}
        self.strategies = {}
        self._loaded = False

    def ensure_loaded(self, base_path: str = "data"):
        """
        Ensure data is loaded (lazy loading).

        Loads data from disk only on first call. Subsequent calls are no-ops.

        Args:
            base_path: Base directory containing strategy JSON files
        """
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            self.load_data(base_path)
            self._loaded = True

    def load_data(self, base_path="data", targeting_file="targeting_policies.json", movement_file="movement_policies.json", strategy_file="combat_strategies.json"):
        # Load Targeting Policies
        targeting_data = load_json(os.path.join(base_path, targeting_file), default={})
        self.targeting_policies = targeting_data.get('policies', {})

        # Load Movement Policies
        movement_data = load_json(os.path.join(base_path, movement_file), default={})
        self.movement_policies = movement_data.get('policies', {})

        # Load Strategies
        strategy_data = load_json(os.path.join(base_path, strategy_file), default={})
        self.strategies = strategy_data.get('strategies', {})

        log_info(f"StrategyManager loaded: {len(self.strategies)} strategies, {len(self.targeting_policies)} targeting, {len(self.movement_policies)} movement")

    def get_strategy(self, strategy_id):
        """Get a strategy definition by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.strategies.get(strategy_id, self.defaults['strategy'])

    def get_targeting_policy(self, policy_id):
        """Get a targeting policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.targeting_policies.get(policy_id, self.defaults['targeting'])

    def get_movement_policy(self, policy_id):
        """Get a movement policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.movement_policies.get(policy_id, self.defaults['movement'])

    def resolve_strategy(self, strategy_id):
        """Returns fully resolved strategy object with policy data embedded (helper)."""
        strat_def = self.get_strategy(strategy_id)

        t_pol = self.get_targeting_policy(strat_def.get('targeting_policy'))
        m_pol = self.get_movement_policy(strat_def.get('movement_policy'))

        return {
            'definition': strat_def,
            'targeting': t_pol,
            'movement': m_pol
        }


def load_combat_strategies(filepath=None):
    """
    Entry point for loading. Filepath arg is an optional override for base path.

    NOTE: This function is deprecated. StrategyManager now uses lazy loading.
    Kept for backward compatibility with existing code.
    """
    manager = StrategyManager.instance()
    manager.clear()

    # Determine base path from filepath or default
    if filepath:
        if os.path.isdir(filepath):
            base_dir = filepath
        else:
            base_dir = os.path.dirname(filepath)
    else:
        base_dir = "data"

    manager.load_data(base_dir)
    manager._loaded = True


def get_strategy_names():
    """Return list of available strategy IDs for UI."""
    manager = StrategyManager.instance()
    manager.ensure_loaded()
    return list(manager.strategies.keys())


def reset_strategy_manager():
    """
    Reset the StrategyManager for test isolation.

    Clears all loaded data but keeps the singleton instance.
    """
    StrategyManager.instance().clear()
