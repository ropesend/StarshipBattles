"""
Game UI Package
Explicitly imports submodules to prevent pytest-xdist race conditions.
This ensures consistent initialization regardless of which worker imports first.

Note: workshop_screen is NOT eagerly imported here because it has module-level
side effects (Tkinter initialization) that can cause test isolation issues.
The original circular dependency concern (AR-006) has been resolved through
lazy imports in ui.builder (see left_panel.py, right_panel.py, detail_panel.py).
"""

# Pre-import submodules in dependency order
# Exclude workshop_screen due to module-level Tkinter initialization side effects
from game.ui.renderer import sprites, camera, game_renderer
from game.ui.screens import battle_scene, battle_screen
from game.ui.panels import battle_panels, builder_widgets

# Export for convenience (optional but recommended)
__all__ = [
    'sprites',
    'camera',
    'game_renderer',
    'battle_scene',
    'battle_screen',
    'battle_panels',
    'builder_widgets'
]
