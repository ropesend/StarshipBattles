# Phase 1: User-decision gating

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Surface each data-intent decision point to the user and record the chosen option in `decisions.md`. NO data file edits in this phase.

---

## Tasks

### Task 1.1: Present `efficient_engines` decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A (no code change in this phase)

- [ ] Surface plan.md "User Decision Points" item 1 to user
- [ ] User picks (a) delete, (b) redesign, or (c) keep inert
- [ ] If (b), capture: intended target ability keys + corrected effect formula + whether row should remain mandatory-on-allowed
- [ ] Record chosen option + rationale in `decisions.md`
- [ ] Verify: `decisions.md` table has an `efficient_engines` row dated today

**Notes:** [Filled during implementation]

### Task 1.2: Present `mini_capital_missile` type decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A

- [ ] Surface plan.md "User Decision Points" item 2 to user
- [ ] User picks (a) keep `BeamWeaponAbility`, (b) retype to `SeekerWeaponAbility`, or (c) defer
- [ ] If (b), note cascade effects on seeker_*/range_mount/precision_mount/facing/turret_mount valid-target sets (see `findings/source_review.md` static scan)
- [ ] Record chosen option + rationale in `decisions.md`

**Notes:** [Filled during implementation]

### Task 1.3: Present `facing` / `turret_mount` seeker-allowance decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A

- [ ] Surface plan.md "User Decision Points" item 3 to user
- [ ] User picks (a) remove `SeekerWeaponAbility` from both, (b) keep with documented intent, or (c) defer
- [ ] If (b), add explicit `decisions.md` entry "facing/turret_mount intentionally allow seekers as forward-compat" so this does not keep resurfacing as ambiguous drift
- [ ] Record chosen option + rationale in `decisions.md`

**Notes:** [Filled during implementation]

### Task 1.4: Re-validate static scan after decisions captured [Simple]
**File:** `Projects/active_projects/PROJ-497/findings/source_review.md`
**Tests:** N/A

- [ ] Re-run the static-analysis script in `findings/source_review.md` and confirm no NEW broken rows appeared since this project was created
- [ ] If new rows appear, surface to user before continuing — they may belong to a different project

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `decisions.md` has at least three new rows (one per decision point) with date + chosen option + rationale
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
