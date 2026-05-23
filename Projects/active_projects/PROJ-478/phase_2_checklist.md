# Phase 2: CAT-2 Tests Nothing Real

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete or rewrite the 18 verified CAT-2 tests-nothing-real tests identified by review `2026-05-20_210550_test-review`. These tests bypass `__init__`, replace production methods with inline lambdas, mock phantom methods that don't exist in production, or read documentation files instead of game code. Reclaim ~280 LOC by removing tests that have zero coverage value or by converting bypass-init patterns to real construction with mocked dependencies.

---

## Tasks

### Task 2.1: test_workshop_screen.py — bypass-init / lambda-replacement cluster (13 tests)
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

- [ ] Delete `test_event_router_handle_event_uses_lambda` (lines 236-247) — lambda replaces production method; assertion checks lambda output only.
- [ ] Rewrite `test_save_ship_lambda` (lines 300-309) — current test patches phantom method `_save_ship`; production method is `save_ship` (no underscore). Rewrite to call real `save_ship()` or delete. _(verification adjusted from review's "delete" — production method exists with similar name; rewriting preserves test intent rather than dropping coverage. See verification_report.md.)_
- [ ] Rewrite `test_load_ship_lambda` (lines 311-320) — current test patches phantom `_load_ship`; production is `load_ship`. Rewrite to call real `load_ship()` or delete. _(verification adjusted as above.)_
- [ ] Rewrite `test_on_select_target_pressed_lambda` (lines 322-331) — current test patches phantom `_on_select_target_pressed`; production is `on_select_target_pressed`. Rewrite to call real method or delete. _(verification adjusted as above.)_
- [ ] Delete the 4 dynamic-property tests at lines 264-272, 274-281, 283-290, 396-410 — each installs a property on the test instance and asserts on it; never exercises the production property.
- [ ] Delete `test_dragged_item_dynamic_property` (lines 412-425) — same dynamic-property pattern.
- [ ] Delete `test_cleanup_with_mock_handler` (lines 435-449) — `mock_cleanup` uses `hasattr` check; production cleanup uses truthiness. Mock diverges.
- [ ] Delete `test_handle_resize_with_mock` (lines 451-467) — `mock_handle_resize` omits production's `layer_panel_width` recalculation; tests an incomplete mock.
- [ ] Delete `test_clear_design_with_mock` (lines 581-594) — mock does 3 of production's 5 operations; tests partial mock.
- [ ] Delete `test_apply_loaded_ship_with_mock` (lines 616-634) — mock does 4 of production's 5 operations; tests partial mock.
- [ ] Verify: `pytest tests/unit/ui/screens/test_workshop_screen.py` passes; LOC delta ≈ -180 (12 deletes + 3 rewrites).

### Task 2.2: test_strategy_ui_tooltips.py
**File:** `tests/unit/ui/screens/test_strategy_ui_tooltips.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_tooltips.py`

- [ ] Rewrite `test_get_tooltip_text_returns_hotkey` (lines 34-50) — replace exact `"Enter"` / `"Shift+P"` / `"Shift+G"` string assertions against `Paths.DEFAULT_KEYBINDINGS_FILE` with injected/conftest-controlled bindings, so the test exercises the mapping logic rather than the production defaults file.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_ui_tooltips.py` passes; LOC delta ≈ +5 (richer setup).

### Task 2.3: test_codex_consult_skills.py
**File:** `tests/unit/agent_coordination/test_codex_consult_skills.py`
**Tests:** `pytest tests/unit/agent_coordination/test_codex_consult_skills.py` (if moved, run from new path)

- [ ] Move the entire file (101 LOC) to `tests/static_guards/` or `tests/projects/` — tests serve a valid purpose (agent skill metadata validation) but are mis-located as unit tests; zero `game.*` imports. _(verification adjusted from review's "delete" — the metadata-validation purpose is real; relocate rather than discard. See verification_report.md.)_
- [ ] Verify: tests pass from new location; LOC delta ≈ -101 from `tests/unit/`, +101 in new directory.

### Task 2.4: test_codex_interagent_discussion_skills.py
**File:** `tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py`
**Tests:** `pytest tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py` (if moved, run from new path)

- [ ] Move the entire file (160 LOC, 10 doc-linting tests) to `tests/static_guards/` or `tests/projects/` — same rationale as Task 2.3; tests read `.agents/skills/*.md` and assert string containment.
- [ ] Verify: tests pass from new location; LOC delta ≈ -160 from `tests/unit/`.

### Task 2.5: test_panel_full_open_benchmark.py
**File:** `tests/regression/test_panel_full_open_benchmark.py`
**Tests:** `pytest tests/regression/test_panel_full_open_benchmark.py` (or new location)

- [ ] Move both benchmark methods (lines 137-179, 2 tests, 42 LOC total) to a dedicated profiling script directory outside `tests/` — both construct UI windows in a loop and call `_print_span_medians()` with zero assertions.
- [ ] Verify: `pytest tests/regression/` passes (one fewer test file); LOC delta ≈ -42 from `tests/`.

### Task 2.6: test_interaction.py (research scene)
**File:** `tests/unit/research/research_scene/test_interaction.py`
**Tests:** `pytest tests/unit/research/research_scene/test_interaction.py`

- [ ] Rewrite `test_detect_cycles_called_during_init` (lines 214-239) — current test calls `mock_tree.detect_cycles()` itself then asserts it was called (tautology). Construct a real `ResearchTreeScene` and assert `detect_cycles` is called as an `__init__` side effect. _(verification adjusted from review's "delete" — the original test's intent has value if rewritten with real construction. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/research/research_scene/test_interaction.py` passes; LOC delta ≈ -5 net.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3 — CAT-3 Dead Test Code)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
