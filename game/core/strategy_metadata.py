"""
Strategy Metadata Service - Provides strategy names and IDs to UI without AI layer dependency.

This service holds the display-facing metadata for combat strategies (names, IDs) without
any AI-layer logic. The AI layer's StrategyManager populates this service when it loads data.

Thread Safety:
    - Instance creation is thread-safe via SingletonMeta
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

from typing import Dict, List, Optional

# Module-level reference (PROJ-258)
_default_service: Optional['StrategyMetadataService'] = None


class StrategyMetadataService:
    """Service providing strategy metadata (names, IDs) to UI layer.

    PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext.

    This decouples the UI from the AI layer's StrategyManager by providing
    only the display-relevant data (names, IDs) without AI behavior logic.
    """

    def __init__(self):
        """Initialize the StrategyMetadataService."""
        self._strategies: Dict[str, dict] = {}

    @classmethod
    def instance(cls) -> 'StrategyMetadataService':
        """PROJ-258 compatibility shim — returns module-level instance."""
        global _default_service
        if _default_service is None:
            _default_service = cls()
        return _default_service

    @classmethod
    def reset(cls) -> None:
        """PROJ-258 compatibility shim — replaces module-level instance."""
        global _default_service
        _default_service = cls()

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
