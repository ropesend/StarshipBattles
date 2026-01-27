# Regression Report

## Summary
| Metric | Count |
|--------|-------|
| Total Regressions Found | 5 |
| Critical | 1 (not fixed from original) |
| Major | 3 |
| Minor | 1 |

## Regression Findings

### REG-01: Builder/Workshop Terminology Not Fully Unified
**Related Original Finding:** NC-02
**Severity:** Major
**Location:**
- `game/ui/screens/builder_utils.py`
- `game/ui/screens/builder_selection.py`
- `game/ui/panels/builder_widgets.py`
- `game/ui/screens/builder/` (directory with 21 files)

**Issue:** The original review recommended renaming builder_* files to workshop_* and renaming the builder/ directory to workshop/. However, all builder_* files and the builder/ directory still exist with original names. While workshop_* files were created in parallel, the old builder terminology was not removed, creating a dual-terminology system.

**Evidence:**
- `builder_utils.py` exists (modified 2026-01-23)
- `builder_selection.py` exists (modified 2026-01-17)
- `builder_widgets.py` exists (modified 2026-01-24)
- `builder/` directory exists with 21 Python files
- Both old and new terminology exists simultaneously

**Recommendation:** Complete the migration by deleting/renaming builder_* files and updating all imports to use workshop_* equivalents.

**Effort:** Medium

---

### REG-02: Workshop Files Import From Builder Directory
**Related Original Finding:** NC-02
**Severity:** Major
**Location:** `game/ui/screens/workshop_screen.py:24-36`

**Issue:** The new workshop_screen.py imports components from the old builder/ directory, creating inconsistency where "Workshop" UI imports from "Builder" directory.

**Evidence:**
```python
from game.ui.panels.builder_widgets import ModifierEditorPanel
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from game.ui.screens.builder_utils import PANEL_WIDTHS, PANEL_HEIGHTS, MARGINS, BuilderEvents...
from game.ui.screens.builder_selection import process_selection_change, get_primary_selection
```

**Recommendation:** Update imports to use workshop terminology after builder files are renamed.

**Effort:** Simple

---

### REG-03: Builder Method Names in Main Application
**Related Original Finding:** NC-02
**Severity:** Minor
**Location:** `game/app.py:162-179,682`

**Issue:** Main application uses builder-related method names instead of workshop terminology.

**Evidence:**
```python
@profile_action("App: Start Builder")
def start_builder(self, return_to=None, context=None):
context.on_return = self.on_builder_return
self.builder_scene = DesignWorkshopGUI(...)
def on_builder_return(self, custom_ship=None):
self.start_builder(return_to=STRATEGY, context=context)
```

**Recommendation:** Rename methods to use workshop/design terminology: `start_workshop()`, `on_workshop_return()`, `workshop_scene`.

**Effort:** Simple

---

### REG-04: Method Alias for Ship Stats Not Removed
**Related Original Finding:** NC-10
**Severity:** Minor
**Location:** `game/simulation/systems/stats.py:300`

**Issue:** The `to_hit_profile` alias for `total_defense_score` was kept as a "legacy/alias for UI until fully refactored". Original review recommended removal in Phase 2.

**Evidence:**
```python
# Legacy/Alias for UI until fully refactored
ship.to_hit_profile = ship.total_defense_score
```

**Recommendation:** Remove the alias and update UI code to use `total_defense_score` directly.

**Effort:** Simple

---

### REG-05: Duplicate BattleScene Class Not Removed
**Related Original Finding:** NC-01 (CRITICAL)
**Severity:** Critical (Not Fixed)
**Location:**
- `game/ui/screens/battle.py:15`
- `game/ui/screens/battle_scene.py:29`

**Issue:** Original review marked this as CRITICAL and recommended deleting `battle.py`. Both files still exist with duplicate `BattleScene` class definitions.

**Evidence:**
- `battle.py` exists (modified 2026-01-26, 9340 bytes)
- `battle_scene.py` exists (modified 2026-01-25, 16562 bytes)
- Both define `class BattleScene`

**Recommendation:** Delete `game/ui/screens/battle.py`. The modern version in `battle_scene.py` uses `BattleService` while the legacy version uses `BattleEngine`.

**Effort:** Simple

---

## Areas Checked Without Regressions

- **Singleton Pattern Aliases (NC-09):** No `get_instance()` aliases found. Singletons correctly use `instance()` pattern.
- **Fleet Warp Method Aliases (NC-10):** `has_resources_for_warp()` is correct. Old `has_energy_for_warp()` not found.
- **PathSegment Naming (NC-10):** Uses `end` attribute correctly, not old `hex` alias.
- **Shim Files Cleanup:** Successfully removed:
  - `ship_builder_service.py` - REMOVED
  - `builder_screen.py` - REMOVED
  - `builder_viewmodel.py` - REMOVED
  - `builder_data_loader.py` - REMOVED
  - `builder_event_router.py` - REMOVED
- **Intentional Distinctions:** Battle vs Combat, Fleet vs Team, Turn vs Tick terminology consistent.

---

*Report generated: 2026-01-27*
*Validation Agent: Regression Hunter*
