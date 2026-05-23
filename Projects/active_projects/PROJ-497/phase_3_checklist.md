# Phase 3: Doc + decisions update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make sure docs and decisions reflect the chosen data surface so PROJ-498's matrix test encodes the intended truth.

**Precondition:** Phase 2 complete; all approved edits applied + green.

---

## Tasks

### Task 3.1: Update `docs/guides/modifier_system.md` allow_abilities section [Simple]
**File:** `docs/guides/modifier_system.md`
**Tests:** N/A (docs)

- [ ] Find allow_abilities discussion (PROJ-489 audit F7 noted line 98, 285)
- [ ] Add a "data-intent decisions" reference pointing at PROJ-497's decisions.md (or the index of decisions)
- [ ] If `efficient_engines` was deleted, remove references in this doc
- [ ] Confirm doc/code consistent per CLAUDE.md "keep code and docs consistent"

**Notes:** [Filled during implementation]

### Task 3.2: Update `docs/guides/adding_modifiers.md` [Simple]
**File:** `docs/guides/adding_modifiers.md`
**Tests:** N/A

- [ ] Locate allow_abilities/allow_types guidance
- [ ] Add note that allow_abilities keys MUST match component ability key namespace (`CombatPropulsion`/`ResourceGeneration`/`ManeuveringThruster`/... — NOT `Engine`/`Generator`/`Weapon`/`Thruster`)
- [ ] Add a brief example of a row that would silently match zero components

**Notes:** [Filled during implementation]

### Task 3.3: Handoff note to PROJ-498 [Simple]
**File:** `Projects/active_projects/PROJ-498/findings/source_review.md` (append)
**Tests:** N/A

- [ ] Append "PROJ-497 outcomes" section listing the final data surface (which rows changed, which decisions were "leave alone")
- [ ] PROJ-498's rejection-matrix test must encode this final surface, not the surface at PROJ-489's audit time

**Notes:** [Filled during implementation]

### Task 3.4: Resolve or update DI-2026-05-23-004 [Simple]
**File:** `AgentCoordination/discovered_issues/log.jsonl`
**Tests:** N/A

- [ ] If `efficient_engines` was deleted/fixed, mark DI-2026-05-23-004 as `resolved` with the PROJ-497 reference
- [ ] If user chose (c) keep inert, mark DI as `accepted-known` with rationale

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Docs match data
- [ ] PROJ-498 has the handoff note
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting audit"
