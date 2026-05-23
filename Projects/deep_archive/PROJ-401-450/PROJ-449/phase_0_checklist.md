# Phase 0: Pre-flight audit (rg counts, PROJ-443 Phase 5b carry-over verification)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 0`
> 2. Pin the audit counts in `findings/phase_0_audit.md`
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Pin the actual call-site footprint so Phases 1-4 size correctly. **No code changes.** Verify or adjust the PROJ-443 Phase 5b "18 files" audit-of-record against current HEAD. If counts are dramatically larger than expected (>40 files for ShipInstance side OR >30 files for the Planet side), surface to user before proceeding.

**File ownership rule:** This project owns every wrapper-related deletion and the matching test migrations. There are no cross-bucket cycles by design (Codex r4). Phase 0 is read-only — no `game/` or `tests/` edits.

**Source-of-truth findings:** [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md) — F-A-002/003/004/005, F-C-020.

---

## Tasks

### Task 0.1: Audit `ShipInstance` legacy-kwarg call sites [Simple]
**Files:** read-only; output to `findings/phase_0_audit.md`
**Tools:** `Grep`

- [x] Raw count files containing `consumable_levels=`:
  ```bash
  rg -l "consumable_levels=" tests/
  rg -c "consumable_levels=" tests/
  ```
- [x] Raw count files containing `cargo_contents=`:
  ```bash
  rg -l "cargo_contents=" tests/
  rg -c "cargo_contents=" tests/
  ```
- [x] **Filter false positives — known non-constructor sites (verified 2026-05-19 codex audit):**
- [x] Apply constructor-context filter via multiline grep + Python script + helper-definition spot-checks (see findings/phase_0_audit.md)
- [x] Compute union of both filtered sets — this is the ShipInstance Phase-4 sweep set
- [x] Compare against PROJ-443 Phase 5b audit-of-record (18 files). Result: 8 files (under-count vs. 18, explained in §F of findings)
- [x] Capture each occurrence's file:line in `findings/phase_0_audit.md` under section "ShipInstance sweep set"

**Notes:** PROJ-443 Phase 5b 2026-05-17 row in decisions.md is the prior audit-of-record. Pre-audit `rg` from 2026-05-19 showed: `consumable_levels=` in 16 distinct files (raw), `cargo_contents=` in 8 distinct files (raw). Total raw occurrences ~63. The raw counts INCLUDE helper-call false positives — apply the filter step above before applying the gate. Mirror the Planet-audit shape (Task 0.2 already filters out method-call false positives like `Empire.add_to_stockpile(...)`).

---

### Task 0.2: Audit `Planet` legacy-kwarg call sites [Simple]
**Files:** read-only; output to `findings/phase_0_audit.md`

- [x] Count files passing `stockpile=`, `max_stockpile=`, or `staging_yard=` to a Planet constructor
- [x] Resolve false positives: filter out matches where the kwarg is being passed to something other than `Planet(...)`
- [x] Capture each true-positive file:line in `findings/phase_0_audit.md` under section "Planet sweep set"

**Notes:** Pre-audit `rg` from 2026-05-19 showed 148 total occurrences across 26 files for the full pattern. Most are method-call arguments, not constructor kwargs. Expected true-positive constructor-kwarg sites: <10.

---

### Task 0.3: Verify `planet_serde` reconstruction site [Simple]
**File:** `game/strategy/data/planet_serde.py` (read)

- [x] Confirm `planet_from_dict_kwargs` still emits the legacy public-kwarg names at lines 157-159 (`stockpile=`, `max_stockpile=`, `staging_yard=`)
- [x] Confirm `planet_to_dict` still routes through the `.stockpile` / `.max_stockpile` / `.staging_yard` property reads (lines 50-52)
- [x] Document the serde site count in `findings/phase_0_audit.md` (Section D)

---

### Task 0.4: Verify fixture site count [Simple]
**File:** `tests/fixtures/strategy_entities.py` (read)

- [x] Confirm 4 sites (Codex r3 spot-check) — verified at lines 140, 318, 320, 425 (Section E)
- [x] No additional sites surfaced in this file

---

### Task 0.5: Check PROJ-443 Phase 5b context [Simple]
**Files:** `Projects/active_projects/PROJ-443/decisions.md`, `Projects/active_projects/PROJ-443/phase_5_checklist.md` (read)

- [x] PROJ-443 5b audit-of-record reviewed
- [x] Cross-reference complete: actual sweep is 8 files vs. prior 18-file estimate; delta explained in Section F (F-A-012 deferral + MagicMock false positives + intermediate manager-API migrations)

---

### Task 0.6: Write `findings/phase_0_audit.md` [Simple]
**File:** `Projects/active_projects/PROJ-449/findings/phase_0_audit.md` (new)
**Tests:** none (pure documentation)

- [x] All sections written: §A ShipInstance sweep set (8 files), §B Planet sweep set (3 files), §C production-code (0), §D serde dependencies (2 sites), §E fixture sites (4 sites), §F PROJ-443 5b cross-reference (delta explained), §G gate decision (PROCEED clean)

**Gate criteria:**
- ShipInstance sweep set ≤ 25 files → proceed
- ShipInstance sweep set 25-40 files → proceed but flag in plan.md Current State
- ShipInstance sweep set > 40 files → PAUSE and surface to user (the wrapper-retention rationale was sized for 18 files)
- Planet sweep set ≤ 15 files → proceed
- Planet sweep set > 15 files → flag but proceed (Planet side wasn't previously attempted)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `findings/phase_0_audit.md` exists and has all 7 sections populated (A-G)
- [x] Plan.md Quick Status row for Phase 0 → Complete
- [x] Plan.md Current State updated with audit summary numbers
- [x] Gate criteria did NOT trigger pause: ShipInstance sweep = 8 files (≤25), Planet sweep = 3 files (≤15)
- [x] No production code or test code changed in this phase

## Notes / Risks / Coordination Touchpoints
- **PROJ-443 Phase 5b context**: the prior audit found a 2.5× under-estimate (original 7 → actual 18). Plan for similar variance here.
- **No worktrees** per standing preference — serial execution in main checkout.
- **PROJ-450 is downstream of Phase 3** — coordinate phase-3-complete signal in plan.md so PROJ-450 Phase 0 can verify the precondition.
