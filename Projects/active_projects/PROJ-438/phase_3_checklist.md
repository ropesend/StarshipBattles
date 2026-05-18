# Phase 3: ShipInstance residual state-surface consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce the remaining post-container `ShipInstance` surface without turning the phase into a 910-caller shim sweep.

---

## Tasks

### Task 3.1: [Task list to be authored at phase start]
**File:** `game/strategy/data/ship_instance.py` / `game/strategy/data/ship_instance_serializer.py` / `game/strategy/data/ship_instance_bridge.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/save_load/test_roundtrip_ships.py`

- [ ] Author detailed subtasks at phase start.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
