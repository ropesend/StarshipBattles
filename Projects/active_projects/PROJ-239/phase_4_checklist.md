# Phase 4: Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring strategy layer documentation up to date with code reality
**Priority:** High

---

## Tasks

### Task 4.1: DOCC-001 — Update orders_system.md: FleetOrder → Order [Simple]
**File:** `docs/systems/orders_system.md`

The entire doc still uses `FleetOrder` as the class name. Per PROJ-238, the class is now `Order`.

- [ ] Find/replace `FleetOrder` → `Order` throughout orders_system.md
- [ ] Update the "FleetOrder Data Structure" section heading and code examples
- [ ] Update the Key Files table entry
- [ ] Update the "Adding a New Order Type" tutorial code examples (DOCC-014)
- [ ] Verify: all references to the class use `Order`, not `FleetOrder`

### Task 4.2: DOCC-002 — Add missing order types to orders_system.md [Simple]
**File:** `docs/systems/orders_system.md`

`ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` order types exist in `ACTION_ORDER_TYPES` and `PLANET_ACTION_ORDER_TYPES` but the doc doesn't mention them.

- [ ] Add these to the "Order Type Categories" section under a "Planet Action Orders" subsection
- [ ] Document their target format, processing engine (PlanetActionEngine), and behavior
- [ ] Add to the `ACTION_ORDER_TYPES` listing in the doc

### Task 4.3: DOCC-003 — Document QualityEngine and AtmosphereEngine [Simple]
**Files:** `docs/systems/strategy_layer.md`, `game/strategy/engine/turn_engine.py`

Two post-loop engines (QualityEngine, AtmosphereEngine) exist in the turn engine but appear nowhere in documentation.

- [ ] Add QualityEngine and AtmosphereEngine to the "Per-Tick Phase Execution Order" table in strategy_layer.md (as post-loop phases, after PopulationEngine)
- [ ] Add their interfaces to the "Sub-Engine Interfaces" table if applicable
- [ ] Update the turn_engine.py module docstring to include the 4 missing phases (Phase 0c1, 0f, 1.6, and the two post-loop phases) — this is DOCC-006
- [ ] Add `SetAtmosphereTargetCommand` to the "Registered Handlers" table (DOCC-004)

### Task 4.4: DOCC-012 — Add missing DTOs to strategy_layer.md [Simple]
**File:** `docs/systems/strategy_layer.md`

`FleetOrderInfo`, `ShipInfo`, `WarpPointInfo` are exported from the DTO package but not listed in docs.

- [ ] Add these DTOs to the DTO types list in strategy_layer.md section 1
- [ ] Brief description of each DTO's purpose


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
