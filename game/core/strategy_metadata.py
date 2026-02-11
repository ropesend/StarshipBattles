"""
Strategy Metadata Service - Provides strategy names and IDs to UI without AI layer dependency.

This service holds the display-facing metadata for combat strategies (names, IDs) without
any AI-layer logic. The AI layer's StrategyManager populates this service when it loads data.

Thread Safety:
    - Instance creation is thread-safe via double-checked locking
    - Read operations are safe; write operations should only happen during data loading

Usage:
    # UI layer reads strategy metadata
    service = StrategyMetadataService.instance()
    names = service.get_strategy_names()  # For dropdowns
    display_name = service.get_strategy_display_name('aggressive_ranged')

    # AI layer populates the service
    StrategyMetadataService.instance().set_strategies(strategies_dict)

Testing:
    - Use reset() to destroy instance completely
    - Use clear() to reset data but preserve instance
"""

import os
import threading
from typing import Dict, List, Optional

from game.core.json_utils import load_json
from game.core.logger import log_info
from game.core.exceptions import StateException


class StrategyMetadataService:
    """
    Singleton service providing strategy metadata (names, IDs) to UI layer.

    This decouples the UI from the AI layer's StrategyManager by providing
    only the display-relevant data (names, IDs) without AI behavior logic.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking
        - Data is populated by AI layer on load

    Usage:
        service = StrategyMetadataService.instance()
        names = service.get_strategy_names()
        name = service.get_strategy_display_name('aggressive_ranged')
    """
    _instance: Optional['StrategyMetadataService'] = None
    _lock = threading.Lock()

    def __init__(self):
        """
        Initialize the StrategyMetadataService.

        Raises:
            StateException: If called directly instead of via instance()
        """
        if StrategyMetadataService._instance is not None:
            raise StateException(
                "StrategyMetadataService is a singleton. Use StrategyMetadataService.instance()",
                code="CORE001",
                context={"class": "StrategyMetadataService"}
            )

        self._strategies: Dict[str, dict] = {}

    @classmethod
    def instance(cls) -> 'StrategyMetadataService':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton StrategyMetadataService instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def clear(self) -> None:
        """
        Reset all strategy data. Used for test isolation.

        Preserves the instance but clears all data.
        """
        self._strategies = {}

    @property
    def strategies(self) -> Dict[str, dict]:
        """
        Get the raw strategies dictionary.

        Returns:
            Dict mapping strategy_id to strategy metadata dict.
            Each strategy dict has at minimum: {'name': str}
        """
        return self._strategies

    def get_strategy_names(self) -> List[str]:
        """
        Get list of strategy display names for UI dropdowns.

        Returns:
            Sorted list of strategy display names
        """
        return sorted(
            strat.get('name', strat_id)
            for strat_id, strat in self._strategies.items()
        )

    def get_strategy_display_name(self, strategy_id: str) -> str:
        """
        Resolve a strategy ID to its display name.

        Args:
            strategy_id: The internal strategy ID

        Returns:
            The display name, or the strategy_id itself if not found
        """
        strategy = self._strategies.get(strategy_id, {})
        return strategy.get('name', strategy_id)

    def get_strategy_id_by_name(self, display_name: str) -> Optional[str]:
        """
        Resolve a display name back to a strategy ID.

        Args:
            display_name: The display name shown in UI

        Returns:
            The strategy ID, or None if not found
        """
        for strat_id, strat in self._strategies.items():
            if strat.get('name', strat_id) == display_name:
                return strat_id
        return None

    def set_strategies(self, strategies: Dict[str, dict]) -> None:
        """
        Set the strategies data directly.

        Called by StrategyManager when it loads data.

        Args:
            strategies: Dict mapping strategy_id to strategy metadata
        """
        self._strategies = strategies.copy()

    def load_data(
        self,
        base_path: str = "data",
        strategy_file: str = "combat_strategies.json"
    ) -> None:
        """
        Load strategy metadata from JSON file.

        This method allows direct loading without going through StrategyManager.
        Used by WorkshopDataLoader.

        Args:
            base_path: Base directory containing the strategy JSON file
            strategy_file: Name of the strategies JSON file
        """
        strategy_data = load_json(
            os.path.join(base_path, strategy_file),
            default={}
        )
        self._strategies = strategy_data.get('strategies', {})
        log_info(
            f"StrategyMetadataService loaded: {len(self._strategies)} strategies"
        )
