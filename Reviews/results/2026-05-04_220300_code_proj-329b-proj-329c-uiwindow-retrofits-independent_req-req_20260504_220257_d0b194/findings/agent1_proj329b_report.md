# Agent 1 Report — PROJ-329B Production Refactor Review

**Review scope:** EmpirePanelWindow, EmpireBuildQueueWindow, SaveSelectionWindow, RaceBrowserDialog, DesignSelectorWindow, EventLogWindow, StarListWindow  
**Base:** `StrategyModalWindow` (5 files) + direct `UIWindow` (3 files)  
**Date:** 2026-05-04

---

## PROJ-329B Behavioral Parity (EmpirePanelWindow)

**File:** `game/ui/screens/empire_panel_window.py:72–136`  
**Fixture:** `tests/fixtures/empire_panel_window_ui_builder.py`

### Stage 1 cheap state (lines 100–119)
All state is set BEFORE `super().__init__`:
- `self.empire` (101), `self.on_close_callback` (102), `self._registries` (103), `self._race_registry` (104)
- `self.tab_buttons = []` (107), `self.step_panels = []` (108), `self.current_tab = TAB_TREASURY` (109)
- `self._asset_loader = RaceAssetLoader()` (112)
- `self._resource_icons = load_resource_icons()` (116)
- `self._treasury_panel = None` (119) — widget ref placeholder

**Verdict:** Correct construction order. No state is set AFTER `super().__init__` that logically belongs in Stage 1.

### Stage 2 shell (lines 122–128)
```python
super().__init__(rect, manager, window_display_title="Empire Overview", resizable=False, window_manager=window_manager)
```
Correctly forwards `window_manager` as kwarg per Pattern §33 / PROJ-313 convention.

### Stage 3 bypass check (lines 131–136)
```python
if getattr(self, '_window_init_bypassed', False):
    if ui_builder is not None:
        ui_builder.build(self)
    return
(ui_builder or EmpirePanelUiBuilder()).build(self)
```
- **Bypass path:** `StrategyModalWindow.__init__` (line 118–131 of `strategy_modal_window.py`) sets `_window_init_bypassed = True` when `type(self).bypass_init` is set, then returns early before `UIWindow.__init__`. The check after `super().__init__` correctly branches: only calls `ui_builder.build(self)` when builder is non-None.
- **Production path:** `_window_init_bypassed` is set to `False` in `StrategyModalWindow.__init__` (line 134), so `(ui_builder or EmpirePanelUiBuilder()).build(self)` executes — defaulting to production builder when `ui_builder` is `None`.

**Verdict:** Both paths correct.

### Public method behavior

**`process_event`** (line 539–558): Calls `super().process_event(event)` first, then checks `UI_BUTTON_PRESSED` against `self.tab_buttons`. Returns `handled`. Correct.

**`kill`** (line 560–564): Calls `self.on_close_callback()` if set, then `super().kill()`. Correct — matches `StrategyModalWindow.kill()` which handles deregistration.

### Findings

| Severity | Finding |
|----------|---------|
| **OBSERVATION** | `self._resource_icons = load_resource_icons()` at line 116 runs in Stage 1 (before `super().__init__`). Comment says "cheap I/O cached at module level" — the call returns pre-loaded dict from AssetManager, so this is safe. If the cache ever misses and triggers real I/O that needs an initialized display, it would be a latent issue. Currently benign. |

---

## Pattern §33 Conformance (EmpireBuildQueueWindow)

**File:** `game/ui/screens/empire_build_queue_window.py:153–211`  
**Fixture:** `tests/fixtures/empire_build_queue_window_ui_builder.py`

### Stage 1 cheap state (lines 173–195)
- `self.empire`, `self.galaxy`, `self.on_close_callback`, `self.on_navigate_to_hex` ✓
- `self._session`, `self._facade` ✓
- Layout constants (`sidebar_width`, `header_height`, `row_height`) ✓
- MVVM components: `_event_bus`, `_viewmodel`, `_filter_mgr` ✓

### Missing widget ref placeholders in Stage 1

| Widget ref | Set in Stage 1? | Set by |
|------------|:-:|-------|
| `self.sidebar_panel` | ✗ | Builder (Stage 3) |
| `self.main_panel` | ✗ | Builder (Stage 3) |
| `self._sidebar` | ✗ | Builder (Stage 3) |
| `self._virtual_table` | ✗ | Builder (Stage 3) |
| `self.scroll_bar` | ✗ | Builder (Stage 3) |
| `self._data_source` | ✗ | Builder (Stage 3) |
| `self._column_manager` | ✗ | Builder (Stage 3) |
| `self._selection` | ✗ | Builder (Stage 3) |

Pattern §33 canonical shape (from the task description):
```python
self._init_widget_refs()
```
All widget refs should be initialized to `None`/empty in Stage 1 as defensive placeholders.

### Explicit `ui_builder` parameter (line 165)
```python
ui_builder: Optional["EmpireBuildQueueUiBuilder"] = None,
```
✓ Correctly declared with default `None`.

### Null/Mock fixture pair
`tests/fixtures/empire_build_queue_window_ui_builder.py`:
- `NullEmpireBuildQueueWindowUiBuilder` (line 24–28): no-op ✓
- `MockEmpireBuildQueueWindowUiBuilder` (line 31–65): populates widget slots with MagicMocks ✓

Both implement `build(screen) -> None` protocol. ✓

### Production path (line 211)
```python
(ui_builder or EmpireBuildQueueUiBuilder()).build(self)
```
✓ Correct — defaults to production builder when `ui_builder` is `None`.

### Bypass path (lines 206–209)
```python
if getattr(self, '_window_init_bypassed', False):
    if ui_builder is not None:
        ui_builder.build(self)
    return
```
✓ Correct — only calls builder when explicitly provided.

### Findings

| Severity | Finding |
|----------|---------|
| **MAJOR** | 8 widget refs (`sidebar_panel`, `main_panel`, `_sidebar`, `_virtual_table`, `scroll_bar`, `_data_source`, `_column_manager`, `_selection`) not initialized in Stage 1 (`empire_build_queue_window.py:173–195`). Pattern §33 requires `_init_widget_refs()` placeholders before `super().__init__`. While production paths always set these via the builder in Stage 3 (before any event handler can access them), a test using `NullEmpireBuildQueueWindowUiBuilder` that subsequently calls `kill()` (line 591: `self._virtual_table.kill()`) would crash with `AttributeError`. |

---

## Mixed UIWindow Base Classes

### SaveSelectionWindow

**File:** `game/ui/screens/save_selection_window.py:96–151`  
**Base class:** `pygame_gui.elements.UIWindow` (line 96)

| Criterion | Status | Detail |
|-----------|:------:|--------|
| Inline `getattr(type(self), 'bypass_init', False)` guard | ✓ | Line 133 |
| Assigns `self.ui_manager = manager` in bypass | ✓ | Line 134 |
| Assigns `self._window_init_bypassed = True` in bypass | ✓ | Line 135 |
| Does NOT assign `self.rect` in bypass | ✓ | No rect assignment in bypass branch |
| `ui_builder.build(self)` only when non-None | ✓ | Lines 137–138 |
| `super().__init__` only in production path | ✓ | Lines 141–147 (after guard, after bypass return) |
| All cheap state + delegates BEFORE guard | ✓ | Lines 119–129 before line 133 |

**Verdict:** Fully conformant. No issues.

**Fixture:** `tests/fixtures/save_selection_window_ui_builder.py` — `NullSaveSelectionWindowUiBuilder` + `MockSaveSelectionWindowUiBuilder` pair present. ✓

---

### RaceBrowserDialog

**File:** `game/ui/screens/race_browser_dialog.py:82–145`  
**Base class:** `pygame_gui.elements.UIWindow` (line 82)

| Criterion | Status | Detail |
|-----------|:------:|--------|
| Inline `getattr(type(self), 'bypass_init', False)` guard | ✓ | Line 128 |
| Assigns `self.ui_manager = manager` in bypass | ✓ | Line 129 |
| Assigns `self._window_init_bypassed = True` in bypass | ✓ | Line 130 |
| Does NOT assign `self.rect` in bypass | ✓ | No rect assignment in bypass branch |
| `ui_builder.build(self)` only when non-None | ✓ | Lines 131–132 |
| `super().__init__` only in production path | ✓ | Lines 135–141 (after guard, after bypass return) |
| All cheap state + delegates BEFORE guard | ✓ | Lines 115–125 before line 128 |

**Verdict:** Fully conformant. No issues.

**Fixture:** `tests/fixtures/race_browser_dialog_ui_builder.py` — `NullRaceBrowserDialogUiBuilder` + `MockRaceBrowserDialogUiBuilder` pair present. ✓

---

### DesignSelectorWindow

**File:** `game/ui/screens/design_selector_window.py:45–107`  
**Base class:** `UIWindow` (imported from `pygame_gui.elements`, line 17; used at line 45)

| Criterion | Status | Detail |
|-----------|:------:|--------|
| Inline `getattr(type(self), 'bypass_init', False)` guard | ✓ | Line 96 |
| Assigns `self.ui_manager = manager` in bypass | ✓ | Line 97 |
| Assigns `self._window_init_bypassed = True` in bypass | ✓ | Line 98 |
| Does NOT assign `self.rect` in bypass | ✓ | No rect assignment in bypass branch |
| `ui_builder.build(self)` only when non-None | ✓ | Lines 99–100 |
| `super().__init__` only in production path | ✓ | Lines 103–104 (after guard, after bypass return) |
| All cheap state + delegates BEFORE guard | ✓ | Lines 68–93 before line 96 |

**Verdict:** Fully conformant. No issues.

**Fixture:** `tests/fixtures/design_selector_window_ui_builder.py` — `NullDesignSelectorWindowUiBuilder` + `MockDesignSelectorWindowUiBuilder` pair present. ✓

---

## Quick Scan (EventLogWindow, StarListWindow)

### EventLogWindow

**File:** `game/ui/screens/event_log_window.py:75–155`  
**Base class:** `StrategyModalWindow` (line 75)

- ✅ Follows the StrategyModalWindow subclass pattern: Stage 1 cheap state (lines 115–133), Stage 2 `super().__init__` (lines 141–147), Stage 3 bypass check + builder (lines 150–155).
- ✅ `_window_init_bypassed` check uses correct post-super pattern (line 150).
- ✅ `ui_builder` parameter with default `None` (line 112).
- ✅ 4 widget refs initialized to `None` in Stage 1: `data_source` (128), `column_manager` (129), `virtual_table` (130), `sidebar` (133).

| Severity | Finding |
|----------|---------|
| **MINOR** | Several filter-button and panel widget refs (`sidebar_panel`, `header_panel`, `table_panel`, `btn_all`, `btn_combat`, `btn_production`, `btn_colonies`, `btn_fleet_ops`, `filter_buttons`) are NOT initialized in Stage 1. They are created by `_init_layout()` (called from the builder in Stage 3). While these are never accessed between Stage 2 and Stage 3 (production guarantees the builder runs first), the pattern convention would place them as `None` placeholders in Stage 1. No behavioral impact. |

**Fixture:** `tests/fixtures/event_log_window_ui_builder.py` — `NullEventLogWindowUiBuilder` + `MockEventLogWindowUiBuilder` pair present. ✓

---

### StarListWindow

**File:** `game/ui/screens/star_list_window.py:140–232`  
**Base class:** `DataListWindowMixin, StrategyModalWindow` (line 128)

- ✅ Follows the StrategyModalWindow subclass pattern: Stage 1 cheap state (lines 155–216), Stage 2 `super().__init__` (lines 219–224), Stage 3 bypass check + builder (lines 227–232).
- ✅ `_window_init_bypassed` check uses correct post-super pattern (line 227).
- ✅ `ui_builder` parameter with default `None` (line 143).
- ✅ Explicit initializations in Stage 1: `self.selected_star = None` (157), `self.btn_navigate = None` (158), `self.ui_filters = {}` (191).

| Severity | Finding |
|----------|---------|
| **MINOR** | Several sidebar and table widget refs (`sidebar_panel`, `sidebar_scroller`, `txt_name_filter`, `btn_all_types`, `btn_none_types`, `btn_apply`, `btn_save_preset`, `txt_preset_name`, `dd_presets`, `main_panel`, `column_manager`, `data_source`, `selection`, `virtual_table`) are NOT initialized in Stage 1. They are created by the `StarListWindowUiBuilder` in Stage 3. Same pattern-convention gap as EventLogWindow — no behavioral impact since builder always runs before any event handler. |

**Fixture:** `tests/fixtures/star_list_window_ui_builder.py` — `NullStarListWindowUiBuilder` + `MockStarListWindowUiBuilder` pair present. ✓

---

## Summary

| Area | Files | Verdict |
|------|-------|---------|
| Behavioral parity (EmpirePanelWindow) | 1 | ✅ Correct. 1 OBSERVATION. |
| Pattern §33 conformance (EmpireBuildQueueWindow) | 1 | ⚠️ 1 MAJOR: missing 8 widget ref placeholders in Stage 1. |
| Mixed UIWindow base classes | 3 | ✅ All 3 fully conformant. All 6 checklist items pass. |
| Quick scan remaining files | 2 | ✅ Both follow StrategyModalWindow pattern. 2 MINOR: incomplete widget ref placeholders in Stage 1. |

### Severity tally
- **CRITICAL:** 0
- **MAJOR:** 1 (EmpireBuildQueueWindow — `tests/fixtures/empire_build_queue_window_ui_builder.py:24` Null builder + `kill()` crash risk)
- **MINOR:** 2 (EventLogWindow, StarListWindow — incomplete widget ref placeholders)
- **OBSERVATION:** 1 (EmpirePanelWindow — `load_resource_icons()` in Stage 1)
