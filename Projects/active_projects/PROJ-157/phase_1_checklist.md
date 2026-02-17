# Phase 1: Safe Deletions (Zero-Risk)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-157 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete files with zero unique tests or that test no production code.

---

## Baseline
- [ ] Run `pytest tests/ -x -q` and record test count
- [ ] Record baseline: _____ tests passed

---

## Task 1.1: Delete diagnostic scripts and non-test files [Simple]
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Delete `tests/trace_cargo.py` (52 lines) - diagnostic script, no test functions
- [ ] Delete `tests/unit/performance/generate_test_data.py` (99 lines) - utility script with `__main__` guard
- [ ] Delete `tests/unit/performance/profile_simulation.py` (210 lines) - cProfile profiling script
- [ ] Delete `tests/unit/performance/stress_test.py` (137 lines) - stress testing script
- [ ] Delete `tests/unit/performance/strategy_tournament.py` (263 lines) - tournament simulation script
- [ ] Run tests, verify pass

**Notes:**

---

## Task 1.2: Delete trivial scaffold files (import/hasattr checks only) [Simple]
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Delete `tests/unit/combat/test_combat_endurance_edge_cases.py` (27 lines) - one test is `pass`, other is `hasattr` check
- [ ] Delete `tests/unit/combat/test_targeting_edge_cases.py` (23 lines) - only checks modules importable
- [ ] Delete `tests/unit/entities/test_ship_formation_edge_cases.py` (22 lines) - only checks module/class exist
- [ ] Delete `tests/unit/entities/test_projectile_edge_cases.py` (22 lines) - only checks module/class exist
- [ ] Delete `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` (28 lines) - import existence checks only
- [ ] Delete `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` (27 lines) - import existence checks only
- [ ] Delete `tests/unit/core/test_error_codes_coverage.py` (~150 lines) - pure duplicate of `test_error_codes.py`, zero unique methods
- [ ] Delete `tests/unit/core/test_superweapon_input_actions.py` (~93 lines) - spot-checks already covered by exhaustive `test_covers_all_actions` iteration
- [ ] Delete `tests/unit/core/test_resource_loading.py` (~185 lines) - has duplicate class name (silently overwritten), `test_resources.py` is strict superset
- [ ] Delete `tests/unit/core/logger/test_warning.py` (~56 lines) - all tests duplicated or trivial existence checks
- [ ] Delete `tests/unit/ai/controllable_interface/test_interface_definition.py` (259 lines) - pure `hasattr` checks, ABC enforces at instantiation
- [ ] Run tests, verify pass

**Notes:**

---

## Task 1.3: Delete over-mocked files that test zero production code [Simple]
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Delete `tests/unit/ui/test_overlay.py` (127 lines) - tests Python's `not` operator on MagicMock, zero game imports
- [ ] Delete `tests/unit/ui/test_slider_snap_logic.py` (97 lines) - tests local helper methods defined on test class, no game import
- [ ] Delete `tests/unit/combat/test_lead.py` (143 lines) - tests local `MockVector` and local `solve_lead()`, not production `TargetingSystem.solve_lead()`
- [ ] Delete `tests/unit/combat/test_ccd.py` (208 lines) - tests local CCD algorithm never implemented in production
- [ ] Delete `tests/unit/research/research_controls/test_handle_event.py` (274 lines) - zero production code imported
- [ ] Delete `tests/unit/research/research_controls/test_event_formatting.py` (182 lines) - zero production code imported
- [ ] Delete `tests/unit/research/research_controls/test_node_selection.py` (113 lines) - zero production code imported
- [ ] Delete `tests/unit/ai/formation_prediction/test_other_behaviors.py` (164 lines) - ALL tests are strictly weaker copies of `test_behavior_units.py`
- [ ] Run tests, verify pass

**Notes:**

---

## Task 1.4: Delete old simulation framework [Simple]
**Tests:** `pytest tests/unit/simulation/ -x -q --tb=short`

- [ ] Delete `tests/unit/simulation/run_component_tests.py` (506 lines) - standalone script using pygame.init(), outside pytest
- [ ] Delete `tests/unit/simulation/component_logger.py` - utility only used by framework
- [ ] Delete `tests/unit/simulation/component_sim_tools.py` - utility only used by framework
- [ ] Delete `tests/unit/simulation/log_parser.py` - utility only used by framework
- [ ] Read `tests/unit/simulation/__init__.py` and remove exports referencing deleted files (ComponentTestLogger, TestEventType, enable_test_logging, TestLogParser, LogEvent)
- [ ] Run tests, verify pass

**Notes:**

---

## Task 1.5: Delete other confirmed files [Simple]
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Delete `tests/unit/regressions/test_crash_regressions.py` (114 lines) - zero positive assertions, catches `Exception` silently, commented-out assertions
- [ ] Delete `tests/unit/simulation/ship_combat_engine/test_creation_and_lead.py` (~100 lines) - `ShipCombatEngine` is pure delegation to `TargetingSystem`, which has 34 comprehensive tests
- [ ] Delete `tests/unit/simulation/ship_combat_engine/test_targeting.py` (~152 lines) - same reason as above
- [ ] Run tests, verify pass

**Notes:**

---

## Task 1.6: Delete 8 empty/dead conftest.py files [Simple]
**Tests:** `pytest tests/ -x -q --tb=short`

5 truly empty (docstring only):
- [ ] Delete `tests/unit/core/math_utils/conftest.py` (3 lines, docstring only)
- [ ] Delete `tests/unit/ui/schematic_view/conftest.py` (2 lines, docstring only)
- [ ] Delete `tests/unit/ui/battle_state_viewer/conftest.py` (5 lines, docstring + unused `import pytest`)
- [ ] Delete `tests/unit/ui/left_panel/conftest.py` (3 lines, docstring + unused `import pytest`)
- [ ] Delete `tests/unit/research/tech_tree/conftest.py` (6 lines, docstring + unused `import pytest`)

3 import-only dead code (imports with `# noqa: F401` but no tests use the fixtures):
- [ ] Delete `tests/unit/builder/conftest.py` (12 lines, imports 7 fixtures, none used by 25 tests in dir)
- [ ] Delete `tests/unit/systems/conftest.py` (12 lines, imports 6 fixtures, none used by 18 tests in dir)
- [ ] Delete `tests/unit/ai/conftest.py` (8 lines, imports 2 fixtures, none used by 16 tests in dir)
- [ ] Run tests, verify pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Record post-phase test count: _____ tests passed (delta: _____)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
