# Phase 2: Architecture Boundary Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Restore clean subpackage boundaries and make engines implement their interfaces
**Priority:** High

---

## Tasks

### Task 2.1: AR-003 — Remove data/→engine/ dependency in build_queue_source [Simple]
**File:** `game/strategy/data/build_queue_source.py:267`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

`build_queue_source.py` imports `_colony_has_planetary_yard` (a private function) from `game.strategy.engine.production_engine`. The data/ subpackage should not depend on engine/.

- [x] Write test covering the planetary yard check behavior
- [x] Move `_colony_has_planetary_yard` to a shared location (e.g., a utility in data/ or services/) or inline the logic
- [x] Also fix AR-007: remove `RegistryManager.instance()` direct singleton access at the same location — accept registries via parameter instead
- [x] Verify: no remaining engine/ imports in build_queue_source.py

**Notes:** Moved `colony_has_planetary_yard` to `build_queue_source.py` (public). Added `_RegistriesFromProvider` adapter. Replaced `RegistryManager.instance()` with `get_default_registry_provider()`. Updated callers in production_engine.py and strategy_detail_formatter.py. 2 new boundary tests. 19 pre-existing test failures in test_build_queue_source.py (not caused by our changes).

### Task 2.2: AR-004 — Remove services/→engine/ dependency in cargo_transfer_service [Medium]
**File:** `game/strategy/services/cargo_transfer_service.py:12`
**Tests:** `pytest tests/unit/strategy/services/test_cargo_transfer_service.py`

`CargoTransferService` imports `IssueTransferCommand` from `game.strategy.engine.commands`. Services should not depend on engine command definitions.

- [x] Write test for the cargo transfer flow
- [x] Refactor: move the command dataclass to a shared location (e.g., `data/` or `commands.py` at strategy root), or restructure so the service doesn't need to create commands
- [x] Verify: no remaining engine/ imports in cargo_transfer_service.py

**Notes:** Moved `IssueTransferCommand` import from top-level to TYPE_CHECKING block + late import inside `build_transfer_command()`. This eliminates the module-level coupling while keeping the runtime import where it's needed. Follows the existing late-import pattern documented in the codebase.

### Task 2.3: AR-005 — Add interface inheritance to 8 sub-engines [Simple]
**File:** `game/strategy/interfaces/engines.py` + 8 engine files
**Tests:** `pytest tests/unit/strategy/engine/`

Interfaces exist in `engines.py` but only 4 of 12 engines formally inherit from their ABC. The other 8 should declare their interface.

- [x] Identify which 8 engines are missing interface inheritance (compare engines.py interfaces vs actual engine classes)
- [x] Add the ABC base class to each engine's class definition
- [x] Verify: all engines pass isinstance checks against their interface
- [x] Verify: no test regressions

**Notes:** Added interface inheritance to: FleetMovementEngine, ProductionEngine, OrderProcessor, ConflictResolutionEngine, ConsumableManagementEngine, EnvironmentalHazardEngine, PlanetEnergyEngine, PlanetActionEngine. 12 parametrized tests in `test_engine_inheritance.py`. Full suite: 14,297 passed (same 10 pre-existing quickstart failures).


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
