
import pytest
from unittest.mock import MagicMock
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, create_component, LayerType
from game.core.registry import RegistryManager

@pytest.fixture
def registry_with_hull():
    """Populate RegistryManager with test data, restoring original state after test."""
    from tests.infrastructure.session_cache import SessionRegistryCache

    mgr = RegistryManager.instance()

    # Save original state to restore after test
    original_vehicle_classes = dict(mgr.vehicle_classes)
    original_components = dict(mgr.components)

    mgr.vehicle_classes.clear()
    mgr.components.clear()

    mgr.vehicle_classes.update({
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
            ]
        },
        "Cruiser": {
            "type": "Ship",
            "max_mass": 5000,
            "default_hull_id": "hull_cruiser",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
            ]
        }
    })

    mgr.components.update({
        "hull_escort": Component({
            "id": "hull_escort",
            "name": "Escort Hull",
            "type": "Hull",
            "mass": 50,
            "hp": 100,
            "abilities": {"HullComponent": True}
        }),
        "hull_cruiser": Component({
            "id": "hull_cruiser",
            "name": "Cruiser Hull",
            "type": "Hull",
            "mass": 200,
            "hp": 400,
            "abilities": {"HullComponent": True}
        }),
        "test_armor": Component({
            "id": "test_armor",
            "name": "Test Armor",
            "type": "Armor",
            "mass": 10,
            "hp": 20,
            "abilities": {}
        })
    })

    yield mgr

    # Restore original state after test completes
    # This prevents other tests from seeing partial registry data
    mgr.vehicle_classes.clear()
    mgr.components.clear()
    mgr.vehicle_classes.update(original_vehicle_classes)
    mgr.components.update(original_components)

@pytest.mark.use_custom_data
class TestHullLayerMigration:
    """Tests for the dedicated Hull Layer implementation (Phase 1)."""

    def test_hull_layer_initialization(self, registry_with_hull):
        """Verify Ship initializes with a HULL layer even if not in class def."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        assert LayerType.HULL in ship.layers
        assert ship.layers[LayerType.HULL]['radius_pct'] == 0.0
        assert 'HullOnly' in ship.layers[LayerType.HULL]['restrictions']

    def test_hull_auto_equip_to_hull_layer(self, registry_with_hull):
        """Verify default hull is equipped to LayerType.HULL, not CORE."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        hull_layer_comps = ship.layers[LayerType.HULL]['components']
        core_layer_comps = ship.layers[LayerType.CORE]['components']
        
        assert len(hull_layer_comps) == 1
        assert hull_layer_comps[0].id == "hull_escort"
        assert hull_layer_comps[0].layer_assigned == LayerType.HULL
        
        # Verify CORE is empty (or at least doesn't have the hull)
        assert not any(c.id == "hull_escort" for c in core_layer_comps)

    def test_mass_and_hp_aggregation(self, registry_with_hull):
        """Verify hull in HULL layer still contributes to ship stats."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        ship.recalculate_stats()
        
        # Escort Hull: mass 50, hp 100
        assert ship.mass == 50.0
        assert ship.max_hp == 100

    def test_serialization_excludes_hull_layer(self, registry_with_hull):
        """Verify to_dict does not include HULL layer to prevent duplication on load."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        # Add armor to CORE to ensure layers dict isn't empty
        armor = create_component("test_armor")
        ship.add_component(armor, LayerType.CORE)
        
        data = ship.to_dict()
        
        assert "HULL" not in data['layers']
        assert "CORE" in data['layers']
        
        # Verify no hull_ component is in CORE serialization either (as safety)
        for comp_data in data['layers']['CORE']:
            assert not comp_data['id'].startswith('hull_')

    def test_change_class_migrates_to_new_hull_layer(self, registry_with_hull):
        """Verify change_class correctly manages the HULL layer."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        # Add armor to CORE
        armor = create_component("test_armor")
        ship.add_component(armor, LayerType.CORE)
        
        # Change to Cruiser
        ship.change_class("Cruiser", migrate_components=True)
        
        # Should have Cruiser hull in HULL layer
        assert ship.layers[LayerType.HULL]['components'][0].id == "hull_cruiser"
        assert ship.layers[LayerType.HULL]['components'][0].layer_assigned == LayerType.HULL
        
        # Should have armor in CORE layer
        assert any(c.id == "test_armor" for c in ship.layers[LayerType.CORE]['components'])
        
        # Should NOT have Escort hull anywhere (using helper method)
        assert not any(c.id == "hull_escort" for c in ship.get_all_components())

    def test_hull_layer_ordinality(self, registry_with_hull):
        """Verify HULL layer is index 0 in internal ordering for radius calculation."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        # radius_pct calculation
        # HULL is 0.0
        # CORE mass pct is 1.0 (default)
        # total_capacity = 1.0 (excluding HULL)
        # CORE radius = sqrt(1.0 / 1.0) = 1.0
        
        assert ship.layers[LayerType.HULL]['radius_pct'] == 0.0
        assert ship.layers[LayerType.CORE]['radius_pct'] == 1.0
