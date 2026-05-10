# PROJ-270 File Manifest

> Generated during project init. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.

## Production Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| combat_lab/services/test_execution_service.py | Production | 1 | `run_headless` bypasses `run_battle` — migrate to unified entry |
| combat_lab/scenarios/templates.py | Production | 1, 2 | Phase 1: delete 5 `setup()` methods (lines 145, 357, 553, 801, 1042). Phase 2: rewrite `_run_validation` (line 1406) to accept `BattleOutcome` |
| combat_lab/scenarios/base.py | Production | 2 | Phase 2: change `TestScenario._run_validation` contract |
| combat_lab/scenarios/propulsion_scenarios.py | Production | 1 | Delete legacy `setup()` (lines 941–943) |
| combat_lab/scenarios/tohit_attack_fleet_scenarios.py | Production | 1 | Audit for any remaining legacy `setup()` |
| combat_lab/runner.py | Production | 2 | Remove `engine_ref` closure; validator consumes outcome |
| combat_lab/spec_compiler.py | Production | 2 | Possibly extend if outcome adoption reveals missing scenario data |
| combat_lab/battle_state_capture.py | Production | 2 | Verify interaction with new validator contract |
| game/simulation/battle_controller.py | Production | 1, 4 | Phase 1: delete `run_headless` (line 232). Phase 4: accept `BattleSpec`, emit `BattleOutcome` |
| game/simulation/battle_runner.py | Production | 4 | Export `start_engine_from_spec` + `extract_outcome` for `BattleController` use |
| game/simulation/battle_config.py | Production | 5 | Trim: delete `test_scenario` (line 66), `map_bounds` (line 69). Move `ReturnDestination` (line 25) to UI |
| game/simulation/battle_state.py | Production | 5 | Delete `mode: str = "manual"` (line 607); touches `to_dict`/`from_dict`/`capture_from_engine` |
| game/simulation/battle_outcome.py | Production | 2, 4 | Audit `AIPolicy`, `CombatPolicies`, `ComponentStateSpec.is_active`, `TaskForceOutcome` usage; extend/delete |
| game/simulation/battle_spec.py | Production | 5 | Audit unused spec fields (see above) |
| game/simulation/services/battle_service.py | Production | 4 | Verify interaction with `BattleController` refactor |
| game/simulation/combat/fleet_aura_manager.py | Production | 6 | `_append_external_from_entry`: log unknown stat_keys (stop silent skip) |
| game/simulation/managers/battle_state_manager.py | Production | 5 | Remove `mode` threading if downstream of `BattleState.mode` deletion |
| game/app.py | Production | 3 | `start_battle` (line 543) migrates through `build_manual_battle_spec` |
| game/ui/screens/battle_setup_screen.py | Production | 3 | `_start_battle` (line 1022); delete `_sync_complex_toggles_to_state` indirection (line 1121) |
| game/ui/screens/battle_setup/spec_compiler.py | Production | 3, 6 | Phase 3: consumed directly by `_start_battle`. Phase 6: map complex toggles to real stat_keys where applicable |
| game/ui/screens/battle_screen.py | Production | 4 | `BattleScreen.start` constructs `BattleController` from spec |
| game/ui/screens/battle_results_screen.py | Production | 4 | Read `BattleOutcome`, not live `BattleEngine` state |
| game/ui/screens/test_lab/screen.py | Production | 1, 2, 4 | Same closure/validator patterns as test_executor |
| game/ui/screens/test_lab/test_executor.py | Production | 1, 2 | Remove closure trick; validator consumes outcome |
| game/ui/services/battle_factories.py | Production | 8 | Delete stub module (currently docstring-only) |
| game/simulation/combat/battle_mode_handler.py | Production | 8 | Delete stub module (currently docstring-only) |
| game/strategy/combat/spec_compiler.py | Production | 6 | Storm `shield_capacity_mult`, fleet `shield_mult`, fleet `damage_mult` → real stat_keys (not "placeholder") |
| game/ui/navigation/return_destination.py | New production | 5 | New file; receives `ReturnDestination` enum moved from `battle_config.py` |

## Test Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| tests/unit/combat_lab/services/test_test_execution_service.py | Test (modify) | 1 | Add failing test for Phase 1.1 (spec-driven `run_headless`) |
| tests/unit/simulation/battle_controller/test_execution.py | Test (modify) | 1 | Add failing test asserting `run_headless` method deleted |
| tests/unit/combat_lab/test_outcome_validation.py | Test (new) | 2 | Failing tests per validator type — outcome-consumption contract |
| tests/unit/combat_lab/test_validator_to_outcome_mapping.py | Test (new) | 2 | Per-template validator field mapping tests |
| tests/unit/combat_lab/test_spec_compiler.py | Test (modify) | 2 | Extend if new forensic data added |
| tests/unit/ui/screens/test_battle_setup_spec_flow.py | Test (new) | 3 | Failing tests asserting Start button produces BattleSpec with right teams, boundary, modifiers |
| tests/integration/ui/test_visual_battle_outcome.py | Test (new) | 4 | End-to-end: 2v2 battle through BattleController produces BattleOutcome reaching BattleResultsScreen |
| tests/unit/simulation/test_battle_config.py | Test (rewrite from stub) | 5 | Tests for trimmed BattleConfig surface |
| tests/unit/simulation/test_battle_state.py | Test (modify) | 5 | Remove `mode` field tests; keep save/load coverage |
| tests/unit/ui/navigation/test_return_destination.py | Test (new) | 5 | Tests for moved enum |
| tests/unit/strategy/combat/test_spec_compiler_battle_math.py | Test (new) | 6 | Failing tests: storm hex reduces shields in outcome; shield_mult team modifier applies |
| tests/unit/strategy/combat/test_post_battle_hook.py | Test (modify) | 7 | Add speed-recalc regression test |
| tests/unit/simulation/combat/test_fleet_aura_manager.py | Test (modify) | 6 | Assert unknown stat_keys log warning (not silent skip) |
| tests/unit/simulation/battle_controller/test_initialization.py | Test (modify) | 7 | Add regression guard: `_is_started=True` cannot be set externally |
| tests/fixtures/test_scenarios.py | Test fixture (modify) | 7 | Replace `teams=()` short-circuit with real-spec fixture |
| tests/unit/strategy/conflict_resolution/conftest.py | Test conftest (modify) | 7 | Remove stale `update_from_battle_results = MagicMock()` |
| tests/unit/strategy/test_engine_event_emission.py | Test (modify) | 7 | Remove stale MagicMock assignments |
| tests/unit/simulation/test_unified_entry_guard.py | Test (new) | 8 | Acceptance-criteria grep guard — fails if forbidden symbols re-enter live code |
| tests/unit/simulation/combat/test_battle_mode_handlers.py | Test (delete) | 8 | Stub file; delete |
| tests/unit/ui/services/test_battle_factories.py | Test (delete) | 8 | Stub file; delete |
| tests/unit/strategy/fleet/test_fleet_battle_adapter_identity.py | Test (delete) | 8 | Stub file; delete |
| tests/unit/simulation/battle_controller/test_config.py | Test (delete) | 8 | Stub file; delete |
| tests/unit/simulation/battle_controller/test_edge_cases.py | Test (delete) | 8 | Stub file; delete |
| tests/unit/simulation/battle_controller/test_retreat_priority.py | Test (delete) | 8 | Stub file; delete |

## Documentation Files

| File | Phase | Notes |
|------|-------|-------|
| docs/systems/combat_simulation.md | 8 | §0–§2 rewrite: remove forward-references to "Task 6.9", describe the now-true unified flow |
| docs/02_PATTERNS.md | 8 | §13 "Spec Compiler + run_battle" — remove any deferred-work language |
| docs/01_ARCHITECTURE.md | 8 | Battle Flow §339-381 — update if visual-mode BattleController diagram changed |
| docs/systems/strategy_layer.md | 6 | Strategic-to-Combat Bridge section — document real stat_keys (not placeholder) |
| docs/04_SERVICES.md | 4 | BattleService section — remove "for headless callers, prefer run_battle" (now true for all callers) |

## Project Management Files

| File | Phase | Notes |
|------|-------|-------|
| Projects/active_projects/PROJ-269/plan.md | 0 | Cross-link Current State to PROJ-270 (done at project init) |
| Projects/projects_index.md | 0 | PROJ-270 entry added by `create_project.py` (done at init) |
| Projects/active_projects/PROJ-270/phase_{1..8}_checklist.md | Each | Phase completion notes added during implementation |
| Projects/active_projects/PROJ-270/plan.md | Each | Current State + Quick Status updated after each phase |

## Conflict Detection Notes for Parallel Execution

Phases 1–4 are sequentially dependent (1 → 2 → 4; 3 can parallel 2). Phases 5, 6, 7 can run in parallel once Phase 4 lands. Phase 8 depends on all others.

**No overlap:**
- Phase 1 (headless) and Phase 3 (battle setup) touch different files — safe to parallel if needed.
- Phase 5 (DTO cleanup) and Phase 6 (battle math) touch different files.

**Forced sequential:**
- Phase 2 must precede Phase 4 (outcome contract dependency).
- Phase 8 is always last.
