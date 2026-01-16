"""
AI-related test fixtures.

This module provides reusable fixtures for AI-related tests,
centralizing the strategy_manager_with_test_data fixture that
was duplicated across ai/ and combat/ conftest files.

Usage in conftest.py:
    from tests.fixtures.ai import strategy_manager_with_test_data  # noqa: F401
"""
import pytest

from tests.fixtures.paths import get_unit_test_data_dir
from game.ai.controller import StrategyManager


@pytest.fixture
def strategy_manager_with_test_data(unit_test_data_dir):
    """
    Set up StrategyManager with test data.

    Loads AI strategies from the test data directory, ensuring reproducible
    test behavior independent of production data.

    This fixture:
    1. Gets the singleton StrategyManager instance
    2. Loads test targeting, movement, and strategy policies
    3. Yields the manager for test use
    4. Clears the manager after the test
    """
    manager = StrategyManager.instance()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
        strategy_file="test_combat_strategies.json"
    )
    manager._loaded = True
    yield manager
    manager.clear()
