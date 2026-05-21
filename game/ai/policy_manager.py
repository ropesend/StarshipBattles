"""
Policy Manager - Loads and provides lookup for targeting and movement policies.

Replaces StrategyManager. Loads targeting_policies.json and movement_policies.json
directly — no intermediate combat_strategies.json indirection.

Exception Handling
==================
- All policy lookups return defaults for missing keys (graceful degradation)
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, Optional

from game.core.json_utils import load_json

logger = logging.getLogger(__name__)

# Module-level reference (PROJ-258 pattern)
_default_policy_manager: Optional['PolicyManager'] = None


def get_default_policy_manager() -> 'PolicyManager':
    """Get the module-level PolicyManager reference.

    Auto-creates on first access if not yet set.

    Returns:
        The module-level PolicyManager instance.
    """
    global _default_policy_manager
    if _default_policy_manager is None:
        _default_policy_manager = PolicyManager()
    return _default_policy_manager


def set_default_policy_manager(manager: 'PolicyManager') -> None:
    """Set the module-level PolicyManager reference (PROJ-471 Task 2.2).

    Called from ``ApplicationContext.create_production()`` so the module-level
    default and ``ctx.policy_manager`` reference the same instance (prevents
    singleton divergence). Replaces the prior raw module-attribute assignment.
    """
    global _default_policy_manager
    _default_policy_manager = manager


class PolicyManager:
    """Manager for targeting and movement policies.

    Loads per-ship behavior definitions from data files:
    - targeting_policies.json: Target scoring rules (standard, sniper, brawler, etc.)
    - movement_policies.json: Movement behaviors (kite_max, brawl_close, etc.)

    Access patterns:
        - Production: get_default_policy_manager()
        - Tests: PolicyManager() for direct construction

    Thread Safety:
        - Data loading (load_data/ensure_loaded) is thread-safe via locking
        - Once loaded, all read operations are safe without synchronization
    """
    _data_lock = threading.Lock()

    def __init__(self):
        """Initialize the PolicyManager."""
        self.targeting_policies: Dict[str, Any] = {}
        self.movement_policies: Dict[str, Any] = {}
        self._loaded = False
        self.defaults = {
            'targeting': {'name': 'Default', 'rules': [{'type': 'nearest', 'weight': 100}]},
            'movement': {'behavior': 'kite', 'engage_distance': 'max_range', 'retreat_hp_threshold': 0.1, 'avoid_collisions': True},
        }

    def clear(self) -> None:
        """
        Reset all policies. Used for test isolation.

        Preserves the instance but clears all data and resets the loaded flag.
        """
        self.targeting_policies = {}
        self.movement_policies = {}
        self._loaded = False

    def ensure_loaded(self, base_path: str = "data") -> None:
        """
        Ensure data is loaded (lazy loading).

        Loads data from disk only on first call. Subsequent calls are no-ops.

        Args:
            base_path: Base directory containing policy JSON files
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
    ) -> None:
        # Load Targeting Policies
        targeting_data = load_json(os.path.join(base_path, targeting_file), default={})
        self.targeting_policies = targeting_data.get('policies', {})

        # Load Movement Policies
        movement_data = load_json(os.path.join(base_path, movement_file), default={})
        self.movement_policies = movement_data.get('policies', {})

        logger.info(f"PolicyManager loaded: {len(self.targeting_policies)} targeting, {len(self.movement_policies)} movement")

    def get_targeting_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get a targeting policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.targeting_policies.get(policy_id, self.defaults['targeting'])

    def get_movement_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get a movement policy by ID. Triggers lazy loading if needed."""
        self.ensure_loaded()
        return self.movement_policies.get(policy_id, self.defaults['movement'])
