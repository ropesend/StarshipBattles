
import unittest
import os
import sys

sys.path.append(os.getcwd())

from game.simulation.components.component import load_components, create_component, SeekerWeapon, load_modifiers

def test():
    load_components("data/components.json")
    load_modifiers("data/modifiers.json")
    
    missile = create_component('capital_missile')
    print(f"Initial Range: {missile.range}")
    
    missile.add_modifier('range_mount', 1.0)
    print(f"Range after modifier: {missile.range}")
    
    expected = int(missile.projectile_speed * missile.endurance * 0.8 * 2.0)
    print(f"Expected: {expected}")
    
    if missile.range == expected:
        print("SUCCESS")
    else:
        print("FAILURE")

    # Debug modifiers
    print("Modifiers on missile:")
    for m in missile.modifiers:
        print(f"  {m.definition.id} = {m.value}")

if __name__ == "__main__":
    test()
