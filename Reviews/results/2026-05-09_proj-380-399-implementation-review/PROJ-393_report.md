# PROJ-393 Implementation Review

Date: 2026-05-09
Reviewer: Codex

## Verdict

FAIL - audit blocked.

The implementation removed several planned legacy paths and the focused tests I ran are green, but PROJ-393 is not audit-ready. `validate_audit_ready.py` fails because the project marks phases complete while required phase-completion and full-regression checklist items remain unchecked. The plan also closed with three Phase 3 tasks deferred, so the original Phase 3 goals were not fully met by this project.

I also found one remaining behavioral gap: passenger-load validation still accepts a missing `species_id`, while the executor now treats missing `species_id` as a no-op after PROJ-393 removed the first-species fallback.

## Validation Result

Command:

```text
python Projects/scripts/validate_audit_ready.py PROJ-393
```

Result: failed.

Validator blockers:

- Phase 1 > Task 1.1: 4 unchecked completion subtasks.
- Phase 2 > Task 2.6: 5 unchecked completion/regression subtasks.
- Phase 3 > Task 3.8: 5 unchecked completion/regression subtasks.
- Index warning: PROJ-393 is still `Planning` in `Projects/projects_index.md`.

Additional phase validators:

- `python Projects/scripts/validate_phase.py PROJ-393 1` failed: Task 1.1 incomplete and Phase 1 status says complete.
- `python Projects/scripts/validate_phase.py PROJ-393 2` failed: Task 2.6 incomplete and Phase 2 status says complete; 5 notes warnings.
- `python Projects/scripts/validate_phase.py PROJ-393 3` failed: Task 3.8 incomplete and Phase 3 status says complete; 7 warnings.

## Tests And Checks Run

- `pytest tests/unit/test_run_loop.py tests/unit/research/research_scene/test_event_routing_and_draw.py tests/unit/ui/screens/test_galaxy_test_screen.py tests/unit/strategy/validation/test_planet_order_validator.py tests/unit/ui/panels/test_build_queue_drag_handler.py tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/ui/screens/test_build_queue_helpers.py tests/unit/ui/test_sprites.py tests/unit/ui/test_sprite_loading.py tests/unit/strategy/engine/order_handlers/test_transfer_handler.py tests/unit/strategy/engine/test_transfer_order.py tests/unit/strategy/engine/test_order_processor_transfer.py -q` - 303 passed.
- `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py tests/unit/ui/screens/test_planet_list_window.py tests/unit/ui/screens/test_build_queue_panel_factory.py tests/unit/ui/panels/test_planet_report_panel_characterization.py tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/ui/screens/test_battle_screen_edge_cases.py -q` - 184 passed.
- `pytest tests/ -k "transfer or load_population or passengers" -q` - 325 passed.
- Asset scan for basename `Comp_NNN` under `assets/Images/Components` - no matches.
- Inline probe of `TransferValidator.validate(..., cargo_type="passengers", direction="load", species_id=None, skip_location_check=True)` - returned `ValidationResult(is_valid=True, errors=[], warnings=[], error_code=None)`.

I did not run the full sharded suite. The audit gate already failed, and the PROJ-393 checklists themselves leave the full sharded suite unchecked/deferred.

## Plan Goals vs Actual Implementation

### Phase 1

Goal: delete four stale comments only.

Current implementation appears to have met the code goal. The direct task checkboxes are checked, and no focused code risk was found. Literal project execution is still not clean because the Phase 1 completion checklist remains unchecked even though the phase status says `Complete`.

### Phase 2

Goal: move the research and galaxy-test scene input path to the current scene API and remove four test-injection fallback branches.

The core implementation appears to be in place:

- `game/run_loop.py:202-208` now calls `update_input` for the relevant scenes rather than a `handle_input` branch.
- `game/ui/research/research_scene.py` and `game/ui/screens/galaxy_test/screen.py` expose `handle_event` and `update_input`.
- `game/strategy/validation/planet_order_validator.py:50-64` and `:93-102` use component-key-specific validation without the old ability-name fallback.
- `game/ui/panels/build_queue_drag_handler.py:53-71` requires `on_remove_from_queue`, and `:208` calls the injected callback.

Focused tests for these areas passed. Literal execution is not audit-clean because Task 2.6 still leaves the full sharded suite unchecked and the phase-completion checklist is unchecked.

### Phase 3

Goal: delete seven mixed legacy/backward-compat paths.

Implemented or currently resolved in the tree:

- `game/strategy/engine/planet_action_engine.py:352-376` removed the non-dict `PlanetaryShield` target fallback.
- `game/ui/screens/build_queue_helpers.py:11-17` and `game/ui/screens/strategy_ui.py:28-31` now lazy-load planetary resource IDs.
- `game/ui/renderer/sprites.py:11-12` has only the canonical portrait pattern; `_LEGACY_PATTERN` is gone.
- `game/strategy/engine/order_handlers/transfer_branches.py:101-111` removed the first-species passenger-load fallback.

Not fully met by PROJ-393:

- Task 3.2 did not delete `fleet_id`; the verification report says `fleet_id` is canonical and the originally imagined `entity_id` path did not exist.
- Task 3.3 did not fully migrate callers off `view=None` during PROJ-393; current code contains later PROJ-397 comments and behavior in `format_planet_info` and `PlanetSelectionWindow`.
- Task 3.5 did not reclaim the Combat Lab attributes during PROJ-393; the verification report says they were live behavior, not dead compatibility state.

## Literal Checklist Execution

The plan and checklists overstate completion:

- `Projects/active_projects/PROJ-393/plan.md:20-25` says the project is closed with no blockers.
- `Projects/active_projects/PROJ-393/plan.md:74-76` says all phase checklists are complete and focused tests passed, while full sharded is deferred.
- `Projects/active_projects/PROJ-393/phase_1_checklist.md:29-32` leaves all phase-completion subtasks unchecked.
- `Projects/active_projects/PROJ-393/phase_2_checklist.md:59` leaves the full sharded suite unchecked, and `:66-69` leaves phase-completion subtasks unchecked.
- `Projects/active_projects/PROJ-393/phase_3_checklist.md:78` leaves the full sharded suite unchecked, and `:85-88` leaves phase-completion subtasks unchecked.
- `Projects/projects_index.md:13` still marks PROJ-393 as `Planning`.

The verification report is more honest than the plan: it records the three Phase 3 deferrals and also records stage-boundary regressions that focused tests missed.

## Findings

### F-01 Critical: Project is marked complete even though audit readiness and phase validators fail

Evidence:

- `Projects/active_projects/PROJ-393/plan.md:20-25` says the active phase is closed, the next action is closeout, and blockers are none.
- `Projects/active_projects/PROJ-393/plan.md:75` says all phase checklists are complete.
- `Projects/active_projects/PROJ-393/phase_1_checklist.md:29-32`, `phase_2_checklist.md:59,66-69`, and `phase_3_checklist.md:78,85-88` leave required boxes unchecked.
- `Projects/projects_index.md:13` still says `Planning`.

Impact: The project cannot be accepted as audit-passed. The project metadata is internally inconsistent, and Protocol 04 explicitly says a failed audit-readiness check blocks audit completion.

### F-02 Major: Passenger-load validation still permits orders that execution now no-ops

Evidence:

- `game/strategy/validation/transfer_validator.py:189-223` validates passenger load capacity and population, but only checks `species_id` if it is present. Missing `species_id` still returns success when the colony has population.
- `game/strategy/engine/order_handlers/transfer_branches.py:101-111` now requires `species_id`; missing `species_id` logs a warning and returns `0`.
- My inline probe confirmed `TransferValidator.validate(..., cargo_type="passengers", direction="load", species_id=None, skip_location_check=True)` returns `is_valid=True`.

Impact: A command can pass validation and be queued, then perform no transfer at execution time. This is a real behavior gap left after deleting the implicit first-species fallback. The plan accounted for order-handler test fallout, but did not update the upstream validation contract to reject now-invalid passenger-load commands.

### F-03 Major: Initial Phase 3 plan treated live contracts as easy legacy deletions

Evidence:

- `Projects/active_projects/PROJ-393/phase_3_checklist.md:23-30` shows Task 3.2 was deferred because `fleet_id` remained canonical.
- `Projects/active_projects/PROJ-393/findings/verification_report.md:51-58` says there was no `entity_id` replacement path and that `view=None` migration required a separate facade-plumbing scope.
- `Projects/active_projects/PROJ-393/findings/verification_report.md:61-62` says the Combat Lab vars were actively used, not stale.

Impact: The plan failed to establish prerequisites before promising deletion. These should have been discovery/design tasks with stop conditions, or separate projects from the start. As written, the project was allowed to close after deferring material goals.

### F-04 Minor: Test-audit method was too narrow for deleted fallback behavior

Evidence:

- `Projects/active_projects/PROJ-393/findings/verification_report.md:71-77` says stage-boundary sharded testing caught regressions missed by phase-scoped tests.
- `Projects/active_projects/PROJ-393/findings/verification_report.md:114-130` explicitly documents that grepping for the field name missed tests that omitted the now-required field.

Impact: The implementation ultimately fixed the known test regressions, but the plan's audit method was weaker than the risk. Future fallback removals should search for positive behavior shapes, not only direct references to the removed field or branch.

## Plan Gaps And Missed Assumptions

- The plan assumed `fleet_id` was backward compatibility, but verification found it was canonical.
- The plan assumed `view=None` was a removable legacy branch, but real construction paths and tests lacked facade access.
- The plan assumed Combat Lab BattleScreen attributes were stale because PROJ-270 was archived, but verification found production/test-lab flows still used them.
- The plan treated "focused tests pass" as sufficient for fallback deletion, but its own verification report later shows full/stage-boundary regression testing was necessary.
- The plan did not connect the `species_id` execution-contract change to `TransferValidator`, so validation and execution now disagree.

## Residual Risks

- Full-suite status for PROJ-393 is not recorded as a checked project artifact.
- Current code includes later PROJ-397 remediation comments/changes in areas that PROJ-393 deferred. I did not audit PROJ-397 separately.
- Tests pass in the focused scopes I ran, but there is no regression test asserting that passenger-load command validation rejects missing `species_id` before an order is queued.
- Some remaining `ResourceCatalog.from_json()` calls outside the two PROJ-393 files still exist; the Phase 3 checklist explicitly scoped them out, so I did not treat them as PROJ-393 failures.

