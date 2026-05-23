# Phase 0: Re-measure target files after PROJ-449 + PROJ-451 ship

**Status:** Complete
**Depends on:** PROJ-451 merged into main (hard gate for Phases 1+2+3). PROJ-449 merged into main (hard gate for Phase 3 only; advisory for Phases 1-2).
**Review Mode:** lightweight (read-only audit; no code changes)
**Files:** `Projects/active_projects/PROJ-459/findings/phase_0_remeasurement.md` (new)

**Objective:** Confirm that this project's scope is still accurate after PROJ-449 (wrapper retirement) and PROJ-451 (production resource-consumption semantics) ship. Re-measure LOC of all three target files and confirm the extraction targets still live where the original findings said they did. **Mandatory phase — without re-measurement, scope may be wrong.**

Per audit feedback (Bucket D, response.md), dependencies are now phase-scoped:
- **PROJ-451** is a hard predecessor for Phase 1 (and all later phases) because it changes the production-resource surface adjacent to the fleet.py serde extraction line.
- **PROJ-449** is a hard predecessor for Phase 3 only (ship_instance.py LOC verdict). For Phases 1-2, PROJ-449 in flight is acceptable — record its status as informational, do not block.

---

## Tasks

### Task 0.1: Verify dependency status [Simple]

- [x] `git log --oneline -50` to see recent commits; confirm a "PROJ-451" merge commit is present (HARD gate). Note whether a "PROJ-449" merge commit is present (advisory for Phases 1-2, hard for Phase 3).
- [x] Check `Projects/archived_projects/` for archived PROJ-449 and PROJ-451 directories (or active with all phases complete).
- [x] If **PROJ-451** is still in flight: stop. Phase 0 cannot complete. Update `plan.md` Current State with a blocker note and exit.
- [x] If only **PROJ-449** is still in flight: Phases 1 and 2 can proceed; Phase 3 must wait. Record this disposition in `findings/phase_0_remeasurement.md` so the downstream agent knows to pause before Phase 3.

### Task 0.2: Re-measure target file LOC [Simple]

**Files:** `game/strategy/data/fleet.py`, `game/strategy/data/planet_gen.py`, `game/strategy/data/ship_instance.py`

- [x] Run (PowerShell):
  ```powershell
  (Get-Content game/strategy/data/fleet.py | Measure-Object -Line).Lines
  (Get-Content game/strategy/data/planet_gen.py | Measure-Object -Line).Lines
  (Get-Content game/strategy/data/ship_instance.py | Measure-Object -Line).Lines
  ```
  Record the three LOC values.
- [x] Compare against the 2026-05-19 baseline:
  - fleet.py: 686 LOC (baseline)
  - planet_gen.py: 610 LOC (baseline)
  - ship_instance.py: 839 LOC (baseline)
- [x] Note any drift (PROJ-449 / PROJ-451 may have grown or shrunk fleet.py independently of the wrapper work; ship_instance.py is expected to DROP).

### Task 0.3: Verify Phase 1 extraction target locations [Simple]

**File:** `game/strategy/data/fleet.py`

- [x] Grep for `def to_dict` and `def from_dict` in fleet.py; confirm both still exist on `Fleet`.
- [x] Confirm `Fleet.to_dict` body is still ~30 LOC (per 2026-05-19 sample: fleet.py:520-557 = 37 LOC).
- [x] Confirm `Fleet.from_dict` body is still ~80 LOC (per 2026-05-19 sample: fleet.py:558-655 = 98 LOC).
- [x] Confirm `Fleet.resolve_order_references` still exists (per 2026-05-19 sample: fleet.py:657).
- [x] Record in `findings/phase_0_remeasurement.md` whether the extraction surface matches expectations or has drifted.

### Task 0.4: Verify Phase 2 split candidates in planet_gen.py [Simple]

**File:** `game/strategy/data/planet_gen.py`

- [x] Grep `^    def ` in planet_gen.py; record the method list and approximate per-method LOC bands.
- [x] Confirm the 4 candidate split axes from `findings/PROJ-459_findings.md` (orbital arrangement / moon generation / body construction / surface-type-resource) still match the structure.
- [x] Note if any new methods have appeared.

### Task 0.5: Re-measure ship_instance.py and inspect post-PROJ-449 surface [Simple]

**File:** `game/strategy/data/ship_instance.py`

- [x] Re-measure LOC (this is the gate for Phase 3).
- [x] Read `ship_instance.py` end-to-end to confirm which shims PROJ-449 actually retired vs. which survive:
  - Was the `_ship_instance_init_with_legacy_kwargs` module-level wrapper deleted?
  - Were the `consumable_levels` / `cargo_contents` @property/@setter pairs deleted?
  - Do the 5 TD-06 high-value shims (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) survive?
- [x] Estimate the LOC contribution of any surviving shims (block of lines + comment narration).
- [x] Provisional Phase 3 verdict:
  - LOC < 500: ready to close in Phase 3.
  - LOC >= 500: ready to spin out as PROJ-461 in Phase 3.

### Task 0.6: Write `findings/phase_0_remeasurement.md` [Simple]

- [x] Create the file with sections:
  1. Dependency status (PROJ-449 + PROJ-451 confirmed merged)
  2. Re-measurement table (file / baseline LOC / current LOC / delta)
  3. Phase 1 extraction surface confirmation (locations of to_dict / from_dict / resolve_order_references)
  4. Phase 2 split candidate inspection (method list with LOC bands)
  5. Phase 3 provisional verdict (close or spinout)
- [x] Commit the findings file. No production code touched.
- [x] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [x] PROJ-451 confirmed merged into main (HARD gate)
- [x] PROJ-449 status recorded: merged (Phase 3 can proceed), or in-flight (Phases 1-2 still OK; Phase 3 pauses)
- [x] LOC re-measured for fleet.py, planet_gen.py, ship_instance.py
- [x] Extraction targets confirmed at expected locations (Phase 1)
- [x] Split candidates confirmed in planet_gen.py (Phase 2)
- [x] Phase 3 provisional verdict recorded (or "pending PROJ-449" if PROJ-449 not yet merged)
- [x] `findings/phase_0_remeasurement.md` committed
- [x] No production code touched
- [x] Sharded suite green (baseline confirmed for downstream phases)
