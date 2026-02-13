# Duplication & Fragmentation Report: UI Screens and Panels

**Scope:** `game/ui/screens/`, `game/ui/panels/`
**Date:** 2026-02-13
**Agent:** Sweep Agent - Duplication & Fragmentation (Sweep Cycle 2)

---

## Executive Summary

This report identifies code duplication, near-duplication, copy-paste drift, and fragmented implementations within the UI layer (`game/ui/screens/` and `game/ui/panels/`). The analysis covers 65+ Python files totaling approximately 20,000+ lines of code.

**Key Findings:**
- 2 CRITICAL issues (significant duplication requiring immediate refactor)
- 4 MAJOR issues (substantial patterns worth consolidating)
- 5 MINOR issues (smaller duplications with low risk)
- 3 INFO items (noted patterns, acceptable as-is)

The codebase shows evidence of **prior refactoring efforts** (PROJ-108, PROJ-12, DUP-UI1-002, DUP-UI1-005) that have already consolidated several patterns, but significant opportunities remain.

---

## Findings

### CRITICAL

#### CRITICAL: ID-Based Expansion Tracking Pattern Duplicated in Battle Panels

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` (lines 59-86, 263-286)

**Description:**
`ShipStatsPanel` and `SeekerMonitorPanel` both implement nearly identical ID-based expansion state tracking patterns:

```python
# ShipStatsPanel (lines 59-86)
def _get_ship_id(self, ship):
    ship_id = getattr(ship, 'id', None)
    if isinstance(ship_id, str):
        return ship_id
    ship_name = getattr(ship, 'name', None)
    if isinstance(ship_name, str):
        return ship_name
    return str(id(ship))

def _is_expanded(self, ship):
    return self._get_ship_id(ship) in self.expanded_ships

def _toggle_expanded(self, ship):
    ship_id = self._get_ship_id(ship)
    if ship_id in self.expanded_ships:
        self.expanded_ships.discard(ship_id)
    else:
        self.expanded_ships.add(ship_id)

# SeekerMonitorPanel (lines 263-286) - nearly identical
def _get_projectile_id(self, proj):
    proj_id = getattr(proj, 'id', None)
    if isinstance(proj_id, str):
        return proj_id
    return str(id(proj))

def _is_seeker_expanded(self, proj):
    return self._get_projectile_id(proj) in self.expanded_seekers

def _toggle_seeker_expanded(self, proj):
    proj_id = self._get_projectile_id(proj)
    if proj_id in self.expanded_seekers:
        self.expanded_seekers.discard(proj_id)
    else:
        self.expanded_seekers.add(proj_id)
```

**Impact:** ~40 lines of duplicated logic. Changes to expansion tracking must be synchronized manually.

**Recommendation:** Extract a reusable `ExpansionTracker` mixin or utility class that handles ID extraction and toggle state management. The base class `BattlePanel` is the natural place for this abstraction.

---

#### CRITICAL: Multi-Select Row Click Handling Duplicated Across Windows

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (lines 883-928)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (lines 304-337)

**Description:**
Both windows implement nearly identical Ctrl+click multi-select logic:

```python
# FleetReportWindow._handle_row_click (lines 883-928)
mods = pygame.key.get_mods()
ctrl_held = bool(mods & pygame.KMOD_CTRL)

if ctrl_held:
    if ship_index in self.selected_indices:
        if len(self.selected_indices) > 1:
            self.selected_indices.discard(ship_index)
    else:
        self.selected_indices.add(ship_index)
else:
    self.selected_indices = {ship_index}

# Update single selection tracking
if len(self.selected_indices) == 1:
    sole_idx = next(iter(self.selected_indices))
    self.selected_ship = filtered_ships[sole_idx]
else:
    self.selected_ship = None

# EmpireBuildQueueWindow.handle_row_click (lines 304-337) - nearly identical
if ctrl_held:
    if index in self.selected_indices:
        if len(self.selected_indices) > 1:
            self.selected_indices.discard(index)
    else:
        self.selected_indices.add(index)
else:
    self.selected_indices = {index}

if len(self.selected_indices) == 1:
    sole_idx = next(iter(self.selected_indices))
    self.selected_index = sole_idx
    self.selected_source = self.filtered_sources[sole_idx]
else:
    self.selected_index = -1
    self.selected_source = None
```

**Impact:** ~50 lines duplicated. Selection behavior inconsistencies are likely if only one file is updated.

**Recommendation:** Create a `MultiSelectMixin` or `SelectionController` class that encapsulates:
- `selected_indices: Set[int]`
- `handle_row_click(index, ctrl_held) -> None`
- `get_single_selection() -> Optional[int]`

---

### MAJOR

#### MAJOR: Window Open/Close Pattern Repeated in StrategyWindowManager

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\strategy_window_manager.py` (entire file)

**Description:**
Each window type follows the same boilerplate pattern:

```python
def open_<window_type>(self) -> None:
    if self.<window>:
        self.<window>.kill()

    # Calculate rect
    w, h = <width>, <height>
    rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

    self.<window> = <WindowClass>(
        rect, self.manager, <args>,
        on_close_callback=self._on_<window>_closed,
    )

def _on_<window>_closed(self) -> None:
    self.<window> = None
```

This pattern is repeated 8+ times (planet_list, build_queue_list, empire_build_queue, event_log, fleet_orders, fleet_report, transfer_dialog, empire_panel).

**Impact:** ~200 lines of boilerplate that could be reduced by 60-70%.

**Recommendation:** Create a generic `_open_window()` helper method:
```python
def _open_window(self, attr_name: str, window_class, rect_scale: tuple, *args, **kwargs):
    existing = getattr(self, attr_name)
    if existing:
        existing.kill()
    w = int(self.width * rect_scale[0])
    h = int(self.height * rect_scale[1])
    rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)
    def on_close():
        setattr(self, attr_name, None)
    window = window_class(rect, self.manager, *args, on_close_callback=on_close, **kwargs)
    setattr(self, attr_name, window)
```

---

#### MAJOR: Timestamp Formatting Duplicated Within SaveSelectionWindow

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\save_selection_window.py` (lines 146-151, 169-175)

**Description:**
The same datetime parsing and formatting logic appears twice in the same file:

```python
# First occurrence (lines 146-151)
try:
    from datetime import datetime
    dt = datetime.fromisoformat(timestamp)
    time_str = dt.strftime("%Y-%m-%d %H:%M")
except ValueError as e:
    log_warning(f"Failed to parse save timestamp '{timestamp}': {e}")
    time_str = timestamp[:16] if len(timestamp) >= 16 else timestamp

# Second occurrence (lines 169-175) - nearly identical
try:
    from datetime import datetime
    dt = datetime.fromisoformat(turn_time)
    turn_time_str = dt.strftime("%m-%d %H:%M")
except ValueError as e:
    log_warning(f"Failed to parse turn timestamp '{turn_time}': {e}")
    turn_time_str = ""
```

**Impact:** Code maintenance issue. The import is inside the function (inefficient), and error handling differs slightly.

**Recommendation:** Extract to a helper method at module level or as an instance method.

---

#### MAJOR: Scrollbar + List Panel Pattern Repeated Across Multiple Windows

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (lines 471-487)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (lines 172-192)
- `C:\Dev\Starship Battles\game\ui\screens\event_log_window.py` (lines 86-112)
- `C:\Dev\Starship Battles\game\ui\screens\planet_list_window.py` (similar pattern)

**Description:**
Each window creates a scrollable list with nearly identical setup:

```python
# Create list panel
self.list_panel = UIPanel(
    relative_rect=pygame.Rect(x, y, width - scrollbar_width, height),
    manager=self.ui_manager,
    container=self,
    anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
)

# Create scrollbar
self.scroll_bar = UIVerticalScrollBar(
    relative_rect=pygame.Rect(-scrollbar_width, y, scrollbar_width, height),
    visible_percentage=1.0,
    manager=self.ui_manager,
    container=self,
    anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
)
```

**Impact:** ~30 lines duplicated per window (4+ occurrences = 120+ lines).

**Recommendation:** Create a `ScrollableListPanel` composite widget that encapsulates the list panel + scrollbar setup and provides common methods like `set_content_height()`, `get_visible_range()`, etc.

---

#### MAJOR: Filter Toggle Button Pattern Repeated

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (lines 244-265, 278-296, etc.)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (lines 700-760)

**Description:**
Both files create filter toggle buttons with nearly identical code:

```python
for filter_id, label in filter_configs:
    is_on = self.view_model.is_filter_enabled(filter_id)
    btn_text = f"[{label}]" if is_on else label
    btn = UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text=btn_text,
        manager=self.ui_manager,
        container=container,
        object_id=f"#filter_{filter_id}"
    )
    if is_on:
        btn.select()
    self.filter_buttons[filter_id] = btn
    y += spacing
```

This pattern repeats 4+ times in FleetReportWindow and 3+ times in EmpireBuildQueueWindow.

**Impact:** ~100+ lines of duplicated filter button creation code.

**Recommendation:** Create a `FilterButtonGroup` helper class or factory function.

---

### MINOR

#### MINOR: HP/Damage Color Calculation Functions

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\ship_detail_panel.py` (lines 25-46) - `get_damage_color()`
- `C:\Dev\Starship Battles\game\ui\panels\ship_stats_renderer.py` (lines 77-93) - `get_hp_bar_color()`

**Description:**
Two functions compute colors based on HP percentage with different thresholds and color values.

**Recommendation:** Consolidate into a single function with configurable thresholds.

---

#### MINOR: Population/Number Formatting Duplication

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\planet_report_panel.py` (lines 303-310) - `_format_compact_number()`
- `C:\Dev\Starship Battles\game\ui\screens\strategy_detail_fmt.py` (lines 102-113) - inline formatting

**Description:**
Both files implement K/M suffix formatting for large numbers.

**Recommendation:** Extract to a shared formatting utility module.

---

#### MINOR: RaceThemeGallery Not Using BaseGallery

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\race_theme_gallery.py`
- `C:\Dev\Starship Battles\game\ui\panels\base_gallery.py`

**Description:**
`RaceThemeGallery` has similar structure to `BaseGallery` subclasses but does not extend it. The `_sanitize_object_id()` method (lines 215-217) is duplicated.

**Recommendation:** Evaluate integration with BaseGallery or extract shared utility.

---

#### MINOR: Window Kill/Cleanup Pattern Slightly Inconsistent

**Files:**
- Multiple window classes have varying cleanup patterns in `kill()` methods

**Description:**
Most windows follow `on_close_callback -> super().kill()` but some add extra cleanup or omit callbacks.

**Recommendation:** Standardize on a base pattern.

---

#### MINOR: Dropdown Recreation Utility

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\transfer_dialog.py` (lines 147-158)

**Description:**
`_recreate_dropdown()` works around pygame_gui's lack of dropdown update method. Could be useful elsewhere.

**Recommendation:** Move to a shared UI utility module if other dialogs need dynamic dropdowns.

---

### INFO

#### INFO: BaseGallery Already Extracted (RESOLVED)

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\base_gallery.py`

**Description:**
Good example of duplication already addressed. `BaseGallery` provides a shared abstract base for `RacePortraitGallery` and `RaceFlagGallery` (DUP-UI1-005 resolution).

---

#### INFO: Ship Stats Renderer Already Extracted

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\ship_stats_renderer.py`

**Description:**
Drawing utilities for ship statistics have been properly extracted into a dedicated module.

---

#### INFO: Strategy Detail Formatters Properly Separated

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\strategy_detail_fmt.py`
- `C:\Dev\Starship Battles\game\ui\screens\strategy_detail_formatter.py`

**Description:**
Intentional separation - `strategy_detail_fmt.py` has pure formatting functions, `strategy_detail_formatter.py` provides stateful wrapper.

---

## Summary Statistics

| Severity | Count | Estimated Lines Affected |
|----------|-------|--------------------------|
| CRITICAL | 2     | ~90 lines                |
| MAJOR    | 4     | ~450 lines               |
| MINOR    | 5     | ~100 lines               |
| INFO     | 3     | N/A (resolved/acceptable)|

**Total Actionable Duplication:** ~640 lines across 11 distinct patterns

---

## Recommended Refactoring Priority

1. **CRITICAL: Multi-Select Row Click** - Extract `SelectionController` (affects 2 windows, high bug risk)
2. **CRITICAL: Expansion Tracking** - Extract `ExpansionTracker` mixin (affects battle panels)
3. **MAJOR: Window Manager Boilerplate** - Create generic `_open_window()` helper
4. **MAJOR: Scrollable List Pattern** - Create `ScrollableListPanel` composite
5. **MAJOR: Filter Toggle Buttons** - Create `FilterButtonGroup` factory
6. **MAJOR: Timestamp Formatting** - Quick local refactor in SaveSelectionWindow

---

*Report generated by Sweep Agent - Duplication & Fragmentation (Cycle 2)*
