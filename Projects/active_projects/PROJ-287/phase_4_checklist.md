# Phase 4: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update docs, run full suite, close the project.

---

## Tasks

### Task 4.1: Update architecture doc [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] Under the "Key Protocols" section, add `IRaceRegistry` to the cross-layer boundary protocols table: `get_race(race_id) -> Optional[RaceConfig]`. One-line description: "Session-cached race-config lookup; UI reads via facade."

**Notes:**

### Task 4.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Add a `### Race Registry (PROJ-287)` subsection under Strategy Layer Services:
  - `CachedRaceRegistry` at `game/strategy/systems/race_library.py`
  - Session-scoped, lazy-init via `StrategySessionFacade.get_race_registry()`
  - Invalidation via `invalidate(race_id?)` called by the race-editor save flow
  - Cross-reference `Empire.resident_species()` as the companion API for "iterate empire's species"

**Notes:**

### Task 4.3: Update patterns doc (optional) [Simple]
**File:** `docs/02_PATTERNS.md`

- [ ] Under the "Facade / Delegate" or "CQRS-lite" section, add a note that `StrategySessionFacade.get_race_registry()` follows the same lazy-init pattern as the other session-scoped read interfaces.

**Notes:** Optional — skip if the existing pattern descriptions already cover it.

### Task 4.4: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green (apart from known persistent flakes).
- [ ] Net new tests: ~10 (6 on `TestCachedRaceRegistry` + 3 on facade + 6 on `resident_species` ≈ 15 actually).

**Notes:**

### Task 4.5: Close project [Simple]

- [ ] Update `plan.md § Current State` to "ALL 4 PHASES COMPLETE — awaiting user sign-off".
- [ ] Verify `projects_index.md` status.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
