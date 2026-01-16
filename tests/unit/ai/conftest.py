"""
Conftest for AI module tests.

Provides fixtures and setup for AI-related tests.
"""
import pytest
from pathlib import Path

from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir
from game.ai.controller import StrategyManager


@pytest.fixture
def ai_test_data_dir() -> Path:
    """Return the unit test data directory for AI tests."""
    return get_unit_test_data_dir()


@pytest.fixture
def strategy_manager_with_test_data(ai_test_data_dir):
    """
    Set up StrategyManager with test data.

    Loads AI strategies from the test data directory, ensuring reproducible
    test behavior independent of production data.
    """
    manager = StrategyManager.instance()
    manager.load_data(
        str(ai_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
        strategy_file="test_combat_strategies.json"
    )
    manager._loaded = True
    yield manager
    manager.clear()


@pytest.fixture
def data_path() -> Path:
    """Return the production data directory path."""
    return get_data_dir()
