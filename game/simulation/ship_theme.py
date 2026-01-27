"""DEPRECATED: ShipThemeManager moved to game.ui.assets.ship_theme_manager.

Import from game.ui.assets instead. This re-export maintained for backward compatibility.
Will be removed in a future version.
"""
import warnings

from game.ui.assets.ship_theme_manager import ShipThemeManager

# Emit deprecation warning on import
warnings.warn(
    "Importing ShipThemeManager from game.simulation.ship_theme is deprecated. "
    "Use 'from game.ui.assets import ShipThemeManager' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['ShipThemeManager']
