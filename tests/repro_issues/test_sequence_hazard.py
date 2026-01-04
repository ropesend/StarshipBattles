
import pytest
try:
    from game.simulation.components.component import COMPONENT_REGISTRY, MODIFIER_REGISTRY
    from game.simulation.entities.ship import VEHICLE_CLASSES
except ImportError:
    pytest.skip("Could not import registries", allow_module_level=True)

# These tests rely on default execution order (line definition order) or alphabetical.
# We name them to ensure alphabetical order: test_a_... runs before test_b_...

def test_a_pollution_setter():
    """Injects 'poison' into global registries."""
    COMPONENT_REGISTRY["POISON_COMPONENT"] = {"name": "Poison"}
    MODIFIER_REGISTRY["POISON_MOD"] = {"effect": "Toxic"}
    VEHICLE_CLASSES["POISON_SHIP"] = {"class": "Hazard"}
    
    assert "POISON_COMPONENT" in COMPONENT_REGISTRY

def test_b_pollution_victim():
    """Asserts that the environment is clean (fails if pollution persists)."""
    # If no isolation mechanism is in place, these asserts will FAIL.
    assert "POISON_COMPONENT" not in COMPONENT_REGISTRY, "Pollution detected: COMPONENT_REGISTRY leaked state!"
    assert "POISON_MOD" not in MODIFIER_REGISTRY, "Pollution detected: MODIFIER_REGISTRY leaked state!"
    assert "POISON_SHIP" not in VEHICLE_CLASSES, "Pollution detected: VEHICLE_CLASSES leaked state!"
