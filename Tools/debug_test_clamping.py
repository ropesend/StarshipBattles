
import sys
import os
sys.path.append(os.getcwd())

from game.simulation.systems.resource_manager import ResourceRegistry, ResourceState

def run():
    reg = ResourceRegistry()
    reg.register_storage('fuel', 100)
    res = reg.get_resource('fuel')
    res.current_value = 50
    print(f"Initial: Max={res.max_value}, Cur={res.current_value}")
    
    # Test reset_stats
    reg.reset_stats()
    print(f"After Reset: Max={res.max_value}, Cur={res.current_value}")
    
    if res.current_value == 0:
        print("FAIL: Reset Stats cleared Current Value!")
    else:
        print("PASS: Current Value persisted")

    # Test set_max clamping
    res.set_max(0)
    print(f"After set_max(0): Max={res.max_value}, Cur={res.current_value}")
    
    if res.current_value != 0:
         print("FAIL: set_max(0) failed to clamp!")

if __name__ == "__main__":
    run()
