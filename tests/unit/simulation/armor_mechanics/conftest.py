"""Shared fixtures for armor mechanics tests."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_ship_with_emissive():
    """Create a mock ship with emissive armor."""
    ship = MagicMock()
    ship.is_alive = True
    ship.emissive_armor = 15  # Ignores first 15 damage
    ship.shield_regenerating_armor = 0
    ship.current_shields = 0
    ship.max_shields = 0
    ship.hp = 100
    ship.layers = {}
    ship.recalculate_stats = MagicMock()
    ship.update_derelict_status = MagicMock()
    return ship


@pytest.fixture
def mock_ship_base():
    """Create a basic mock ship for armor tests."""
    ship = MagicMock()
    ship.is_alive = True
    ship.emissive_armor = 0
    ship.shield_regenerating_armor = 0
    ship.current_shields = 0
    ship.max_shields = 0
    ship.hp = 100
    ship.layers = {}
    ship.recalculate_stats = MagicMock()
    ship.update_derelict_status = MagicMock()
    return ship


