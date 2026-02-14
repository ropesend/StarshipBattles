# Duplication & Fragmentation Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 119 (99 in game/ui/screens/, 20 in game/ui/panels/)
- **Total Issues Found:** 10
- **Critical:** 1 | **Major:** 4 | **Minor:** 4 | **Info:** 1

## Findings

#### CRITICAL: Duplicate ColumnManager Classes
**ID:** DUP-UI1-001
**Location:** `game/ui/screens/column_manager.py:49-234` AND `game/ui/screens/planet_list_columns.py:11-201`
**Issue:** Two completely separate `ColumnManager` classes exist with overlapping functionality:
- `column_manager.py` - Generic column manager for FleetReportWindow with value extraction
- `planet_list_columns.py` - Column manager for PlanetListWindow with header button UI

Both have:
- `get_visible_columns()` method with identical implementation
- Column visibility toggling (`toggle_column` vs `toggle_visibility`)
- Column reordering via swap methods

Additionally, `empire_build_queue_filter_manager.py` has a third implementation of `get_visible_columns()` and `toggle_column_visibility()`.

**Impact:** Three separate implementations of the same column management pattern means:
- Bug fixes must be applied to all three locations
- Inconsistent APIs (`toggle_column` vs `toggle_visibility` vs `toggle_column_visibility`)
- New features (like column persistence) would need triple implementation

**Recommendation:** Create a single `BaseColumnManager` in `game/ui/shared/` with:
- Core methods: `get_visible_columns()`, `toggle_visibility()`, `swap_columns()`
- Have all three locations inherit/compose from it
- Keep specific implementations (UI header buttons, value extraction) in subclasses

**Effort:** Medium - Requires refactoring 3 classes and updating their usages

---

#### MAJOR: Duplicate draw_stat_bar Implementations
**ID:** DUP-UI1-002
**Location:** `game/ui/panels/battle_panels.py:26-28` AND `game/ui/panels/ship_stats_renderer.py:30-44`
**Issue:** Two implementations of progress bar drawing:
- `BattlePanel.draw_stat_bar()` - Instance method that delegates to the module function
- `ship_stats_renderer.draw_stat_bar()` - Standalone function with the actual implementation

The BattlePanel class wraps the function call unnecessarily. While the module function is the authoritative version, the wrapper adds indirection.

**Impact:** Low maintenance risk (wrapper exists), but adds unnecessary indirection and cognitive overhead.

**Recommendation:** Remove the wrapper method from `BattlePanel` and have all callers use the module function directly.

**Effort:** Simple - Delete wrapper method, update 0-2 call sites within BattlePanel

---

#### MAJOR: Duplicate HP Color Calculation Logic
**ID:** DUP-UI1-003
**Location:** `game/ui/panels/ship_stats_renderer.py:77-93` AND `game/ui/panels/ship_detail_panel.py:25-46` AND `game/ui/panels/battle_panels.py:405`
**Issue:** HP percentage to color mapping appears in three places:
1. `get_hp_bar_color(hp_pct, is_active)` in ship_stats_renderer.py
2. `get_damage_color(hp_percentage)` in ship_detail_panel.py
3. Inline ternary in battle_panels.py line 405

All use similar thresholds (0.5, 0.2/0.25) and similar color schemes (green/yellow/red) but with slightly different values and logic.

**Impact:**
- Visual inconsistency between panels (different yellow cutoff points)
- Changes to health visualization require multiple updates
- Potential for visual bugs when one location is updated and others aren't

**Recommendation:** Consolidate into single `get_hp_color()` function in `ship_stats_renderer.py` and use it everywhere.

**Effort:** Simple - Extract common function, replace inline logic

---

#### MAJOR: Duplicate Number Magnitude Formatting
**ID:** DUP-UI1-004
**Location:** Multiple files with k/M suffix formatting:
- `game/ui/screens/strategy_detail_fmt.py:103-114` (population)
- `game/ui/screens/empire_build_queue_formatter.py:177-181` (resource costs)
- `game/ui/screens/planet_list_filters.py:301-305` (resource quantities)
- `game/ui/panels/planet_report_panel.py:306-309` (production rates)

**Issue:** Each location implements the same pattern:
```python
if value >= 1_000_000:
    return f"{value / 1_000_000:.1f}M"
elif value >= 1_000:
    return f"{value / 1_000:.0f}k"
else:
    return str(int(value))
```

**Impact:**
- Inconsistent thresholds (some use 1000, some 1_000)
- Inconsistent precision (some use `.1f`, some `.0f`)
- Any changes to formatting rules need 4+ updates

**Recommendation:** Create `game/ui/utils/number_format.py` with:
```python
def format_quantity(value: float, precision: int = 1) -> str:
    """Format large numbers with k/M suffixes."""
```

**Effort:** Simple - Extract function, update call sites

---

#### MAJOR: RaceThemeGallery Does Not Extend BaseGallery
**ID:** DUP-UI1-005
**Location:** `game/ui/panels/race_theme_gallery.py:22-202` vs `game/ui/panels/base_gallery.py:26-264`
**Issue:** `RaceFlagGallery` and `RacePortraitGallery` both extend `BaseGallery`, but `RaceThemeGallery` does not, despite having near-identical structure:
- Same `__init__` signature pattern
- Same `_create_content()` pattern
- Same `_sanitize_object_id()` method (duplicated)
- Same `handle_button_click()` pattern
- Same `set_from_config()` pattern

The only difference is that RaceThemeGallery uses a list of buttons instead of a grid of thumbnail images.

**Impact:**
- `_sanitize_object_id()` is duplicated verbatim (lines 157-159 in race_theme_gallery.py)
- Violates DRY when extending gallery features
- Future gallery types will need to decide whether to duplicate or refactor

**Recommendation:** Refactor `BaseGallery` to support both grid and list layouts, then have `RaceThemeGallery` extend it.

**Effort:** Medium - Requires BaseGallery extension and RaceThemeGallery rewrite

---

#### MINOR: Duplicate Portrait Loading Logic
**ID:** DUP-UI1-006
**Location:** `game/ui/screens/design_image_helper.py:52-105` AND `game/ui/panels/design_report_panel.py:168-266`
**Issue:** Both files implement fallback portrait loading with gradient placeholder generation:
- Both try multiple file paths for portraits
- Both generate placeholder gradients with class initials on failure
- Both have type-based color mappings

The `design_image_helper.py` version is cleaner (function-based, cached), while `design_report_panel.py` has a larger, embedded version.

**Impact:** Minor - design_report_panel could use the helper but implements its own version.

**Recommendation:** Have `design_report_panel._update_portrait()` delegate to `design_image_helper.load_portrait_thumbnail()`.

**Effort:** Simple - Update import and delegate

---

#### MINOR: World-to-Screen Coordinate Transforms
**ID:** DUP-UI1-007
**Location:** 14 files containing world_to_screen/screen_to_world transforms:
- `game/ui/screens/formation/renderer.py:70-100`
- `game/ui/screens/strategy_renderer.py` (via camera)
- `game/ui/renderer/camera.py` (canonical)
- Plus 11 other files

**Issue:** The canonical `Camera` class in `game/ui/renderer/camera.py` provides world_to_screen and screen_to_world methods. However:
- `FormationRenderer` has its own inline coordinate transform methods
- Some files access `camera.world_to_screen()` directly, others call local helpers

**Impact:** Low - FormationRenderer has different requirements (no camera object, just canvas-local transforms). This is likely intentional.

**Recommendation:** Document that FormationRenderer intentionally uses local transforms (no Camera dependency for simplicity).

**Effort:** None - Add clarifying comment only

---

#### MINOR: Filter/Sort Pattern Duplication
**ID:** DUP-UI1-008
**Location:**
- `game/ui/screens/fleet_report_filters.py` (filter_ships, sort_ships)
- `game/ui/screens/planet_list_filters.py` (filter_planets, sort_planets)
- `game/ui/screens/empire_build_queue_filter_manager.py` (filter_sources, sort_sources)

**Issue:** Three separate filter/sort implementations following the same pattern:
1. Filter with multiple criteria (AND logic)
2. Sort by column with type-aware key extraction
3. Support for ascending/descending

Each is entity-specific (ships, planets, build sources) so some divergence is expected.

**Impact:** Low - Different entity types justify separate implementations, but the sorting logic is very similar.

**Recommendation:** Consider a generic `create_sort_key_extractor()` utility that handles common column value extraction patterns.

**Effort:** Medium - Would require careful abstraction

---

#### MINOR: Event Router Pattern Similarity
**ID:** DUP-UI1-009
**Location:** `game/ui/screens/workshop_event_router.py` AND `game/ui/screens/strategy_event_router.py`
**Issue:** Both event routers follow identical patterns:
- `__init__(self, ui/gui)` storing parent reference
- `handle_event()` / `route_event()` as main entry point
- `_handle_button_pressed()` for UI button events
- `_handle_keydown()` for keyboard events

However, the actual event handling is screen-specific, so this is more pattern similarity than code duplication.

**Impact:** None - Pattern consistency is good; no actual code to consolidate.

**Recommendation:** Document the event router pattern in architecture docs for future implementers.

**Effort:** None - Pattern is appropriate

---

#### INFO: Previously Resolved Duplication (DUP-UI1-002)
**ID:** DUP-UI1-010
**Location:** `game/ui/screens/test_lab/formatting_utils.py`
**Issue:** File header mentions "DUP-UI1-002 resolution" - this indicates prior duplication was identified and consolidated into this shared module.

**Impact:** Positive - Shows the team actively consolidates duplication.

**Recommendation:** None - This is a good example of previous cleanup work.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-UI1-001 (CRITICAL)** - Three ColumnManager implementations need consolidation to prevent divergent bug fixes and inconsistent APIs.

2. **DUP-UI1-003 (MAJOR)** - HP color calculation is duplicated with slight variations, causing potential visual inconsistency.

3. **DUP-UI1-004 (MAJOR)** - Number formatting (k/M suffixes) is implemented in 4+ locations with inconsistent precision.

4. **DUP-UI1-005 (MAJOR)** - RaceThemeGallery should extend BaseGallery like its sibling galleries.

5. **DUP-UI1-002 (MAJOR)** - draw_stat_bar wrapper method adds unnecessary indirection.
