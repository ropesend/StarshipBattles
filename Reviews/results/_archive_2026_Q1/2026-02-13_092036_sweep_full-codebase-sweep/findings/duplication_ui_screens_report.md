# Duplication & Fragmentation Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 44 (21 in game/ui/panels/, 23+ in game/ui/screens/)
- **Total Issues Found:** 9
- **Critical:** 1 | **Major:** 4 | **Minor:** 3 | **Info:** 1

## Findings

#### CRITICAL: Number Formatting with K/M Suffixes Duplicated
**ID:** DUP-UI1-001
**Location:** `game/ui/panels/planet_report_panel.py:303-310` AND `game/ui/screens/strategy_detail_fmt.py:101-130`
**Issue:** Two separate implementations of compact number formatting with K/M suffixes. The `planet_report_panel.py` has a `_format_compact_number()` method that formats values with K/M suffixes, while `strategy_detail_fmt.py` has inline code duplicating this logic three times (for total_pop, max_pop, and individual pop.count). The implementations have slight inconsistencies: panel uses lowercase 'k' while strategy_fmt uses uppercase 'K'.
**Impact:** High maintenance risk - inconsistent formatting across the UI (lowercase 'k' vs uppercase 'K'), bug fixes must be applied in multiple places, cognitive overhead from remembering which formatter to use where.
**Recommendation:** Extract to a shared utility function in `game/ui/utils.py` like `format_compact_number(value: float, lowercase: bool = False) -> str`. Replace all inline usages.
**Effort:** Simple

#### MAJOR: Virtual Scrolling List Pattern Repeated
**ID:** DUP-UI1-002
**Location:** `game/ui/screens/planet_list_window.py:154-195`, `game/ui/screens/fleet_report_window.py:639-784`, `game/ui/screens/empire_build_queue_window.py:201-216`, `game/ui/screens/event_log_window.py:194-226`
**Issue:** Four windows implement nearly identical virtual scrolling patterns: creating a list panel with UIVerticalScrollBar, calculating visible percentage, setting scroll_position to 0.0, and calling redraw_scrollbar(). Each window has similar `refresh_list()` methods that rebuild row elements and update scrollbar state. The planet_list_window extracted its rendering to `VirtualListRenderer`, but the others haven't followed this pattern.
**Impact:** ~50-80 lines duplicated across 4 windows. Changes to scrollbar handling must be applied in multiple places. The `fleet_report_window.py` and `empire_build_queue_window.py` have almost identical mouse wheel handling code (lines 470-480 in build_queue, 873-950 in fleet_report).
**Recommendation:** Extract a `VirtualScrollableList` base class or mixin that handles: scrollbar setup, visible percentage calculation, scroll position management, mouse wheel handling, and row pool management. The existing `VirtualListRenderer` could be expanded or a new shared class created.
**Effort:** Medium

#### MAJOR: Filter Toggle Button Pattern Duplicated
**ID:** DUP-UI1-003
**Location:** `game/ui/screens/fleet_report_window.py:252-416`, `game/ui/screens/planet_list_window.py:309-333`, `game/ui/screens/empire_build_queue_window.py:786-819`
**Issue:** Three windows implement similar filter toggle button patterns with `[x]`/`[ ]` prefix patterns for showing toggle state. Each has similar logic for:
- Creating buttons with `[{label}]` when selected, `{label}` when not
- Handling button clicks to toggle filter state
- Updating button text on state change
- Refreshing the list after toggle

The fleet_report_window repeats this pattern 5 times internally (lines 252, 283, 314, 345, 384) for different filter categories.
**Impact:** ~30 lines duplicated per filter category. Adding a new filter type requires copying the entire pattern. Inconsistent toggle behavior across windows if one is updated and others are not.
**Recommendation:** Create a `ToggleFilterButton` widget class or a `FilterButtonGroup` that encapsulates: button creation with toggle state indicator, click handling, state management, and callback on change.
**Effort:** Medium

#### MAJOR: Placeholder Surface Creation
**ID:** DUP-UI1-004
**Location:** `game/ui/panels/build_queue_portraits.py:144-160`, `game/ui/screens/fleet_report_window.py:761-772`, `game/ui/screens/race_asset_loader.py:93-100`
**Issue:** Three separate `_create_placeholder()` methods that create placeholder surfaces for missing images. Each implementation creates a surface, fills it with a background color, and draws some indicator (crossed lines, border, etc.). The implementations vary slightly in style but serve the same purpose.
**Impact:** Small maintenance burden (15-20 lines each). If placeholder style needs to change for visual consistency, three places need updating.
**Recommendation:** Create a shared `create_placeholder_surface(size: int, style: str = 'default') -> pygame.Surface` function in `game/ui/utils.py`. Support multiple styles if needed.
**Effort:** Simple

#### MAJOR: Sidebar Filter Section Building Pattern
**ID:** DUP-UI1-005
**Location:** `game/ui/screens/empire_build_queue_window.py:687-784`, `game/ui/screens/fleet_report_window.py:220-420`, `game/ui/screens/planet_list_sidebar.py`
**Issue:** Multiple windows build filter sidebars with similar patterns: section labels, toggle buttons with `[x]`/`[ ]` prefixes, y-offset tracking as buttons are added. The empire_build_queue_window builds Location Type, Queue Status, Capabilities, and Search sections. Fleet_report_window builds Type, Warp, Spaceyard, Cargo, and Special filter sections. Both track y_off and increment it similarly after each element.
**Impact:** ~100 lines of similar layout code across windows. Adding new filter types requires understanding the layout pattern each time.
**Recommendation:** Create a `FilterSidebarBuilder` helper class that provides methods like `add_section_header(title)`, `add_toggle_group(options, filter_dict)`, `add_search_box()`, and tracks y-offset internally.
**Effort:** Medium

#### MINOR: Image Scaling with smoothscale
**ID:** DUP-UI1-006
**Location:** `game/ui/screens/empire_panel_window.py:274,288`, `game/ui/screens/planet_list_renderer.py:160`, `game/ui/panels/planet_report_panel.py:196`, `game/ui/screens/strategy_detail_formatter.py:213`, `game/ui/panels/system_tree_panel.py:51`
**Issue:** Multiple places call `pygame.transform.smoothscale(img, (size, size))` to scale images to fixed sizes. While each usage has different target sizes, the pattern of "load image, check validity, scale to target" is repeated.
**Impact:** Low - this is a simple one-liner. However, some usages don't check for None or missing texture before scaling.
**Recommendation:** Consider a utility function `scale_image(surface: Optional[pygame.Surface], target_size: Tuple[int, int], fallback: Optional[pygame.Surface] = None) -> pygame.Surface` that handles None checks and provides a consistent fallback.
**Effort:** Simple

#### MINOR: Column Visibility Toggle Handling
**ID:** DUP-UI1-007
**Location:** `game/ui/screens/planet_list_window.py:346-357`, `game/ui/screens/empire_build_queue_window.py:662-681`
**Issue:** Both windows have similar `_handle_column_toggle_click()` methods that: iterate through column toggle buttons, find the clicked one, toggle visibility, update button text with `[x]`/`[ ]` prefix, rebuild headers, and refresh the list.
**Impact:** ~20 lines duplicated. Pattern already uses `ColumnManager` but toggle handling is still duplicated.
**Recommendation:** Move column toggle handling into `ColumnManager` class or create a `ColumnToggleSidebar` widget.
**Effort:** Simple

#### MINOR: Screenshot Toast Display
**ID:** DUP-UI1-008
**Location:** `game/ui/screens/planet_list_window.py:412-424`
**Issue:** The `_show_screenshot_toast()` method creates a `UIMessageWindow` toast with hardcoded dimensions from UIConfig. This pattern may be duplicated in other windows that support F12 screenshots (not found in this shard, but likely exists elsewhere).
**Impact:** Low - only observed once in this shard, but the pattern should be centralized.
**Recommendation:** Move to a shared `show_toast(manager, message, title="Screenshot")` function in `game/ui/utils.py` or in `ScreenshotManager`.
**Effort:** Simple

#### INFO: BaseGallery Abstract Class Already Consolidated
**ID:** DUP-UI1-009
**Location:** `game/ui/panels/base_gallery.py`
**Issue:** This is a positive finding - the codebase already extracted common gallery code into an abstract base class (`BaseGallery`) as part of PROJ-108 to resolve DUP-UI1-005 from a previous sweep. `RacePortraitGallery` and `RaceFlagGallery` now inherit from this base, eliminating ~150 lines of duplication.
**Impact:** None - this is an example of good consolidation.
**Recommendation:** Use this as a template for similar consolidations (e.g., scrollable list windows).
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-UI1-001 (CRITICAL): Number Formatting** - Active divergence between implementations (lowercase 'k' vs uppercase 'K') creates visual inconsistency. Simple fix with high impact.

2. **DUP-UI1-002 (MAJOR): Virtual Scrolling Lists** - 4 windows with ~60 lines each of duplicated scrollbar/list management code. Consolidation would significantly reduce maintenance burden.

3. **DUP-UI1-003 (MAJOR): Filter Toggle Buttons** - Pattern repeated across 3 windows and 5+ times within fleet_report_window alone. A widget class would save significant code.

4. **DUP-UI1-005 (MAJOR): Sidebar Filter Building** - ~100 lines of similar y-offset tracking and section building code. A builder pattern would improve maintainability.

5. **DUP-UI1-004 (MAJOR): Placeholder Surfaces** - 3 different placeholder implementations that should look consistent. Simple extraction to a utility.
