# Phase 4: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update docs, run full suite, close the project.

---

## Tasks

### Task 4.1: Update architecture doc [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [x] Under the "Key Protocols" section, add `IRaceRegistry` to the cross-layer boundary protocols table: `get_race(race_id) -> Optional[RaceConfig]`. One-line description: "Session-cached race-config lookup; UI reads via facade."

**Notes:** Completed in Phase 1 alongside Task 1.1. The architecture doc now lists IRaceRegistry in the Cross-Layer Boundary Protocols section with the `CachedRaceRegistry` implementation cross-reference, and `game.core` export count was bumped 45 → 46.

### Task 4.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [x] Add a `### Race Registry (PROJ-287)` subsection under Strategy Layer Services:
  - `CachedRaceRegistry` at `game/strategy/systems/race_library.py`
  - Session-scoped, lazy-init via `StrategySessionFacade.get_race_registry()`
  - Invalidation via `invalidate(race_id?)` called by the race-editor save flow
  - Cross-reference `Empire.resident_species()` as the companion API for "iterate empire's species"

**Notes:** Added after the PROJ-285 Colony Economy Multiplier subsection. Documents the protocol, the cache + None-result caching rule, the lazy-init facade accessor, the invalidation discipline (including the optional `race_registry` kwarg on `RaceSetupScreen`), the Empire.resident_species companion API, and cross-references `docs/01_ARCHITECTURE.md § Key Protocols`.

### Task 4.3: Update patterns doc (optional) [Simple]
**File:** `docs/02_PATTERNS.md`

- [x] Under the "Facade / Delegate" or "CQRS-lite" section, add a note that `StrategySessionFacade.get_race_registry()` follows the same lazy-init pattern as the other session-scoped read interfaces.

**Notes:** SKIPPED per task's own "optional" guidance. Pattern 6 (CQRS-lite) already describes the facade as the single UI-to-engine entry with read methods returning read-only contracts — `get_race_registry()` slots into that description as-is. Adding PROJ-specific callouts to general patterns docs creates noise without new information; the service catalog (Task 4.2) is the right home for the specifics.

### Task 4.4: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green (apart from known persistent flakes).
- [x] Net new tests: ~10 (6 on `TestCachedRaceRegistry` + 3 on facade + 6 on `resident_species` ≈ 15 actually).

**Notes:** 14984/14985 passed in 137.4s across 12 shards. Single failure is the pre-existing flake `test_copy_designs_without_themes_preserves_original` flagged in the handoff (theme bleed between the fixtures, already documented across PROJ-286/287). Net new in this project = 19 tests: 7 `TestCachedRaceRegistry` + 3 `TestRaceRegistryAccessor` + 3 `TestRaceRegistryInvalidationOnSave` + 6 `TestEmpireResidentSpecies`. No regressions.

### Task 4.5: Close project [Simple]

- [x] Update `plan.md § Current State` to "ALL 4 PHASES COMPLETE — awaiting user sign-off".
- [x] Verify `projects_index.md` status.

**Notes:** plan.md table and Current State block updated. `Projects/active_projects/projects_index.md` status entry for PROJ-287 advanced to reflect all four phases complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
