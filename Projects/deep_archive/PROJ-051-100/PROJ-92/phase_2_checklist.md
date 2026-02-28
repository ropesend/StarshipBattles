# Phase 2: Delete no-op TYPE_CHECKING blocks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-92 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove 6 vestigial `if TYPE_CHECKING: pass` blocks and clean up unused `TYPE_CHECKING` imports.

---

## Tasks

### Task 2.1: Clean up 6 files [Simple]
**Tests:** `pytest tests/ -n 12 -q`

**File 1:** `game/ui/services/component_service.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 18-19)
- [ ] Remove `TYPE_CHECKING` from typing import (line 13)

**File 2:** `game/ui/services/vehicle_class_service.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 20-21)
- [ ] Remove `TYPE_CHECKING` from typing import (line 16)

**File 3:** `game/strategy/services/fleet_navigation_service.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 63-64)
- [ ] Remove `TYPE_CHECKING` from typing import (line 56)

**File 4:** `game/strategy/engine/fleet_order_processor.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 23-24)
- [ ] Remove `TYPE_CHECKING` from typing import (line 16)

**File 5:** `game/strategy/engine/maintenance_engine.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 23-24)
- [ ] Remove `TYPE_CHECKING` from typing import (line 19)

**File 6:** `game/strategy/engine/production_engine.py`
- [ ] Remove `if TYPE_CHECKING: pass` block (lines 30-31)
- [ ] Remove `TYPE_CHECKING` from typing import (line 20)

- [ ] Run `pytest tests/ -n 12 -q` — all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
