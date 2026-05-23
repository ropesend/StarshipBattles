# Phase 1: CAT-1 Trivial Pass

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete or convert to `pytest.skip` the 24 verified CAT-1 trivial-pass tests identified by review `2026-05-20_210550_test-review`. Reclaim ~150 LOC by removing tests that exercise no production code: `assert True`, `assert not hasattr`, import-then-assert-not-None, and self-fulfilling assignments.

---

## Tasks

### Task 1.1: test_workshop_viewmodel_public_api.py
**File:** `tests/unit/workshop/test_workshop_viewmodel_public_api.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_viewmodel_public_api.py`

- [ ] Delete `test_callable_method` (lines 107-108) — `assert callable(method)` is tautological for any method resolved from a class.
- [ ] Delete the 9 `isinstance(X, property)` tests (lines 110-135) — trivial descriptor existence checks with zero behavioral coverage.
- [ ] Verify: `pytest tests/unit/workshop/test_workshop_viewmodel_public_api.py` passes; LOC delta ≈ -28.

### Task 1.2: test_strategy_renderer_public_api.py
**File:** `tests/unit/ui/screens/test_strategy_renderer_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_public_api.py`

- [ ] Delete the 7 structural tests (lines 16-91) — isclass / constant isinstance / signature checks / hasattr+signature / property loop. All pass on any import success.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_renderer_public_api.py` passes; LOC delta ≈ -75.

### Task 1.3: test_role.py
**File:** `tests/unit/core/test_role.py`
**Tests:** `pytest tests/unit/core/test_role.py`

- [ ] Delete the 4 trivial Role tests (lines 45-80) — dataclass equality, same-id inequality, tuple type check, import path identity. Exercises Python `__eq__` not Role logic.
- [ ] Optional: trim the 3 trailing `TypeError`-on-missing-arg tests if they don't add Role-specific coverage (Python language behavior).
- [ ] Verify: `pytest tests/unit/core/test_role.py` passes; LOC delta ≈ -36.

### Task 1.4: test_colony_yard_registries.py
**File:** `tests/unit/strategy/data/test_colony_yard_registries.py`
**Tests:** `pytest tests/unit/strategy/data/test_colony_yard_registries.py`

- [ ] Delete the lone `hasattr` fixture test (lines 81-84) — single-attribute structural check.
- [ ] Verify: `pytest tests/unit/strategy/data/test_colony_yard_registries.py` passes; LOC delta ≈ -4.

### Task 1.5: test_strategy_widgets.py
**File:** `tests/unit/ui/screens/test_strategy_widgets.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_widgets.py`

- [ ] Delete `test_graph_can_be_imported` (lines 53-57) — import smoke test, asserts not None.
- [ ] Delete `test_spectrum_graph_can_be_imported` (lines 124-128) — same pattern.
- [ ] Delete `test_atmosphere_graph_can_be_imported` (lines 203-207) — same pattern.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_widgets.py` passes; LOC delta ≈ -15.

### Task 1.6: test_keybindings_scene.py
**File:** `tests/unit/ui/screens/test_keybindings_scene.py`
**Tests:** `pytest tests/unit/ui/screens/test_keybindings_scene.py`

- [ ] Delete `test_update_does_not_raise` (lines 272-275) — calls `scene.update(0.016)` with zero assertions.
- [ ] Delete `test_draw_does_not_raise` (lines 276-279) — calls `scene.draw(surface)` with zero assertions.
- [ ] Verify: `pytest tests/unit/ui/screens/test_keybindings_scene.py` passes; LOC delta ≈ -8.

### Task 1.7: test_planet_report_panel.py
**File:** `tests/unit/ui/panels/test_planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [ ] Delete the `_resource_grid_items` self-fulfilling test (lines 88-97) — assigns `[]` then asserts `isinstance(..., list)`. If a behavioral test for `_build_resource_grid` is needed, write a fresh one with a real input.
- [ ] Verify: `pytest tests/unit/ui/panels/test_planet_report_panel.py` passes; LOC delta ≈ -10.

### Task 1.8: test_fleet_aura_cache.py
**File:** `tests/unit/simulation/combat/test_fleet_aura_cache.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py`

- [ ] Delete `test_providers_dirty_flag_exists` (lines 44-47) — `hasattr(mgr, '_providers_dirty')` attribute-existence check.
- [ ] Verify: `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py` passes; LOC delta ≈ -4.

### Task 1.9: test_battle_outcome_replay_id.py
**File:** `tests/unit/simulation/test_battle_outcome_replay_id.py`
**Tests:** `pytest tests/unit/simulation/test_battle_outcome_replay_id.py`

- [ ] Replace `hasattr` + None-default test (lines 23-33) with an integration test that runs `extract_outcome` with `engine.replay_id` set and verifies the outcome carries it through `BattleResult` → `COMBAT_RESOLVED` event.
- [ ] _(verification adjusted from review's "delete" — the integration replacement preserves the original intent of validating replay_id propagation; deletion would leave a coverage gap. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/simulation/test_battle_outcome_replay_id.py` passes; LOC delta ≈ -10 net (replace 10 LOC with focused integration test).

### Task 1.10: test_ship_loading.py
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py`

- [ ] Fix `test_all_ships_match_expected_stats` (lines 80-131) — add `assert len(ship_files) >= 1` before the loop so the test fails when the directory is empty.
- [ ] Verify: `pytest tests/unit/builder/test_ship_loading.py` passes; LOC delta ≈ +1.

### Task 1.11: test_bulk_add.py
**File:** `tests/unit/builder/test_bulk_add.py`
**Tests:** `pytest tests/unit/builder/test_bulk_add.py`

- [ ] Fix `test_bulk_add_success` (lines 9-30) — add `assert ship.layers[LayerType.ARMOR].components[0] is comp` to verify component identity, not just length.
- [ ] Verify: `pytest tests/unit/builder/test_bulk_add.py` passes; LOC delta ≈ +1.

### Task 1.12: consumable_management_engine/conftest.py
**File:** `tests/unit/strategy/consumable_management_engine/conftest.py`
**Tests:** `pytest tests/unit/strategy/consumable_management_engine/`

- [ ] Delete the entire conftest (lines 1-52) — 4 fixtures, zero test functions, sibling `test_initialization.py` duplicates them inline. _(Confirmed: no production import uses these fixtures.)_
- [ ] Or, alternatively, switch `test_initialization.py` to consume the conftest fixtures and remove the inline duplicates there.
- [ ] Verify: `pytest tests/unit/strategy/consumable_management_engine/` passes; LOC delta ≈ -52 (delete approach).

### Task 1.13: test_fleet_navigation_consistency.py
**File:** `tests/integration/strategy/test_fleet_navigation_consistency.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_navigation_consistency.py`

- [ ] Rewrite `test_already_at_destination_consistency` (lines 308-326) — replace the `len(fleet.orders) == 0` assertion with `assert fleet.location == loc`. The order-queue internal is implementation detail.
- [ ] Verify: `pytest tests/integration/strategy/test_fleet_navigation_consistency.py` passes; LOC delta ≈ -2.

### Task 1.14: test_superweapon_event_payloads.py
**File:** `tests/unit/strategy/engine/test_superweapon_event_payloads.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py`

- [ ] Delete the empty-body test (lines 106-113) — body is only a docstring, no assertions.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py` passes; LOC delta ≈ -8.

### Task 1.15: test_galaxy_state_encapsulation.py
**File:** `tests/unit/strategy/test_galaxy_state_encapsulation.py`
**Tests:** `pytest tests/unit/strategy/test_galaxy_state_encapsulation.py`

- [ ] Delete the empty-frozenset-loop test (lines 106-119) — `ALLOWED_FILES = frozenset()` means the `for` loop never executes and the trailing `assert` is unreachable.
- [ ] Verify: `pytest tests/unit/strategy/test_galaxy_state_encapsulation.py` passes; LOC delta ≈ -14.

### Task 1.16: test_planet_fleet_empire_post_436_contract.py
**File:** `tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py`

- [ ] Delete the `assert True` test (line 98) — body is literally `assert True`; docstring confirms it's a documentation marker only.
- [ ] Verify: `pytest tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py` passes; LOC delta ≈ -8.

### Task 1.17: test_event_log_sidebar.py
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`

- [ ] Delete `test_event_log_sidebar_class_exists` (lines 78-81) — import-then-assert pattern; assert never reached on import failure.
- [ ] Verify: `pytest tests/unit/ui/screens/test_event_log_sidebar.py` passes; LOC delta ≈ -4.

### Task 1.18: test_galaxy_test_screen.py
**File:** `tests/unit/ui/screens/test_galaxy_test_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_galaxy_test_screen.py`

- [ ] Evaluate the isinstance+comparison guard (lines 16-22) — already downgraded to MINOR (constants validation). If team accepts as a refactor guard, keep; otherwise delete (~6 LOC).
- [ ] Verify: `pytest tests/unit/ui/screens/test_galaxy_test_screen.py` passes; LOC delta ≈ 0 or -6 depending on decision.

### Task 1.19: test_post_battle_hook_builder.py
**File:** `tests/unit/strategy/combat/test_post_battle_hook_builder.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook_builder.py`

- [ ] Rewrite `test_build_hook_threads_mine_groups_and_engine_ref` (lines 37-54) — replace `assert callable(hook)` with behavioral assertions: assert `board.update()` called, assert `engine_ref` modified, assert mine group state changed.
- [ ] Verify: `pytest tests/unit/strategy/combat/test_post_battle_hook_builder.py` passes; LOC delta ≈ +5 (richer asserts).

### Task 1.20: test_codex_project_config.py
**File:** `tests/unit/tools/test_codex_project_config.py`
**Tests:** `pytest tests/unit/tools/test_codex_project_config.py`

- [ ] Move the entire file (22 LOC) to `tests/tooling/` or delete — validates `.codex/config.toml` external agent config, not game production code.
- [ ] Verify: `pytest tests/unit/tools/` passes (or test runs from new location); LOC delta ≈ -22 from `tests/unit/`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2 — CAT-2 Tests Nothing Real)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
