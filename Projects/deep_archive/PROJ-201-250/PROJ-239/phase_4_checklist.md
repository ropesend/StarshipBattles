# Phase 4: Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Bring strategy layer documentation up to date with code reality
**Priority:** High

---

## Tasks

### Task 4.1: DOCC-001 — Update orders_system.md: FleetOrder → Order [Simple]
**File:** `docs/systems/orders_system.md`

- [x] Find/replace `FleetOrder` → `Order` throughout orders_system.md
- [x] Update the "FleetOrder Data Structure" section heading and code examples
- [x] Update the Key Files table entry
- [x] Update the "Adding a New Order Type" tutorial code examples (DOCC-014)
- [x] Verify: all references to the class use `Order`, not `FleetOrder`

**Notes:** 7 occurrences replaced. Section heading now "Order Data Structure".

### Task 4.2: DOCC-002 — Add missing order types to orders_system.md [Simple]
**File:** `docs/systems/orders_system.md`

- [x] Add these to the "Order Type Categories" section under a "Planet Action Orders" subsection
- [x] Document their target format, processing engine (PlanetActionEngine), and behavior
- [x] Add to the `ACTION_ORDER_TYPES` listing in the doc

**Notes:** Added "Planet Action Orders" subsection with ACTIVATE_ABILITY and DEACTIVATE_ABILITY.

### Task 4.3: DOCC-003 — Document QualityEngine and AtmosphereEngine [Simple]
**Files:** `docs/systems/strategy_layer.md`, `game/strategy/engine/turn_engine.py`

- [x] Add QualityEngine and AtmosphereEngine to post-loop phases in strategy_layer.md
- [x] Update the turn_engine.py module docstring to include all missing phases (0c1, 0f, 1.6, post-loop)
- [x] Add `SetAtmosphereTargetCommand` to the "Registered Handlers" table (DOCC-004)

**Notes:** Added 4 missing phases to module docstring (0c1, 0f, 1.6, plus 2 post-loop phases numbered 3 & 4). Added QualityEngine + AtmosphereEngine to strategy_layer.md. Added SetAtmosphereTargetCommand to command table.

### Task 4.4: DOCC-012 — Add missing DTOs to strategy_layer.md [Simple]
**File:** `docs/systems/strategy_layer.md`

- [x] Add FleetOrderInfo, ShipInfo, WarpPointInfo to DTO types list
- [x] Brief description of each DTO's purpose

**Notes:** Added 3 missing DTOs with descriptions.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
