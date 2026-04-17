# Phase 7: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 7`

**Status:** Not Started
**Objective:** Document the materializer service in the docs directory.

---

## Tasks

### Task 7.1: Add materializer to `04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** Manual review

- [ ] Add a new service entry: "ShipMaterializer"
- [ ] Describe: protocol (`IShipMaterializer`), two implementations (InstanceBackedMaterializer, DesignOnlyMaterializer), access pattern (`get_default_ship_materializer()` / `set_default_ship_materializer()`)
- [ ] Note: Combat Lab swaps to DesignOnlyMaterializer at startup; everything else uses the default InstanceBackedMaterializer

**Notes:**

### Task 7.2: Update architecture doc service list [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** Manual review

- [ ] Update the ApplicationContext services list (where 10 services are currently enumerated) to include ship_materializer
- [ ] Service count is now 11 — update any "10 services" references (grep for "10 services" and "10 singletons")

**Notes:**

### Task 7.3: Update combat_simulation.md canonical example [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] Find the "Unified entry" code example (around L56-66 in the current file)
- [ ] Remove the `ship_builder=my_ship_builder` line from the canonical example
- [ ] Add a note below: "`ship_builder` is an optional test-override. Production code relies on the ship_materializer service in ApplicationContext — callers configure it (if needed) before invoking `run_battle`."

**Notes:**

### Task 7.4: Update memory [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md` (or relevant memory file)
**Tests:** Manual

- [ ] Add bullet: "ApplicationContext now manages 11 services; ship_materializer added in PROJ-274; InstanceBackedMaterializer is default, DesignOnlyMaterializer used by Combat Lab"

**Notes:**

### Task 7.5: Final regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green
- [ ] No stale `ship_builder=` production references (grep `grep -rn "ship_builder=" game/ | grep -v test | grep -v "#"` — zero in production files outside battle_runner / battle_controller signatures)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — mark project COMPLETE
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 7`
- [ ] User verification: launch strategy → start battle → ships materialize correctly; launch Combat Lab → run test → ships materialize correctly
