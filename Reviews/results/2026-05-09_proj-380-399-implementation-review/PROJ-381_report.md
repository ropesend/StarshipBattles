# PROJ-381 Implementation Review

**Project:** PROJ-381 - Error handling cleanup, strategy/ui/assets/sim  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** Needs follow-up. The current codebase meets most of PROJ-381's user-visible and hygiene goals, especially after PROJ-395 remediated several serious review findings, but the implementation is not clean against the literal plan. One battle-context preservation path is still incomplete, and the project checklists overstate test traceability.

## Validation Result

- `python Projects/scripts/validate_audit_ready.py PROJ-381`: **PASSED**
  - All 3 phases complete.
  - All 30 tasks complete.
  - No blockers reported.
  - Warning: project index still lists `PROJ-381` as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-381 1`: **PASSED**, 3 warnings for empty task Notes.
- `python Projects/scripts/validate_phase.py PROJ-381 2`: **PASSED**, 15 warnings for empty task Notes.
- `python Projects/scripts/validate_phase.py PROJ-381 3`: **PASSED**, 12 warnings for empty task Notes.

## Tests Run

- `pytest -q -p no:cacheprovider tests/integration/ui/test_strategy_turn_error_boundary.py tests/unit/ui/services/image/test_background.py tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py tests/unit/strategy/services/test_design_validator.py tests/unit/strategy/test_game_session.py tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py tests/unit/strategy/turn_engine/test_turn_state_snapshot.py tests/unit/strategy/data/test_star_generation_config.py tests/unit/strategy/adapters/test_simulation_adapter.py tests/unit/simulation/battle_runner/test_spec_component_validation.py`
  - **96 passed in 2.50s**
- Inline probe: patched `game.strategy.adapters.simulation_adapter.run_battle` to raise `ValidationException`.
  - Observed raw `ValidationException`, not `BattleResolutionError`; context was `{}`.

Full sharded suite was not run for this sub-review. The project plan also says the full sharded run was deferred to an orchestrator boundary.

## Plan Goals vs Actual Implementation

### Phase 1 - Critical UI Error Boundary

Current code meets the core goal: turn-processing failures now surface in game instead of escaping to the top-level crash handler. `StrategyGameStateManager.process_full_turn()` catches `TurnFailedError` and, defensively, raw `EnginePhaseError`, clears progress overlay state in `finally`, skips autosave/event-log work after a failed turn, and opens `TurnFailedDialog`.

Important caveat: the initial PROJ-381 plan failed to account for modal input blocking. The follow-up PROJ-395 review found that the first PROJ-381 dialog used a raw `UIMessageWindow`, allowing click-through. Current code has been corrected with `TurnFailedDialog(StrategyModalWindow)`, and the current regression test covers modal registration.

### Phase 2 - Major Hygiene and Boundary Fixes

The broad-catch comments, JSON helper migrations, `ImageUnexpectedError`, `SessionInitializationError`, design-validator error surfacing, and conflict modifier ERROR logging are implemented and covered by focused tests. PROJ-395 also corrected several initially missed or weak items, including `CommandRegistry.register()` duplicate-command errors and command-handler test assertions.

### Phase 3 - Minor Context, Narrowing, and Parity Work

Most goals are implemented: `EnginePhaseError` context has `turn_number` and `save_path`; `ImageBackgroundCall.wait()` exists; star generation config now lets `ValueError`/`KeyError` propagate; JSON file reads moved to `load_json`; crash snapshots use `save_json`.

The exception-context goal for strategy battle resolution is incomplete: `SimulationBattleResolver` only wraps `SimulationException`, but `run_battle` can raise `ValidationException`, and the checklist explicitly required a `ValidationException` regression test.

## Literal Checklist Execution

- All checklist boxes are checked and validators pass.
- Checklist `Tests:` paths in Phase 2 and Phase 3 mostly point to non-existent paths such as `tests/strategy/...` instead of the actual `tests/unit/strategy/...` layout. This makes the checklist hard to rerun literally.
- `phase_3_checklist.md` Task 3.10 says to inject `ValidationException` from `run_battle`; the implemented test intentionally switched to a custom `SimulationException` and leaves the named case uncovered.
- `phase_3_checklist.md` Task 3.9 says the UI catch should switch to `TurnFailedError` and never see raw `EnginePhaseError`; current code still imports and catches `EnginePhaseError` as a defensive fallback. PROJ-395 documents this as deferred MAJ-014.
- The project `Verification` section still has the full sharded suite and audit/user verification unchecked.

## Findings

### 1. Major - Battle context wrapper misses `ValidationException` from `run_battle`

**Evidence:**
- `Projects/active_projects/PROJ-381/phase_3_checklist.md:78-79` says battle context preservation should keep `fleet_ids`, `hex_coord`, and `empire_ids`, and specifically requires a regression test injecting `ValidationException`.
- `game/strategy/adapters/simulation_adapter.py:292-300` catches only `SimulationException`.
- `game/simulation/battle_runner.py:640-652` raises `ValidationException` for `ShipSpec.components` entries that do not map to a materialized component.
- `tests/unit/strategy/adapters/test_simulation_adapter.py:391-404` explicitly avoids the checklist's `ValidationException` case and tests a custom `SimulationException` instead.
- Inline probe confirmed current behavior: a patched `run_battle` raising `ValidationException` propagates raw with empty context.

**Impact:** A real validation failure in the simulation battle path can still lose the strategy battle context that B-6 was meant to preserve. Crash/log consumers will not get `fleet_ids`, `empire_ids`, or `hex_coord` for that failure class.

### 2. Minor - Facade conversion is not directly pinned, and the UI still accepts raw engine errors

**Evidence:**
- `Projects/active_projects/PROJ-381/phase_3_checklist.md:71-72` requires facade-level conversion to `TurnFailedError` and says the UI handler should not see raw `EnginePhaseError` after the fix.
- `game/strategy/facade/strategy_session_facade.py:194-201` implements conversion, but `rg "TurnFailedError" tests` only finds UI boundary tests, not a facade test.
- `game/ui/screens/strategy_game_state_manager.py:19` imports `EnginePhaseError`, and `game/ui/screens/strategy_game_state_manager.py:149-158` catches it.

**Impact:** The behavior is robust for users, but the layer-separation claim is not literally met and the facade conversion can regress without a focused unit test.

### 3. Minor - Checklist test references are stale/non-runnable

**Evidence:**
- Phase 2 `Tests:` lines such as `phase_2_checklist.md:17`, `:23`, `:43`, `:94`, and `:103` point to missing paths.
- Phase 3 `Tests:` lines such as `phase_3_checklist.md:17`, `:32`, `:69`, `:76`, and `:83` point to missing paths.
- The actual tests live mainly under `tests/unit/...`, and focused current paths pass.

**Impact:** The implementation can be validated, but not by following the project checklist literally. This weakens the audit trail and hides coverage substitutions like the `ValidationException` to `SimulationException` change.

## Plan Gaps and Missed Assumptions

- The original B-5 plan treated "show an error dialog" as sufficient and missed Pattern #31 modal blocking. PROJ-395 fixed this, but PROJ-381 was not audit-clean on its own.
- The B-6 plan did not settle the exception taxonomy at the strategy/simulation boundary. It named `SimulationException` in the implementation bullet but `ValidationException` in the test bullet; current code follows the narrower implementation bullet and misses a real `run_battle` failure type.
- The project validation scripts check checkbox completion but not whether `Tests:` commands point to real files or whether required tests assert the exact planned failure type.

## Residual Risks

- Full sharded suite was not rerun in this sub-review.
- `Projects/projects_index.md` still lists PROJ-381 as `Planning`, matching the audit-ready warning.
- Empty task Notes across all phases make it harder to reconstruct why some test substitutions happened.

