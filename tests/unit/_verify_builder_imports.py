import sys
import os
import pygame

pygame.init()
pygame.display.set_mode((100, 100))

sys.path.append(os.getcwd())

try:
    # Attempt to import the builder submodules (legacy BuilderScreen removed in PROJ-121)
    from game.ui.screens.builder import BuilderLeftPanel, ComponentListItem
    print("Imports successful.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed: {e}")
    sys.exit(1)

print("Verification script passed.")
