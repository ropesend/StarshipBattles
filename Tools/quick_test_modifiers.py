"""Debug verification that mandatory modifiers are added when components are added to ships."""
import sys
import os
sys.path.insert(0, os.getcwd())

from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
from game.simulation.components.component import load_components, create_component
from game.core.registry import RegistryManager, get_modifier_registry

# Initialize
print("Loading data...")
initialize_ship_data()
load_components("data/components.json")

# Load modifiers
from game.simulation.components.component import load_modifiers
load_modifiers("data/modifiers.json")

# Check modifier registry
mods = get_modifier_registry()
print(f"Modifier registry has {len(mods)} modifiers")
print(f"simple_size_mount in registry: {'simple_size_mount' in mods}")

# Create ship and add a weapon
ship = Ship("Test", 0, 0, (255, 255, 255))
laser = create_component('laser_cannon')

print(f"\nBefore add_component:")
print(f"  Modifiers: {[m.definition.id for m in laser.modifiers]}")
print(f"  Component type: {laser.type_str}")

# Test ensure_mandatory_modifiers directly
from ui.builder.modifier_logic import ModifierLogic
print(f"\nMandatory modifiers for this component: {ModifierLogic.get_mandatory_modifiers(laser)}")
ModifierLogic.ensure_mandatory_modifiers(laser)
print(f"After ensure_mandatory_modifiers directly:")
print(f"  Modifiers: {[m.definition.id for m in laser.modifiers]}")

# Now test via add_component
laser2 = create_component('laser_cannon')
print(f"\nBefore add_component for laser2:")
print(f"  Modifiers: {[m.definition.id for m in laser2.modifiers]}")

ship.add_component(laser2, LayerType.OUTER)

print(f"After add_component:")
print(f"  Modifiers: {[m.definition.id for m in laser2.modifiers]}")
