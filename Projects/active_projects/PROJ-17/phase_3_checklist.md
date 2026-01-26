# Phase 3: Move ShipThemeManager to UI [Medium Risk]

**Objective:** Relocate ShipThemeManager from simulation to UI layer where pygame usage is appropriate.

**Status:** Not Started

**Depends on:** Phase 1 complete (can run parallel to Phase 2)

**Tests to run after phase:** `pytest tests/unit/ui/ tests/unit/entities/test_ship_theme_logic.py -v`

---

## Task 3.1: Create UI Assets Directory [Simple]

**Directory:** `game/ui/assets/`

- [ ] Create directory: `mkdir game/ui/assets`
- [ ] Create `game/ui/assets/__init__.py` with content:

```python
"""UI asset management - images, themes, sprites."""
from .ship_theme_manager import ShipThemeManager

__all__ = ['ShipThemeManager']
```

**Notes:**

---

## Task 3.2: Move ShipThemeManager [Medium]

**From:** `game/simulation/ship_theme.py`
**To:** `game/ui/assets/ship_theme_manager.py`

- [ ] Copy entire file: `cp game/simulation/ship_theme.py game/ui/assets/ship_theme_manager.py`
- [ ] Verify the copy succeeded by checking file exists
- [ ] Review imports in new file - should be fine as-is (uses pygame, which is allowed in UI)

**Notes:**

---

## Task 3.3: Create Backward-Compatible Re-export [Simple]

**File:** `game/simulation/ship_theme.py`

- [ ] Replace entire content with:

```python
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
```

- [ ] Save file

**Notes:**

---

## Task 3.4: Update Direct Importers [Medium]

Update imports from `game.simulation.ship_theme` to `game.ui.assets.ship_theme_manager`:

### UI Renderer
- [ ] `game/ui/renderer/game_renderer.py` - Update ShipThemeManager import

### UI Screens
- [ ] `game/ui/screens/builder_screen.py` - Update ShipThemeManager import
- [ ] `game/ui/screens/workshop_screen.py` - Update ShipThemeManager import
- [ ] `game/ui/screens/race_setup_screen.py` - Update ShipThemeManager import
- [ ] `game/ui/screens/race_browser_dialog.py` - Update ShipThemeManager import
- [ ] `game/ui/screens/fleet_report_window.py` - Update ShipThemeManager import

### UI Panels
- [ ] `game/ui/panels/ship_detail_panel.py` - Update ShipThemeManager import
- [ ] `game/ui/panels/race_theme_gallery.py` - Update ShipThemeManager import

### Tests (if directly importing)
- [ ] Check `conftest.py` for ShipThemeManager imports
- [ ] Check test files in `tests/unit/entities/test_ship_theme_logic.py`

**Import pattern to use:**
```python
# Old:
from game.simulation.ship_theme import ShipThemeManager

# New:
from game.ui.assets import ShipThemeManager
```

**Notes:**

---

## Phase 3 Verification

After completing all tasks:

- [ ] Run: `pytest tests/unit/ui/ -v`
- [ ] Run: `pytest tests/unit/entities/test_ship_theme_logic.py -v`
- [ ] Launch game and verify ship images display in builder
- [ ] Launch game and verify ship images display in battle
- [ ] Verify ShipThemeManager is in UI: `ls game/ui/assets/ship_theme_manager.py`
- [ ] Verify re-export exists: `grep -n "from game.ui.assets" game/simulation/ship_theme.py`

**Phase complete when all boxes checked.**
