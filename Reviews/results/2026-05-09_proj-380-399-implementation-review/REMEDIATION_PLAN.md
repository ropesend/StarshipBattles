# Remediation Plan — PROJ-380..399 Implementation Review

**Date:** 2026-05-09
**Source reviews:** `Reviews/results/2026-05-09_proj-380-399-implementation-review/` (20 per-project + consolidated)
**Verifier:** Re-checked the 6 critical implementation blockers against current source on `feat/03c-phase-aware-execution`.

The reviews confirm the implementation arc is **not audit-clean**. Each project's narrow code goal mostly landed and focused tests passed, but the project-system bookkeeping (checklists, manifests, index, design docs) is repeatedly inconsistent, several deletions were too narrowly scoped, and a handful of real production bugs slipped through focused-test coverage. This document organizes the work that remains.

---

## TIER 1 — Production behavior bugs (verified live in source)

These are actual code defects, not bookkeeping. Each was verified by reading the cited file. Fix before re-running the canonical full sharded suite.

### B-01 (PROJ-392) `NewGameSetupScreen._create_ui()` calls a deleted wrapper
- **File:** `game/ui/screens/new_game_setup_screen.py:348`
- **Symptom:** Line 348 reads `self.save_name_input.set_text(self.generate_default_save_name())`. Task 2.9 deleted the `generate_default_save_name` static method on the screen but left this caller. **Production `AttributeError` when the New Game UI builds.**
- **Verified:** `hasattr(NewGameSetupScreen, "generate_default_save_name") == False`; `hasattr(NewGameSetupController, "generate_default_save_name") == True`.
- **Fix:** Replace with `self._controller.generate_default_save_name()` (or wherever the screen accesses its controller). Add a coverage path that exercises `_create_ui()` end-to-end.

### B-02 (PROJ-393) Passenger-load validator accepts missing `species_id`, executor no-ops
- **File:** `game/strategy/validation/transfer_validator.py:215-221` (inside `_validate_load`)
- **Symptom:** The species check is gated on `if species_id:` — when `species_id` is None the validator returns success. After PROJ-393 deleted the first-species fallback in `transfer_branches.py:106`, the executor logs a warning and transfers 0. Validation and execution disagree: an order can pass validation, get queued, then perform no transfer.
- **Verified:** Inline probe in the review: `TransferValidator.validate(..., cargo_type="passengers", direction="load", species_id=None, skip_location_check=True)` → `is_valid=True`.
- **Fix:** Inside the `cargo_type == "passengers"` block, treat missing `species_id` as a validation error (e.g., new `MISSING_SPECIES_ID` code). Add a regression test asserting validation rejects orders the executor would no-op.

### B-03 (PROJ-381) `SimulationBattleResolver` only catches `SimulationException`
- **File:** `game/strategy/adapters/simulation_adapter.py:292-300`
- **Symptom:** The wrapper catches `SimulationException` and re-raises as `BattleResolutionError` with full battle context. But `run_battle` (`battle_runner.py:640`) raises `ValidationException` for invalid `ShipSpec.components`. That class is not in the catch tuple; raw `ValidationException` propagates with empty context. PROJ-381 Phase 3 Task 3.10 explicitly required a regression test injecting `ValidationException`; the implemented test substituted a custom `SimulationException`.
- **Fix:** Catch `(SimulationException, ValidationException)` and wrap both with battle context. Replace the substituted test with the originally-required `ValidationException` injection.

### B-04 (PROJ-382 / 387 / 394) 36 stale `_MockGalaxy` test failures
- **Files:** `tests/unit/strategy/data/test_galaxy_entity_registry.py:16-27` + `:73-75`; `tests/unit/strategy/data/test_galaxy_spatial_index.py:16-27` + `:78-80`
- **Symptom:** Both files define `_MockGalaxy` with the deleted private field names (`_global_hex_planets`, `_planet_to_system`, `_zone_to_system`, `_global_hex_zones`, `_next_planet_id`). The delegates now read `state.global_hex_planets`, `state.planet_to_system`, etc. **36 failures**, dominated by `AttributeError: '_MockGalaxy' object has no attribute 'next_planet_id'`.
- **Verified:** I ran `pytest tests/unit/strategy/data/test_galaxy_spatial_index.py tests/unit/strategy/data/test_galaxy_entity_registry.py` → `36 failed, 21 passed`.
- **Fix:** Replace `_MockGalaxy` doubles with real `GalaxyState` instances (or a shared `make_galaxy_stub()` helper) using the canonical field names. Verify production callers pass `galaxy.state` rather than `galaxy` itself.

### B-05 (PROJ-386) Save-format compatibility tolerated in touched files
Two surfaces survive after the 4 named deletions:
- **File:** `game/strategy/data/ship_instance_serializer.py:106` — `consumable_levels=data.get('consumable_levels', data.get('resource_levels', {}))`. This is a field-rename shim accepting old saves. **Verified live.**
- **File:** `game/ui/screens/battle_setup_state.py:117-130` (`BattleSetupSide.from_dict`) — explicitly tolerates legacy saves missing `system_complex_toggles`/`sector_complex_toggles`, defaults them to `{}`. The class docstring frames this as legacy compat.
- **Fix:** Per CLAUDE.md Rule 3 ("old saves are disposable"), delete both fallbacks. Tests expecting these legacy shapes should be deleted (they tested the legacy path). Add positive-shape regression confirming new format round-trips.
- **Edge case:** `ShipInstanceSerializer.from_dict()` raises raw `KeyError` on missing `components` (not the documented `PersistenceException`). Fix: route through `require_keys()` so failures wrap to the canonical exception.

### B-06 (PROJ-382) Projectile EventBus injection not wired through production constructors
- **Files:** `game/simulation/entities/projectile.py:8-20`, `:40-42`, `:119-122`, `:138-141`; `game/simulation/combat/families/seeker.py:55-65`; `game/simulation/combat/families/projectile.py:33-43`; `game/simulation/battle_state.py:564-575`.
- **Symptom:** `event_logger` kwarg added to `Projectile`, but production callers don't pass one. Default is a no-op. `SEEKER_EXPIRE` telemetry silently dropped in normal play.
- **Fix:** Thread the EventBus through the construction chain (likely `BattleState` → `WeaponFiringSystem` → `Projectile`/`Seeker`).

---

## TIER 2 — Audit-readiness / project-system blockers

These don't change runtime behavior but block Protocol 04 closeout. Several projects claim completion while `validate_audit_ready.py` or `validate_phase.py` fails.

### A-01 PROJ-382: validator FAIL — Phases 1–5 still `Status: Not Started`
**Path:** All 5 phase checklists at `Projects/active_projects/PROJ-382/phase_*_checklist.md:8`. **12 errors, 32 unchecked tasks.**
- Mark each phase status correctly (some are genuinely complete, some have outstanding work per Tier 1 — reconcile with B-04, B-06 status).
- Reconcile the Phase 5 record: current `superweapon_order_processor.py` is 434 LOC (under ceiling), but the checklist still says "Task 5.4 deferred." Either later PROJ-396 closeout work landed it here, or the records were never synced.

### A-02 PROJ-393: validator FAIL — Phase 1/2/3 task sub-checkboxes unchecked
**Paths:** `phase_1_checklist.md:29-32`, `phase_2_checklist.md:59,66-69`, `phase_3_checklist.md:78,85-88`.
- Three deferrals (Task 3.2/3.3/3.5) closed without meeting original goals. Records call them "deferred"; consolidation should either (a) accept and re-scope into PROJ-397 (already done for some), (b) reopen the items, or (c) explicitly archive as "scope was wrong from the start."

### A-03 PROJ-395: validator FAIL — required artifacts not maintained
- 2 of 14 MAJORs closed as deferred (MAJ-013, MAJ-014). Plan claims complete.
- Phase 2 stated goal "all 14 MAJOR closed" not met. Reconcile.

### A-04 PROJ-397: every phase checklist still says "Not Started" with all subtasks unchecked
**Paths:** All 3 phase checklists. Code goals appear implemented (verified by independent reviewer), but the project-system records contradict that.
- Phase 3 `fleet_id` deferral text still calls fleet_id "needs design" while Phase 3 commit `53b621303` already implemented the canonical-fleet_id decision (Path B simplified). Update text.
- The F-05 introspection-only test (asserts signature shape rather than constructing) needs a real-construction test.

### A-05 PROJ-398: phase marked complete; Phase 1 tasks still unchecked
Same shape as A-04. Skeleton plan/manifest never populated.

### A-06 PROJ-399: same — Phase 1 unchecked, project index says `Planning`

### A-07 PROJ-396: required artifacts not maintained
- Phase checklists, manifest, design doc, project index never updated to reflect implementation.
- Full regression claim ("19735/19745 sharded pass") not literally checked off in evidence.

### A-08 PROJ-389: audit fails because Task 1.6 partial + verification unchecked
- 4 test files + 3 doc files migrated beyond the audit's 6-caller estimate; manifest not updated.

### A-09 PROJ-384: blocker text still in plan even though regression task remains unchecked

### A-10 `Projects/projects_index.md` has stale `Planning` entries for **15+ projects** (380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399)
Verified by every reviewer's audit-readiness warning. Single sweep can update all once the audit-readiness blockers are resolved.

---

## TIER 3 — Stale documentation and architecture wording

### D-01 PROJ-383: Docs still describe deleted `command_handlers.py` shim as current
- **Search:** `grep -rn "game.strategy.engine.command_handlers" docs/` — find every remaining reference.
- **Fix:** Update each doc to point at `game.strategy.engine.handlers/` (the canonical package).

### D-02 PROJ-390: Docs still direct callers to use deleted module-level `log_event`/`set_event_handler`/`get_event_handler`
- **Search:** `grep -rn "log_event\|set_event_handler\|get_event_handler" docs/`
- **Fix:** Per the architecture, EventBus is session-scoped (PROJ-252). Update docs to reflect constructor injection as the only supported path.

### D-03 PROJ-395: `docs/05_ERROR_HANDLING.md` still contradicts the EventBus architecture
- Concrete scope unspecified by the reviewer; hand off to a doc-sweep subagent.

### D-04 PROJ-380: Stale `pixel_to_hex` import notes remain after migration
- The migration to `Camera.hex_at_screen` happened, but old import-comment crumbs survive.
- **Search:** `grep -rn "pixel_to_hex" game/ui/screens/strategy_*` for residual comments.

### D-05 PROJ-394: `Galaxy` facade docstring still labels migrated forwarders as "public + grandfathered private API"
- **File:** `game/strategy/data/galaxy.py:67`. Update wording — the 5 spatial private forwarders were intentionally removed.

### D-06 PROJ-396: New `superweapon_handlers/` package modules use legacy `Optional[...]` typing
- Modern syntax (`X | None`) is the project convention.

### D-07 PROJ-380 + 391 + 396: Several new modules use legacy `Optional[...]` annotations
- Same pattern; sweep all three sets together.

### D-08 PROJ-391: `FormationSpec` serialization still preserves a loose `object` slot
- Drops invalid formations silently. Tighten the type and add a regression that asserts unknown shapes raise.

### D-09 PROJ-380: Touched production files still over 500-LOC ceiling
- Reviewer flagged but didn't list; do a `find game/ -name "*.py" -exec wc -l {} \; | awk '$1 > 500'` sweep on the project's manifest files.

---

## TIER 4 — Coverage gaps

### C-01 PROJ-397: `EmpireBuildQueueWindow` constructor test verifies signature only via introspection
- Add a test that actually instantiates the class and exercises a code path through it.

### C-02 PROJ-381: Facade conversion `EnginePhaseError` → `TurnFailedError` has no direct unit test
- `game/strategy/facade/strategy_session_facade.py:194-201` implements the conversion. The UI test exercises the boundary, not the facade. Add a focused facade unit test.

### C-03 PROJ-381: UI still imports + catches raw `EnginePhaseError`
- `game/ui/screens/strategy_game_state_manager.py:19, 149-158`. PROJ-395 marked this as deferred MAJ-014 (defensive fallback). Either close the deferral with a written architectural decision, or remove the catch.

### C-04 PROJ-397: `PlanetSelectionWindow` facade threading lacks direct unit coverage

### C-05 PROJ-386: No negative tests proving legacy save shapes are rejected
- After fixing B-05, add tests that assert old shapes raise.

### C-06 PROJ-393: No regression test asserting passenger-load command validation rejects missing `species_id`
- Goes with B-02.

---

## TIER 5 — Outstanding deferrals from the orchestration session

These are items I (the orchestrator) deferred during the run with explicit user-visible rationale. They aren't in the review reports but should travel with this remediation document.

### From PROJ-395 (review) — 2 MAJOR deferred
- **MAJ-013** EventBus Pattern #10 shim — pre-existing, not a PROJ-381 regression. Separate cleanup.
- **MAJ-014** Defensive raw `EnginePhaseError` catch — architectural decision pending. (Same as C-03.)

### From PROJ-393 (orchestration) — 3 deferred items, 2 already closed in PROJ-397
- LEG-02-004 `fleet_id` field full deletion → PROJ-397 Path B simplified (canonical retained, dead `entity_type` removed).
- LEG-02-006 `view=None` branch → PROJ-397 Phase 3 Task 3.2 closed.
- LEG-03-023 Combat Lab vars → PROJ-397 Phase 1 closed.

### From PROJ-382 (orchestration) — 1 deferred → closed in PROJ-396
- Task 5.4 `superweapon_order_processor.py` 723 LOC decomp → PROJ-396 Phase 3 (Option B free-functions package).

### Future-cleanup buckets (recorded earlier; not in scope for this remediation pass)
| Source | Severity | Count | Notes |
|--------|----------|-------|-------|
| PROJ-380 review | MINOR | 8 | Consolidation polish |
| PROJ-380 review | INFO | 30 | Future cleanup notes |
| PROJ-381 review | MINOR | 18 | Test polish, comment normalization |
| PROJ-381 review | INFO | 7 | Cleanup follow-ups |
| PROJ-382 review | MINOR | 14 | Pattern polish |
| PROJ-382 review | INFO | 24 | Future opportunities |
| PROJ-383 review | MINOR | 1 | Index status (covered by A-10) |
| PROJ-383 review | INFO | 2 | — |
| PROJ-385 review | INFO | 7 | Polish |
| PROJ-386 review | MINOR | 2 | — |
| PROJ-386 review | INFO | 4 | — |
| PROJ-387 review | MINOR | 3 | (D-05 covers one) |
| PROJ-387 review | INFO | 10 | — |
| PROJ-388 review | INFO | 1 | — |
| PROJ-389 review | INFO | 1 | — |
| PROJ-390 review | MINOR | 3 | (D-02 covers one) |
| PROJ-391 review | MINOR | 1 | (D-08 covers it) |
| PROJ-393 review | MINOR | 8 | Test polish |
| PROJ-393 review | INFO | 4 | — |

---

## Execution order

Per the consolidated review's recommended order, but verified against the live code:

### Wave 1 — Code/behavior fixes (Tier 1)
Run in parallel where files don't conflict:
1. **B-01** PROJ-392 deleted-wrapper call (single file, single line)
2. **B-02** PROJ-393 transfer validator (one file, add 1 case)
3. **B-03** PROJ-381 SimulationBattleResolver catch tuple (one file, one signature change)
4. **B-04** PROJ-387/394 stale `_MockGalaxy` doubles (two test files, mechanical migration)
5. **B-05** PROJ-386 save-format tolerance + KeyError → PersistenceException (two files)
6. **B-06** PROJ-382 EventBus injection through production constructors (~5 files in chain)

After Wave 1: run focused tests for each, then `python Tools/test_sharded/test_sharded.py`. Should be **0 failures, 0 errors** (PROJ-399 closed the pre-existing-failure cluster already).

### Wave 2 — Audit-readiness reconciliation (Tier 2)
Mechanical bookkeeping. Can be one large subagent pass:
- Run `python Projects/scripts/validate_audit_ready.py PROJ-XXX` on each of the 14 projects with stale records.
- For each failure: check off completed work in checklists, update phase status, update plan Current State.
- Single sweep at the end: update `Projects/projects_index.md` to mark complete projects as `Complete`.

### Wave 3 — Doc/architecture wording (Tier 3)
- D-01, D-02, D-03 first (architecture-impacting)
- D-04, D-05, D-06, D-07, D-08, D-09 in any order

### Wave 4 — Coverage gaps (Tier 4)
- After Wave 1's behavior fixes land, add the regression tests these gaps describe.

### Wave 5 — Deferral closure (Tier 5)
- Ratify or actively close MAJ-013 and MAJ-014 from PROJ-395.
- Optional: address MINOR/INFO future-cleanup items selectively.

---

## Suggested next-action prompts

If continuing this work in a fresh session, start each wave with one subagent:

```
Wave 1 (one subagent per blocker, run in parallel where files disjoint):
  B-01: fix new_game_setup_screen.py:348 + cover _create_ui()
  B-02: fix transfer_validator.py species_id check + regression test
  B-03: simulation_adapter.py catch ValidationException + regression test
  B-04: migrate _MockGalaxy fixtures in 2 test files to GalaxyState
  B-05: delete component_damage/resource_levels fallbacks + complex_toggles tolerance
  B-06: thread EventBus through Projectile/Seeker construction

Wave 2: one subagent for audit-readiness sweep across 14 projects.
Wave 3: one subagent for docs sweep.
Wave 4: one subagent for coverage gaps.
Wave 5: user decision on deferral closure.
```

**Final canonical regression:** `python Tools/test_sharded/test_sharded.py` after Wave 1 completes. Target: 19799+ passed, 0 failed, 0 errors.
