"""
Test Ship Core Behavior - Task 3.2 Verification
Tests the unified Ship stats architecture from Hull Component & Ship Cohesion refactor.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, create_component, LayerType
from game.core.registry import RegistryManager, get_vehicle_classes, get_component_registry


# --- Fixtures ---

@pytest.fixture
def registry_with_hull():
    """
    Populate RegistryManager with Escort class and its hull_escort component.
    Uses use_custom_data marker to skip production hydration.
    """
    mgr = RegistryManager.instance()
    
    # Vehicle class with default_hull_id
    mgr.vehicle_classes.update({
        "Escort": {
            "type": "Ship",
            "hull_mass": 50,  # Legacy fallback (should NOT be used)
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.5, "restrictions": []},
            ],
            "requirements": {}
        }
    })
    
    # Hull component - must be a Component instance with clone() method
    hull_data = {
        "id": "hull_escort",
        "name": "Escort Hull",
        "type": "Hull",
        "mass": 50,
        "hp": 100,  # Note: Component expects 'hp' not 'max_hp'
        "abilities": {"HullComponent": True}
    }
    hull_component = Component(hull_data)
    mgr.components["hull_escort"] = hull_component
    
    yield mgr


@pytest.fixture
def registry_no_hull():
    """
    Populate RegistryManager with TestShip class that has NO default_hull_id.
    This tests the legacy fallback path.
    """
    mgr = RegistryManager.instance()
    
    # Vehicle class WITHOUT default_hull_id
    mgr.vehicle_classes.update({
        "TestShip": {
            "type": "Ship",
            "hull_mass": 100,  # Should be used as legacy fallback
            "max_mass": 2000,
            # NO default_hull_id
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.5, "restrictions": []},
            ],
            "requirements": {}
        }
    })
    
    yield mgr


@pytest.fixture
def ship_with_components(registry_with_hull):
    """Create a Ship with known components for mass/HP verification."""
    mgr = registry_with_hull
    
    # Add a simple Armor component - must be a Component instance
    armor_data = {
        "id": "test_armor",
        "name": "Test Armor",
        "type": "Armor",
        "mass": 25,
        "hp": 50,  # Component expects 'hp' not 'max_hp'
        "abilities": {}
    }
    armor_component = Component(armor_data)
    mgr.components["test_armor"] = armor_component
    
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
    
    # Add armor component to PRIMARY layer
    armor = create_component("test_armor")
    if armor:
        ship.add_component(armor, LayerType.OUTER)
    
    ship.recalculate_stats()
    return ship


@pytest.fixture
def ship_with_bridge(registry_with_hull):
    """Create a Ship with Bridge component having CommandAndControl ability."""
    mgr = registry_with_hull
    
    # Add Bridge component with CommandAndControl - must be Component instance
    bridge_data = {
        "id": "test_bridge",
        "name": "Test Bridge",
        "type": "Bridge",
        "mass": 30,
        "hp": 40,  # Component expects 'hp' not 'max_hp'
        "abilities": {"CommandAndControl": True}
    }
    bridge_component = Component(bridge_data)
    mgr.components["test_bridge"] = bridge_component
    
    ship = Ship(name="BridgeShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
    
    # Add bridge to CORE layer
    bridge = create_component("test_bridge")
    if bridge:
        ship.add_component(bridge, LayerType.CORE)
    
    ship.recalculate_stats()
    return ship


# --- Test Cases ---

@pytest.mark.use_custom_data
class TestHullAutoEquip:
    """TC-3.2.1: Hull Auto-Equip Verification"""
    
    def test_hull_auto_equip(self, registry_with_hull):
        """Verify Ship auto-equips default_hull_id from vehicle class."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        core_comps = ship.layers[LayerType.CORE]['components']
        assert len(core_comps) >= 1, "Expected at least 1 component in CORE layer"
        
        # Find the hull component
        hull_comp = next((c for c in core_comps if c.id == "hull_escort"), None)
        assert hull_comp is not None, "hull_escort should be auto-equipped"
        
        # Attribute Shadowing: base_mass should be 0 when hull is equipped
        assert ship.base_mass == 0.0, "base_mass should be 0 when Hull component is equipped"


@pytest.mark.use_custom_data
class TestLegacyFallback:
    """TC-3.2.2: Legacy Fallback (No Hull)"""
    
    def test_no_hull_fallback(self, registry_no_hull):
        """Verify Ship uses legacy hull_mass when no default_hull_id."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="TestShip")
        
        core_comps = ship.layers[LayerType.CORE]['components']
        
        # No auto-equipped components expected
        hull_comps = [c for c in core_comps if hasattr(c, 'type') and c.type == 'Hull']
        assert len(hull_comps) == 0, "No Hull component should be in CORE when default_hull_id is missing"
        
        # Legacy fallback: base_mass should be the legacy hull_mass value
        assert ship.base_mass == 100.0, "base_mass should be legacy hull_mass (100) when no Hull component"


@pytest.mark.use_custom_data
class TestMassAggregation:
    """TC-3.2.3: Mass Aggregation"""
    
    def test_mass_from_components(self, ship_with_components):
        """Verify Ship.mass equals sum of all component masses + base_mass."""
        ship = ship_with_components
        
        # Calculate expected mass
        component_mass = sum(
            c.mass for layer in ship.layers.values() for c in layer['components']
        )
        expected_mass = ship.base_mass + component_mass
        
        # Ship.mass should match
        assert ship.mass == expected_mass, f"Ship.mass ({ship.mass}) != expected ({expected_mass})"


@pytest.mark.use_custom_data
class TestHPAggregation:
    """TC-3.2.4: HP Aggregation"""
    
    def test_hp_from_components(self, ship_with_components):
        """Verify Ship.max_hp equals sum of component max_hp values."""
        ship = ship_with_components
        
        expected_hp = sum(
            c.max_hp for layer in ship.layers.values() for c in layer['components']
        )
        
        assert ship.max_hp == expected_hp, f"Ship.max_hp ({ship.max_hp}) != expected ({expected_hp})"


@pytest.mark.use_custom_data
class TestDerelictStatus:
    """TC-3.2.5: Derelict Status from CommandAndControl"""
    
    def test_ship_not_derelict_with_bridge(self, ship_with_bridge):
        """Verify ship is NOT derelict when CommandAndControl component is operational."""
        ship = ship_with_bridge
        
        # Find bridge component
        bridge = next(
            (c for layer in ship.layers.values() 
             for c in layer['components']
             if hasattr(c, 'has_ability') and c.has_ability('CommandAndControl')),
            None
        )
        
        if bridge is None:
            pytest.skip("No CommandAndControl component found in test setup")
        
        # Ensure bridge is operational
        assert bridge.current_hp > 0, "Bridge should be operational initially"
        
        ship.update_derelict_status()
        # Note: Derelict depends on requirements in vehicle class
        # With empty requirements {}, ship should NOT be derelict
        assert ship.is_derelict is False, "Ship should NOT be derelict with operational bridge"
    
    def test_derelict_when_requirements_unmet(self, registry_with_hull):
        """Verify ship becomes derelict when requirements are not met."""
        mgr = registry_with_hull
        
        # Update vehicle class to require CommandAndControl
        mgr.vehicle_classes["Escort"]["requirements"] = {
            "command": {"ability": "CommandAndControl", "min_value": True}
        }
        
        # Add Bridge component for the command requirement - must be Component instance
        bridge_data = {
            "id": "test_bridge",
            "name": "Test Bridge",
            "type": "Bridge",
            "mass": 30,
            "hp": 40,  # Component expects 'hp'
            "abilities": {"CommandAndControl": True}
        }
        bridge_component = Component(bridge_data)
        mgr.components["test_bridge"] = bridge_component
        
        ship = Ship(name="DerelictTest", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
        
        # Add and then destroy bridge
        bridge = create_component("test_bridge")
        if bridge:
            ship.add_component(bridge, LayerType.CORE)
        
        ship.recalculate_stats()
        ship.update_derelict_status()
        
        # Should NOT be derelict initially
        assert ship.is_derelict is False, "Ship should not be derelict with operational bridge"
        
        # Destroy the bridge
        if bridge:
            bridge.current_hp = 0
        
        ship.update_derelict_status()
        
        # Should BE derelict now
        assert ship.is_derelict is True, "Ship should be derelict after bridge destruction"
