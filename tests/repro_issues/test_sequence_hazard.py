
import pytest
try:
    from game.core.registry import RegistryManager
except ImportError:
    pytest.skip("Could not import registries", allow_module_level=True)

# These tests rely on default execution order (line definition order) or alphabetical.
# We name them to ensure alphabetical order: test_a_... runs before test_b_...

def test_a_pollution_setter():
    """Injects 'poison' into global registries."""
    comps = RegistryManager.instance().components
    mods = RegistryManager.instance().modifiers
    classes = RegistryManager.instance().vehicle_classes
    
    comps["POISON_COMPONENT"] = {"name": "Poison"}
    mods["POISON_MOD"] = {"effect": "Toxic"}
    classes["POISON_SHIP"] = {"class": "Hazard"}
    
    assert "POISON_COMPONENT" in comps

def test_b_pollution_victim():
    """Asserts that the environment is clean (fails if pollution persists)."""
    # If no isolation mechanism is in place, these asserts will FAIL.
    comps = RegistryManager.instance().components
    mods = RegistryManager.instance().modifiers
    classes = RegistryManager.instance().vehicle_classes
    
    assert "POISON_COMPONENT" not in comps, "Pollution detected: components leaked state!"
    assert "POISON_MOD" not in mods, "Pollution detected: modifiers leaked state!"
    assert "POISON_SHIP" not in classes, "Pollution detected: vehicle_classes leaked state!"
