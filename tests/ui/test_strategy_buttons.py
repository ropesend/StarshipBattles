
import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.ui.screens.strategy_screen import StrategyInterface
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire

class MockScene:
    def __init__(self):
        self.camera = MagicMock()
        self.camera.zoom = 1.0
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = MagicMock()
        self.turn_engine = MagicMock()
        # Ensure validate_colonize_order returns valid for owned fleet test
        self.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=True)

@pytest.fixture
def strategy_ui():
    pygame.init()
    pygame.display.set_mode((800, 600))
    scene = MockScene()
    ui = StrategyInterface(scene, 800, 600)
    return ui

from game.strategy.data.hex_math import HexCoord

def create_dummy_planet(name, owner_id=None):
    p = Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        planet_type=PlanetType.TERRESTRIAL
    )
    p.owner_id = owner_id
    return p

def test_build_button_visibility_owned_planet(strategy_ui):
    """Test that build button is visible for owned planets."""
    # Setup
    planet = create_dummy_planet("Test Planet", strategy_ui.scene.current_empire.id)
    
    # Act
    strategy_ui.show_detailed_report(planet)
    
    # Assert
    assert strategy_ui.btn_build_ship.visible == 1, "Build button should be visible for owned planet"

def test_build_button_visibility_unowned_planet(strategy_ui):
    """Test that build button is hidden for unowned planets."""
    # Setup
    planet = create_dummy_planet("Alien Planet", 999)
    
    # Act
    strategy_ui.show_detailed_report(planet)
    
    # Assert
    assert strategy_ui.btn_build_ship.visible == 0, "Build button should be hidden for unowned planet"

def test_fleet_buttons_visibility_owned_fleet(strategy_ui):
    """Test that fleet buttons are visible for owned fleets."""
    # Setup
    fleet = Fleet(1, strategy_ui.scene.current_empire.id, (0,0))
    fleet.ships = ["Ship"]
    
    # Act
    strategy_ui.show_detailed_report(fleet)
    
    # Assert
    assert strategy_ui.btn_colonize.visible == 1, "Colonize button should be visible for owned fleet"
    assert strategy_ui.btn_orders.visible == 1, "Orders button should be visible for owned fleet"

def test_fleet_buttons_visibility_enemy_fleet(strategy_ui):
    """Test that fleet buttons are hidden for enemy fleets."""
    # Setup
    fleet = Fleet(2, 999, (0,0)) # Enemy
    fleet.ships = ["Ship"]
    
    # Act
    strategy_ui.show_detailed_report(fleet)
    
    # Assert
    assert strategy_ui.btn_colonize.visible == 0, "Colonize button should be hidden for enemy fleet"
    assert strategy_ui.btn_orders.visible == 0, "Orders button should be hidden for enemy fleet"
