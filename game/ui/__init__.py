"""
Game UI Package
Explicitly imports submodules to prevent pytest-xdist race conditions.
"""

# Pre-import all submodules in dependency order
# This ensures consistent initialization regardless of which worker imports first
from game.ui.renderer import sprites, camera, game_renderer
from game.ui.screens import battle_scene, battle_screen, builder_screen
from game.ui.panels import battle_panels, builder_widgets

# Export for convenience (optional but recommended)
__all__ = [
    'sprites', 
    'camera', 
    'game_renderer',
    'battle_scene', 
    'battle_screen', 
    'builder_screen',
    'battle_panels', 
    'builder_widgets'
]
