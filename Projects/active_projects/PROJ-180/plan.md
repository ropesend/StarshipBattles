# PROJ-180: PROJ-172 Post-Refactor Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-180` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-180 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Ghost Code | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Eradicate Backward Compat Properties | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract WeaponsInputHandler | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Planning - Awaiting Approval
**Last Action:** Plan created from PROJ-172 audit findings + independent code review
**Next Action:** User approval, then begin Phase 1
**Blockers:** None
**Baseline:** 12338 passed, 1 skipped, 0 failures

## Overview
Clean up remaining issues from the PROJ-172 god-class MVVM decomposition. Three categories of work:
1. Delete confirmed ghost code (trivial)
2. Eradicate backward-compatibility property shims in BuildQueueScreen and update all callers (medium)
3. Extract tooltip hover geometry from WeaponsReportPanel into a new WeaponsInputHandler (medium)

## Goals
- Eradicate all backward-compatibility shims per project policy (no "just in case" layers)
- Complete MVVM separation in WeaponsReportPanel by extracting InputHandler
- Remove dead code that misleads future maintainers

## Scope
**In:**
- Ghost code deletion in `empire_build_queue_sidebar.py`
- Backward-compat property removal in `build_queue_screen.py` + all caller updates
- WeaponsInputHandler extraction from `weapons_panel.py`
- Test updates for all of the above

**Out:**
- TestLabScreen controller delegation properties (necessary, not backward-compat shims)
- FormationEditor refactoring (already clean decomposition)
- BattleStateViewer changes (appropriate single-class pattern)
- "Why" comment improvements (documentation polish, not structural)

## Key Files
| Component | File Path |
|-----------|-----------|
| Ghost code | `game/ui/screens/empire_build_queue_sidebar.py` |
| Backward compat properties | `game/ui/screens/build_queue_screen.py` |
| Tooltip hover geometry | `game/ui/screens/builder/weapons_panel.py` |
| Weapons ViewModel | `game/ui/screens/builder/weapons_viewmodel.py` |
| Unit test - build queue | `tests/unit/ui/screens/test_build_queue_screen.py` |
| Unit test - hotkeys | `tests/unit/ui/screens/test_sub_window_hotkeys.py` |
| Integration - basics | `tests/integration/ui/build_queue_screen/test_basics.py` |
| Integration - formatting | `tests/integration/ui/test_build_queue_formatting.py` |
| Integration - drag drop | `tests/integration/ui/test_build_queue_drag_drop.py` |
| Integration - queue sel | `tests/integration/ui/build_queue_screen/test_queue_selector.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- `Projects/active_projects/PROJ-172/review_report.md` - Original audit report

## Initial Analysis
Independent code review by 5 parallel agents confirmed all audit findings:
- `get_column_visibility_changed()` is pure ghost code: always returns False, zero callers in entire codebase
- 14 backward-compat properties exist in BuildQueueScreen, all delegating to `self.panels.*` or `self.renderer.*`
- 8 of 14 properties have zero production callers (test-only); remaining 6 have internal-only production usage
- `_check_tooltip_hover` performs 4 geometry calculations that violate MVVM separation
- No WeaponsInputHandler exists yet; pattern precedent exists in FormationInputHandler

## Swarm Findings Summary
### Architecture
- All 6 decomposed classes have clean dependency graphs with zero circular imports
- MVVM compliance ranges from 70% (BuildQueueScreen) to 98% (TestLabScreen)
- BattleStateViewer appropriately remains a single class (thin utility, no decomposition needed)

### Key Patterns to Reuse
- **FormationInputHandler**: `game/ui/screens/formation/input_handler.py` - precedent for pixel-to-game-unit mapping in InputHandler
- **EventBus pattern**: Already used in WeaponsViewModel for state change notifications

### Risks Identified
1. **Test coupling to backward-compat properties** - ~50 references across 6 test files need updating. Mitigation: systematic file-by-file updates with test runs after each.
2. **test_sub_window_hotkeys dual-path mocking** - Tests set properties on both `screen.*` and `screen.panels.*`. Need careful review to avoid breaking mock wiring.

---

## Phases

### Phase 1: Delete Ghost Code [Simple]
**Objective:** Remove the dead `get_column_visibility_changed()` method
**Status:** Not Started

#### Task 1.1: Delete ghost method from sidebar [Simple]
**File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -x`
- [ ] Delete the section comment at line 261-263 (`# Column State Access...`)
- [ ] Delete method `get_column_visibility_changed()` at lines 265-276
- [ ] Run tests to verify no breakage
**Notes:**

---

### Phase 2: Eradicate Backward Compatibility Properties [Medium]
**Objective:** Remove all 14 backward-compat property shims from BuildQueueScreen and update every caller to use `screen.panels.*` or `screen.renderer.*` directly
**Status:** Not Started

#### Task 2.1: Update unit test - test_build_queue_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py -x`
- [ ] Line 468: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 470: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Line 475: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 533: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 535: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Line 540: `screen.queue_items = [MagicMock()...]` → `screen.renderer.queue_items = [MagicMock()...]`
- [ ] Line 542: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Run tests to verify
**Notes:**

#### Task 2.2: Update unit test - test_sub_window_hotkeys.py [Simple]
**File:** `tests/unit/ui/screens/test_sub_window_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py -x`
- [ ] Line 125: `screen.btn_close = MagicMock()` → `screen.panels.btn_close = MagicMock()`
- [ ] Line 128-131: `screen.btn_category_*` → `screen.panels.btn_category_*` (4 lines)
- [ ] Line 227: `screen.btn_close.set_tooltip` → `screen.panels.btn_close.set_tooltip`
- [ ] Line 245-248: `screen.btn_category_*.set_tooltip` → `screen.panels.btn_category_*.set_tooltip` (4 lines)
- [ ] Check lines 218, 236 for dual-path mock wiring — if `screen.panels.btn_close = screen.btn_close` exists, simplify to direct `screen.panels.btn_close` usage
- [ ] Run tests to verify
**Notes:**

#### Task 2.3: Update integration test - test_basics.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_basics.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py -x`
- [ ] Lines 136-137: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [ ] Lines 142-143: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Lines 148-149: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Lines 152-155: `build_queue_screen.btn_category_*` → `build_queue_screen.panels.btn_category_*` (4 lines)
- [ ] Lines 160-161: `build_queue_screen.btn_close` → `build_queue_screen.panels.btn_close`
- [ ] Update any `hasattr` checks to reference `panels.*` path
- [ ] Run tests to verify
**Notes:**

#### Task 2.4: Update integration test - test_build_queue_formatting.py [Simple]
**File:** `tests/integration/ui/test_build_queue_formatting.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py -x`
- [ ] Line 141-142: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [ ] Line 147: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Line 163: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [ ] Line 179: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Line 197: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Line 216: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Lines 233-234: `build_queue_screen.design_report` → `build_queue_screen.panels.design_report`
- [ ] Run tests to verify
**Notes:**

#### Task 2.5: Update integration test - test_build_queue_drag_drop.py [Simple]
**File:** `tests/integration/ui/test_build_queue_drag_drop.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py -x`
- [ ] Line 118: `build_queue_screen.items_scrollable` → `build_queue_screen.panels.items_scrollable`
- [ ] Line 157: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [ ] Line 207: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [ ] Lines 232-233: `build_queue_screen.queue_scrollable` → `build_queue_screen.panels.queue_scrollable`
- [ ] Line 255: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [ ] Run tests to verify
**Notes:**

#### Task 2.6: Update integration test - test_queue_selector.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -x`
- [ ] Line 374: `bq.queue_items` → `bq.renderer.queue_items`
- [ ] Run tests to verify
**Notes:**

#### Task 2.7: Delete backward-compat properties from BuildQueueScreen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ -n 12` (full suite — this is the critical deletion step)
- [ ] Delete the section comment at lines 157-159 (`# Backward Compatibility Properties...`)
- [ ] Delete all 14 property definitions at lines 161-234 (queue_items getter/setter, filter_panel, items_list_panel, planet_report, btn_close, btn_category_complex, btn_category_ship, btn_category_satellite, btn_category_fighter, background, items_scrollable, build_queue_panel, queue_scrollable, design_report)
- [ ] Run full test suite to verify zero breakage
**Notes:**

---

### Phase 3: Extract WeaponsInputHandler [Medium]
**Objective:** Move tooltip hover geometry calculations from WeaponsReportPanel into a new WeaponsInputHandler, completing MVVM separation
**Status:** Not Started

#### Task 3.1: Create WeaponsInputHandler [Medium]
**File:** `game/ui/screens/builder/weapons_input_handler.py` (new file)
**Tests:** `pytest tests/unit/ui/builder/ -x`
- [ ] Create `WeaponsInputHandler` class with:
  - `detect_tooltip_hover(weapon, ship, bar_y, start_x, weapon_bar_width, bar_width, weapon_range, content_rect, mouse_pos, viewmodel) -> Optional[dict]`
  - Move geometry logic from `_check_tooltip_hover` (lines 316-335 of weapons_panel.py): content_rect collision, hit_rect collision, pixel-to-ratio mapping, ratio-to-range mapping
  - Keep ViewModel tooltip data call: `viewmodel.calculate_tooltip_data(weapon, ship, hover_range)`
- [ ] Add module docstring explaining role in MVVM pattern
- [ ] No pygame imports needed (use tuple coordinates and Rect from caller)
**Notes:** Follow FormationInputHandler pattern for structure

#### Task 3.2: Write unit tests for WeaponsInputHandler [Simple]
**File:** `tests/unit/ui/builder/test_weapons_input_handler.py` (new file)
**Tests:** `pytest tests/unit/ui/builder/test_weapons_input_handler.py -x`
- [ ] Test `detect_tooltip_hover` returns None when mouse outside content_rect
- [ ] Test `detect_tooltip_hover` returns None when mouse outside hit_rect
- [ ] Test `detect_tooltip_hover` correctly maps pixel position to hover range
- [ ] Test `detect_tooltip_hover` clamps hover_range to [0, weapon_range]
- [ ] Test `detect_tooltip_hover` returns tooltip_data with 'pos' key set
**Notes:**

#### Task 3.3: Wire WeaponsInputHandler into WeaponsReportPanel [Simple]
**File:** `game/ui/screens/builder/weapons_panel.py`
**Tests:** `pytest tests/unit/ui/builder/ -x`
- [ ] Import `WeaponsInputHandler` at top of file
- [ ] Create `self._input_handler = WeaponsInputHandler()` in `__init__`
- [ ] In `draw()` method, replace `self._check_tooltip_hover(...)` call with `self._input_handler.detect_tooltip_hover(...)`
- [ ] Delete `_check_tooltip_hover` method (lines 316-335)
- [ ] Update module docstring to mention WeaponsInputHandler role
- [ ] Run tests to verify
**Notes:**

#### Task 3.4: Full regression test [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] Verify 12338+ tests pass, 0 failures
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 12338 passed, 1 skipped (baseline established 2026-02-24)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new warnings introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] All backward-compat properties deleted from build_queue_screen.py
- [ ] `get_column_visibility_changed` deleted from empire_build_queue_sidebar.py
- [ ] WeaponsInputHandler extracted and tested
- [ ] No references to deleted properties remain in codebase

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (ghost code deleted)
- [ ] Phase 2 complete (backward-compat properties eradicated)
- [ ] Phase 3 complete (WeaponsInputHandler extracted)
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
