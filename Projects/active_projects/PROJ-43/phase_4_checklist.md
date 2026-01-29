# Phase 4: TurnEngine Constructor DI Refactor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert TurnEngine from lazy @property imports to full constructor dependency injection

---

## Prerequisites
- [ ] Phase 1 complete (IBattleResolver already exists)

## Background

**Current Pattern (Lazy @property):**
```python
@property
def movement_engine(self):
    if self._movement_engine is None:
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        self._movement_engine = FleetMovementEngine(self._session)
    return self._movement_engine
```

**Target Pattern (Constructor DI):**
```python
def __init__(self, session, *,
             movement_engine: IMovementEngine = None,
             production_engine: IProductionEngine = None, ...):
    self._movement_engine = movement_engine or FleetMovementEngine(session)
```

**User Decision:** Full constructor DI for extensibility and testability.

---

## Tasks

### Task 4.1: Create Strategy Engine Interfaces [Medium]
**File:** `game/strategy/interfaces/engines.py` (NEW)
**Tests:** `pytest tests/unit/strategy/interfaces/`

Create protocols for all TurnEngine sub-engines:

- [ ] Create `IMovementEngine` protocol:
  - `process_fleet_movements(fleets, system_map)`
  - Other methods from FleetMovementEngine
- [ ] Create `IProductionEngine` protocol:
  - `process_production(systems, empire)`
  - Other methods from ProductionEngine
- [ ] Create `IOrderProcessor` protocol:
  - `process_orders(fleets)`
  - Other methods from FleetOrderProcessor
- [ ] Create `IConflictEngine` protocol:
  - `resolve_conflicts(fleets, system_map)`
  - Other methods from ConflictResolutionEngine
- [ ] Create `IResourceEngine` protocol:
  - `process_resources(systems, empire)`
  - Other methods from ResourceManagementEngine
- [ ] Update `game/strategy/interfaces/__init__.py` to export all interfaces
- [ ] Create unit tests verifying interface definitions

**Notes:**

---

### Task 4.2: Verify Sub-Engine Compatibility [Simple]
**Files:** All sub-engine files
**Tests:** N/A (verification)

- [ ] Verify `FleetMovementEngine` matches IMovementEngine
- [ ] Verify `ProductionEngine` matches IProductionEngine
- [ ] Verify `FleetOrderProcessor` matches IOrderProcessor
- [ ] Verify `ConflictResolutionEngine` matches IConflictEngine
- [ ] Verify `ResourceManagementEngine` matches IResourceEngine
- [ ] Document any signature mismatches

**Notes:**

---

### Task 4.3: Refactor TurnEngine Constructor [Complex]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

**Current lazy imports (lines 72-125):**
- Line 72-73: SimulationBattleResolver
- Line 92-93: FleetMovementEngine
- Line 100-101: ProductionEngine
- Line 108-109: FleetOrderProcessor
- Line 116-117: ConflictResolutionEngine
- Line 124-125: ResourceManagementEngine

**Changes:**
- [ ] Add interface imports at module level
- [ ] Update `__init__` signature to accept optional engine parameters:
  ```python
  def __init__(
      self,
      session: 'GameSession',
      *,
      battle_resolver: IBattleResolver = None,
      movement_engine: IMovementEngine = None,
      production_engine: IProductionEngine = None,
      order_processor: IOrderProcessor = None,
      conflict_engine: IConflictEngine = None,
      resource_engine: IResourceEngine = None
  ):
  ```
- [ ] Initialize engines in constructor with defaults
- [ ] Remove lazy @property implementations
- [ ] Keep property getters for compatibility (return stored instances)
- [ ] Move imports to module level (or keep in constructor for defaults)
- [ ] Verify existing IBattleResolver injection still works

**Notes:**

---

### Task 4.4: Create Engine Factory Function [Simple]
**File:** `game/strategy/engine/turn_engine.py` (or new file)
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py`

- [ ] Create `create_default_turn_engine(session)` factory function
- [ ] Factory creates TurnEngine with all default sub-engines
- [ ] Simplifies instantiation for production code
- [ ] Document usage pattern

**Notes:**

---

### Task 4.5: Update TurnEngine Instantiation Sites [Medium]
**Files:** All files that create TurnEngine
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/`

- [ ] Find all TurnEngine instantiation sites:
  - `grep -r "TurnEngine(" game/`
  - `grep -r "TurnEngine(" tests/`
- [ ] Update each to either:
  - Use factory function for default behavior
  - Pass explicit engines for test mocking
- [ ] Verify all sites updated

**Notes:**

---

### Task 4.6: Create Mock Engines for Testing [Medium]
**File:** `tests/unit/strategy/mocks/mock_engines.py` (NEW)
**Tests:** N/A (test utilities)

- [ ] Create `MockMovementEngine` implementing IMovementEngine
- [ ] Create `MockProductionEngine` implementing IProductionEngine
- [ ] Create `MockOrderProcessor` implementing IOrderProcessor
- [ ] Create `MockConflictEngine` implementing IConflictEngine
- [ ] Create `MockResourceEngine` implementing IResourceEngine
- [ ] Document usage in test files

**Notes:**

---

### Task 4.7: Update Existing TurnEngine Tests [Medium]
**File:** `tests/unit/strategy/test_turn_engine.py`
**Tests:** Self-referential

- [ ] Add tests for constructor injection
- [ ] Add tests verifying each engine can be injected
- [ ] Add tests verifying default engines are created when not provided
- [ ] Add tests using mock engines
- [ ] Verify all existing tests still pass

**Notes:**

---

### Task 4.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/strategy/`

- [ ] Run strategy integration tests
- [ ] Verify turn processing still works end-to-end
- [ ] Verify save/load works with new TurnEngine
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 5 sub-engine interfaces defined (IMovementEngine, etc.)
- [ ] TurnEngine uses constructor DI for all engines
- [ ] No lazy @property imports remain
- [ ] All TurnEngine instantiation sites updated
- [ ] Mock engines available for testing
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
