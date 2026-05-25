# Phase 1: User-decision gating

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Surface each data-intent decision point to the user and record the chosen option in `decisions.md`. NO data file edits in this phase.

---

## Tasks

### Task 1.1: Present `efficient_engines` decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A (no code change in this phase)

- [x] Surface plan.md "User Decision Points" item 1 to user
- [x] User picks (a) delete, (b) redesign, or (c) keep inert
- [x] If (b), capture: intended target ability keys + corrected effect formula + whether row should remain mandatory-on-allowed
- [x] Record chosen option + rationale in `decisions.md`
- [x] Verify: `decisions.md` table has an `efficient_engines` row dated today

**Notes:** User picked (b) REDESIGN. Specifics (target ability keys, formula, mandatory posture) are NOT YET specified by user; surfaced as a follow-up question to the orchestrator with concrete options. Recorded in `decisions.md` "Pending user follow-up" section. Phase 2 Task 2.1 is therefore BLOCKED on this follow-up.

### Task 1.2: Present `mini_capital_missile` type decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A

- [x] Surface plan.md "User Decision Points" item 2 to user
- [x] User picks (a) keep `BeamWeaponAbility`, (b) retype to `SeekerWeaponAbility`, or (c) defer
- [x] If (b), note cascade effects on seeker_*/range_mount/precision_mount/facing/turret_mount valid-target sets (see `findings/source_review.md` static scan)
- [x] Record chosen option + rationale in `decisions.md`

**Notes:** User picked (b) RETYPE. Cascade verified and recorded in `decisions.md` Decision 2 + Decision 2 cascade rows (seeker_* gain mini_capital_missile; range_mount/precision_mount lose it; turret_mount/facing/rapid_fire unchanged).

### Task 1.3: Present `facing` / `turret_mount` seeker-allowance decision to user [Simple]
**File:** `Projects/active_projects/PROJ-497/decisions.md`
**Tests:** N/A

- [x] Surface plan.md "User Decision Points" item 3 to user
- [x] User picks (a) remove `SeekerWeaponAbility` from both, (b) keep with documented intent, or (c) defer
- [x] If (b), add explicit `decisions.md` entry "facing/turret_mount intentionally allow seekers as forward-compat" so this does not keep resurfacing as ambiguous drift
- [x] Record chosen option + rationale in `decisions.md`

**Notes:** User picked (b) KEEP with rich rationale. Seekers honor firing-arc/facing for launch direction but ignore arc for target acquisition. Documented verbatim. `docs/systems/ability_reference.md:287` flagged as ambiguous (doc-clarification candidate, deferred out of PROJ-497).

### Task 1.4: Re-validate static scan after decisions captured [Simple]
**File:** `Projects/active_projects/PROJ-497/findings/source_review.md`
**Tests:** N/A

- [x] Re-run the static-analysis script in `findings/source_review.md` and confirm no NEW broken rows appeared since this project was created
- [x] If new rows appear, surface to user before continuing — they may belong to a different project

**Notes:** Re-ran the live-rule scan (no `deny_abilities` enforcement). Result identical to the table in `findings/source_review.md` — `efficient_engines` 0 valid, all others as recorded. No new broken rows. Recorded in decisions.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `decisions.md` has at least three new rows (one per decision point) with date + chosen option + rationale
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
