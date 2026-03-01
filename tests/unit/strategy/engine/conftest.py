"""Shared fixtures for strategy engine tests."""
import pytest

from game.strategy.engine.maintenance_engine import MaintenanceEngine
from game.strategy.engine.empire_economy_calculator import EmpireEconomyCalculator


@pytest.fixture
def maintenance_engine(fresh_registries):
    """Create a MaintenanceEngine with registries.

    PROJ-218: Now requires registries for cost calculation via Ship loading.
    """
    return MaintenanceEngine(registries=fresh_registries)


@pytest.fixture
def economy_calculator(fresh_registries):
    """Create an EmpireEconomyCalculator with registries.

    PROJ-218: Uses registries for maintenance cost calculation.
    """
    return EmpireEconomyCalculator(registries=fresh_registries)
