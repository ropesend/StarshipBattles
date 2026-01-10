import pytest
from game.simulation.entities.ship import Ship
from game.simulation.components.component import LayerType
from game.core.registry import RegistryManager

@pytest.fixture(autouse=True)
def cleanup_registry():
    yield
    RegistryManager.instance().clear()

def test_hull_missing_required_abilities():
    """
    Reproduction test for BUG-10.
    Verifies that hull components are missing CommandAndControl and CombatPropulsion.
    """
    from game.simulation.entities.ship import load_vehicle_classes
    from game.simulation.components.component import load_components
    
    load_vehicle_classes()
    load_components()
    
    # Escort class auto-equips hull_escort
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
    
    # 1. Check CommandAndControl
    has_command = any(c.has_ability('CommandAndControl') 
                      for layer in ship.layers.values() 
                      for c in layer['components'])
    # Find the hull component
    hull = None
    for layer in ship.layers.values():
        for c in layer['components']:
            if c.type_str == 'Hull':
                hull = c
                break
        if hull:
            break
    assert hull is not None, "Ship should have a hull component."

    # Check for requirement abilities (markers)
    assert hull.has_ability('RequiresCommandAndControl'), "Hull component should include RequiresCommandAndControl capability"
    
    # Ship hulls and Fighter hulls should require combat movement
    if "Ship" in hull.allowed_vehicle_types or "Fighter" in hull.allowed_vehicle_types:
        assert hull.has_ability('RequiresCombatMovement'), "Ship/Fighter hull component should include RequiresCombatMovement capability"

def test_validation_fails_when_requirements_unmet():
    """Verify that ship validation fails if requirement abilities are present but targets are missing."""
    from game.simulation.entities.ship import Ship, load_vehicle_classes
    from game.simulation.components.component import load_components
    from game.simulation.ship_validator import ShipDesignValidator
    
    load_vehicle_classes()
    load_components()
    
    # Create an Escort (has hull_escort which requires C&C and CombatPropulsion)
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort")
    validator = ShipDesignValidator()
    
    # Should fail because it has no Bridge (C&C) and no Engine (CombatPropulsion)
    result = validator.validate_design(ship)
    assert not result.is_valid
    
    error_msgs = result.errors
    assert any("Needs Command capability" in msg for msg in error_msgs)
    assert any("Needs Combat propulsion" in msg for msg in error_msgs)

if __name__ == "__main__":
    # Manual run for debugging
    from game.simulation.entities.ship import initialize_ship_data
    initialize_ship_data()
    try:
        test_hull_missing_required_abilities()
        print("Test PASSED (Bug not found?)")
    except AssertionError as e:
        print(f"Test FAILED as expected: {e}")
