# Phase 4: Planet / Fleet / Empire state-surface slimming

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow the bounded aggregate-root/entity surfaces that remain after storage migration: `Planet` save-schema breadth and directly-owned adjunct state, `Fleet` / `Empire` persistence-facing aggregate behavior, and matching `galaxy_protocols.py` read contracts. Do not let this expand into a generic entity-polish sweep.

---

## Tasks

### Task 4.1: [Task list to be authored at phase start]
**File:** `game/strategy/data/planet.py` / `planet_serde.py` / `fleet.py` / `empire.py`
**Tests:** `pytest tests/unit/strategy/data/ tests/integration/save_load/`

- [ ] Author detailed subtasks at phase start.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
