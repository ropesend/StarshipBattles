# Duplication & Fragmentation Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 125 (101 screens + 24 panels)
- **Total Issues Found:** 10
- **Critical:** 1 | **Major:** 3 | **Minor:** 4 | **Info:** 2

## Findings

#### CRITICAL: Screenshot Toast Notification Pattern Duplicated in 3+ Locations
**ID:** DUP-UI1-001
**Location:** `game/ui/screens/planet_list_window.py:412-424` AND `game/ui/screens/build_queue_screen.py:1055-1068` AND `game/ui/screens/strategy_input_handler.py:868-881`
**Issue:** The `_show_screenshot_toast()` method is implemented nearly identically in three different files. All three create a UIMessageWindow with similar dimensions, positioning (center, y=80), HTML message format, and exception handling. The only differences are:
- Which manager reference they use (self.ui_manager vs self.manager vs self.scene.ui.manager)
- Slight variations in exception types caught
- build_queue_screen.py has extra debug logging

**Impact:**
- Bug risk: If toast appearance needs to change, 3 places must be updated
- Exception handling varies, suggesting copy-paste drift
- ~15 lines duplicated 3x = 45 lines of redundant code

**Recommendation:** Extract to a shared utility function in `game/ui/utils/screenshot_utils.py`:
```python
def show_screenshot_toast(screen_width: int, manager, message: str = "Screenshot saved!"):
    """Show toast notification for screenshot feedback."""
```

**Effort:** Simple

---

#### MAJOR: Column Manager Fragmentation Across Windows
**ID:** DUP-UI1-002
**Location:** `game/ui/screens/column_manager.py` AND `game/ui/screens/planet_list_columns.py` AND `game/ui/screens/empire_build_queue_filter_manager.py`
**Issue:** Three separate column management implementations exist:
1. `column_manager.py` - ColumnManager class for fleet reports (234 lines)
2. `planet_list_columns.py` - ColumnManager class for planet list (different implementation)
3. `empire_build_queue_filter_manager.py` - Inline column visibility logic (toggle_column_visibility, get_visible_columns)

All three implement:
- Column visibility toggling
- Getting visible columns
- Column reordering (some)
- Deep copying column configs

**Impact:**
- Different APIs for the same concept
- Some windows use one approach, others use another
- empire_build_queue_window.py imports from planet_list_columns.py but also has its own logic

**Recommendation:** Consolidate into a single `BaseColumnManager` class that can be specialized per window type. The fleet report's ColumnManager is the most complete and could serve as the base.

**Effort:** Medium

---

#### MAJOR: Filter State Management Pattern Repeated
**ID:** DUP-UI1-003
**Location:** `game/ui/screens/fleet_report_filters.py` AND `game/ui/screens/planet_list_filters.py` AND `game/ui/screens/empire_build_queue_filter_manager.py`
**Issue:** Each window implements its own filtering infrastructure:
- `fleet_report_filters.py`: filter_ships(), sort_ships(), calculate_fleet_stats()
- `planet_list_filters.py`: filter_planets(), sort_planets(), get_column_value()
- `empire_build_queue_filter_manager.py`: BuildQueueFilterManager class with filter_sources(), sort_sources()

Common patterns in all:
- Filter state dicts (show_X: bool)
- AND-logic filter composition
- Sort key extraction with column ID matching
- Special handling for numeric vs string columns

**Impact:**
- ~200 lines of structurally similar filtering logic repeated 3x
- Inconsistent sort key implementations
- Adding a new filter pattern requires updating each separately

**Recommendation:** Create a `BaseFilterManager` abstract class with:
- Generic filter predicate composition
- Pluggable sort key extractors
- Common filter state management

**Effort:** Medium

---

#### MAJOR: Compact Number Formatting Logic Isolated
**ID:** DUP-UI1-004
**Location:** `game/ui/panels/planet_report_panel.py:303-310` AND `game/ui/screens/planet_list_filters.py:297-308`
**Issue:** Number formatting with K/M suffixes is implemented in at least 2 places:

planet_report_panel.py:
```python
def _format_compact_number(self, value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.0f}k"
    else:
        return str(int(value))
```

planet_list_filters.py (get_resource_str):
```python
if quantity >= 1000000:
    quantity_str = f"{quantity/1000000:.1f}M"
elif quantity >= 1000:
    quantity_str = f"{quantity/1000:.0f}k"
else:
    quantity_str = str(quantity)
```

**Impact:** Low risk but indicates missing utility function. Format inconsistencies could emerge.

**Recommendation:** Extract to `game/ui/utils/format_utils.py` as a shared utility.

**Effort:** Simple

---

#### MINOR: RaceThemeGallery Not Using BaseGallery
**ID:** DUP-UI1-005
**Location:** `game/ui/panels/race_theme_gallery.py` vs `game/ui/panels/base_gallery.py`
**Issue:** RacePortraitGallery and RaceFlagGallery both extend BaseGallery (good consolidation done in PROJ-108), but RaceThemeGallery does not. It implements similar patterns:
- `_sanitize_object_id()` method (identical to BaseGallery)
- `handle_button_click()` method (same structure)
- `set_from_config()` method (same pattern)
- `_discover_themes()` with caching (similar to `_discover_assets()`)

**Impact:** RaceThemeGallery has ~200 lines that partially duplicate BaseGallery patterns. Less severe because theme gallery has different preview behavior (list vs grid).

**Recommendation:** Either extend BaseGallery with theme-specific overrides, or document why it differs. The `_sanitize_object_id()` method should definitely be extracted as it's identical.

**Effort:** Simple

---

#### MINOR: Report Panel Pattern Similarity
**ID:** DUP-UI1-006
**Location:** `game/ui/panels/planet_report_panel.py` AND `game/ui/panels/design_report_panel.py` AND `game/ui/panels/ship_detail_panel.py`
**Issue:** Three "report panel" classes share structural patterns:
- All have `__init__` with manager, rect, container parameters
- All create a UIPanel as self.panel
- All have `kill()` methods with similar cleanup patterns
- All have update methods for displaying entity data

However, they don't share a common base class.

**Impact:** Low immediate risk. Future enhancements to one panel may not propagate to others.

**Recommendation:** Consider a `BaseReportPanel` ABC if new report panels are planned. Current duplication is tolerable since each panel has domain-specific rendering.

**Effort:** Medium (would require refactoring existing panels)

---

#### MINOR: Portrait/Image Loading Logic Scattered
**ID:** DUP-UI1-007
**Location:** `game/ui/panels/design_report_panel.py:168-266` AND `game/ui/panels/ship_detail_panel.py:125-160` AND `game/ui/screens/race_asset_loader.py`
**Issue:** Portrait/ship image loading with fallback placeholder generation appears in multiple files:
- design_report_panel._update_portrait() - 100 lines with path resolution, scaling, placeholder generation
- ship_detail_panel._get_scaled_image() - 35 lines with scaling and placeholder
- race_asset_loader.py - Centralized but not used by all panels

The design_report_panel and ship_detail_panel both generate gradient-based placeholder images with ship name/class text overlay.

**Impact:** Placeholder styling could diverge. Path resolution logic is duplicated.

**Recommendation:** Extend ShipThemeManager or create PortraitHelper utility to handle fallback generation consistently.

**Effort:** Simple

---

#### MINOR: Sidebar Builder Pattern Could Be Generalized
**ID:** DUP-UI1-008
**Location:** `game/ui/screens/planet_list_sidebar.py` AND `game/ui/screens/empire_build_queue_window.py:634-784`
**Issue:** Both implement sidebar building with:
- Column toggle buttons with [x]/[ ] prefix
- Filter toggle buttons with similar patterns
- UIScrollingContainer for tall content
- Apply button at bottom

The planet_list_sidebar.py is extracted (good), but empire_build_queue_window.py has inline `_build_sidebar_column_toggles()` and `_build_sidebar_filters()` methods (~150 lines).

**Impact:** Low. Different enough that full extraction may not be worthwhile.

**Recommendation:** If more windows need sidebars, extract a SidebarBuilder utility. Current state is acceptable.

**Effort:** Medium

---

#### INFO: Well-Refactored Gallery System
**ID:** DUP-UI1-009
**Location:** `game/ui/panels/base_gallery.py` AND `game/ui/panels/race_portrait_gallery.py` AND `game/ui/panels/race_flag_gallery.py`
**Issue:** POSITIVE FINDING - BaseGallery successfully extracts common gallery logic (~264 lines), allowing RacePortraitGallery (152 lines) and RaceFlagGallery (163 lines) to focus on asset-specific differences. This is a good example of DRY application.

**Impact:** None - this is a model to follow.

**Recommendation:** Document as pattern for future gallery-style UI components.

**Effort:** N/A

---

#### INFO: DesignStatsPanel Successful Extraction
**ID:** DUP-UI1-010
**Location:** `game/ui/panels/design_stats_panel.py`
**Issue:** POSITIVE FINDING - DesignStatsPanel (452 lines) successfully consolidates ship stats display logic that was previously duplicated between BuilderRightPanel and BuildQueueScreen. The StatRow helper class provides clean abstraction for label/value/unit rows.

**Impact:** None - good consolidation already done.

**Recommendation:** Use this pattern for other stat display panels.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-UI1-001 (Critical)**: Screenshot toast notification duplicated 3x - Extract to shared utility. Quick win with immediate benefit.

2. **DUP-UI1-002 (Major)**: Column Manager fragmentation - Three different implementations for the same concept. Should consolidate to reduce confusion.

3. **DUP-UI1-003 (Major)**: Filter state management repeated - Similar filtering infrastructure in 3 windows. Common base class would reduce code and ensure consistency.

4. **DUP-UI1-004 (Major)**: Compact number formatting - Simple extraction to utility function. Prevents format drift.

5. **DUP-UI1-005 (Minor)**: RaceThemeGallery not using BaseGallery - At minimum, extract `_sanitize_object_id()` as shared utility.
