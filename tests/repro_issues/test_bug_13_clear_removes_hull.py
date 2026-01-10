import pytest
from unittest.mock import MagicMock, patch
from game.simulation.entities.ship import Ship
from game.simulation.components.component import LayerType, Component
from game.core.registry import RegistryManager
from game.ui.screens.builder_screen import BuilderSceneGUI

@pytest.fixture
def simple_ship_registry():
    RegistryManager.instance().clear()
    
    classes = {
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 1.0}
            ]
        }
    }
    
    components = {
        "hull_escort": {
            "id": "hull_escort",
            "name": "Escort Hull",
            "type": "Hull",
            "mass": 100,
            "hp": 500
        }
    }
    
    with patch('game.core.registry.get_vehicle_classes', return_value=classes), \
         patch('game.simulation.entities.ship.get_vehicle_classes', return_value=classes), \
         patch('game.simulation.components.component.get_component_registry', return_value={k: Component(v) for k,v in components.items()}):
        yield

def test_clear_design_removes_hull_logic_repro(simple_ship_registry):
    """
    BUG-13 Reproduction: Verify that _clear_design removes the hull component.
    """
    # Instantiate BuilderSceneGUI without calling __init__ to avoid UI complexity
    gui = BuilderSceneGUI.__new__(BuilderSceneGUI)
    
    # Setup minimal required state
    gui.ship = Ship("Test Ship", 0, 0, (255,255,255), ship_class="Escort")
    gui.template_modifiers = {"some_mod": 1.0}
    gui.controller = MagicMock()
    gui.right_panel = MagicMock()
    gui.modifier_panel = MagicMock()
    gui.layer_panel = MagicMock()
    gui.event_bus = MagicMock()
    
    # Verify initial hull exists (added by Ship.__init__ for Escort class)
    hull_comps = gui.ship.layers[LayerType.HULL]['components']
    assert len(hull_comps) == 1, "Ship should start with a hull component"
    
    # Add a non-hull component to another layer
    laser = Component({"id": "small_laser", "name": "Laser", "type": "Weapon", "mass": 10, "hp": 50})
    gui.ship.layers[LayerType.CORE]['components'].append(laser)
    
    # Trigger the bug by calling the actual method
    BuilderSceneGUI._clear_design(gui)
    
    # Verify the bug
    # 1. Non-hull component is correctly removed
    assert len(gui.ship.layers[LayerType.CORE]['components']) == 0
    
    # 2. Hull component is INCORRECTLY removed (This is the bug)
    hull_comps_after = gui.ship.layers[LayerType.HULL]['components']
    
    if len(hull_comps_after) == 0:
        print("\n[CONFIRMED] BUG-13: Hull was removed during Clear Design.")
    
    # This assertion should FAIL to confirm the bug
    assert len(hull_comps_after) > 0, "Hull component should NOT be removed by Clear Design"

if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))
