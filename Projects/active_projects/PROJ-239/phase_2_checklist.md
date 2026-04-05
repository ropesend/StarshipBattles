# Phase 2: Architecture Boundary Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Restore clean subpackage boundaries and make engines implement their interfaces
**Priority:** High

---

## Tasks

### Task 2.1: AR-003 — Remove data/→engine/ dependency in build_queue_source [Simple]
**File:** `game/strategy/data/build_queue_source.py:267`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

`build_queue_source.py` imports `_colony_has_planetary_yard` (a private function) from `game.strategy.engine.production_engine`. The data/ subpackage should not depend on engine/.

- [ ] Write test covering the planetary yard check behavior
- [ ] Move `_colony_has_planetary_yard` to a shared location (e.g., a utility in data/ or services/) or inline the logic
- [ ] Also fix AR-007: remove `RegistryManager.instance()` direct singleton access at the same location — accept registries via parameter instead
- [ ] Verify: no remaining engine/ imports in build_queue_source.py

### Task 2.2: AR-004 — Remove services/→engine/ dependency in cargo_transfer_service [Medium]
**File:** `game/strategy/services/cargo_transfer_service.py:12`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py`

`CargoTransferService` imports `IssueTransferCommand` from `game.strategy.engine.commands`. Services should not depend on engine command definitions.

- [ ] Write test for the cargo transfer flow
- [ ] Refactor: move the command dataclass to a shared location (e.g., `data/` or `commands.py` at strategy root), or restructure so the service doesn't need to create commands
- [ ] Verify: no remaining engine/ imports in cargo_transfer_service.py

### Task 2.3: AR-005 — Add interface inheritance to 8 sub-engines [Simple]
**File:** `game/strategy/interfaces/engines.py` + 8 engine files
**Tests:** `pytest tests/unit/strategy/engine/`

Interfaces exist in `engines.py` but only 4 of 12 engines formally inherit from their ABC. The other 8 should declare their interface.

- [ ] Identify which 8 engines are missing interface inheritance (compare engines.py interfaces vs actual engine classes)
- [ ] Add the ABC base class to each engine's class definition
- [ ] Verify: all engines pass isinstance checks against their interface
- [ ] Verify: no test regressions

**Notes:** This should be purely additive — just adding the base class to each class definition. No logic changes needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
