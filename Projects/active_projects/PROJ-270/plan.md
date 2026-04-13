# PROJ-270: Unified Battle Simulator Entry/Exit — Closure

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-270` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-270 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Headless single-entry cleanup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Combat Lab outcome adoption | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Battle Setup spec migration | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Visual-mode BattleOutcome contract | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. DTO cleanup | Partial (5.3 done; 5.1/5.2/5.4/5.5 remain) | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Strategic-modifier battle-math restoration (bounded) | Complete (Track A) | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Test coverage backfill | Partial (7.1/7.4 done; 7.2/7.3/7.5 remain) | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Final cleanup + acceptance audit | Partial (8.1/8.3 done; 8.2/8.4-8.7 remain) | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-04-12 — Session end (6 of 8 phases complete or partial; Phase 4 deferred to next session)
**Active Phase:** Phase 4 — Visual-Mode BattleOutcome Contract (deferred — highest-risk remaining work)
**Last Action:** Massive single-session progress. Phases 1, 2, 3, 6 (Track A), 8.3 complete. Phase 5.3, 7.1, 7.4, 8.1 done (partial coverage of those phases). The user-facing PROJ-270 acceptance criteria is now largely met for headless, strategy, Combat Lab, and Battle Setup paths — only visual-mode (Phase 4) and residual DTO cleanup (Phase 5.1/5.2/5.4/5.5) remain.
**Next Action:** Phase 4 — refactor `BattleController` to accept a `BattleSpec` and emit a `BattleOutcome` at battle end. `BattleResultsScreen` reads outcome. Highest-risk remaining work; requires careful TDD + manual smoke at end of phase. Once Phase 4 lands, the pytest guard in `tests/unit/simulation/test_unified_entry_guard.py` should be extended with a `TestVisualModeEmitsOutcome` class.
**Blockers:** None.
**Context for Next Agent:**
- **Completed this session:**
  - Phase 1: Headless single-entry bypasses eliminated (`test_execution_service.run_headless`, `BattleController.run_headless`, all 7 scenario `setup()` methods); new shared helper `combat_lab/services/scenario_run_helper.py`
  - Phase 2: `_run_validation(outcome, telemetry)` is the new contract across all 30 scenario files; new `combat_lab/telemetry.py`; the `engine_ref` closure trick is eradicated
  - Phase 3: `app.py::start_battle(spec)` + `battle_setup_screen._start_battle` → `build_manual_battle_spec` live production path
  - Phase 5.3: `BattleState.mode` field deleted
  - Phase 6 Track A: strategy compiler emits real `shield_capacity_mult` / `damage_mult` stat_keys for storm + fleet multipliers; `FleetAuraManager._append_external_from_entry` logs placeholder skips once per source
  - Phase 7.1: `_is_started` regression guard tests
  - Phase 7.4: 14 stale `update_from_battle_results = MagicMock()` assignments removed
  - Phase 8.1: 6 docstring-only stub test files deleted
  - Phase 8.3: `tests/unit/simulation/test_unified_entry_guard.py` — 8 guard tests locking the acceptance criteria
- **Regression state:** `pytest tests/` **14572 passed** / 3 pre-existing build-queue UI failures / 3 pre-existing AI import errors. Combat Lab **162/162 fast** + **170/170 full** green.
- **Deferred to follow-up sessions:**
  - **Phase 4 (visual-mode outcome contract):** MEDIUM-HIGH risk; `BattleController` spec acceptance + `BattleResultsScreen` rewrite + manual launcher smoke
  - **Phase 5.1:** delete `BattleConfig.test_scenario` field (need to route scenario-for-validation through a different channel)
  - **Phase 5.2:** move `ReturnDestination` enum from `game/simulation/battle_config.py` to `game/ui/navigation/`
  - **Phase 5.4:** collapse `BattleConfig.map_bounds` into `BattleSpec.boundary` (requires `RetreatManager` to consume `BoundaryRegion`)
  - **Phase 5.5:** audit `AIPolicy` / `CombatPolicies` / `ComponentStateSpec.is_active` / `TaskForceOutcome` for deletion vs wiring
  - **Phase 6.4a (sub-task):** delete `FleetAuraManager.initialize(config=...)` legacy branch — dead in production, requires 5 test rewrites
  - **PROJ-271:** `flat_shield_bonus` additive stat_key + suppressor opponent-team routing (battle-math Track B)
  - **Phase 7.2:** speed-recalc regression test in `test_post_battle_hook.py`
  - **Phase 7.3:** rewrite visual-mode UI fixture with real spec (`tests/fixtures/test_scenarios.py`)
  - **Phase 7.5:** re-fill `test_battle_config.py` with current-surface tests
  - **Phase 8.2:** delete stub modules `battle_factories.py` + `battle_mode_handler.py` once `docs/` refs are updated
  - **Phase 8.4:** manual-audit walkthrough of acceptance criteria
  - **Phase 8.5:** docs rewrite (`combat_simulation.md` §0–§1, `02_PATTERNS.md` §13, scenario base.py docstring examples)
  - **Phase 8.6:** archive PROJ-269 + PROJ-270 after user verification
  - **Phase 8.7:** final project regression gate including manual launcher smoke
- **Key files created this session:**
  - `combat_lab/services/scenario_run_helper.py` (shared headless driver)
  - `combat_lab/telemetry.py` (Combat Lab forensic bundle)
  - `tests/unit/simulation/test_unified_entry_guard.py` (acceptance-criteria guard)
  - `tests/unit/combat_lab/test_template_no_legacy_setup.py` (Task 1.3 regression guard)
- **PROJ-269:** still in `active_projects/` until its manual launcher smoke — independent of PROJ-270.

## Overview

Close the residual architectural gaps PROJ-269 Phase 6 left open. Make the user-facing claim "every battle enters via `run_battle(spec) → BattleOutcome`" actually true — today 5 production paths still bypass `run_battle`, visual-mode produces no `BattleOutcome`, Combat Lab validators discard the outcome, and placeholder stat_key decisions silently killed storm/fleet-modifier/complex-toggle battle math (a real gameplay regression vs pre-PROJ-269). PROJ-270 eradicates those gaps, restores the bounded subset of strategic modifiers that map 1:1 to existing stat_keys, and delivers a pytest guard test that locks the unified-entry contract in place going forward.

## Goals

- Every battle in production (Combat Lab headless, Combat Lab visual, Battle Setup, strategy, test-lab UI) enters via `run_battle(spec)` and exits via `BattleOutcome`.
- Combat Lab scenario validators consume `BattleOutcome` rather than capturing the live engine via a closure trick.
- Visual-mode UI (`BattleScreen`, `BattleResultsScreen`) reads from `BattleOutcome`, not live `BattleEngine` state.
- Strategic modifiers that previously affected battle math — storm shield interference, fleet `shield_mult`, fleet `damage_mult` — apply correctly again via real stat_keys (not placeholder).
- "Legacy-compatible / retained for now" dead code is eradicated per CLAUDE.md System Migration Policy.
- Test coverage backfills the genuine gaps (`_is_started=True` regression guard, speed-recalc regression, realistic visual-mode UI tests).
- Acceptance-criteria grep audit runs as a pytest guard so regressions are caught on PR.

## Scope

**In:**
- Migrate `test_execution_service.run_headless`, `BattleController.run_headless`, scenario template `setup(battle_engine)` methods to the unified entry.
- Rewrite Combat Lab `_run_validation` contract to accept `BattleOutcome`.
- Migrate `app.py::start_battle` and `battle_setup_screen._start_battle` through `build_manual_battle_spec`.
- Refactor `BattleController` to consume a `BattleSpec` and emit a `BattleOutcome` at battle end.
- Rewrite `BattleResultsScreen` to read from `BattleOutcome`.
- Trim `BattleConfig` to operational-only fields; move `ReturnDestination` to UI layer; delete `BattleState.mode` zombie field; collapse `BattleConfig.map_bounds` into `BattleSpec.boundary`.
- Map storm shield interference, fleet `shield_mult`, fleet `damage_mult` to real stat_keys in the strategy compiler (stat_key values that exist today: `shield_capacity_mult`, `damage_mult`).
- Delete the 7 docstring-only stub test files and 2 deprecation-stub modules (`battle_factories.py`, `battle_mode_handler.py`).
- Backfill test coverage (regression guards, visual-mode realism, speed-recalc test).
- Update `docs/systems/combat_simulation.md`, `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md` to reflect the now-true unified flow.
- Acceptance-criteria pytest guard test.

**Out (deferred to follow-up projects):**
- `FleetCombatModifiers.flat_shield_bonus` (needs new additive stat_key binding — scope trim point in Phase 6; deferred to PROJ-271 if time-boxed).
- Suppressor effects that apply negative multipliers to opponent teams (needs opponent-team routing in compiler — deferred to PROJ-271 if time-boxed).
- Complex-toggle content authoring bridge (design registry → stat_key mapping file) — deferred to content work outside PROJ-270.
- `HitRecord.modifiers_applied` per-hit contribution tracing (still "active-at-hit-time" per PROJ-269 decisions).
- PROJ-269's manual launcher smoke + project audit (remain with PROJ-269 itself).

## Key Files

| Component | File Path | Notes |
|-----------|-----------|-------|
| Headless service | [combat_lab/services/test_execution_service.py](../../../combat_lab/services/test_execution_service.py) | Phase 1: `run_headless` bypasses `run_battle` (lines 120–227) |
| Combat Lab runner | [combat_lab/runner.py](../../../combat_lab/runner.py) | Phase 2: `engine_ref` closure (line 175); `_run_validation(engine)` (line 228) |
| Test executor | [game/ui/screens/test_lab/test_executor.py](../../../game/ui/screens/test_lab/test_executor.py) | Phase 1/2: same closure pattern (lines 271, 303, 313) |
| Scenario templates | [combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py) | Phase 1: 5 legacy `setup(battle_engine)` at lines 145, 357, 553, 801, 1042; `_run_validation` at line 1406 |
| Scenario base | [combat_lab/scenarios/base.py](../../../combat_lab/scenarios/base.py) | Phase 2: `TestScenario._run_validation` contract |
| Propulsion custom scenarios | [combat_lab/scenarios/propulsion_scenarios.py](../../../combat_lab/scenarios/propulsion_scenarios.py) | Phase 1: Legacy `setup()` lines 941–943 |
| Battle controller | [game/simulation/battle_controller.py](../../../game/simulation/battle_controller.py) | Phase 1: delete `run_headless` (line 232); Phase 4: accept `BattleSpec` |
| Battle runner | [game/simulation/battle_runner.py](../../../game/simulation/battle_runner.py) | Phase 4: export `start_engine_from_spec`/`extract_outcome` for visual driver |
| Battle config | [game/simulation/battle_config.py](../../../game/simulation/battle_config.py) | Phase 5: trim fields (current 12 → visual-ops only); `ReturnDestination` (line 25) moves to UI |
| Battle state | [game/simulation/battle_state.py](../../../game/simulation/battle_state.py) | Phase 5: delete `mode: str = "manual"` (line 607); touches `to_dict/from_dict/capture_from_engine` |
| Battle outcome | [game/simulation/battle_outcome.py](../../../game/simulation/battle_outcome.py) | Phase 2/4: extend fields if needed for validator parity |
| App entry | [game/app.py](../../../game/app.py) | Phase 3: `start_battle` (line 543) inline controller setup → `build_manual_battle_spec` |
| Battle setup screen | [game/ui/screens/battle_setup_screen.py](../../../game/ui/screens/battle_setup_screen.py) | Phase 3: `_start_battle` (line 1022), `_sync_complex_toggles_to_state` (line 1121) |
| Battle screen | [game/ui/screens/battle_screen.py](../../../game/ui/screens/battle_screen.py) | Phase 4: construct `BattleController` from spec |
| Battle results screen | [game/ui/screens/battle_results_screen.py](../../../game/ui/screens/battle_results_screen.py) | Phase 4: consume `BattleOutcome`, not live engine |
| Strategy compiler | [game/strategy/combat/spec_compiler.py](../../../game/strategy/combat/spec_compiler.py) | Phase 6: storm / fleet modifier placeholder → real stat_keys |
| Battle setup compiler | [game/ui/screens/battle_setup/spec_compiler.py](../../../game/ui/screens/battle_setup/spec_compiler.py) | Phase 6: complex toggles → real stat_keys where mappable |
| Fleet aura manager | [game/simulation/combat/fleet_aura_manager.py](../../../game/simulation/combat/fleet_aura_manager.py) | Phase 6: log unknown stat_keys instead of silent skip |

## Related Documents

- [design.md](design.md) — Audit findings, architectural decisions, validator-to-outcome mapping
- [decisions.md](decisions.md) — Full decisions log (scope, sequencing, acceptance)
- [manifest.md](manifest.md) — File inventory for parallel execution
- Parent project: [PROJ-269](../PROJ-269/plan.md) — Unified Battle Simulator Entry/Exit (implementation declared complete; closure work moved to PROJ-270)

## Verification

### Per-phase gates
- `pytest tests/ --testmon` green after each task (incremental)
- `python -m combat_lab.run_tests --fast --no-history` stays ≥ 162/162 after each phase
- Phase-specific failing tests turn green

### Final project gates
- [ ] `pytest tests/` green at baseline or better (starting baseline: 14577 passed, 3 pre-existing build-queue failures, 3 pre-existing AI import errors)
- [ ] `python -m combat_lab.run_tests --fast --no-history` 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` (full, includes -HT) 170/170 green
- [ ] Acceptance-criteria pytest guard (Phase 8.3) green — no forbidden symbols re-entered live code
- [ ] Manual smoke via `python launcher.py`:
  - Combat Lab visual single + headless single + run-all batch
  - Battle Setup 2v2 with at least one toggled complex modifier
  - Strategy fleet conflict with damage-persistence verification across multiple turns
- [ ] Project audit (`Projects/protocols/04_audit_project.md`)
- [ ] Docs read start-to-finish without forward-references to unlanded tasks
- [ ] All 8 phase checklists green
- [ ] User verified
