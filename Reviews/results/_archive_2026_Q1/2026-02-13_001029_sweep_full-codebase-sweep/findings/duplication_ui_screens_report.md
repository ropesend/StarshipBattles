# Duplication & Fragmentation Report: UI Screens and Panels

**Sweep Date:** 2026-02-13
**Scope:** `game/ui/screens/` and `game/ui/panels/`
**Agent:** Duplication & Fragmentation Sweep

---

## Executive Summary

This report identifies code duplication, near-duplicates, and fragmented implementations across the UI layer. The codebase shows evidence of **prior refactoring efforts** (PROJ-108, PROJ-12, DUP-UI1-002, DUP-UI1-005) that have already consolidated several patterns. However, remaining opportunities exist for further consolidation.

**Overall Assessment:** The UI layer is reasonably well-factored with some remaining MINOR and INFO-level issues.

---

## Findings

### DUP-UI-001 [INFO] - Portrait/Image Loading with Placeholder Generation

**Files:**
- `game/ui/panels/design_report_panel.py` (lines 168-264)
- `game/ui/panels/ship_detail_panel.py` (lines 125-160)
- `game/ui/screens/design_image_helper.py` (lines 52-105)

**Description:**
Three locations implement similar portrait loading with placeholder generation:
1. `DesignReportPanel._update_portrait()` - loads portrait with gradient fallback
2. `ShipDetailPanel._get_scaled_image()` - scales images with placeholder icon
3. `design_image_helper.py` - centralized portrait/topdown loading with cache

**Analysis:**
The `design_image_helper.py` module is the canonical implementation with proper caching. The panel-specific implementations have slightly different requirements (DesignReportPanel needs text overlay, ShipDetailPanel needs simple placeholder shapes).

**Recommendation:**
Consider extending `design_image_helper.py` with optional placeholder customization parameters rather than duplicating fallback logic.

**Severity Justification:** INFO - The implementations serve different contexts with minor variations, and a central helper already exists.

---

### DUP-UI-002 [INFO] - Section Header Rendering Pattern

**Files:**
- `game/ui/panels/ship_detail_panel.py` (lines 328-337) - `_add_section_header()`
- `game/ui/panels/design_stats_panel.py` (lines 289-317) - `_build_section()`
- `game/ui/screens/test_lab/screen.py` (lines 1506-1518) - `_draw_section()`

**Description:**
Multiple panels implement section header rendering with the pattern `"-- TITLE --"`:
- `ShipDetailPanel` uses `f"-- {title} --"` with UILabel
- `DesignStatsPanel` uses `f"-- {title} --"` with UILabel
- `TestLabScreen` renders headers using pygame fonts directly

**Analysis:**
These are visually similar but use different rendering approaches (pygame_gui vs raw pygame). The pygame_gui panels could potentially share a common helper, but the TestLabScreen uses a fundamentally different drawing approach (manual pygame rendering).

**Recommendation:**
For pygame_gui panels, consider a shared `create_section_header()` factory function. Leave TestLabScreen's manual rendering as-is since it's a different paradigm.

**Severity Justification:** INFO - The patterns are similar but serve different rendering systems.

---

### DUP-UI-003 [MINOR] - HP/Damage Color Calculation Functions

**Files:**
- `game/ui/panels/ship_detail_panel.py` (lines 25-46) - `get_damage_color()`
- `game/ui/panels/ship_stats_renderer.py` (lines 77-93) - `get_hp_bar_color()`

**Description:**
Two functions compute colors based on HP percentage:

```python
# ship_detail_panel.py
def get_damage_color(hp_percentage: float) -> Tuple[int, int, int]:
    if hp_percentage <= 0:
        return (100, 100, 100)  # Gray - destroyed
    elif hp_percentage < 0.5:
        return (200, 100, 100)  # Red
    elif hp_percentage < 0.75:
        return (200, 200, 100)  # Yellow
    else:
        return (100, 200, 100)  # Green

# ship_stats_renderer.py
def get_hp_bar_color(hp_pct, is_active=True):
    if not is_active:
        return (100, 50, 50)
    if hp_pct > 0.5:
        return (0, 200, 0)
    elif hp_pct > 0.2:
        return (200, 200, 0)
    return (200, 50, 50)
```

**Analysis:**
Both functions serve the same purpose but use different thresholds and color values. The `ship_stats_renderer` version also handles an `is_active` parameter.

**Recommendation:**
Consolidate into a single function in `ship_stats_renderer.py` (or a new `ui/colors.py` module) with configurable thresholds. Replace usages in `ship_detail_panel.py`.

**Severity Justification:** MINOR - Different thresholds may cause inconsistent visual feedback across UI elements.

---

### DUP-UI-004 [INFO] - UIScrollingContainer Setup Pattern

**Files:**
- `game/ui/panels/design_stats_panel.py` (lines 179-184)
- `game/ui/panels/ship_detail_panel.py` (lines 92-96)
- `game/ui/panels/builder_widgets.py` (lines 124-130)
- `game/ui/panels/base_gallery.py` (lines 154-160)
- `game/ui/screens/test_lab/screen.py` (multiple locations)

**Description:**
Many classes create UIScrollingContainer with similar boilerplate:
```python
self.scroll_container = UIScrollingContainer(
    relative_rect=pygame.Rect(...),
    manager=self.manager,
    container=self.panel/self.container,
    allow_scroll_x=False,  # Usually false
    allow_scroll_y=True    # Usually true
)
```

**Analysis:**
This is standard pygame_gui usage rather than duplication. The parameters vary by context (different rects, containers).

**Recommendation:**
No action needed - this is idiomatic pygame_gui usage.

**Severity Justification:** INFO - Standard library usage pattern, not problematic duplication.

---

### DUP-UI-005 [RESOLVED] - Gallery Base Class Extraction

**Files:**
- `game/ui/panels/base_gallery.py`
- `game/ui/panels/race_portrait_gallery.py`
- `game/ui/panels/race_flag_gallery.py`

**Description:**
This duplication was already identified and fixed (see PROJ-108 Phase 6, DUP-UI1-005 resolution). The `BaseGallery` abstract class now provides shared functionality for:
- Scrollable thumbnail gallery
- Preview area for selected asset
- Button click handling
- Selection highlighting

**Analysis:**
RacePortraitGallery and RaceFlagGallery now extend BaseGallery, implementing only asset-specific discovery and preview logic.

**Status:** RESOLVED - No further action needed.

---

### DUP-UI-006 [MINOR] - RaceThemeGallery Not Using BaseGallery

**Files:**
- `game/ui/panels/race_theme_gallery.py`
- `game/ui/panels/base_gallery.py`

**Description:**
`RaceThemeGallery` (202 lines) has similar structure to `BaseGallery` subclasses but does not extend it:
- Has `_create_content()` method
- Has `_discover_themes()` method
- Has `handle_button_click()` method
- Has `set_from_config()` method
- Has `_sanitize_object_id()` method (duplicate of BaseGallery line 215-217)

**Analysis:**
While RaceThemeGallery displays themes in a list (vs. thumbnail grid), it shares significant structural patterns with BaseGallery. The `_sanitize_object_id()` method is identical.

**Recommendation:**
Either:
1. Extend BaseGallery with theme-specific overrides, OR
2. Extract `_sanitize_object_id()` to a shared utility module

**Severity Justification:** MINOR - Missed consolidation opportunity during PROJ-108.

---

### DUP-UI-007 [INFO] - Value Formatting Utilities (Already Consolidated)

**Files:**
- `game/ui/screens/test_lab/formatting_utils.py`

**Description:**
The `format_value()` function was already extracted to consolidate duplicate formatting logic from `test_run_details.py` and `test_run_card.py` (see DUP-UI1-002 resolution).

**Status:** RESOLVED - No further action needed.

---

### DUP-UI-008 [MINOR] - Population/Number Formatting Duplication

**Files:**
- `game/ui/panels/planet_report_panel.py` (lines 303-310) - `_format_compact_number()`
- `game/ui/screens/strategy_detail_fmt.py` (lines 102-113) - inline formatting

**Description:**
Both files implement K/M suffix formatting for large numbers:

```python
# planet_report_panel.py
def _format_compact_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    return str(int(value))

# strategy_detail_fmt.py (inline)
if total_pop >= 1_000_000:
    pop_str = f"{total_pop / 1_000_000:.1f}M"
elif total_pop >= 1_000:
    pop_str = f"{total_pop / 1_000:.0f}K"
else:
    pop_str = str(total_pop)
```

**Recommendation:**
Extract `_format_compact_number()` to a shared formatting utility module (e.g., `game/ui/formatting.py` or `game/core/formatting.py`) and use it in `strategy_detail_fmt.py`.

**Severity Justification:** MINOR - Small code duplication, easy to consolidate.

---

### DUP-UI-009 [INFO] - Graph Widget Base Classes

**Files:**
- `game/ui/panels/strategy_widgets.py` (lines 4-14) - `DataGraph` base class

**Description:**
The `DataGraph` base class provides common functionality for `SpectrumGraph` and `AtmosphereGraph`:
- Surface creation with background color
- `clear()` method with border
- `render()` abstract method

**Analysis:**
This is good design - the base class properly extracts common graph functionality.

**Status:** No issue - proper abstraction in place.

---

### DUP-UI-010 [INFO] - Panel kill() Method Pattern

**Files:**
- `game/ui/panels/design_stats_panel.py` (lines 442-452)
- `game/ui/panels/ship_detail_panel.py` (lines 442-447)
- `game/ui/panels/design_report_panel.py` (lines 277-284)
- Multiple other panels

**Description:**
Most panel classes implement a `kill()` method that:
1. Cleans up child UI elements
2. Kills the main panel container
3. Resets internal state

**Analysis:**
This is a necessary lifecycle pattern for pygame_gui panels. Each panel has different internal state to clean up, so a common base class would not significantly reduce code.

**Recommendation:**
No action needed - this is proper resource cleanup.

**Severity Justification:** INFO - Necessary lifecycle pattern with contextual variations.

---

### DUP-UI-011 [INFO] - Text Wrapping Functions

**Files:**
- `game/ui/screens/test_lab/screen.py` (lines 1642-1668) - `_draw_wrapped_text()`

**Description:**
TestLabScreen implements manual text wrapping for pygame rendering. This is specific to the manual-drawing approach used by TestLabScreen and doesn't have direct duplicates since other panels use pygame_gui's built-in text handling.

**Status:** No issue - context-specific implementation.

---

### DUP-UI-012 [INFO] - Resource Icon/Color Constants

**Files:**
- `game/ui/panels/ship_stats_renderer.py` (lines 17-27) - `RESOURCE_COLORS`
- `game/ui/panels/strategy_widgets.py` (lines 100-110) - `GAS_COLORS`

**Description:**
Multiple files define color mappings for resources/gases. These serve different purposes (ship resources vs. atmospheric gases) and are appropriately separate.

**Status:** No issue - different domains.

---

## Summary Table

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| DUP-UI-001 | INFO | Portrait/Image Loading with Placeholder | Central helper exists |
| DUP-UI-002 | INFO | Section Header Rendering | Different rendering systems |
| DUP-UI-003 | MINOR | HP/Damage Color Calculation | **Recommend consolidation** |
| DUP-UI-004 | INFO | UIScrollingContainer Setup | Standard library pattern |
| DUP-UI-005 | RESOLVED | Gallery Base Class | Fixed in PROJ-108 |
| DUP-UI-006 | MINOR | RaceThemeGallery Not Using BaseGallery | **Recommend integration** |
| DUP-UI-007 | RESOLVED | Value Formatting | Fixed in DUP-UI1-002 |
| DUP-UI-008 | MINOR | Population/Number Formatting | **Recommend extraction** |
| DUP-UI-009 | INFO | Graph Widget Base | Good abstraction |
| DUP-UI-010 | INFO | Panel kill() Pattern | Necessary cleanup |
| DUP-UI-011 | INFO | Text Wrapping Functions | Context-specific |
| DUP-UI-012 | INFO | Resource/Gas Color Constants | Different domains |

---

## Actionable Recommendations

### Priority 1 (MINOR - Quick Wins)

1. **DUP-UI-003:** Consolidate `get_damage_color()` and `get_hp_bar_color()` into a single function in `ship_stats_renderer.py` with configurable thresholds.

2. **DUP-UI-008:** Extract `_format_compact_number()` to a shared module and use it in `strategy_detail_fmt.py`.

### Priority 2 (MINOR - Moderate Effort)

3. **DUP-UI-006:** Evaluate whether `RaceThemeGallery` should extend `BaseGallery`. At minimum, extract `_sanitize_object_id()` to a shared utility.

### No Action Required

The remaining INFO-level findings are either:
- Already resolved (PROJ-108, DUP-UI1-002, DUP-UI1-005)
- Appropriate contextual variations
- Standard library usage patterns
- Proper abstractions already in place

---

## Notes

1. The codebase shows evidence of ongoing duplication cleanup (PROJ-108, DUP-UI1-002, DUP-UI1-005), indicating good maintainability practices.

2. The TestLabScreen (1909 lines) uses manual pygame drawing rather than pygame_gui, which creates a natural boundary preventing consolidation with pygame_gui-based panels.

3. Several potential duplications are actually appropriate because they serve different layers or rendering systems.
