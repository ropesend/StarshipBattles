# Phase 2: CAT-8 Needless Complexity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-323 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce the 32 verified CAT-8 needless-complexity cases (flatten nested patches, reduce mock setup boilerplate).

> **Class-level autouse caveat:** Before promoting any per-test patches to class-level autouse fixtures, scan each test method in the class for patch-value customizations. If any method overrides a shared patch with a different return value or side effect, that method must remain in its own class or use a function-scoped patch — class-level autouse cannot accommodate per-method customization without workarounds that defeat the purpose.

---

## Tasks

### Task 2.1: test_ai_controller_unit.py [Medium]
**File:** `tests/unit/ai/test_ai_controller_unit.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [ ] [S02-CAT8-001] `5+ levels of patch nesting + nonlocal` (lines 284-362): Extract _build_behavior_context helper if promoted, or restructure controller for separable context construction.
- [ ] [S02-CAT8-002] `TestCheckAvoidance complex mock chain` (lines 448-621): Extract _setup_avoidance_test(threats, ship_pos, ship_radius) helper.

- [ ] Verify: `pytest tests/unit/ai/test_ai_controller_unit.py` passes; LOC delta ≈ 158

**Notes:** _(none yet)_

---

### Task 2.2: test_virtual_table.py [Medium]
**File:** `tests/unit/ui/components/table/test_virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py`

- [ ] [S11-CAT8-002] `Repetitive mock setup` (lines 83-555): Extract _build_virtual_table fixture.
- [ ] [S11-CAT8-010] `test_update_visible_rows_disables_edge_action_buttons` (lines 668-770): Split into multiple smaller tests with explicit scroll positions.

- [ ] Verify: `pytest tests/unit/ui/components/table/test_virtual_table.py` passes; LOC delta ≈ 252

**Notes:** _(none yet)_

---

### Task 2.3: test_three_empire_battle.py [Simple]
**File:** `tests/integration/conflict_resolution/test_three_empire_battle.py`
**Tests:** `pytest tests/integration/conflict_resolution/test_three_empire_battle.py`

- [ ] [S11-CAT8-006] `test_three_empire_battle_reports_destroyed_fleets setup` (lines 127-152): Extract _three_empire_setup helper.

- [ ] Verify: `pytest tests/integration/conflict_resolution/test_three_empire_battle.py` passes; LOC delta ≈ 26

**Notes:** _(none yet)_

---

### Task 2.4: test_flat_shield_bonus.py [Simple]
**File:** `tests/integration/strategy/test_flat_shield_bonus.py`
**Tests:** `pytest tests/integration/strategy/test_flat_shield_bonus.py`

- [ ] [S11-CAT8-005] `Deep helper nesting` (lines 32-99): Inline simpler helpers; flatten composition.

- [ ] Verify: `pytest tests/integration/strategy/test_flat_shield_bonus.py` passes; LOC delta ≈ 67

**Notes:** _(none yet)_

---

### Task 2.5: test_combat_utils.py [Simple]
**File:** `tests/unit/ai/test_combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [ ] [S10-CAT8-001] `_create_pdc_ship lambda hybrid` (lines 317-341): Use patch.object or real objects.

- [ ] Verify: `pytest tests/unit/ai/test_combat_utils.py` passes; LOC delta ≈ 7

**Notes:** _(none yet)_

---

### Task 2.6: test_builder_improvements.py [Simple]
**File:** `tests/unit/builder/test_builder_improvements.py`
**Tests:** `pytest tests/unit/builder/test_builder_improvements.py`

- [ ] [S01-CAT8-001] `test_loading_sync` (lines 44-126): Extract mock-ship creation into a shared helper. Mock only attributes the SUT actually reads.

- [ ] Verify: `pytest tests/unit/builder/test_builder_improvements.py` passes; LOC delta ≈ 83

**Notes:** _(none yet)_

---

### Task 2.7: test_caption_schemas_validate.py [Simple]
**File:** `tests/unit/qa/test_caption_schemas_validate.py`
**Tests:** `pytest tests/unit/qa/test_caption_schemas_validate.py`

- [ ] [S11-CAT8-009] `Hardcoded schema list` (lines 40-51): Auto-discover *.schema.json in schemas dir.

- [ ] Verify: `pytest tests/unit/qa/test_caption_schemas_validate.py` passes; LOC delta ≈ 12

**Notes:** _(none yet)_

---

### Task 2.8: test_callbacks.py [Simple]
**File:** `tests/unit/research/research_scene/test_callbacks.py`
**Tests:** `pytest tests/unit/research/research_scene/test_callbacks.py`

- [ ] [S03-CAT8-002] `5-7 nested patch blocks` (lines 17-323): Promote shared patches to class-level autouse fixture.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_callbacks.py` passes; LOC delta ≈ 307

**Notes:** _(Plan-review M-02 (2026-05-03): apply class-level autouse caveat from phase header — scan test methods for per-method patch customization before promoting.)_

---

### Task 2.9: test_initialization.py [Simple]
**File:** `tests/unit/research/research_scene/test_initialization.py`
**Tests:** `pytest tests/unit/research/research_scene/test_initialization.py`

- [ ] [S03-CAT8-003] `5-6 nested patch blocks` (lines 13-262): Promote shared patches to class-level fixture.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_initialization.py` passes; LOC delta ≈ 250

**Notes:** _(Plan-review M-02 (2026-05-03): apply class-level autouse caveat from phase header — scan test methods for per-method patch customization before promoting.)_

---

### Task 2.10: test_interaction.py [Simple]
**File:** `tests/unit/research/research_scene/test_interaction.py`
**Tests:** `pytest tests/unit/research/research_scene/test_interaction.py`

- [ ] [S04-CAT8-002] `Every test patches 6 classes` (lines 21-27, 52-57, 83-88, 129-134, 164-169, 203-207, 236-240): Promote shared patches to a class autouse fixture.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_interaction.py` passes; LOC delta ≈ 50

**Notes:** _(Plan-review M-02 (2026-05-03): apply class-level autouse caveat from phase header — scan test methods for per-method patch customization before promoting.)_

---

### Task 2.11: test_fleet_aura_extended.py [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py`

- [ ] [S11-CAT8-008] `_make_modifier_stack helper` (lines 56-94): Inline or simplify the factory.

- [ ] Verify: `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py` passes; LOC delta ≈ 39

**Notes:** _(none yet)_

---

### Task 2.12: test_ship_stats_calculator_phases.py [Simple]
**File:** `tests/unit/simulation/services/test_ship_stats_calculator_phases.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_stats_calculator_phases.py`

- [ ] [S11-CAT8-003] `_create_mock_ship 45 LOC` (lines 28-72): Use real Ship with sparse fixtures or simplify to dependency-injected ship.

- [ ] Verify: `pytest tests/unit/simulation/services/test_ship_stats_calculator_phases.py` passes; LOC delta ≈ 45

**Notes:** _(none yet)_

---

### Task 2.13: test_battle_runner_di.py [Simple]
**File:** `tests/unit/simulation/test_battle_runner_di.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner_di.py`

- [ ] [S09-CAT8-001] `test_no_simulation_call_to_get_default_registry_provider` (lines 218-271): Keep the existing test in the suite (it's the canonical CI gate). If the same check is also added as a pre-commit hook for fast local feedback, extract the check logic into a shared helper used by both — do not duplicate.

- [ ] Verify: `pytest tests/unit/simulation/test_battle_runner_di.py` passes; LOC delta ≈ 54

**Notes:** _(Plan-review M-04 (2026-05-03): pre-commit hooks are bypassable with --no-verify; the test suite is the canonical quality gate.)_

---

### Task 2.14: test_fleet_navigation_action_timing.py [Simple]
**File:** `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py`

- [ ] [S10-CAT8-002] `Nested patching of internal deps` (lines 55-69, 113-127, 171-185, 247-259, 290-300): **Document why 2-level nesting is acceptable** (the simpler option). Add a comment to the test class explaining the nesting is intentional for boundary patching of two distinct DI dependencies.
      _(verification adjusted from review's "Reduce 3+ levels of nested patching by injecting dependencies." — see verification_report.md)_

- [ ] Verify: `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py` passes; LOC delta ≈ 60

**Notes:** _(Plan-review M-09 (2026-05-03): chose documentation-only path over DI injection to avoid production signature changes in a P2 polish project.)_

---

### Task 2.15: test_damage_calculator.py [Simple]
**File:** `tests/unit/strategy/test_damage_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_damage_calculator.py`

- [ ] [S11-CAT8-011] `Granular boundary test class` (lines 606-822): Same as F-10; keep distinct edge cases as-is.

- [ ] Verify: `pytest tests/unit/strategy/test_damage_calculator.py` passes; LOC delta ≈ 216

**Notes:** _(none yet)_

---

### Task 2.16: test_engine_event_emission.py [Simple]
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`

- [ ] [S04-CAT8-001] `Triple-nested with patch` (lines 102-125, 138-157, 727-741): Extract a class fixture or use patch.multiple to flatten.

- [ ] Verify: `pytest tests/unit/strategy/test_engine_event_emission.py` passes; LOC delta ≈ 59

**Notes:** _(none yet)_

---

### Task 2.17: test_planet_specific_colonization.py [Simple]
**File:** `tests/unit/strategy/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/test_planet_specific_colonization.py`

- [ ] [S11-CAT8-007] `4 galaxy fixtures` (lines 196-244): Single factory _make_galaxy(*planet_specs).

- [ ] Verify: `pytest tests/unit/strategy/test_planet_specific_colonization.py` passes; LOC delta ≈ 49

**Notes:** _(none yet)_

---

### Task 2.18: test_colony_demographic_view.py [Simple]
**File:** `tests/unit/ui/panels/test_colony_demographic_view.py`
**Tests:** `pytest tests/unit/ui/panels/test_colony_demographic_view.py`

- [ ] [S08-CAT8-003] `_facade_for helper` (lines 82-103): Construct facade via real init with mocked dependencies; avoid attribute patching.

- [ ] Verify: `pytest tests/unit/ui/panels/test_colony_demographic_view.py` passes; LOC delta ≈ 22

**Notes:** _(none yet)_

---

### Task 2.19: test_design_report_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_design_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_design_report_panel.py`

- [ ] [S06-CAT8-001] `All tests bypass constructor` (lines 36-372): Construct via real __init__ with mocked pygame_gui.

- [ ] Verify: `pytest tests/unit/ui/panels/test_design_report_panel.py` passes; LOC delta ≈ 336

**Notes:** _(none yet)_

---

### Task 2.20: test_modifier_control_row.py [Simple]
**File:** `tests/unit/ui/screens/builder/test_modifier_control_row.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_control_row.py`

- [ ] [S11-CAT8-004] `2 near-identical fixtures` (lines 12-139): Promote to module-level fixture.

- [ ] Verify: `pytest tests/unit/ui/screens/builder/test_modifier_control_row.py` passes; LOC delta ≈ 45

**Notes:** _(none yet)_

---

### Task 2.21: test_build_queue_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

> **Cross-project:** PROJ-322 will DELETE this unit file entirely (its plan-review committed to that approach). Skip Task 2.21 if PROJ-322 has run; the integration tests at `tests/integration/ui/build_queue_screen/` will remain.

- [ ] [S12-CAT8-001] `Tautological error/edge case tests` (lines 442-580): Remove all tautological tests; rewrite to exercise real edge-case behavior.
- [ ] Audit lines 442-580: produce explicit keep/delete list per "tautological" criterion (assert True / assert x == x / asserts mock state set in same test). Tests that exercise a code path — even poorly — should be rewritten, not deleted.

- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen.py` passes; LOC delta ≈ 140

_(Plan-review M-01 (2026-05-03): if file still exists after PROJ-322 runs, audit lines 442-580 and produce an explicit keep/delete list before deleting any tests.)_

**Notes:** _(none yet)_

---

### Task 2.22: test_cargo_quick_dialog_resolution.py [Simple]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py`

- [ ] [S08-CAT8-002] `Live pygame.Rect + side_effect lambdas` (lines 30-103): Replace lambda chains with a fake mapper class.

- [ ] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py` passes; LOC delta ≈ 74

**Notes:** _(none yet)_

---

### Task 2.23: test_empire_build_queue_sidebar.py [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_sidebar.py`

- [ ] [S12-CAT8-002] `_make_sidebar 4-level nested patches` (lines 36-55): Use patch.multiple or a fixture.

- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_sidebar.py` passes; LOC delta ≈ 20

**Notes:** _(none yet)_

---

### Task 2.24: test_fleet_report_window.py [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`

- [ ] [S03-CAT8-001] `_make_fleet_report_window helper` (lines 48-145): Construct via real __init__ with mocked pygame_gui.

- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py` passes; LOC delta ≈ 98

**Notes:** _(none yet)_

---

### Task 2.25: test_setup_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_setup_screen.py`

- [ ] [S08-CAT8-001] `3 setup_mocks fixtures` (lines 16-27, 247-256, 319-333): Promote to a single shared module-scoped fixture.

- [ ] Verify: `pytest tests/unit/ui/screens/test_setup_screen.py` passes; LOC delta ≈ 36

**Notes:** _(none yet)_

---

### Task 2.26: test_strategy_detail_formatter.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py`

- [ ] [S07-CAT8-001] `6 nested patch blocks` (lines 89-123): Use patch.multiple or a single context manager helper.

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py` passes; LOC delta ≈ 35

**Notes:** _(none yet)_

---

### Task 2.27: test_strategy_renderer.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py`

- [ ] [S06-CAT8-003] `test_star_radius_nonlinear_scaling` (lines 660-684): Promote _hex_radius_to_screen to public helper or test through public draw assertions.

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_renderer.py` passes; LOC delta ≈ 25

**Notes:** _(none yet)_

---

### Task 2.28: test_workshop_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

- [ ] [S06-CAT8-002] `All tests bypass constructor` (lines 182-634): Construct via real __init__ with mocked pygame_gui or migrate to integration tests.

- [ ] Verify: `pytest tests/unit/ui/screens/test_workshop_screen.py` passes; LOC delta ≈ 450

**Notes:** _(none yet)_

---

### Task 2.29: test_detail_panel_rendering.py [Simple]
**File:** `tests/unit/ui/test_detail_panel_rendering.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel_rendering.py`

- [ ] [S05-CAT8-001] `Module cache deletion + 7 patches` (lines 16-41): Stop manipulating sys.modules; use a class autouse fixture for the patches.

- [ ] Verify: `pytest tests/unit/ui/test_detail_panel_rendering.py` passes; LOC delta ≈ 26

**Notes:** _(Plan-review M-02 (2026-05-03): apply class-level autouse caveat from phase header — scan test methods for per-method patch customization before promoting.)_

---

### Task 2.30: test_race_summary_panel.py [Simple]
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] [S11-CAT8-001] `_refresh_with_mocked_uilabel` (lines 447-494): Convert to real construction or a class-scoped fixture.

- [ ] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta ≈ 48

**Notes:** _(none yet)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
