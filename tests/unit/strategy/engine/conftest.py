"""Shared fixtures for strategy engine tests."""
import pytest

from game.strategy.engine.empire_economy_calculator import EmpireEconomyCalculator


@pytest.fixture
def economy_calculator(fresh_registries):
    """Create an EmpireEconomyCalculator with registries.

    PROJ-218: Uses registries for maintenance cost calculation.
    """
    return EmpireEconomyCalculator(registries=fresh_registries)
