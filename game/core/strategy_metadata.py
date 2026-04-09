"""
Strategy Metadata Service - Provides strategy names and IDs to UI without AI layer dependency.

This service holds the display-facing metadata for combat strategies (names, IDs) without
any AI-layer logic. The AI layer's StrategyManager populates this service when it loads data.

Thread Safety:
    - Read operations are safe; write operations should only happen during data loading

Usage:
    # UI layer reads strategy metadata
    from game.core.strategy_metadata import get_default_strategy_metadata_service
    service = get_default_strategy_metadata_service()
    names = service.get_strategy_names()  # For dropdowns
    display_name = service.get_strategy_display_name('aggressive_ranged')

    # AI layer populates the service
    get_default_strategy_metadata_service().set_strategies(strategies_dict)

Testing:
    - Use StrategyMetadataService() for direct construction in tests
    - Use clear() to reset data but preserve instance
"""

from typing import Dict, List, Optional

# Module-level reference (PROJ-258)
_default_service: Optional['StrategyMetadataService'] = None


def get_default_strategy_metadata_service() -> 'StrategyMetadataService':
    """Get the module-level StrategyMetadataService reference.

    Auto-creates on first access if not yet set.

    Returns:
        The module-level StrategyMetadataService instance.
    """
    global _default_service
    if _default_service is None:
        _default_service = StrategyMetadataService()
    return _default_service


class StrategyMetadataService:
    """Service providing strategy metadata (names, IDs) to UI layer.

    PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext.

    This decouples the UI from the AI layer's StrategyManager by providing
    only the display-relevant data (names, IDs) without AI behavior logic.
    """

    def __init__(self):
        """Initialize the StrategyMetadataService."""
        self._strategies: Dict[str, dict] = {}

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
