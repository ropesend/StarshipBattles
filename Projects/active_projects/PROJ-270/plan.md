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
| 2. Combat Lab outcome adoption | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Battle Setup spec migration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Visual-mode BattleOutcome contract | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. DTO cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Strategic-modifier battle-math restoration (bounded) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Test coverage backfill | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Final cleanup + acceptance audit | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-04-12 — Phase 1 COMPLETE
**Active Phase:** Phase 2 — Combat Lab outcome adoption
**Last Action:** Phase 1 Complete. All 5 tasks (1.1–1.5) checked. Headless single-entry bypasses eliminated: `test_execution_service.run_headless` now drives `run_battle(spec)` via new shared `combat_lab/services/scenario_run_helper.py`; `BattleController.run_headless()` deleted; all 7 scenario-class `setup(battle_engine)` methods deleted (5 templates + 2 custom propulsion scenarios + base abstract); "Legacy-compatible / retained for" markers eradicated (one `fleet_aura_manager` legacy branch deferred to Phase 6 sub-task 6.4a — migrating requires rewriting 5 tests). Regression: **14572 passed / 3 pre-existing UI failures / 3 pre-existing AI import errors**; Combat Lab **162/162 fast** + **170/170 full** green.
**Next Action:** Begin Phase 2 Task 2.1 — validator-to-outcome field inventory. Read the 5 Combat Lab templates' `_run_validation` / `validate` methods + the 5 custom non-template scenarios' validators. Enumerate every `engine.*` / `self.attacker.*` / `self.target.*` read. Produce the mapping table in `design.md`. Identify gaps (in-flight projectile counts, per-tick position tracks) and route them to Option B (Combat-Lab-specific `CombatLabTelemetry` bundle, NOT simulation-layer `BattleOutcome` extension — decisions.md Decision 6).
**Blockers:** None.
**Context for Next Agent:**
- Phase 1 created a new module `combat_lab/services/scenario_run_helper.py` exposing `run_scenario_via_run_battle(scenario, *, seed_override, pre_tick_loop_hook, per_tick_hook) -> (engine, outcome)`. This is the shared headless driver used by `test_execution_service.run_headless` (and should be used by `test_executor._run_scenario_via_run_battle` if Phase 2 consolidates further).
- The `engine_ref["engine"] = engine` closure trick STILL LIVES in the helper (returns the captured engine so the Phase-1 validator contract still works). Phase 2 Task 2.5 explicitly deletes this closure once validators consume `BattleOutcome`.
- Docstring examples in `combat_lab/scenarios/base.py` + `__init__.py` still show the legacy `battle_engine.start(...)` API — flagged for Phase 8.5 docs rewrite.
- `fleet_aura_manager.initialize(config=...)` legacy branch (line 90-107) is dead in production but removing requires rewriting 5 tests — captured in Phase 6 checklist as sub-task 6.4a.
- Baseline numbers for Phase 2 gate: 14572 pass / 3 fail / 3 err / 162 combat_lab fast / 170 combat_lab full.
- PROJ-269 still in `active_projects/` until manual launcher smoke — independent of PROJ-270.

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
