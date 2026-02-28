# Phase 1: Delete Zero-Risk Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove files confirmed as pure duplicates, empty scaffolds, or dead code. No unique tests to preserve.
**Priority:** Immediate

---

## PROJ-157 Overlap Summary

PROJ-157 completed the vast majority of Phase 1. PROJ-154 then completed the remaining items (mock_battle_ui_service.py, __init__.py cleanup, fleet_resource_aggregator, conflict_core, build_queue_source_errors).

Only `update_test_ships.py` remains — it was in neither PROJ-154 nor PROJ-157's scope.

---

## Tasks

### Task 1.1: Delete old component test framework [Simple] — DONE by PROJ-157
**Files:** `tests/unit/simulation/`

- [x] Delete `tests/unit/simulation/run_component_tests.py` (505 lines) — PROJ-157
- [x] Delete `tests/unit/simulation/component_logger.py` (278 lines) — PROJ-157
- [x] Delete `tests/unit/simulation/component_sim_tools.py` (156 lines) — PROJ-157
- [x] Delete `tests/unit/simulation/log_parser.py` (360 lines) — PROJ-157
- [x] Delete `tests/unit/simulation/output/logs/` directory — PROJ-157 (already gone pre-PROJ-157)
- [x] Delete `tests/unit/simulation/test_configs/` directory — PROJ-157 (already gone pre-PROJ-157)
- [x] Clean up `tests/unit/simulation/__init__.py` — PROJ-157
- [x] Delete `tests/unit/simulation/update_test_ships.py` (57 lines — old utility script)
- [x] Run tests to verify no regressions

**Notes:** Only `update_test_ships.py` remains.

### Task 1.2: Delete trivial scaffold files [Simple] — DONE by PROJ-157

- [x] Delete `tests/unit/entities/test_ship_formation_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/entities/test_projectile_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/entities/test_ability_aggregator_scope.py` — PROJ-157

### Task 1.3: Delete confirmed core duplicates [Simple] — DONE by PROJ-157

- [x] Delete `tests/unit/core/test_error_codes_coverage.py` — PROJ-157
- [x] Delete `tests/unit/core/test_superweapon_input_actions.py` — PROJ-157
- [x] Delete `tests/unit/core/test_resource_loading.py` — PROJ-157
- [x] Delete `tests/unit/core/logger/test_warning.py` — PROJ-157

### Task 1.4: Delete ShipCombatEngine delegation duplicates [Simple] — DONE by PROJ-157

- [x] Delete `tests/unit/simulation/ship_combat_engine/test_creation_and_lead.py` — PROJ-157
- [x] Delete `tests/unit/simulation/ship_combat_engine/test_targeting.py` — PROJ-157

### Task 1.5: Delete UI dead code [Simple] — DONE by PROJ-154 + PROJ-157

- [x] Delete `tests/unit/ui/test_overlay.py` — PROJ-157
- [x] Delete `tests/unit/ui/test_race_validator.py` — PROJ-157 (merged unique tests to screens/ version, then deleted)
- [x] Delete `tests/unit/ui/test_slider_snap_logic.py` — PROJ-157
- [x] Delete `tests/unit/ui/mocks/mock_battle_ui_service.py` — PROJ-154
- [x] Clean up `tests/unit/ui/mocks/__init__.py` — PROJ-154 (now contains empty `__all__ = []`)
- [x] Run tests to verify no regressions — PROJ-154

### Task 1.6: Delete AI/Combat dead code [Simple] — DONE by PROJ-157

- [x] Delete `tests/unit/ai/controllable_interface/test_interface_definition.py` — PROJ-157
- [x] Delete `tests/unit/combat/test_combat_endurance_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/combat/test_targeting_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/combat/test_lead.py` — PROJ-157
- [x] Delete `tests/unit/combat/test_ccd.py` — PROJ-157
- [x] Delete `tests/unit/ai/formation_prediction/test_other_behaviors.py` — PROJ-157
- [x] Delete `tests/unit/research/research_controls/test_handle_event.py` — PROJ-157
- [x] Delete `tests/unit/research/research_controls/test_event_formatting.py` — PROJ-157
- [x] Delete `tests/unit/research/research_controls/test_node_selection.py` — PROJ-157

### Task 1.7: Delete Strategy scaffolds and duplicates [Simple] — DONE by PROJ-154 + PROJ-157

- [x] Delete `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` — PROJ-157
- [x] Delete `tests/unit/strategy/test_hex_math.py` — PROJ-157 (verified core version is superset)
- [x] Delete `tests/unit/strategy/test_fleet_resource_aggregator.py` — PROJ-154
- [x] Delete `tests/unit/strategy/conflict_resolution/test_conflict_core.py` — PROJ-154
- [x] Delete `tests/unit/strategy/data/test_build_queue_source_errors.py` — PROJ-154
- [x] Run tests to verify no regressions — PROJ-154

### Task 1.8: Delete scripts and diagnostic files [Simple] — DONE by PROJ-157

- [x] Delete `tests/trace_cargo.py` — PROJ-157
- [x] Delete `tests/unit/performance/generate_test_data.py` — PROJ-157
- [x] Delete `tests/unit/performance/profile_simulation.py` — PROJ-157
- [x] Delete `tests/unit/performance/stress_test.py` — PROJ-157
- [x] Delete `tests/unit/performance/strategy_tournament.py` — PROJ-157
- [x] Delete `tests/unit/regressions/test_crash_regressions.py` — PROJ-157

### Task 1.9: Delete empty conftest.py files [Simple] — DONE by PROJ-157

- [x] Delete `tests/unit/core/math_utils/conftest.py` — PROJ-157
- [x] Delete `tests/unit/ui/schematic_view/conftest.py` — PROJ-157
- [x] Delete `tests/unit/ui/battle_state_viewer/conftest.py` — PROJ-157
- [x] Delete `tests/unit/ui/left_panel/conftest.py` — PROJ-157
- [x] Delete `tests/unit/research/tech_tree/conftest.py` — PROJ-157
- [x] Delete `tests/unit/builder/conftest.py` — PROJ-157 (verified unused)
- [x] Delete `tests/unit/systems/conftest.py` — PROJ-157 (verified unused)
- [x] Delete `tests/unit/ai/conftest.py` — PROJ-157 (verified unused)

---

## Remaining Work Summary

1 file still needs deletion:
1. `tests/unit/simulation/update_test_ships.py` (Task 1.1)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
