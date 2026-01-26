"""
Game UI Package
Explicitly imports submodules to prevent pytest-xdist race conditions.
Note: workshop_screen is NOT eagerly imported here to avoid circular dependency
with ui.builder package.
"""

# Pre-import submodules in dependency order (excluding workshop_screen due to circular import)
# This ensures consistent initialization regardless of which worker imports first
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
