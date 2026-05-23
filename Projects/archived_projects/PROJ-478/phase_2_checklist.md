# Phase 2: CAT-2 Tests Nothing Real

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete or rewrite the 18 verified CAT-2 tests-nothing-real tests identified by review `2026-05-20_210550_test-review`. These tests bypass `__init__`, replace production methods with inline lambdas, mock phantom methods that don't exist in production, or read documentation files instead of game code. Reclaim ~280 LOC by removing tests that have zero coverage value or by converting bypass-init patterns to real construction with mocked dependencies.

---

## Tasks

### Task 2.1: test_workshop_screen.py — bypass-init / lambda-replacement cluster (13 tests)
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

- [x] Delete `test_event_router_handle_event_uses_lambda` (lines 236-247) — lambda replaces production method; assertion checks lambda output only.
- [x] Rewrite `test_save_ship_lambda` (lines 300-309) — current test patches phantom method `_save_ship`; production method is `save_ship` (no underscore). Rewrite to call real `save_ship()` or delete. _(verification adjusted from review's "delete" — production method exists with similar name; rewriting preserves test intent rather than dropping coverage. See verification_report.md.)_
- [x] Rewrite `test_load_ship_lambda` (lines 311-320) — current test patches phantom `_load_ship`; production is `load_ship`. Rewrite to call real `load_ship()` or delete. _(verification adjusted as above.)_
- [x] Rewrite `test_on_select_target_pressed_lambda` (lines 322-331) — current test patches phantom `_on_select_target_pressed`; production is `on_select_target_pressed`. Rewrite to call real method or delete. _(verification adjusted as above.)_
- [x] Delete the 4 dynamic-property tests at lines 264-272, 274-281, 283-290, 396-410 — each installs a property on the test instance and asserts on it; never exercises the production property.
- [x] Delete `test_dragged_item_dynamic_property` (lines 412-425) — same dynamic-property pattern.
- [x] Delete `test_cleanup_with_mock_handler` (lines 435-449) — `mock_cleanup` uses `hasattr` check; production cleanup uses truthiness. Mock diverges.
- [x] Delete `test_handle_resize_with_mock` (lines 451-467) — `mock_handle_resize` omits production's `layer_panel_width` recalculation; tests an incomplete mock.
- [x] Delete `test_clear_design_with_mock` (lines 581-594) — mock does 3 of production's 5 operations; tests partial mock.
- [x] Delete `test_apply_loaded_ship_with_mock` (lines 616-634) — mock does 4 of production's 5 operations; tests partial mock.
- [x] Verify: `pytest tests/unit/ui/screens/test_workshop_screen.py` passes; LOC delta ≈ -180 (12 deletes + 3 rewrites).

### Task 2.2: test_strategy_ui_tooltips.py
**File:** `tests/unit/ui/screens/test_strategy_ui_tooltips.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_tooltips.py`

- [x] Rewrite `test_get_tooltip_text_returns_hotkey` (lines 34-50) — replace exact `"Enter"` / `"Shift+P"` / `"Shift+G"` string assertions against `Paths.DEFAULT_KEYBINDINGS_FILE` with injected/conftest-controlled bindings, so the test exercises the mapping logic rather than the production defaults file.
- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_ui_tooltips.py` passes; LOC delta ≈ +5 (richer setup).

### Task 2.3: test_codex_consult_skills.py
**File:** `tests/unit/agent_coordination/test_codex_consult_skills.py`
**Tests:** `pytest tests/unit/agent_coordination/test_codex_consult_skills.py` (if moved, run from new path)

- [x] Move the entire file (101 LOC) to `tests/static_guards/` or `tests/projects/` — tests serve a valid purpose (agent skill metadata validation) but are mis-located as unit tests; zero `game.*` imports. _(verification adjusted from review's "delete" — the metadata-validation purpose is real; relocate rather than discard. See verification_report.md.)_
- [x] Verify: tests pass from new location; LOC delta ≈ -101 from `tests/unit/`, +101 in new directory.

### Task 2.4: test_codex_interagent_discussion_skills.py
**File:** `tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py`
**Tests:** `pytest tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py` (if moved, run from new path)

- [x] Move the entire file (160 LOC, 10 doc-linting tests) to `tests/static_guards/` or `tests/projects/` — same rationale as Task 2.3; tests read `.agents/skills/*.md` and assert string containment.
- [x] Verify: tests pass from new location; LOC delta ≈ -160 from `tests/unit/`.

### Task 2.5: test_panel_full_open_benchmark.py
**File:** `tests/regression/test_panel_full_open_benchmark.py`
**Tests:** `pytest tests/regression/test_panel_full_open_benchmark.py` (or new location)

- [x] Move both benchmark methods (lines 137-179, 2 tests, 42 LOC total) to a dedicated profiling script directory outside `tests/` — both construct UI windows in a loop and call `_print_span_medians()` with zero assertions.
- [x] Verify: `pytest tests/regression/` passes (one fewer test file); LOC delta ≈ -42 from `tests/`.

### Task 2.6: test_interaction.py (research scene)
**File:** `tests/unit/research/research_scene/test_interaction.py`
**Tests:** `pytest tests/unit/research/research_scene/test_interaction.py`

- [x] Rewrite `test_detect_cycles_called_during_init` (lines 214-239) — current test calls `mock_tree.detect_cycles()` itself then asserts it was called (tautology). Construct a real `ResearchTreeScene` and assert `detect_cycles` is called as an `__init__` side effect. _(verification adjusted from review's "delete" — the original test's intent has value if rewritten with real construction. See verification_report.md.)_
- [x] Verify: `pytest tests/unit/research/research_scene/test_interaction.py` passes; LOC delta ≈ -5 net.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3 — CAT-3 Dead Test Code)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._

---

## Phase 2 Notes (executed 2026-05-22)

**Disposition summary (Task 2.1 — `test_workshop_screen.py`):**

- **Deleted** (CAT-2 lambda-replaces-prod / partial-mock / dynamic-property tests with zero coverage value):
  - `test_handle_event_delegates_to_event_router` — installed a lambda then asserted on it.
  - `test_event_bus_subscription_supported` — `hasattr(event_bus, 'emit')` on a MagicMock (always true).
  - `test_ship_property_returns_viewmodel_ship`, `test_selected_components_returns_viewmodel_selection`, `test_available_components_returns_viewmodel_available` — dynamic property installed on the test instance, then asserted on the test-installed property.
  - `test_update_stats_rebuilds_layer_panel` — assigned `screen.update_stats = mock_update_stats` then called it.
  - `test_selected_component_property_delegates_to_controller`, `test_dragged_item_property_delegates_to_controller` — same dynamic-property anti-pattern.
  - `test_cleanup_clears_ui_manager` — `mock_cleanup` does a `hasattr` check (production code uses truthiness; the mock diverges).
  - `test_handle_resize_updates_dimensions` — `mock_handle_resize` omits the production `layer_panel_width` recalculation.
  - `test_clear_design_delegates_to_viewmodel` — mock implements 3 of production's 5 ops (no `update_stats`, no `rebuild_modifier_ui`, no `on_selection_changed`).
  - `test_apply_loaded_ship_updates_viewmodel` — mock implements 4 of production's 5 ops (no `update_stats`, no `rebuild_modifier_ui`).

- **Rewritten** (CAT-2 phantom-method tests where the production method DID exist under a different name):
  - `test_save_ship_delegates_to_ship_io` — was patching phantom `_save_ship`; rewritten to call real `DesignWorkshopScreen.save_ship(screen)` and assert `mocks['ship_io'].save_ship.assert_called_once_with()`.
  - `test_load_ship_delegates_to_ship_io` — same pattern, real method `load_ship`.
  - `test_on_select_target_pressed_delegates_to_ship_io` (renamed from `test_select_target_delegates_to_ship_io`) — same pattern, real method `on_select_target_pressed`.

- **Kept** (TestWorkshopContextInitialization, TestWorkshopDataReloading, TestWorkshopErrorHandling, TestWorkshopButtonDefinitions, TestWorkshopUpdateLoop, TestWorkshopClearDesign's confirm test, TestWorkshopApplyLoadedShip → empty so removed) — these exercise either real attribute storage or behaviorally distinct mocking patterns not in the CAT-2 cluster.

**Disposition summary (Task 2.2 — `test_strategy_ui_tooltips.py`):**

- **Rewritten:** `test_get_tooltip_text_returns_hotkey` and `test_unbound_actions_return_empty_string` — replaced `mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE)` + exact-string asserts against production defaults with `mapper.load(None)` + `mapper.set_binding(action, KeyBinding(...))` per case. Now exercises the `KeyBinding.display_text()` mapping logic for 3 modifier shapes (none / shift+letter / Enter alias) without coupling to the production defaults file.

**Disposition summary (Tasks 2.3 & 2.4 — codex skill tests):**

- **Moved:**
  - `tests/unit/agent_coordination/test_codex_consult_skills.py` → `tests/static_guards/test_codex_consult_skills.py`. The actual source path was `tests/static_guards/` per manifest claim "tests/unit/agent_coordination/" — file was found at that location during execution. Fixed the `parents[3]` → `parents[2]` repo-root walker (file lives one directory shallower now).
  - `tests/unit/tools/test_codex_interagent_discussion_skills.py` → `tests/static_guards/test_codex_interagent_discussion_skills.py`. **Manifest path was wrong** — claimed `tests/unit/agent_coordination/`, actual was `tests/unit/tools/`. Same `parents[3]` → `parents[2]` fix.

**Disposition summary (Task 2.5 — panel benchmark):**

- **Moved:** `tests/performance/test_panel_full_open_benchmark.py` → `profiling/panels/bench_panel_full_open.py`. **Manifest path was wrong** — claimed `tests/regression/`, actual was `tests/performance/`. New location is outside `tests/` so pytest no longer collects it; updated docstring to reflect new invocation paths.

**Disposition summary (Task 2.6 — research scene detect_cycles):**

- **Rewritten:** `test_detect_cycles_called_during_init` — replaced the `mock_tree.detect_cycles()` tautology with real `ResearchTreeScene(...)` construction. Patches `TechTree.load_from_json` to return the mock, plus `StarshipUIManager`, `ResearchControlPanel`, `ResearchRenderer`, `Camera`, `ResearchTracker` so construction succeeds headless. Now the assertion `mock_tree.detect_cycles.assert_called_once()` proves the scene's `__init__` fires the validation pass at production line 93.

**Path corrections discovered during execution:**
- Task 2.3 source: actual `tests/static_guards/` (already moved before I checked), not `tests/unit/agent_coordination/`.
- Task 2.4 source: actual `tests/unit/tools/`, not `tests/unit/agent_coordination/`.
- Task 2.5 source: actual `tests/performance/`, not `tests/regression/`.
