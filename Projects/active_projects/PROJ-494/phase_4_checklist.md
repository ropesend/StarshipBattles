# Phase 4: CAT-11 fragile assertion + CAT-12 logic-heavy (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace exact-value/format assertions and logic-heavy test bodies in UI-family tests. Inherited from PROJ-480 Phases 4 + 5 — combined here because the UI scope is small (9 tasks) and the techniques (named constants, regex, pre-computed values) overlap.

---

## Tasks

### Task 4.1: test_design_report_panel.py — magic number 750
- [x] Replaced `assert width == 750` with property assertion (`0 < width < 2000`, `isinstance(width, int)`). 14 tests pass.

### Task 4.2: test_workshop_event_router_select_component.py — formula duplication
- [x] Replaced duplicated formula `50 * sqrt(2000/1000)` with property assertions (`mass > 50`, `mass < 150` — sensible bounds for a 2000t design). 3 tests pass.

### Task 4.3: test_test_run_card.py — exact format substrings
- [x] Replaced exact-substring asserts (`"Failed Metric:"`, `"1P 1F 0W"`) with regex patterns (`r"Failed\s*Metric\s*:"`, `r"\b1\s*P\b.*\b1\s*F\b.*\b0\s*W\b"`). 7 tests pass.

### Task 4.4: test_weapons_renderer.py — 9 hardcoded format strings
- [x] Replaced exact-ordered-list assertion with `(label, value)` pair lookup. Each line's expected label+value tested via substring inclusion; order preserved via positional iteration. 3 tests pass.

### Task 4.5: test_list_windows.py — exact pixel coords
- [x] Replaced `rect.topleft == (50, 40)` / `rect.size == (900, 720)` with shape-style assertions (`topleft[0] > 0 and topleft[1] > 0`, `width > 0 and height > 0`). 9 tests pass.

### Task 4.6: test_build_queue_panel_factory.py — 5-level os.path.dirname
- [x] Replaced 5-level `os.path.dirname(...)` chain with `Paths.get_data_dir() / "builder_theme.json"`. 5 tests pass.

### Task 4.7: test_new_game_setup.py — for-loop with manual delta calc
- [x] Replaced loop-with-runtime-max-jump with `all(curve(t+1) - curve(t) <= 1 for t in range(0, 99))`. Replaced loop-with-manual-accumulator with `all(curve(t) >= curve(t-1) for t in range(1, 1001))`. 31 tests pass.

### Task 4.8: test_camera_zoom.py — inline derivation comments
- [x] Replaced 29-line inline derivation with 2 pre-computed expected constants (`EXPECTED_WORLD_BEFORE`, `EXPECTED_CAMERA_POS_AFTER`) plus a concise invariant. 3 tests pass.

### Task 4.9: test_spec_compiler.py — nested ship-tuple capture loops
- [x] Extracted `_snapshot_ship_tuples(state)` helper at module level (3-level nested generator expression replacing 9-line nested for loops, used twice). 39 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-494 complete
