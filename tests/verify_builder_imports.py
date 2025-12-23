import sys
import os
import pygame

pygame.init()
pygame.display.set_mode((100, 100))

sys.path.append(os.getcwd())

try:
    # Attempt to import the modified modules
    from ui.builder import BuilderLeftPanel, ComponentListItem
    from builder_gui import BuilderSceneGUI
    print("Imports successful.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed: {e}")
    sys.exit(1)
    
print("Verification script passed.")
