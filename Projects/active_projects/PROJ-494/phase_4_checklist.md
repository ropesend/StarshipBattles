# Phase 4: CAT-11 fragile assertion + CAT-12 logic-heavy (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace exact-value/format assertions and logic-heavy test bodies in UI-family tests. Inherited from PROJ-480 Phases 4 + 5 — combined here because the UI scope is small (8 tasks) and the techniques (named constants, regex, pre-computed values) overlap.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 4.1: test_design_report_panel.py — magic number 750
**File:** `tests/unit/ui/panels/test_design_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_design_report_panel.py`
**Origin:** PROJ-480 T4.5

- [ ] Replace `assert width == 750` (PROJ-480 cited lines 267-273) with assertion against named constant (`DEFAULT_PANEL_WIDTH`) or property (`0 < width < 2000`).
- [ ] Verify: passes; LOC delta ≈ +1.

### Task 4.2: test_workshop_event_router_select_component.py — formula duplication
**File:** `tests/unit/ui/screens/test_workshop_event_router_select_component.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_event_router_select_component.py`
**Origin:** PROJ-480 T4.6

- [ ] Replace formula `50 * sqrt(2000/1000)` duplication (PROJ-480 cited lines 79-91) with property assertions (`mass > 50`, `mass / expected_base in [0.9, 1.1]`).
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 4.3: test_test_run_card.py — exact format substrings
**File:** `tests/unit/ui/screens/test_lab/test_test_run_card.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/test_test_run_card.py`
**Origin:** PROJ-480 T4.7

- [ ] Replace exact-substring asserts `"Failed Metric:"` / `"1P 1F 0W"` (PROJ-480 cited lines 148, 150) with regex or contains-key assertions.
- [ ] Verify: passes; LOC delta ≈ 0.

### Task 4.4: test_weapons_renderer.py — 9 hardcoded format strings
**File:** `tests/unit/ui/screens/builder/test_weapons_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_weapons_renderer.py`
**Origin:** PROJ-480 T4.8

- [ ] Replace exact ordered list assertion (PROJ-480 cited lines 107-118) with structural assertions (each string contains expected key-value pair) rather than exact strings.
- [ ] Verify: passes; LOC delta ≈ +5.

### Task 4.5: test_list_windows.py — exact pixel coords
**File:** `tests/unit/ui/screens/strategy_windows/test_list_windows.py`
**Tests:** `pytest tests/unit/ui/screens/strategy_windows/test_list_windows.py`
**Origin:** PROJ-480 T4.9

- [ ] Replace `rect.topleft == (50, 40)` / `rect.size == (900, 720)` (PROJ-480 cited lines 64-65) with assertions against named layout constants or shape (`topleft[0] > 0`).
- [ ] Verify: passes; LOC delta ≈ 0.

### Task 4.6: test_build_queue_panel_factory.py — 5-level os.path.dirname
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Origin:** PROJ-480 T5.3

- [ ] Replace 5-level `os.path.dirname` chain to reach `data/builder_theme.json` (PROJ-480 cited lines 208-234) with `Paths` module for repo-root resolution. Move to integration tests.
- [ ] Verify: passes; LOC delta ≈ -10.

**Notes:** Same file is touched by Phase 2 Task 2.1 (T2.3 mock UI fixture). Run Phase 2 first.

### Task 4.7: test_new_game_setup.py — for-loop with manual delta calc
**File:** `tests/unit/ui/test_new_game_setup.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`
**Origin:** PROJ-480 T5.6

- [ ] Replace loop-with-runtime-max_jump-computation (PROJ-480 cited lines 154-165) with `all(system_count_slider_curve(t+1) - system_count_slider_curve(t) <= 1 for t in range(0, 99))`.
- [ ] Replace loop-with-manual-accumulator (PROJ-480 cited lines 185-191) with `all(curve(t) >= curve(t-1) for t in range(1, 1001))`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 4.8: test_camera_zoom.py — inline derivation comments
**File:** `tests/integration/ui/test_camera_zoom.py`
**Tests:** `pytest tests/integration/ui/test_camera_zoom.py`
**Origin:** PROJ-480 T5.7

- [ ] Replace 29-line derivation comments + inline expected-value computation (PROJ-480 cited lines 51-97) with pre-computed expected constants from engineering notes; assert on the constant.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 4.9: test_spec_compiler.py — nested ship-tuple capture loops
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Origin:** PROJ-480 T5.16

- [ ] Extract snapshot-capture logic (39-LOC nested loops, PROJ-480 cited lines 297-335) into a helper function so the assertion stays compact.
- [ ] Verify: passes; LOC delta ≈ -25.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-494 complete
