# Phase 8: Documentation [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create architectural documentation for the orders system.

---

## Tasks

### Task 8.1: Write docs/architecture/orders_system.md [Simple]
**File:** `docs/architecture/orders_system.md` (new)

- [ ] Document: Order lifecycle (queue -> tick progress -> execute -> pop)
- [ ] Document: Action tick mechanics (alignment with movement ticks, interval formula)
- [ ] Document: OrderType categories (MOVEMENT_ORDER_TYPES, ACTION_ORDER_TYPES, BUILD)
- [ ] Document: action_time moddability via component abilities in components.json
- [ ] Document: execution_progress serialization
- [ ] Document: The Tick Contract — how to add a new order type:
  1. Add to OrderType enum
  2. Categorize as MOVEMENT or ACTION
  3. Define action_time in component ability (or default 1)
  4. Add processing method to FleetOrderProcessor or SuperweaponOrderProcessor
  5. Add command handler and register in CommandHandlerRegistry
- [ ] Document: WARP vs MOVE distinction
- [ ] Include timing diagram examples showing tick-by-tick execution

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Documentation is clear and comprehensive
- [ ] `pytest tests/ -n 12` — full suite passes (final verification)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
