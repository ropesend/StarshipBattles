# Sweep Report: UI Screens and Panels Legacy Review

**Shard:** `game/ui/screens/`, `game/ui/panels/`
**Date:** 2026-02-13
**Reviewer:** Claude Code Sweep Agent

---

## Executive Summary

This report documents the findings from an exhaustive review of the `game/ui/screens/` and `game/ui/panels/` directories for legacy system holdovers, deprecated patterns, dead code paths, and incomplete migrations.

**Total Files Scanned:** 99 Python files (75 in screens/, 24 in panels/)

**Findings by Severity:**
- CRITICAL: 0
- MAJOR: 1
- MINOR: 3
- INFO: 6

The codebase shows excellent migration hygiene overall. Multiple project references (PROJ-40, PROJ-43, PROJ-44, PROJ-63, PROJ-66, PROJ-67, PROJ-69, PROJ-76, PROJ-86, PROJ-88, PROJ-89, etc.) indicate completed refactoring work with clean patterns now in place.

---

## Findings

### MAJOR-001: Legacy Modifier Editor Panel

**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\modifier_editor.py`
**Lines:** 1-8
**Severity:** MAJOR
**Phase:** Incomplete Migrations

**Description:**
The file explicitly labels itself as "Legacy modifier editor panel" with a recommendation to "Consider migration to ModifierLogic for new code."

```python
"""Legacy modifier editor panel for the ship builder.

PROJ-43: Now uses ComponentService for modifier registry access instead of
direct MODIFIER_REGISTRY import.

Note: This file contains legacy modifier editing functionality.
Consider migration to ModifierLogic for new code.
"""
```

**Analysis:**
The module is still in active use (197 lines) but is explicitly marked as legacy. It has already been updated with PROJ-43 dependency injection patterns (using ComponentService), but the overall class structure is considered legacy. The docstring recommends using `ModifierLogic` for new code.

**Recommendation:**
Create a ticket to evaluate whether `ModifierEditorPanel` should be:
1. Fully migrated to use `ModifierLogic` exclusively
2. Refactored or consolidated with other modifier systems
3. Left as-is with the legacy label removed if it's actually the intended implementation

---

### MINOR-001: Legacy Single-Selection Fields Maintained for Multi-Select

**File:** `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py`
**Lines:** 328-335
**Severity:** MINOR
**Phase:** Compatibility Shims & Wrappers

**Description:**
The code maintains "legacy single-selection fields" alongside the new multi-select system:

```python
# Update legacy single-selection fields
if len(self.selected_indices) == 1:
    sole_idx = next(iter(self.selected_indices))
    self.selected_index = sole_idx
    self.selected_source = self.filtered_sources[sole_idx]
else:
    self.selected_index = -1
    self.selected_source = None
```

**Analysis:**
This is a backward compatibility pattern maintaining `selected_index` and `selected_source` (single-item) alongside the new `selected_indices` (set-based multi-select). The comment explicitly calls these "legacy" fields.

**Recommendation:**
Verify if any external code depends on `selected_index`/`selected_source`. If all consumers have migrated to `get_selected_sources()`, these fields can be removed.

---

### MINOR-002: Legacy API Reference in Fleet Report

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py`
**Lines:** 956-969
**Severity:** MINOR
**Phase:** Compatibility Shims & Wrappers

**Description:**
A method is marked as "legacy API":

```python
def _on_remove_ship(self, ship):
    """Handle remove single ship from fleet (legacy API)."""
    if not self.empire:
        # No empire, just remove ship without creating new fleet
        if self.fleet.remove_ship(ship):
            self._post_removal_refresh()
        return
    ...
```

**Analysis:**
The method handles single-ship removal (legacy) vs. the newer `_on_remove_selected_ships()` which handles multi-select. The single-ship version is called from `ShipDetailPanel.on_remove_ship` callback, meaning it's still in the UI flow.

**Recommendation:**
This appears to be intentional dual-mode support (single removal from detail panel, multi-removal from selection). If both modes are intended, remove the "legacy API" label. If single-ship removal should be deprecated, route through multi-select.

---

### MINOR-003: Backward Compatibility Property Access

**File:** `C:\Dev\Starship Battles\game\ui\screens\test_lab\screen.py`
**Lines:** 249-252
**Severity:** MINOR
**Phase:** Compatibility Shims & Wrappers

**Description:**
A property is documented as existing for backward compatibility:

```python
@property
def _components_cache(self):
    """Access component cache from data extractor for backward compatibility."""
    return self._data_extractor._components_cache
```

**Analysis:**
This is a pass-through property to maintain backward compatibility with code that expects `_components_cache` to exist on the screen object.

**Recommendation:**
Search for usages of `screen._components_cache` and migrate them to use `screen._data_extractor.load_component()` or equivalent public API. Then remove this property.

---

### INFO-001: Singleton Pattern Usage (Acceptable)

**Files:** Multiple files
**Severity:** INFO
**Phase:** Obsolete Patterns

**Description:**
Multiple files use `.instance()` singleton accessors:
- `ShipThemeManager.instance()` - 6 usages
- `StrategyMetadataService.instance()` - 8 usages
- `ScreenshotManager.instance()` - 4 usages
- `AssetManager.instance()` - 2 usages
- `SpriteManager.instance()` - 1 usage

**Analysis:**
These are service-layer singletons that manage shared resources (themes, metadata, assets, screenshots). Per project conventions documented in PROJ-40 and PROJ-43, these singletons are acceptable patterns for true global services. The project migration notes indicate these are intentional design choices, not legacy holdovers.

**Recommendation:**
No action required. These are appropriate uses of the singleton pattern for resource managers.

---

### INFO-002: Hack Comment for State Passing

**File:** `C:\Dev\Starship Battles\game\ui\screens\battle_screen.py`
**Lines:** 547
**Severity:** INFO
**Phase:** Dead Code Paths

**Description:**
A comment explicitly marks code as a hack:

```python
self.camera.show_overlay = self.ui.show_overlay  # Hack to pass state to renderer
```

**Analysis:**
This comment was identified in the Grep search but the pattern is minimal (single line) and appears to be a known workaround for passing state between UI and camera systems.

**Recommendation:**
Low priority. Consider if a cleaner interface for camera/UI state sharing should be designed, but this is not a legacy system issue.

---

### INFO-003: PROJ-88 Legacy Dispatch Consolidation

**File:** `C:\Dev\Starship Battles\game\ui\screens\strategy_input_handler.py`
**Lines:** 70, 75
**Severity:** INFO
**Phase:** Completed Migrations (Reference Only)

**Description:**
Comments reference consolidation of legacy dispatch:

```python
# PROJ-88: folded from app.py legacy dispatch
```

**Analysis:**
This indicates PROJ-88 successfully consolidated input handling from a legacy `app.py` dispatcher into the dedicated `StrategyInputHandler`. The comments are historical documentation, not active legacy code.

**Recommendation:**
No action required. Comments document completed migration work.

---

### INFO-004: noqa Suppressions

**Files:**
- `strategy_event_router.py:187` - `# noqa: F401` (unused import)
- `workshop_event_router.py:420` - `# noqa: ARG002` (unused argument)

**Severity:** INFO
**Phase:** Dead Code Paths

**Description:**
Two lint suppressions are present:
1. `hex_distance` import marked unused (likely for debugging/future use)
2. `event` argument marked unused in `_handle_right_click`

**Analysis:**
These are minor lint suppressions, not legacy holdovers. The unused import may be intentional for future development or debugging convenience.

**Recommendation:**
Review if `hex_distance` import is needed. If not, remove it along with the noqa comment.

---

### INFO-005: builder_utils Singleton Constants

**File:** `C:\Dev\Starship Battles\game\ui\screens\builder_utils.py`
**Lines:** 54-58
**Severity:** INFO
**Phase:** Obsolete Patterns

**Description:**
Comment labels module-level constants as "Singleton instances":

```python
# Singleton instances for easy import
PANEL_WIDTHS = PanelWidths()
PANEL_HEIGHTS = PanelHeights()
MARGINS = Margins()
```

**Analysis:**
These are frozen dataclasses instantiated at module level for convenient import. The use of "singleton" terminology is informal - these are just module-level constants, which is a standard Python pattern.

**Recommendation:**
Consider renaming the comment to "Module-level constants" for accuracy. Not a legacy issue.

---

### INFO-006: Empty `pass` Statements

**File:** `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py`
**Lines:** 495
**Severity:** INFO
**Phase:** Dead Code Paths

**Description:**
An empty `pass` statement in update loop:

```python
if self.scroll_bar.check_has_moved_recently():
    # Future: update visible rows for virtual scrolling
    pass
```

**Analysis:**
This is a placeholder for future virtual scrolling optimization. The comment explains the intent.

**Recommendation:**
No action required. This is an intentional placeholder, not dead code.

---

## Summary of Patterns Observed

### Clean Patterns Found (No Issues):
1. **PROJ-40 Migration Complete:** LayerType imports from `game.core.constants` are canonical throughout.
2. **PROJ-43 Dependency Injection:** ComponentService injection pattern properly used in modifier_editor.py.
3. **PROJ-86-89 Decomposition:** God classes successfully decomposed (BuildQueueScreen, FleetReportWindow, EmpireBuildQueueWindow all show proper delegation to helper classes).
4. **TYPE_CHECKING Guards:** ShipInstance, Ship, and other domain objects properly guarded with `TYPE_CHECKING` imports.
5. **Ability System:** Uses `comp.has_ability('WeaponAbility')` pattern consistently, not inline type checking.

### Patterns NOT Found (Good Signs):
1. No direct MODIFIER_REGISTRY imports (all via ComponentService)
2. No manual component lookups bypassing registries
3. No inline component stat calculations (all use ability system)
4. No deprecated `hull` attribute access (hull-as-component pattern in use)
5. No TODO/FIXME/HACK markers (except single minor instance)
6. No `if False:` dead code blocks
7. No `# pragma: no cover` exclusions

---

## Conclusion

The `game/ui/screens/` and `game/ui/panels/` directories are in excellent condition with respect to legacy code removal. The one MAJOR finding (`modifier_editor.py` being labeled legacy) requires evaluation to determine if it's truly legacy or simply mislabeled after being updated with modern patterns. The MINOR findings are all documented backward-compatibility measures that should be evaluated for removal once consumers are confirmed migrated.

**Overall Assessment:** CLEAN - Minor cleanup opportunities identified but no systemic legacy holdovers.
