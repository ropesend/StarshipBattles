# Duplication Analysis: game/ui/screens/ and game/ui/panels/

**Scan Date:** 2026-02-13
**Shard:** game/ui/screens/, game/ui/panels/
**Files Analyzed:** 85+ Python files

---

## Executive Summary

This report documents code duplication, near-duplicates, and fragmented implementations found in the UI screens and panels directories. The codebase shows evidence of active refactoring (e.g., BaseGallery extraction), but several patterns of duplication remain.

**Key Statistics:**
- 3 CRITICAL findings (significant impact on maintainability)
- 5 MAJOR findings (moderate impact, should be addressed)
- 8 MINOR findings (localized issues, low priority)
- 4 INFO findings (observations, potential future improvements)

---

## Findings

### CRITICAL

#### CRITICAL: Duplicate Transfer Dialog Implementations
**ID:** DUP-UI1-001

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\transfer_dialog.py` (337 lines)
- `C:\Dev\Starship Battles\game\ui\screens\cargo_quick_dialog.py` (326 lines)

**Description:**
Two dialog classes implement nearly identical cargo/population transfer functionality with significant code overlap:

1. **Common patterns duplicated:**
   - Colony/planet lookup logic (`get_planets_at_hex`, filtering for `owner_id is not None`)
   - Passenger/population iteration logic (checking `population_details` attribute)
   - Transfer command creation (`IssueTransferCommand` with identical parameters)
   - InputMapper integration for keyboard shortcuts (`_apply_tooltips`, `_handle_keydown`)
   - Slider value handling and "All" logic (amount == max -> 0)

2. **Specific duplications:**
   ```python
   # Both files have nearly identical code:
   planets = self.facade.get_planets_at_hex(self.hex_coord)
   colonies = [p for p in planets if p.owner_id is not None]

   # Both check population_details the same way:
   if hasattr(planet_info, 'population_details'):
       for race_id, count, happiness in planet_info.population_details:
   ```

**Impact:** Bug fixes must be applied to both files. Divergence risk is high.

**Recommendation:** Extract a `TransferDialogBase` class or a `TransferHelper` utility module containing:
- Colony/planet lookup methods
- Population enumeration logic
- Command construction helpers
- InputMapper tooltip/keyboard integration

---

#### CRITICAL: Repeated List Window Patterns Without Base Class
**ID:** DUP-UI1-002

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\planet_list_window.py` (517 lines)
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (1094 lines)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (864 lines)
- `C:\Dev\Starship Battles\game\ui\screens\design_selector_window.py` (552 lines)
- `C:\Dev\Starship Battles\game\ui\screens\save_selection_window.py` (396 lines)
- `C:\Dev\Starship Battles\game\ui\screens\event_log_window.py` (264 lines)

**Description:**
Multiple list-based windows share extensive structural patterns without a common base class:

1. **Duplicated patterns:**
   - Scrollbar management with `UIVerticalScrollBar` or `UIScrollingContainer`
   - Row/item rendering with alternating backgrounds
   - Filter button groups with select/unselect toggling
   - Virtual scrolling calculations (`visible_percentage`, `scroll_offset`)
   - Row click handling with collision detection
   - Kill/cleanup patterns clearing row labels

2. **Example: Filter button patterns appear identically:**
   ```python
   # planet_list_window.py, fleet_report_window.py, empire_build_queue_window.py all have:
   for key, btn in self.filter_buttons.items():
       if key == self.current_filter:
           btn.select()
       else:
           btn.unselect()
   ```

3. **Row rebuilding pattern repeated:**
   ```python
   # Appears in multiple files:
   for lbl in self.row_labels:
       lbl.kill()
   self.row_labels.clear()
   ```

**Impact:** 2000+ lines of near-duplicate code across these files. Changes to scrolling, filtering, or row rendering require updating multiple files.

**Recommendation:** Create `BaseListWindow(UIWindow)` with:
- Abstract methods: `_build_row()`, `_get_items()`, `_on_row_click()`
- Common: Filter button management, scroll handling, row clearing
- Configuration: column definitions, row height, filter categories

---

#### CRITICAL: RaceThemeGallery Does Not Extend BaseGallery
**ID:** DUP-UI1-003

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\base_gallery.py` (264 lines)
- `C:\Dev\Starship Battles\game\ui\panels\race_portrait_gallery.py` (152 lines) - extends BaseGallery
- `C:\Dev\Starship Battles\game\ui\panels\race_flag_gallery.py` (164 lines) - extends BaseGallery
- `C:\Dev\Starship Battles\game\ui\panels\race_theme_gallery.py` (202 lines) - DOES NOT extend BaseGallery

**Description:**
`RaceThemeGallery` duplicates functionality that already exists in `BaseGallery`:

1. **Duplicated code in RaceThemeGallery:**
   - `_sanitize_object_id()` method (identical implementation)
   - `set_from_config()` method (same pattern)
   - `handle_button_click()` method (same pattern)
   - Button iteration and selection logic
   - Scrolling container setup

2. **Comment indicates awareness:**
   The file header says "PROJ-12 Phase 4: Extracted from RaceSetupScreen" but unlike the other two galleries, it was never refactored to use BaseGallery in PROJ-108.

**Impact:** Inconsistent implementation. Bug fixes to gallery behavior require updating RaceThemeGallery separately.

**Recommendation:** Refactor `RaceThemeGallery` to extend `BaseGallery` by implementing the required abstract methods. This may require adding abstract methods to BaseGallery for theme-specific preview handling.

---

### MAJOR

#### MAJOR: Duplicate InputMapper Tooltip/Keyboard Integration
**ID:** DUP-UI1-004

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\transfer_dialog.py` lines 229-258
- `C:\Dev\Starship Battles\game\ui\screens\cargo_quick_dialog.py` lines 224-246
- Similar patterns likely in other dialogs

**Description:**
The InputMapper integration pattern is duplicated:

```python
def _apply_tooltips(self) -> None:
    if not self._mapper:
        return
    confirm_hint = self._mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
    if confirm_hint:
        self.btn_confirm.set_tooltip(f"... ({confirm_hint})")
    cancel_hint = self._mapper.get_display_text(InputAction.TRANSFER_CANCEL)
    if cancel_hint:
        self.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

def _handle_keydown(self, event: pygame.event.Event) -> bool:
    if not self._mapper:
        return False
    action = self._mapper.resolve(event, contexts=["transfer"])
    if action == InputAction.TRANSFER_CONFIRM:
        self._issue_order()  # or self._issue_orders()
        return True
    if action == InputAction.TRANSFER_CANCEL:
        self.kill()
        return True
    return False
```

**Impact:** Any changes to keyboard handling patterns must be applied consistently.

**Recommendation:** Create a mixin class `InputMapperMixin` or utility functions for common dialog keyboard handling.

---

#### MAJOR: Repeated ScrollingContainer Setup Patterns
**ID:** DUP-UI1-006

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\event_log_window.py` lines 100-112
- `C:\Dev\Starship Battles\game\ui\screens\design_selector_window.py` (scroll container setup)
- `C:\Dev\Starship Battles\game\ui\panels\empire_treasury_panel.py` lines 86-92
- `C:\Dev\Starship Battles\game\ui\panels\builder_widgets.py` lines 124-131
- `C:\Dev\Starship Battles\game\ui\panels\race_theme_gallery.py` lines 73-79
- Multiple other locations

**Description:**
Nearly identical UIScrollingContainer setup code appears in 10+ locations:

```python
self.scroll_container = UIScrollingContainer(
    relative_rect=pygame.Rect(x, y, width, height),
    manager=self.ui_manager,
    container=self.panel,  # or self, or parent
    allow_scroll_x=False,
    allow_scroll_y=True
)
# Then later:
self.scroll_container.set_scrollable_area_dimensions((width - N, content_height))
```

**Impact:** Inconsistent margin calculations (some use -20, some use -15), repeated boilerplate.

**Recommendation:** Create a factory function `create_vertical_scroll_container(parent, rect, manager)` that standardizes margins and setup.

---

#### MAJOR: Duplicate Resource Icon Loading
**ID:** DUP-UI1-007

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\empire_treasury_panel.py` lines 299-321 (`load_resource_icons()`)
- Similar patterns in other files loading resource icons

**Description:**
Resource icon loading with path construction and scaling is implemented as a standalone function in `empire_treasury_panel.py`. The pattern of:
1. Building path from `Paths.ASSET_DIR`
2. Loading with `pygame.image.load().convert_alpha()`
3. Scaling with `pygame.transform.smoothscale()`

...appears in multiple places throughout the UI code.

**Impact:** Inconsistent icon sizes, repeated file I/O, no caching between components.

**Recommendation:** Move `load_resource_icons()` to a shared `game/ui/assets/resource_icons.py` module with caching.

---

#### MAJOR: Similar Panel Base Classes in battle_panels.py
**ID:** DUP-UI1-008

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` - `BattlePanel`, `ShipStatsPanel`, `SeekerMonitorPanel`, `BattleControlPanel`

**Description:**
While there is a `BattlePanel` base class, the child classes still have significant code duplication:

1. **ID-based expansion tracking** appears twice:
   - `ShipStatsPanel._get_ship_id()`, `_is_expanded()`, `_toggle_expanded()`
   - `SeekerMonitorPanel._get_projectile_id()`, `_is_seeker_expanded()`, `_toggle_seeker_expanded()`

2. **Surface validation pattern** repeated:
   ```python
   if (self.surface is None or
       self.surface.get_width() != self.rect.width or
       self.surface.get_height() != self.rect.height):
       self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
   ```

**Impact:** Bug fixes to expansion tracking must be applied to both panel types.

**Recommendation:** Move ID-based expansion tracking to `BattlePanel` base class as `_get_item_id()`, `_is_item_expanded()`, `_toggle_item_expanded()`. Add `_validate_surface()` helper to base class.

---

#### MAJOR: Duplicate Graph Widget Base Logic
**ID:** DUP-UI1-009

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\strategy_widgets.py` - `DataGraph`, `SpectrumGraph`, `AtmosphereGraph`

**Description:**
While `DataGraph` provides a base class, the two subclasses have significant duplicated rendering logic:

1. **Bar drawing calculation pattern** appears twice:
   ```python
   bar_width = (self.width - 20) / len(items)
   margin_x = 10
   bottom_y = self.height - 10
   max_h = self.height - 20

   # For each bar:
   x = margin_x + i * bar_width
   y = bottom_y - bar_h
   rect = pygame.Rect(x + N, y, bar_width - M, bar_h)
   pygame.draw.rect(self.surface, color, rect)

   # Label rendering with optional rotation
   lbl = font.render(label, True, color)
   if vertical: lbl = pygame.transform.rotate(lbl, 90)
   ```

**Impact:** Any changes to bar graph rendering must be applied to both classes.

**Recommendation:** Extract `_draw_bar()` and `_draw_bar_label()` methods to `DataGraph` base class.

---

### MINOR

#### MINOR: Repeated Window Cleanup Patterns
**ID:** DUP-UI1-010

**Location:**
- Multiple window classes implement `kill()` override with callback invocation

**Description:**
The pattern of overriding `kill()` to invoke a callback appears repeatedly:

```python
def kill(self) -> None:
    if self.on_close_callback:
        self.on_close_callback()
    super().kill()
```

**Impact:** Minor - low risk of divergence.

**Recommendation:** Consider a `CallbackWindow` base class or mixin for windows that need close callbacks.

---

#### MINOR: Duplicate Font Creation
**ID:** DUP-UI1-011

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\battle_state_viewer.py` lines 117-119
- `C:\Dev\Starship Battles\game\ui\screens\battle_ui.py` line 245
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` lines 99-101, 307-309
- Many other locations

**Description:**
Font creation with `pygame.font.SysFont()` or `pygame.font.Font()` is scattered throughout:

```python
font = pygame.font.SysFont("arial", 20)
font_title = pygame.font.Font(None, 28)
```

**Impact:** Inconsistent font usage, repeated object creation.

**Recommendation:** Create a `FontManager` or `UIFonts` constants module with pre-defined font instances.

---

#### MINOR: Repeated Button Rect Calculation Pattern
**ID:** DUP-UI1-012

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\battle_ui.py` lines 222-228
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` lines 519-529

**Description:**
Centered button rect calculation appears in multiple places:

```python
button_width = 300
button_height = 60
x = (self.width - button_width) // 2
y = (self.height - button_height) // 2
return pygame.Rect(x, y, button_width, button_height)
```

**Impact:** Minor - different button sizes make extraction less valuable.

**Recommendation:** Low priority - could extract `centered_rect(width, height, parent_width, parent_height)` utility.

---

#### MINOR: Repeated Row Label Clear Pattern
**ID:** DUP-UI1-013

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\event_log_window.py` lines 197-199
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (similar)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (similar)

**Description:**
```python
for lbl in self.row_labels:
    lbl.kill()
self.row_labels.clear()
```

**Impact:** Minor - simple pattern.

**Recommendation:** Could add `kill_all_ui_elements(elements_list)` utility, but low priority.

---

#### MINOR: Formation Editor State Machine Duplication
**ID:** DUP-UI1-014

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\formation_editor.py`

**Description:**
The FormationEditorScreen has state machine logic spread across multiple `_handle_*` methods with repeated state checks:

```python
if self.state == 'PANNING':
    ...
elif self.state == 'DRAGGING_ITEMS':
    ...
elif self.state == 'RESIZING_GROUP':
    ...
elif self.state == 'POTENTIAL_CLICK':
    ...
```

**Impact:** Minor - contained within single file.

**Recommendation:** Consider using a proper state pattern with state classes, but low priority.

---

#### MINOR: Duplicate Sanitize Object ID Methods
**ID:** DUP-UI1-015

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\base_gallery.py` line 215
- `C:\Dev\Starship Battles\game\ui\panels\race_theme_gallery.py` line 157

**Description:**
Identical method:
```python
def _sanitize_object_id(self, text: str) -> str:
    return text.replace(".", "_").replace(" ", "_")
```

**Impact:** Minor - small utility function.

**Recommendation:** Should be inherited from BaseGallery when RaceThemeGallery is refactored (DUP-UI1-003).

---

#### MINOR: Repeated Color Constants
**ID:** DUP-UI1-016

**Location:**
- Multiple files define similar color tuples inline

**Description:**
Color definitions like `(20, 25, 35)` for dark backgrounds, `(60, 60, 80)` for borders appear repeatedly:

```python
# battle_panels.py
self.surface.fill((20, 25, 35, UIConfig.PANEL_ALPHA))
# battle_state_viewer.py
self.bg_color = (25, 25, 30)
# keybindings_scene.py
screen.fill((20, 25, 35))
```

**Impact:** Minor - colors are slightly different but intended to be similar.

**Recommendation:** Consolidate UI color palette in `UIConfig` or `UIColors` constants.

---

#### MINOR: Similar Handle Resize Patterns
**ID:** DUP-UI1-017

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\keybindings_scene.py` lines 289-294
- `C:\Dev\Starship Battles\game\ui\screens\menu_scene.py` lines 96-101
- `C:\Dev\Starship Battles\game\ui\screens\formation_editor.py` lines 927-934

**Description:**
Similar resize handling pattern:
```python
def handle_resize(self, width: int, height: int) -> None:
    self._width = width
    self._height = height
    self._ui_manager = pygame_gui.UIManager((width, height))
    self._build_ui()
```

**Impact:** Minor - IScene protocol requires this pattern.

**Recommendation:** Document this as a standard IScene resize pattern.

---

### INFO

#### INFO: Well-Extracted BaseGallery Pattern
**ID:** DUP-UI1-018

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\base_gallery.py`

**Description:**
The `BaseGallery` abstraction is a good example of DRY principles being applied. The abstract base class properly encapsulates:
- Scrolling container management
- Asset button creation
- Selection highlighting
- Preview panel coordination

`RacePortraitGallery` and `RaceFlagGallery` correctly extend this base class.

**Recommendation:** Use this as a template for future similar abstractions (e.g., list windows).

---

#### INFO: Existing PROJ-43 DTO Pattern
**ID:** DUP-UI1-019

**Location:**
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` - `_get_ships()` method

**Description:**
The `_get_ships()` method in `BattlePanel` shows good practice of using DTOs from `ui_service` with fallback to direct access. This pattern supports the UI's transition to a DTO-based architecture.

**Recommendation:** Continue this pattern and ensure all UI components use service methods rather than direct domain access.

---

#### INFO: FormationEditor Delegation Pattern
**ID:** DUP-UI1-020

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\formation_editor.py`

**Description:**
The `FormationEditorScreen` properly delegates to:
- `FormationCore` for data management
- `FormationRenderer` for drawing
- `FormationInputHandler` for input state

This is a good separation of concerns that could be applied to other complex screens.

**Recommendation:** Consider similar delegation patterns for `StrategyScreen` and `WorkshopScreen`.

---

#### INFO: Modular Strategy Screen Architecture
**ID:** DUP-UI1-021

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\strategy_screen.py`
- `C:\Dev\Starship Battles\game\ui\screens\strategy_*.py` (multiple support modules)

**Description:**
The strategy screen has been decomposed into multiple modules:
- `strategy_camera_nav.py`
- `strategy_colonization.py`
- `strategy_detail_formatter.py`
- `strategy_event_router.py`
- `strategy_fleet_ops.py`
- `strategy_input_handler.py`
- `strategy_menu_panel.py`
- `strategy_panel_manager.py`
- `strategy_renderer.py`
- `strategy_superweapons.py`
- `strategy_ui.py`
- `strategy_window_manager.py`

This modular approach reduces the main screen file size and improves maintainability.

**Recommendation:** Apply similar decomposition to `build_queue_screen.py` (1099 lines) if it becomes unwieldy.

---

## Summary by Severity

| Severity | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 3 | Transfer dialogs duplication, List window patterns, RaceThemeGallery not extending BaseGallery |
| MAJOR | 5 | InputMapper integration, ScrollingContainer setup, Resource icon loading, Battle panel expansion tracking, Graph widget logic |
| MINOR | 8 | Window cleanup, Font creation, Button rect calculation, Row label clearing, State machine patterns, Sanitize method, Colors, Resize handling |
| INFO | 4 | Good patterns to maintain (BaseGallery, DTO pattern, delegation, modular architecture) |

---

## Recommended Actions

### High Priority (Next Sprint)
1. **DUP-UI1-003:** Refactor `RaceThemeGallery` to extend `BaseGallery`
2. **DUP-UI1-001:** Extract `TransferHelper` from transfer dialogs

### Medium Priority (Backlog)
3. **DUP-UI1-002:** Create `BaseListWindow` abstraction
4. **DUP-UI1-006:** Create scroll container factory
5. **DUP-UI1-008:** Consolidate battle panel expansion tracking

### Low Priority (Tech Debt Tracking)
6. Minor findings can be addressed opportunistically during related work

---

*Report generated by Sweep Agent: Duplication & Fragmentation*
