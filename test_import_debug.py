
import sys
import os
sys.path.append(os.getcwd())

print("Importing Component...")
try:
    from game.simulation.components.component import Component
    print("Component imported.")
except ImportError as e:
    print(f"Failed to import Component: {e}")
    import traceback
    traceback.print_exc()

print("Importing Ship...")
try:
    from game.simulation.entities.ship import Ship
    print("Ship imported.")
except ImportError as e:
    print(f"Failed to import Ship: {e}")
    import traceback
    traceback.print_exc()

print("Importing Stats Config...")
try:
    from ui.builder.stats_config import get_crew_required
    print("Stats Config imported.")
except ImportError as e:
    print(f"Failed to import Stats Config: {e}")
    import traceback
    traceback.print_exc()
