# Phase 1: Delete Zero-Risk Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-155 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove files confirmed as pure duplicates, empty scaffolds, or dead code. No unique tests to preserve.
**Priority:** Immediate

---

## Tasks

### Task 1.1: Delete old component test framework [Simple]
**Files:** `tests/unit/simulation/`
**Tests:** `pytest tests/unit/simulation/ -n 12 -q`

- [ ] Delete `tests/unit/simulation/run_component_tests.py` (505 lines)
- [ ] Delete `tests/unit/simulation/update_test_ships.py` (57 lines)
- [ ] Delete `tests/unit/simulation/component_logger.py` (278 lines)
- [ ] Delete `tests/unit/simulation/component_sim_tools.py` (156 lines)
- [ ] Delete `tests/unit/simulation/log_parser.py` (360 lines)
- [ ] Delete `tests/unit/simulation/output/logs/` directory (7 .log files)
- [ ] Delete `tests/unit/simulation/test_configs/` directory (12 .json files)
- [ ] Clean up `tests/unit/simulation/__init__.py` — remove dead exports (ComponentTestLogger, TestEventType, enable_test_logging, TestLogParser, LogEvent)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.2: Delete trivial scaffold files [Simple]
**Files:** `tests/unit/entities/`
**Tests:** `pytest tests/unit/entities/ -q`

- [ ] Delete `tests/unit/entities/test_ship_formation_edge_cases.py` (21 lines — 2 import checks)
- [ ] Delete `tests/unit/entities/test_projectile_edge_cases.py` (21 lines — 2 import checks)
- [ ] Delete `tests/unit/entities/test_ability_aggregator_scope.py` (36 lines — 5 import checks)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.3: Delete confirmed core duplicates [Simple]
**Files:** `tests/unit/core/`
**Tests:** `pytest tests/unit/core/ -n 12 -q`

- [ ] Delete `tests/unit/core/test_error_codes_coverage.py` (150 lines — all 8 tests duplicated by test_error_codes.py)
- [ ] Delete `tests/unit/core/test_superweapon_input_actions.py` (92 lines — covered by test_input_actions.py exhaustive iteration)
- [ ] Delete `tests/unit/core/test_resource_loading.py` (184 lines — has duplicate class name, test_resources.py is superset)
- [ ] Delete `tests/unit/core/logger/test_warning.py` (55 lines — all tests duplicated in test_logger.py)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.4: Delete ShipCombatEngine delegation duplicates [Simple]
**Files:** `tests/unit/simulation/ship_combat_engine/`
**Tests:** `pytest tests/unit/simulation/ -n 12 -q`

- [ ] Delete `tests/unit/simulation/ship_combat_engine/test_creation_and_lead.py` (100 lines)
- [ ] Delete `tests/unit/simulation/ship_combat_engine/test_targeting.py` (152 lines)
- [ ] Check if ship_combat_engine/ directory is now empty; if so, remove the directory
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.5: Delete UI dead code [Simple]
**Files:** `tests/unit/ui/`
**Tests:** `pytest tests/unit/ui/ -n 4 -q`

- [ ] Delete `tests/unit/ui/test_overlay.py` (127 lines — tests Python `not` operator on MagicMock)
- [ ] Delete `tests/unit/ui/test_race_validator.py` (282 lines — root-level duplicate; screens/ version is superset)
- [ ] Delete `tests/unit/ui/mocks/mock_battle_ui_service.py` (256 lines — never imported by any test)
- [ ] Check `tests/unit/ui/mocks/__init__.py` for MockBattleUIService re-export; clean up if present
- [ ] Delete `tests/unit/ui/test_slider_snap_logic.py` (96 lines — tests methods on test class, no game code)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.6: Delete AI/Combat dead code [Simple]
**Files:** `tests/unit/ai/`, `tests/unit/combat/`, `tests/unit/research/`
**Tests:** `pytest tests/unit/ai/ tests/unit/combat/ tests/unit/research/ -n 12 -q`

- [ ] Delete `tests/unit/ai/controllable_interface/test_interface_definition.py` (258 lines — 30 hasattr checks)
- [ ] Delete `tests/unit/combat/test_combat_endurance_edge_cases.py` (26 lines — `pass` + import check)
- [ ] Delete `tests/unit/combat/test_targeting_edge_cases.py` (22 lines — import checks only)
- [ ] Delete `tests/unit/combat/test_lead.py` (142 lines — tests local MockVector/solve_lead, not production)
- [ ] Delete `tests/unit/combat/test_ccd.py` (207 lines — algorithm never in production; engine/test_ccd.py tests real code)
- [ ] Delete `tests/unit/ai/formation_prediction/test_other_behaviors.py` (163 lines — weaker copies of test_behavior_units.py)
- [ ] Delete `tests/unit/research/research_controls/test_handle_event.py` (273 lines — zero production code imported)
- [ ] Delete `tests/unit/research/research_controls/test_event_formatting.py` (181 lines — zero production code imported)
- [ ] Delete `tests/unit/research/research_controls/test_node_selection.py` (112 lines — zero production code imported)
- [ ] Check if `tests/unit/research/research_controls/` directory is now empty; remove if so
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.7: Delete Strategy scaffolds and duplicates [Simple]
**Files:** `tests/unit/strategy/`
**Tests:** `pytest tests/unit/strategy/ -n 12 -q`

- [ ] Delete `tests/unit/strategy/test_fleet_resource_aggregator.py` (195 lines — root-level subset of data/ version)
- [ ] Delete `tests/unit/strategy/conflict_resolution/test_conflict_core.py` (22 lines — 2 import checks)
- [ ] Delete `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` (26 lines — 3 import checks)
- [ ] Delete `tests/unit/strategy/data/test_build_queue_source_errors.py` (28 lines — empty scaffold)
- [ ] Delete `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` (27 lines — 3 import checks)
- [ ] For `tests/unit/strategy/test_hex_math.py`: verify unique tests (radius-2 ring, diagonal distance, pixel near-center, ring size formula) against `tests/unit/core/test_hex_math_core.py`. If covered, delete. If not, migrate first.
- [ ] Delete `tests/unit/strategy/test_hex_math.py` (298 lines) after verification
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.8: Delete scripts and diagnostic files [Simple]
**Files:** `tests/`, `tests/unit/performance/`, `tests/unit/regressions/`
**Tests:** `pytest tests/ -n 12 -q`

- [ ] Delete `tests/trace_cargo.py` (51 lines — diagnostic script, no test functions)
- [ ] Delete `tests/unit/performance/generate_test_data.py` (99 lines — utility script with __main__ guard)
- [ ] Delete `tests/unit/performance/profile_simulation.py` (209 lines — cProfile script with __main__ guard)
- [ ] Delete `tests/unit/performance/stress_test.py` (136 lines — stress test script with __main__ guard)
- [ ] Delete `tests/unit/performance/strategy_tournament.py` (262 lines — tournament script with __main__ guard)
- [ ] **DO NOT** delete `tests/unit/performance/reproduce_scaling.py` — legitimate pytest test
- [ ] Delete `tests/unit/regressions/test_crash_regressions.py` (113 lines — zero positive assertions)
- [ ] Run tests to verify no regressions

**Notes:**

### Task 1.9: Delete empty conftest.py files [Simple]
**Files:** Various
**Tests:** `pytest tests/ -n 12 -q`

- [ ] Delete `tests/unit/core/math_utils/conftest.py` (2 lines — comment only)
- [ ] Delete `tests/unit/ui/schematic_view/conftest.py` (1 line — docstring only)
- [ ] Delete `tests/unit/ui/battle_state_viewer/conftest.py` (4 lines — docstring + unused pytest import)
- [ ] Delete `tests/unit/ui/left_panel/conftest.py` (2 lines — docstring + unused pytest import)
- [ ] Delete `tests/unit/research/tech_tree/conftest.py` (5 lines — docstring + unused pytest import)
- [ ] **DO NOT** delete builder/, systems/, ai/ conftest.py — they have fixture imports
- [ ] Run tests to verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12 -q` — verify no new failures vs baseline (12,790 passed, 143 failed)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
