"""Shared fixtures for strategy engine tests."""
from unittest.mock import MagicMock

import pytest

from game.strategy.engine.empire_economy_calculator import EmpireEconomyCalculator


@pytest.fixture
def economy_calculator(fresh_registries):
    """Create an EmpireEconomyCalculator with registries.

    PROJ-218: Uses registries for maintenance cost calculation.
    """
    return EmpireEconomyCalculator(registries=fresh_registries)


# PROJ-479 Task 5.4 + Task 6.6 (DUP-005 + HLP-006): canonical mock-empire
# factory. Consolidates 6 byte-identical (with kwarg variants) `_make_empire`
# helpers from sibling test files.
def make_mock_empire(
    empire_id: int = 1,
    colonies=None,
    fleets=None,
    resource_pool=None,
    max_storage=None,
    **overrides,
):
    """Build a MagicMock Empire stub for engine-level tests.

    Args:
        empire_id: empire.id (default 1; some sibling helpers used 0)
        colonies: empire.colonies (default empty list)
        fleets: empire.fleets (default empty list)
        resource_pool: empire.resource_pool — kwarg for harvesting tests
        max_storage: empire.max_storage — kwarg for harvesting tests
        **overrides: any extra attributes to set on the mock

    Returns:
        MagicMock with the standard set of attributes pre-populated.
    """
    empire = MagicMock()
    empire.id = empire_id
    empire.colonies = colonies if colonies is not None else []
    empire.fleets = fleets if fleets is not None else []
    if resource_pool is not None:
        empire.resource_pool = resource_pool
    if max_storage is not None:
        empire.max_storage = max_storage
    for attr, value in overrides.items():
        setattr(empire, attr, value)
    return empire


@pytest.fixture
def mock_empire_factory():
    """Pytest fixture form of `make_mock_empire`."""
    return make_mock_empire
