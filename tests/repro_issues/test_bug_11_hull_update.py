"""
Reproduction test for BUG-11: Hull Not Updated When Switching Ship/Class Type.
This test verifies that changing a ship's class also updates its hull component
to the default_hull_id of the new class.
"""
import pytest
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType
from game.core.registry import RegistryManager

@pytest.fixture
def dual_class_registry():
    """Setup registry with two classes and their respective hulls."""
    mgr = RegistryManager.instance()
    mgr.clear()
    
    # Define classes
    mgr.vehicle_classes.update({
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []}
            ]
        },
        "Frigate": {
            "type": "Ship",
            "max_mass": 2000,
            "default_hull_id": "hull_frigate",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []}
            ]
        }
    })
    
    # Define hulls
    mgr.components.update({
        "hull_escort": Component({
            "id": "hull_escort", "name": "Escort Hull", "type": "Hull", "mass": 50, "hp": 100
        }),
        "hull_frigate": Component({
            "id": "hull_frigate", "name": "Frigate Hull", "type": "Hull", "mass": 100, "hp": 200
        })
    })
    
    return mgr

@pytest.mark.use_custom_data
def test_hull_updates_on_class_change_no_migrate(dual_class_registry):
    """Verify hull updates when changing class (migrate_components=False)."""
    ship = Ship(name="Test", x=0, y=0, color=(255,255,255), ship_class="Escort")
    
    # Initial check
    core_comps = ship.layers[LayerType.CORE]['components']
    assert any(c.id == "hull_escort" for c in core_comps), "Initial hull should be hull_escort"
    
    # Change class
    ship.change_class("Frigate", migrate_components=False)
    
    # Verification
    core_comps = ship.layers[LayerType.CORE]['components']
    assert any(c.id == "hull_frigate" for c in core_comps), "Hull should have updated to hull_frigate"
    assert not any(c.id == "hull_escort" for c in core_comps), "Old hull should be gone"

@pytest.mark.use_custom_data
def test_hull_updates_on_class_change_with_migrate(dual_class_registry):
    """Verify hull updates when changing class (migrate_components=True)."""
    ship = Ship(name="Test", x=0, y=0, color=(255,255,255), ship_class="Escort")
    
    # Change class with migration
    ship.change_class("Frigate", migrate_components=True)
    
    # Verification
    core_comps = ship.layers[LayerType.CORE]['components']
    assert any(c.id == "hull_frigate" for c in core_comps), "Hull should have updated to hull_frigate"
    assert not any(c.id == "hull_escort" for c in core_comps), "Old hull should be gone"
