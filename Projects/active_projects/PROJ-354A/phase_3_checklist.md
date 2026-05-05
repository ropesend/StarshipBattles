# Phase 3: Docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354A 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the new outcome fields and the schema version bump.

See `plan.md` Phase 3 for full task details.

---

## Tasks

### Task 3.1: Update `docs/systems/combat_simulation.md` [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] In § 11 Replay Capture & Playback, document per-component end-state fields:
  - `current_hp`, `max_hp`, `status` (`ComponentStatus.name`), `is_active`
- [ ] Note `REPLAY_SCHEMA_VERSION = "2.0.0"` (was `"1.0.0"`)
- [ ] Note: existing v1 replays surface as `version_drift`, skipped gracefully
- [ ] Update the `> **Last verified:**` blockquote at the top of the doc to today's date with brief change note
- [ ] Verify: documented fields match `_component_state_to_dict` output

**Notes:**

### Task 3.2: Update CLAUDE.md / AGENTS.md if needed [Simple]
**Files:** `CLAUDE.md`, `AGENTS.md`
**Tests:** Manual review

- [ ] Skim both files for "ComponentStateSpec" or "REPLAY_SCHEMA_VERSION 1.0.0" references
- [ ] Verify: either no edits needed, or specific edits applied

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete and ready for verification
