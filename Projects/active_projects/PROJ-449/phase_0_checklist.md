# Phase 0: Pre-flight audit (rg counts, PROJ-443 Phase 5b carry-over verification)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 0`
> 2. Pin the audit counts in `findings/phase_0_audit.md`
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Pin the actual call-site footprint so Phases 1-4 size correctly. **No code changes.** Verify or adjust the PROJ-443 Phase 5b "18 files" audit-of-record against current HEAD. If counts are dramatically larger than expected (>40 files for ShipInstance side OR >30 files for the Planet side), surface to user before proceeding.

**File ownership rule:** This project owns every wrapper-related deletion and the matching test migrations. There are no cross-bucket cycles by design (Codex r4). Phase 0 is read-only — no `game/` or `tests/` edits.

**Source-of-truth findings:** [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md) — F-A-002/003/004/005, F-C-020.

---

## Tasks

### Task 0.1: Audit `ShipInstance` legacy-kwarg call sites [Simple]
**Files:** read-only; output to `findings/phase_0_audit.md`
**Tools:** `Grep`

- [ ] Raw count files containing `consumable_levels=`:
  ```bash
  rg -l "consumable_levels=" tests/
  rg -c "consumable_levels=" tests/
  ```
- [ ] Raw count files containing `cargo_contents=`:
  ```bash
  rg -l "cargo_contents=" tests/
  rg -c "cargo_contents=" tests/
  ```
- [ ] **Filter false positives — known non-constructor sites (verified 2026-05-19 codex audit):**
  - `tests/unit/strategy/data/test_facility_resource_tracking.py:111` — `_make_fuel_facility(consumable_levels=...)` is a helper-call, not a ShipInstance constructor
  - `tests/fixtures/strategy_entities.py:140` — fixture-helper default for PlanetaryFacility (NOT ShipInstance; out-of-scope per F-A-012 note in plan.md)
  - `tests/fixtures/strategy_entities.py:318, 320` — fixture-helper defaults INSIDE `create_test_ship_instance`; these ARE in scope for Phase 1 but should NOT be double-counted in the Phase-4 ShipInstance sweep (Phase 1 migrates them; Phase 4 sees zero matches afterward)
  - Any line where the kwarg is being passed to a fixture helper (`create_test_*`, `_make_*`, `build_*`) — these inherit the constructor decision from Phase 1
- [ ] Apply constructor-context filter. EITHER (a) re-run with stricter pattern:
  ```bash
  # Approximate: match lines where the legacy kwarg appears within 5 lines
  # below "ShipInstance(" — use rg --multiline + lookback or manual review.
  rg -B 5 "consumable_levels=" tests/ | rg -B 0 "ShipInstance\("
  ```
  OR (b) for each raw match, manually verify the enclosing call is `ShipInstance(...)` or `PlanetaryFacility(...)` — record only constructor sites in the sweep set.
- [ ] Compute union of both filtered sets — this is the ShipInstance Phase-4 sweep set
- [ ] Compare against PROJ-443 Phase 5b audit-of-record (18 files). If union > 25 OR < 10, flag the divergence
- [ ] Capture each occurrence's file:line in `findings/phase_0_audit.md` under section "ShipInstance sweep set"

**Notes:** PROJ-443 Phase 5b 2026-05-17 row in decisions.md is the prior audit-of-record. Pre-audit `rg` from 2026-05-19 showed: `consumable_levels=` in 16 distinct files (raw), `cargo_contents=` in 8 distinct files (raw). Total raw occurrences ~63. The raw counts INCLUDE helper-call false positives — apply the filter step above before applying the gate. Mirror the Planet-audit shape (Task 0.2 already filters out method-call false positives like `Empire.add_to_stockpile(...)`).

---

### Task 0.2: Audit `Planet` legacy-kwarg call sites [Simple]
**Files:** read-only; output to `findings/phase_0_audit.md`

- [ ] Count files passing `stockpile=`, `max_stockpile=`, or `staging_yard=` to a Planet constructor:
  ```bash
  rg -l "stockpile=|max_stockpile=|staging_yard=" tests/
  rg -c "stockpile=|max_stockpile=|staging_yard=" tests/
  ```
- [ ] Resolve false positives: filter out matches where the kwarg is being passed to something other than `Planet(...)` (e.g. `Empire.add_to_stockpile(...)` argument). Use `Grep` with surrounding-context flag (`-B 2`) to verify
- [ ] Capture each true-positive file:line in `findings/phase_0_audit.md` under section "Planet sweep set"

**Notes:** Pre-audit `rg` from 2026-05-19 showed 148 total occurrences across 26 files for the full pattern. Most are method-call arguments, not constructor kwargs. Expected true-positive constructor-kwarg sites: <10.

---

### Task 0.3: Verify `planet_serde` reconstruction site [Simple]
**File:** `game/strategy/data/planet_serde.py` (read)

- [ ] Confirm `planet_from_dict_kwargs` still emits the legacy public-kwarg names at lines 157-159 (`stockpile=`, `max_stockpile=`, `staging_yard=`)
- [ ] Confirm `planet_to_dict` still routes through the `.stockpile` / `.max_stockpile` / `.staging_yard` property reads (lines 49-55 per the F-A-002 finding)
- [ ] Document the serde site count in `findings/phase_0_audit.md` (expect 2: from_dict_kwargs writes legacy names, to_dict reads them via property)

---

### Task 0.4: Verify fixture site count [Simple]
**File:** `tests/fixtures/strategy_entities.py` (read)

- [ ] Confirm 4 sites (Codex r3 spot-check):
  - `:140` — `create_test_facility` passes `consumable_levels={"fuel": 50.0, "energy": 100.0}` to `PlanetaryFacility(...)`
  - `:318` — `create_test_ship_instance` passes `consumable_levels={"fuel": 80.0, "energy": 50.0}` to `ShipInstance(...)`
  - `:320` — same function, `cargo_contents={"minerals": 10}`
  - `:425` — `create_test_empire` constructs a hidden `_starting_reserve` colony with `stockpile=dict(seed_pool)`
- [ ] If additional sites surface in this file, add them to the Phase 1 task list

---

### Task 0.5: Check PROJ-443 Phase 5b context [Simple]
**Files:** `Projects/active_projects/PROJ-443/decisions.md`, `Projects/active_projects/PROJ-443/phase_5_checklist.md` (read)

- [ ] Read the 2026-05-17 "Phase 5b: wrapper retained" decisions.md row and confirm the 18-file count + the "19 failures + 16 errors" sharded-suite regression details
- [ ] Cross-reference against the Task 0.1 union count
- [ ] Note any context changes between 2026-05-17 and today (PROJ-444..447 commits, etc.) that might have shifted the audit landscape

---

### Task 0.6: Write `findings/phase_0_audit.md` [Simple]
**File:** `Projects/active_projects/PROJ-449/findings/phase_0_audit.md` (new)
**Tests:** none (pure documentation)

- [ ] Sections:
  - "ShipInstance sweep set" — file list with line refs, total file/occurrence count
  - "Planet sweep set" — file list with line refs (true-positive constructor sites only)
  - "Serde dependencies" — confirmation of planet_serde sites
  - "Fixture sites" — confirmation of strategy_entities.py 4 sites
  - "PROJ-443 5b cross-reference" — does the count line up with the prior audit?
  - "Gate decision" — does the sweep size fit the planned phase structure? If so, declare Phase 1 ready. If not, surface the divergence to the user.

**Gate criteria:**
- ShipInstance sweep set ≤ 25 files → proceed
- ShipInstance sweep set 25-40 files → proceed but flag in plan.md Current State
- ShipInstance sweep set > 40 files → PAUSE and surface to user (the wrapper-retention rationale was sized for 18 files)
- Planet sweep set ≤ 15 files → proceed
- Planet sweep set > 15 files → flag but proceed (Planet side wasn't previously attempted)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `findings/phase_0_audit.md` exists and has all 6 sections populated
- [ ] Plan.md Quick Status row for Phase 0 → Complete
- [ ] Plan.md Current State updated with audit summary numbers
- [ ] If gate criteria triggered "pause": user has explicitly approved before opening Phase 1
- [ ] No production code or test code changed in this phase

## Notes / Risks / Coordination Touchpoints
- **PROJ-443 Phase 5b context**: the prior audit found a 2.5× under-estimate (original 7 → actual 18). Plan for similar variance here.
- **No worktrees** per standing preference — serial execution in main checkout.
- **PROJ-450 is downstream of Phase 3** — coordinate phase-3-complete signal in plan.md so PROJ-450 Phase 0 can verify the precondition.
