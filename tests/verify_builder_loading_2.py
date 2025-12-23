
import os
import sys
import pygame
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Pygame Display
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1920, 1080))

# Import Builder
try:
    from builder_gui import BuilderSceneGUI
    print("Import successful")
except Exception as e:
    print(f"Import Failed: {e}")
    sys.exit(1)

# Initialize
try:
    def callback(x): pass
    gui = BuilderSceneGUI(1920, 1080, callback)
    print("BuilderSceneGUI instantiated")
    
    if hasattr(gui, 'layer_panel'):
        print("LayerPanel exists")
    else:
        print("LayerPanel missing")
        sys.exit(1)
        
    print("Verification Passed")

except Exception as e:
    print(f"Runtime Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
