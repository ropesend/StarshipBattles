"""Canonical ship-class display-name set used by visual themes.

This module is the single source of truth for the set of ship classes
that participate in the `assets/ShipThemes/<Theme>/theme.json` schema.
The :data:`SHIP_CLASSES_WITH_VISUAL_THEMES` frozenset enumerates exactly
the 19 display-form ship-class keys that every theme is expected to
declare, and that :class:`game.ui.assets.ship_theme_manager.ShipThemeManager`
validates against at discovery time.

Added in PROJ-314 (Phase 1) to eliminate string-literal drift between
loader code, theme JSONs, and ad-hoc tests.
"""
from __future__ import annotations


SHIP_CLASSES_WITH_VISUAL_THEMES: frozenset[str] = frozenset({
    # Capital ships (11)
    "Escort",
    "Frigate",
    "Destroyer",
    "Light Cruiser",
    "Cruiser",
    "Heavy Cruiser",
    "Battle Cruiser",
    "Battleship",
    "Dreadnought",
    "Superdreadnought",
    "Monitor",
    # Fighters (4)
    "Fighter (Small)",
    "Fighter (Medium)",
    "Fighter (Large)",
    "Fighter (Heavy)",
    # Satellites (4)
    "Satellite (Small)",
    "Satellite (Medium)",
    "Satellite (Large)",
    "Satellite (Heavy)",
})
"""Canonical 19-entry set of display-form ship-class names that every
visual theme is expected to declare in `theme.json`'s `assets:` block.

Used by:

* :class:`game.ui.assets.ship_theme_manager.ShipThemeManager` for
  schema validation at theme discovery.
* `Tools/regenerate_ship_portraits/audit.py` for coverage reporting.
* Tests pinning the loader contract.
"""
