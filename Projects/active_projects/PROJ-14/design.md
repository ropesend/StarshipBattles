# PROJ-14: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Test Baseline
- **Date:** 2026-01-25
- **Result:** 4561 passed, 1 failed (pre-existing), 1 skipped
- **Pre-existing Failure:** `tests/unit/test_advanced_fleet_orders.py::TestAdvancedFleetOrders::test_intercept_integration` - mock assertion issue (unrelated to Phase 1)

### Phase 1 Scope Verification

Based on deep code review with 6 specialized agents, Phase 1 has **five task areas**:

#### 1. File/Directory Deletion (Low Risk)
| Item | Status | Safe to Delete |
|------|--------|----------------|
| `Debugging/Marked_for_Deletion_2026-01-20/` | DOES NOT EXIST | N/A (already cleaned) |
| `Marked_For_Deletion_2026-01-21_07-33/` (45MB) | EXISTS | YES - no dependencies |
| `MagicMock/` (4KB) | EXISTS | YES - test artifacts |
| 15 debug tools in `Tools/` | ALL EXIST | YES - no dependencies |

#### 2. Log File Handling
Log files (`battle.log`, `combat_lab.log`, `crash_log.txt`) are **ACTIVELY CREATED** by the application:
- `battle.log` - Created by `game/core/logger.py:36`
- `combat_lab.log` - Created by `simulation_tests/logging_config.py:31`
- `crash_log.txt` - Created by `game/app.py:725-726`

**Decision:** Delete from repo AND add to `.gitignore` to prevent future tracking.

#### 3. Commented Code Removal (Low Risk)
5 of 6 locations verified:

| File | Location | Status |
|------|----------|--------|
| `ui/test_lab_scene.py` | Lines 3657-3741 (deprecated method) | FOUND |
| `ui/test_lab_scene.py` | Lines 1941-1942, 2167-2168, 2585-2586, 2718-2719 (debug imports) | ALL FOUND |
| `game/core/profiling.py` | Line 108 | FOUND |
| `simulation_tests/tests/test_example_scenarios.py` | Lines 92-99 | FOUND |
| `tests/unit/combat/test_pdc.py` | Lines 130-131 | FOUND |
| `Tools/process_planet_images.py` | Lines 28-32 | FOUND |
| `game/core/logger.py` | Line 38 | **NOT FOUND** - file refactored |

#### 4. Legacy Button Migration (Moderate Complexity)

**Legacy Button Class:** `ui/components.py` (102 lines)
- Contains: `Button`, `Label`, `Slider` classes
- Only `Button` is actively used

**Usage Locations:**
| File | Instances | Notes |
|------|-----------|-------|
| `game/app.py:125-137` | 10 buttons | Main menu - `update_menu_buttons()` |
| `ui/test_lab_scene.py:52` | 1 button | JSONPopup close button |
| `ui/test_lab_scene.py:153-159` | 2 buttons | ConfirmationDialog confirm/cancel |
| `ui/test_lab_scene.py:2321` | 1 button | TestLabScene back button |
| `tests/unit/ui/test_ui_widgets.py` | Test file | Tests legacy Button (delete) |

**Total Migration Scope:** 14 production buttons + delete test file

#### 5. Test Updates
- Delete `tests/unit/ui/test_ui_widgets.py` (11 tests for obsolete widgets)
- Integration tests cover actual menu behavior

---

## Swarm Findings Summary

### Architecture Analysis (Agent: Architecture Analyst)

**Main Game Loop Pattern (`game/app.py`):**
```
run() loop
  ├─ pygame.event.get() → events list
  └─ _handle_normal_events(events)
       └─ _forward_event_to_scene(event) [by current state]
            ├─ MENU: for btn in menu_buttons: btn.handle_event()
            ├─ STRATEGY: strategy_scene.ui.handle_event()
            └─ TEST_LAB: test_lab_scene.handle_input([event])
```

**Key Finding:** Menu state has mixed UI handling:
- Legacy Button instances for main menu options
- pygame_gui.UIManager only for sub-dialogs (Load Game, Race Setup, New Game)

**Main Menu Button Creation (`game/app.py:125-137`):**
```python
def update_menu_buttons(self):
    self.menu_buttons = [
        Button(WIDTH // 2 - 100, HEIGHT // 2 - 320, 200, 50, "Quickstart 1P", self.start_quickstart_1p),
        # ... 9 more buttons with 70px vertical spacing
    ]
```

### Dependency Mapping (Agent: Dependency Mapper)

**Import Chain:**
```
ui/__init__.py (line 2)
  └─ from .components import Button, Label, Slider

game/app.py (line 17)
  └─ from ui import Button

ui/test_lab_scene.py (line 9)
  └─ from ui.components import Button

tests/unit/ui/test_ui_widgets.py (line 4)
  └─ from ui import Button, Label, Slider
```

**Circular Import Risk:** NONE - UI package is simple with no back-imports

**Debug Tools:** All 15 files are completely isolated. Zero imports from other code.

### Test Impact Analysis (Agent: Test Impact Analyst)

**Tests That Will Be Affected:**
1. `tests/unit/ui/test_ui_widgets.py` - All 11 tests (DELETE FILE)
   - TestButton: 4 tests
   - TestLabel: 3 tests
   - TestSlider: 4 tests

**Tests That Cover Migrated Code:**
- `tests/unit/test_app_integration.py` - App initialization tests
- `tests/unit/ui/test_test_lab_scene.py` - Test lab logic tests (no widget changes)

**Gap Identified:** No end-to-end main menu integration tests exist

### Pattern Reference (Agent: Pattern Scout)

**UIButton Creation Pattern (from `save_selection_window.py:80-85`):**
```python
self.btn_load = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(10, button_y, button_width, 40),
    text="Load",
    manager=self.ui_manager,
    container=container
)
```

**Event Handling Pattern (from `save_selection_window.py:198-210`):**
```python
def process_event(self, event: pygame.event.Event) -> bool:
    handled = super().process_event(event)

    if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.btn_load:
            self._on_load_clicked()
            handled = True

    return handled
```

**Theme Configuration (`data/builder_theme.json:39-55`):**
```json
"button": {
    "colours": {
        "normal_bg": "#1e2530",
        "hovered_bg": "#283040",
        "normal_text": "#aabbdd",
        "hovered_text": "#ddeeff"
    },
    "misc": {
        "shape": "rounded_rectangle",
        "shape_corner_radius": "4"
    }
}
```

### Risk Assessment (Agent: Risk Assessor)

**Risk 1: Main Menu Critical Path (HIGH)**
- Menu is first thing users see
- If migration fails → game unplayable
- **Mitigation:** Test thoroughly after Phase 3; rollback plan (`git revert`)

**Risk 2: Test Lab Dialogs (MEDIUM)**
- If buttons fail → dialogs can't be dismissed
- **Mitigation:** Test each dialog after Phase 4

**Risk 3: Log File Regeneration (LOW)**
- Deleted logs will regenerate on next run
- **Mitigation:** Adding to .gitignore prevents future tracking

### Data Flow Analysis (Agent: Data Flow Tracer)

**Button Callbacks in `game/app.py`:**

| Button | Callback | State Transition |
|--------|----------|------------------|
| Quickstart 1P | `start_quickstart_1p()` | MENU → STRATEGY |
| Quickstart 2P | `start_quickstart_2p()` | MENU → STRATEGY |
| New Game | `start_strategy_layer()` | Shows dialog |
| Load Game | `show_load_menu()` | Shows dialog |
| Race Setup | `start_race_setup()` | Shows dialog |
| Design Workshop | `start_builder()` | MENU → BUILDER |
| Battle Setup | `start_battle_setup()` | MENU → BATTLE_SETUP |
| Formation Editor | `start_formation_editor()` | MENU → FORMATION |
| Combat Lab | `start_test_lab()` | MENU → TEST_LAB |
| Research Tree | `start_research_tree()` | MENU → RESEARCH_TREE |

**Event Handling Difference:**
- **Legacy:** `button.callback()` fires immediately on click
- **pygame_gui:** `pygame_gui.UI_BUTTON_PRESSED` event → check `event.ui_element` → call handler

---

## Key Patterns to Reuse

- **UIButton Creation**: `game/ui/screens/save_selection_window.py:80-85` - standard button pattern
- **Event Handling**: `game/ui/screens/save_selection_window.py:198-210` - UI_BUTTON_PRESSED pattern
- **Theme Styling**: `data/builder_theme.json:39-55` - button color/shape definitions
- **Callback Mapping**: Store `{button: callback}` dict for event routing

---

## Dependencies & Risks

1. **Main menu is critical path** - First thing users see; thorough testing required
2. **Event architecture change** - From direct callbacks to event-based; preserve all state transitions
3. **Test file deletion** - 11 tests removed; integration tests provide coverage

---

## Opportunities Discovered

- Tools directory has independent Button classes (`component_manager.py`, `component_graphic_picker.py`) - these are tool-specific and should NOT be migrated
- pygame_gui theme file already has complete button styling - no custom styling needed

---

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
