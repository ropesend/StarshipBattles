# Duplication & Fragmentation Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 134 (109 in game/ui/screens/, 25 in game/ui/panels/)
- **Total Issues Found:** 10
- **Critical:** 2 | **Major:** 4 | **Minor:** 3 | **Info:** 1

## Findings

#### CRITICAL: BuildQueueScreen instantiation duplicated 3 times in strategy_screen.py
**ID:** DUP-UI1-001
**Location:** `game/ui/screens/strategy_screen.py:401-445` AND `game/ui/screens/strategy_screen.py:503-555` AND `game/ui/screens/strategy_screen.py:557-600`
**Issue:** Three methods (`on_build_yard_click`, `on_navigate_to_hex_build`, `on_fleet_build_click`) each contain a near-identical 20+ line block that:
1. Guards against double-open (`if hasattr(self, 'build_queue_screen') and self.build_queue_screen is not None`)
2. Imports `BuildQueueScreen` and `DesignLibrary`
3. Calls `self.ui.hide_ui()`
4. Gets portrait via `self._get_object_asset(entity)`
5. Creates `DesignLibrary(savegame_path, empire_id)` and `DesignLoaderAdapter()`
6. Constructs `BuildQueueScreen(self.ui.manager, entity, self.session, ...)` with 10 identical kwargs
7. Logs the open action

The only differences are: (a) which entity is passed, (b) how `hex_coord` is calculated, and (c) which log message is printed. The guard clause, import block, UI hide, DI setup, and constructor call are copy-pasted verbatim.
**Impact:** If the BuildQueueScreen constructor signature changes, all three sites must be updated. Bug fixes to the guard logic or DI setup are easily missed in one copy. This already happened once (PROJ-69 added hex_coord to all three).
**Recommendation:** Extract a private method `_open_build_queue_for(entity, hex_coord)` that handles the shared boilerplate. Each caller reduces to 3-5 lines: validate entity, compute hex_coord, call helper.
**Effort:** Simple

#### CRITICAL: Two separate ColumnManager classes with overlapping responsibilities
**ID:** DUP-UI1-002
**Location:** `game/ui/screens/column_manager.py:49` AND `game/ui/screens/planet_list_columns.py:11`
**Issue:** Two entirely separate classes both named `ColumnManager` exist side-by-side:

1. **`column_manager.py`** (PROJ-44 Phase 7): Fleet-report focused. Has `get_column_value(ship, col)`, `swap_column()`, `toggle_column()`, `get_toggleable_columns()`. No UI header management.
2. **`planet_list_columns.py`**: Planet/empire-queue focused. Has `rebuild_headers()`, `handle_header_clicks()`, `swap_columns()`, `toggle_visibility()`, sorting state. Creates pygame_gui UIButton headers.

Both implement: `get_visible_columns()`, column swapping, visibility toggling. The planet_list version also manages header UI elements and sort state. The fleet version also extracts column values from ship data.

Used by:
- `fleet_report_window.py` imports from `column_manager.py`
- `planet_list_window.py` and `empire_build_queue_window.py` import from `planet_list_columns.py`

**Impact:** Developers must know which `ColumnManager` to import. API differs (e.g., `toggle_column` vs `toggle_visibility`, `swap_column` vs `swap_columns`). Shared improvements (e.g., resize handles) must be implemented twice.
**Recommendation:** Unify into a single `ColumnManager` base class. The fleet-specific `get_column_value()` logic belongs in a fleet-specific subclass or separate value extractor. Header UI management can be optional (builder pattern or flag).
**Effort:** Medium

#### MAJOR: Screenshot capture and toast notification duplicated across 3 files
**ID:** DUP-UI1-003
**Location:** `game/ui/screens/build_queue_screen.py:1044-1068` AND `game/ui/screens/planet_list_window.py:400-419` AND `game/ui/screens/strategy_input_handler.py:844-871`
**Issue:** Three separate implementations of `_take_screenshot()` and `_show_screenshot_toast()`:
- `build_queue_screen.py`: `sm.capture(label="build_queue")` + toast with `UIMessageWindow`
- `planet_list_window.py`: `sm.capture(label="planet_list")` + identical toast with `UIMessageWindow`
- `strategy_input_handler.py`: Two variants (`_take_screenshot_full`, `_take_screenshot_viewport`) + toast with `UIMessageWindow`

The toast methods are nearly identical: create `pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)`, center it, create `UIMessageWindow` with "Screenshot saved!" message. Only the `manager` reference and error handling differ slightly.
**Impact:** Three places to maintain if toast format changes. Minor divergence already exists in error handling (one uses `except Exception`, another uses specific exceptions).
**Recommendation:** Add a `show_screenshot_toast(manager, screen_width)` utility function to `ScreenshotManager` or a UI utility module. Optionally, add a `capture_and_notify(label, manager, screen_width)` convenience method.
**Effort:** Simple

#### MAJOR: Resource display formatting duplicated between strategy_ui.py and build_queue_helpers.py
**ID:** DUP-UI1-004
**Location:** `game/ui/screens/strategy_ui.py:279-300` AND `game/ui/screens/build_queue_helpers.py:27-45`
**Issue:** `StrategyUI._update_resource_display()` and `format_empire_resources()` contain identical formatting logic:
```python
for res in PLANET_RESOURCES:
    current = empire.<get_resource>(res)
    cap = empire.max_storage.get(res, 0.0)
    abbr = RESOURCE_ABBREVS.get(res, res[:3])
    if cap > 0:
        parts.append(f"{abbr}: {int(current)}/{int(cap)}")
    elif current > 0:
        parts.append(f"{abbr}: {int(current)}")
```
The only difference is the resource access method: `empire.get_resource(res)` vs `empire.resource_pool.get(res, 0.0)`. The formatting template, abbreviation lookup, and join logic are identical.
**Impact:** If formatting needs to change (e.g., adding percentage, color coding), both must be updated. They could diverge silently.
**Recommendation:** `StrategyUI._update_resource_display()` should call `format_empire_resources(empire)` from `build_queue_helpers.py`. The `get_resource()` vs `resource_pool.get()` difference should be normalized in the Empire class or the formatting function should accept either.
**Effort:** Simple

#### MAJOR: Star system/star formatting duplicated between strategy_detail_formatter.py and strategy_detail_fmt.py
**ID:** DUP-UI1-005
**Location:** `game/ui/screens/strategy_detail_formatter.py:241-277` AND `game/ui/screens/strategy_detail_fmt.py:151-189`
**Issue:** `StrategyDetailFormatter._format_star_system()` and `format_star_system_info()` produce identical HTML output:
```python
text = f"<b>System:</b> {obj.name}<br>"
text += f"<b>Primary:</b> {primary.name}<br>"
text += f"<b>Type:</b> {primary.star_type.name}<br>"
text += f"<b>Mass:</b> {primary.mass:.2f} Sol<br>"
text += f"<b>Temp:</b> {int(primary.temperature)} K<br>"
text += f"<b>Stars:</b> {len(obj.stars)}<br>"
```
Similarly, `_format_star()` (lines 263-277) duplicates `format_star_info()` (lines 174-189). The formatter class methods also add spectrum graph rendering logic, but the text generation is identical.

Additionally, `galaxy_test/system_mode.py:378-397` has a third version of star info formatting (`_format_star_info`) that renders to plain text instead of HTML but extracts the same data fields.
**Impact:** The formatter class was extracted (PROJ-86) but the pure functions in `strategy_detail_fmt.py` still exist and are imported by the formatter. The formatter then wraps them but also re-implements them inline. This is confusing: should callers use the pure functions or the class methods?
**Recommendation:** `StrategyDetailFormatter._format_star_system()` should delegate the text generation to `format_star_system_info()` (which it already imports), keeping only the graph rendering and button visibility logic. Same for `_format_star()` -> `format_star_info()`.
**Effort:** Simple

#### MAJOR: Event log window open methods duplicated within strategy_window_manager.py
**ID:** DUP-UI1-006
**Location:** `game/ui/screens/strategy_window_manager.py:190-213` AND `game/ui/screens/strategy_window_manager.py:215-234`
**Issue:** `open_event_log()` and `open_event_log_with_events(events)` are 95% identical. Both:
1. Kill existing window if present
2. Calculate `w, h = int(self.width * 0.7), int(self.height * 0.7)`
3. Create centered `pygame.Rect`
4. Construct `EventLogWindow(rect, self.manager, events, on_close_callback=...)`

The only difference is where `events` comes from: `open_event_log()` fetches from facade, `open_event_log_with_events()` takes it as a parameter. The rect calculation, window sizing, and construction are copy-pasted.
**Impact:** Low bug risk since they're adjacent, but violates DRY and adds maintenance surface.
**Recommendation:** Merge into a single method with an optional `events` parameter. If `events` is None, fetch from facade.
**Effort:** Simple

#### MINOR: Thin wrapper/proxy methods in StrategyUI delegating to sub-objects
**ID:** DUP-UI1-007
**Location:** `game/ui/screens/strategy_ui.py:247-276` AND `game/ui/screens/strategy_ui.py:339-389`
**Issue:** StrategyUI contains ~20 one-liner methods that do nothing but forward calls to `_detail_formatter` or `_window_manager`:
```python
def _get_label_for_obj(self, obj):
    return self._detail_formatter._get_label_for_obj(obj)

def open_planet_list(self):
    self._window_manager.open_planet_list()

def open_empire_build_queue_window(self):
    self._window_manager.open_empire_build_queue_window()
```
These exist because external callers (StrategyScreen, EventRouter) call `self.ui.open_planet_list()` rather than `self.ui._window_manager.open_planet_list()`.

Additionally, `StrategyDetailFormatter` has thin wrappers around `strategy_detail_fmt` pure functions (lines 124-134):
```python
def _format_spectrum(self, star) -> str:
    return format_spectrum_html(star)
```
**Impact:** Not a correctness issue, but adds ~80 lines of pure boilerplate across two files. Makes it harder to understand the actual code flow.
**Recommendation:** Consider making `_window_manager` and `_detail_formatter` public attributes and having callers access them directly. Alternatively, accept the delegation pattern as an intentional facade (PROJ-86 explicitly chose this pattern for god class decomposition).
**Effort:** Simple (but may conflict with PROJ-86 design intent)

#### MINOR: Population count formatting (K/M suffixes) implemented inline
**ID:** DUP-UI1-008
**Location:** `game/ui/screens/strategy_detail_fmt.py:102-131`
**Issue:** Population formatting with K/M suffixes is implemented inline in `format_planet_info()`:
```python
if total_pop >= 1_000_000:
    pop_str = f"{total_pop / 1_000_000:.1f}M"
elif total_pop >= 1_000:
    pop_str = f"{total_pop / 1_000:.0f}K"
else:
    pop_str = str(total_pop)
```
This pattern is repeated three times in the same function (for `total_pop`, `max_pop`, and `pop.count`). While localized to one file, it's a clear candidate for a utility function like `format_count_suffix(value)`.
**Impact:** Low risk since it's in one file, but the pattern is verbose and error-prone if thresholds need to change.
**Recommendation:** Extract a `format_population(count: int) -> str` utility function and use it for all three cases.
**Effort:** Simple

#### MINOR: Window centering pattern repeated ~15 times without utility
**ID:** DUP-UI1-009
**Location:** `game/ui/screens/strategy_screen.py` (5 instances), `game/ui/screens/strategy_window_manager.py` (5 instances), `game/ui/screens/strategy_detail_formatter.py` (1 instance), `game/ui/screens/build_queue_screen.py` (1 instance)
**Issue:** The pattern of creating a centered rect appears 12+ times across strategy screen files:
```python
rect = pygame.Rect(0, 0, w, h)
rect.center = (self.width // 2, self.height // 2)
```
or equivalently:
```python
rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)
```
A utility function `create_centered_rect` already exists in `game/ui/utils.py` and is used in `_show_load_game_dialog()`, but not in the other ~11 instances.
**Impact:** Low severity individually, but collectively adds clutter. The utility exists but is underutilized.
**Recommendation:** Replace all manual centering with `create_centered_rect(w, h, screen_w, screen_h)` from `game/ui/utils.py`.
**Effort:** Simple

#### INFO: StrategyDetailFormatter._format_star_system duplicates format_star_system_info then adds graph logic
**ID:** DUP-UI1-010
**Location:** `game/ui/screens/strategy_detail_formatter.py:241-259` AND `game/ui/screens/strategy_detail_fmt.py:151-171`
**Issue:** The `_format_star_system` method in `StrategyDetailFormatter` contains the exact same text-building code as the standalone `format_star_system_info()` function, plus additional graph rendering. The formatter already imports `format_star_system_info` but does not use it for the text portion. This is a byproduct of the PROJ-86 god class extraction -- the class methods were extracted as-is without refactoring their internals to delegate to the pure functions that were also extracted.

Note: This is the same issue as DUP-UI1-005 viewed from the architectural perspective. The pure functions in `strategy_detail_fmt.py` were intended to be the single source of truth for text formatting, but the formatter class re-implements them. This overlap is informational because the PROJ-86 extraction was a first pass and consolidation is a known follow-up.
**Impact:** Informational -- no active divergence yet, but the architecture is fragile.
**Recommendation:** Part of DUP-UI1-005 resolution.
**Effort:** N/A (covered by DUP-UI1-005)

## Top 5 Priority Issues

1. **DUP-UI1-001 (CRITICAL):** BuildQueueScreen instantiation duplicated 3x in strategy_screen.py -- 60+ lines of near-identical code across three methods. Simple extraction to a helper method. Highest impact for lowest effort.

2. **DUP-UI1-002 (CRITICAL):** Two separate ColumnManager classes with conflicting APIs. Creates confusion for developers and prevents shared improvements. Medium effort to unify but significant architectural benefit.

3. **DUP-UI1-003 (MAJOR):** Screenshot + toast pattern duplicated in 3 files. Simple extraction to utility, prevents drift in error handling and toast formatting.

4. **DUP-UI1-004 (MAJOR):** Resource display formatting duplicated between StrategyUI and build_queue_helpers. The helper function already exists but StrategyUI reimplements it. Simple one-line fix.

5. **DUP-UI1-005 (MAJOR):** Star system/star formatting duplicated between formatter class and pure functions. The pure functions exist but the class re-implements them inline. Simple delegation fix.
