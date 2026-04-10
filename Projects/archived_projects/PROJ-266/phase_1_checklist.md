# Phase 1: BattleResultsScreen Test Coverage (0% -> meaningful)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-266 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write tests for `BattleResultsScreen` covering initialization, event handling, scroll logic, return navigation, and pure helper functions. No production code changes.

---

## Prerequisites

- [ ] Read `game/ui/screens/battle_results_screen.py` (279 LOC)
- [ ] Read `game/ui/screens/battle_results_data.py` for dataclass structure (test fixtures)
- [ ] Read `tests/unit/ui/test_battle_results_data.py` for existing mock patterns

---

## Tasks

### Task 1.1: Create Test File with Fixtures [Simple]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v`

Create the test file with shared fixtures for `BattleResults`, `ShipResult`, `TeamSummary`, and `WeaponStats` dataclasses. Mock pygame.Surface and fonts.

- [ ] Create `tests/unit/ui/screens/test_battle_results_screen.py`
- [ ] Add helper function to build `BattleResults` with realistic test data (2 teams, 2-3 ships each, weapons)
- [ ] Add helper function to build minimal `BattleResults` (empty ships list)
- [ ] Add pygame mock fixture (mock `pygame.Surface`, `get_font` returns mock font with mock `render()` returning mock surface with `get_rect()`, `get_width()`, `get_height()`)
- [ ] Verify: file imports correctly, no import errors

**Notes:** Use real frozen dataclasses from `battle_results_data.py`, not mocks. Only mock pygame objects.

---

### Task 1.2: Test `_hp_color` Pure Function [Simple]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v -k "hp_color"`

Module-level function `_hp_color(percent)` returns color tuples based on HP thresholds. Pure function, no pygame dependency.

- [ ] Write failing test: `_hp_color(0)` returns `HP_DESTROYED`
- [ ] Write failing test: `_hp_color(-5)` returns `HP_DESTROYED` (below zero)
- [ ] Write failing test: `_hp_color(10)` returns `HP_CRITICAL` (0 < percent < 20)
- [ ] Write failing test: `_hp_color(30)` returns `HP_DAMAGED` (20 <= percent < 50)
- [ ] Write failing test: `_hp_color(50)` returns `HP_HEALTHY` (>= 50)
- [ ] Write failing test: `_hp_color(100)` returns `HP_HEALTHY`
- [ ] Verify: all pass (these test existing code)

**Notes:** Import `_hp_color` and the color constants directly. These are boundary value tests.

---

### Task 1.3: Test Initialization and State [Simple]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v -k "init"`

Test that `BattleResultsScreen.__init__` stores parameters correctly and initializes scroll offsets.

- [ ] Write failing test: constructor stores `screen_width`, `screen_height`, `results`, `scene_callback`
- [ ] Write failing test: scroll offsets initialized to 0
- [ ] Write failing test: `handle_resize()` updates stored dimensions
- [ ] Verify: all pass (mock `get_font` to avoid pygame.font.init)

**Notes:** Must patch `game.ui.fonts.get_font` since constructor calls it. Return a mock font object.

---

### Task 1.4: Test Scroll Logic [Medium]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v -k "scroll"`

Test `_handle_scroll()` method which manages per-column scroll state.

- [ ] Write failing test: mouse_x < midpoint scrolls left column (`_scroll_offset_0`)
- [ ] Write failing test: mouse_x >= midpoint scrolls right column (`_scroll_offset_1`)
- [ ] Write failing test: scroll offset cannot go below 0 (clamped with `max(0, ...)`)
- [ ] Write failing test: positive delta increases scroll offset
- [ ] Verify: all pass

**Notes:** `_handle_scroll(delta, mouse_x)` uses `self.screen_width // 2` as the midpoint.

---

### Task 1.5: Test Return Navigation [Medium]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v -k "return"`

Test `_trigger_return()` and the event paths that invoke it.

- [ ] Write failing test: `_trigger_return()` calls `scene_callback("return_to_destination", destination=...)` with results' return_destination
- [ ] Write failing test: `_trigger_return()` does nothing when `scene_callback` is None
- [ ] Write failing test: keyboard ESCAPE triggers return (via `handle_event`)
- [ ] Write failing test: keyboard RETURN triggers return (via `handle_event`)
- [ ] Verify: all pass

**Notes:** For keyboard tests, construct mock `pygame.event.Event` with `type=pygame.KEYDOWN` and `key=pygame.K_ESCAPE`/`K_RETURN`. Must mock `get_font` in constructor.

---

### Task 1.6: Test Return Button Text Mapping [Simple]
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py -v -k "button_text"`

The `_draw_footer` method maps `return_destination` to button text. Test the mapping logic indirectly by verifying the dictionary in the method.

- [ ] Write test: verify return text mapping covers "test_lab" -> "Return to Combat Lab"
- [ ] Write test: verify return text mapping covers "battle_setup" -> "Return to Battle Setup"
- [ ] Write test: verify return text mapping covers "strategy" -> "Return to Strategy Map"
- [ ] Write test: verify unknown destination falls back to "Return"
- [ ] Verify: all pass

**Notes:** The mapping dict `_RETURN_TEXT` is local to `_draw_footer`. To test it, either call `draw()` with a mock surface and verify the font.render call args, or test the screen's `results.return_destination` propagation through `_trigger_return`. The simplest approach: call `draw()` on a mock surface and check what text was rendered by examining mock font `render()` call args.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/ui/screens/test_battle_results_screen.py -v`
- [ ] No test uses pixel-level assertions (no asserting exact coordinates or color values on surfaces)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
