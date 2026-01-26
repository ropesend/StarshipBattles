import sys
import os

# Ensure component path
sys.path.append(os.getcwd())

from game.simulation.components.component import load_modifiers, Component, load_components
from game.core.registry import RegistryManager
from ui.builder.modifier_logic import ModifierLogic

# Load Data
print("Loading Modifiers...")
load_modifiers()
mods = RegistryManager.instance().modifiers
print(f"Registry Size: {len(mods)}")

if 'automation' not in mods:
    print("Error: automation modifier missing from registry")
else:
    mod = mods['automation']
print(f"Automation Modifier: {mod.name}")
print(f"Min: {mod.min_val}, Max: {mod.max_val}")
print(f"Def: {mod.default_val}")

# Check Logic
print("Checking ModifierLogic range...")
val_range = ModifierLogic.get_local_min_max('automation', None)
print(f"Logic Range (No Component): {val_range}")

# Component Check
comp = Component({'id': 'test', 'name': 'Test', 'type': 'Weapon', 'mass': 10, 'hp': 10})
val_range_c = ModifierLogic.get_local_min_max('automation', comp)
print(f"Logic Range (Component): {val_range_c}")

if mod.max_val > 1.0:
    print("FAIL: Max val is > 1.0, likely default (100) or misconfigured.")
elif val_range[1] > 1.0:
    print("FAIL: Logic returned range > 1.0.")
else:
    print("SUCCESS: Data loaded correct parameters.")
