# Phase 4: Strategy-Simulation Boundary Protocol

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define `IPostBattleShip` protocol in Core to formalize the strategy-simulation boundary. Update ShipInstance, Fleet, and BattleResult to use protocol instead of concrete Ship type.

---

## Tasks

### Task 4.1: Define IPostBattleShip and IResourceReader protocols [Medium]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Add new section after Combat Entity Protocols (~line 287):
  ```
  # =============================================================================
  # Strategy-Simulation Boundary Protocols (PROJ-90)
  # =============================================================================
  ```
- [ ] Add `IResourceReader` protocol:
  ```python
  @runtime_checkable
  class IResourceReader(Protocol):
      """Read-only interface for resource values."""
      def get_value(self, name: str) -> float: ...
      def get_max_value(self, name: str) -> float: ...
  ```
- [ ] Add `IPostBattleShip` protocol:
  ```python
  @runtime_checkable
  class IPostBattleShip(Protocol):
      """
      Minimal interface for reading post-battle ship state.

      Used by ShipInstance.update_from_ship() and Fleet.update_from_battle_results()
      to extract results without depending on the concrete Ship class.
      Defines the Strategy <-> Simulation boundary for post-battle state transfer.
      """
      @property
      def name(self) -> str: ...
      @property
      def hp(self) -> int: ...
      @property
      def max_hp(self) -> int: ...
      @property
      def is_alive(self) -> bool: ...
      @property
      def is_derelict(self) -> bool: ...
      @property
      def layers(self) -> Dict: ...
      @property
      def resources(self) -> Any: ...
  ```
- [ ] Add TypeGuard function `is_post_battle_ship(obj) -> TypeGuard[IPostBattleShip]`
- [ ] Verify: `python -c "from game.core.protocols import IPostBattleShip, IResourceReader; print('OK')"`

**Notes:**

---

### Task 4.2: Update ShipInstance to use protocol [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

- [ ] Add import: `from game.core.protocols import IPostBattleShip`
- [ ] Modify TYPE_CHECKING block (lines 21-24): Remove `from game.simulation.entities.ship import Ship`, keep `Empire` and `GameRegistries`
- [ ] Change `update_from_ship(self, ship: 'Ship')` → `update_from_ship(self, ship: IPostBattleShip)`
- [ ] Change `from_ship(cls, ship: 'Ship', ...)` → `from_ship(cls, ship: IPostBattleShip, ...)`
  - Add docstring note: "Also calls ShipSerializer.to_dict() internally, which requires a full simulation Ship instance."
- [ ] Verify: `pytest tests/unit/strategy/ -n 4`

**Notes:**

---

### Task 4.3: Update Fleet to use protocol [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

- [ ] Add import: `from game.core.protocols import IPostBattleShip`
- [ ] Modify TYPE_CHECKING block (lines 6-8): Remove `from game.simulation.entities.ship import Ship`, keep `GameRegistries`
- [ ] Change `update_from_battle_results(surviving_ships: List['Ship'])` → `List[IPostBattleShip]`
- [ ] Verify: `pytest tests/unit/strategy/ -n 4`

**Notes:**

---

### Task 4.4: Strengthen BattleResult DTO typing [Simple]
**File:** `game/strategy/interfaces/battle_resolver.py`
**Tests:** `pytest tests/unit/strategy/adapters/ tests/unit/strategy/conflict_resolution/ -v`

- [ ] Add import: `from game.core.protocols import IPostBattleShip`
- [ ] Change `team0_survivors: List[Any]` → `List[IPostBattleShip]`
- [ ] Change `team1_survivors: List[Any]` → `List[IPostBattleShip]`
- [ ] Verify: `pytest tests/unit/strategy/adapters/ -v`

**Notes:**

---

### Task 4.5: Add protocol conformance tests [Simple]
**New File:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py -v`

- [ ] Create test file with conformance tests:
  - Test `Ship` satisfies `IPostBattleShip` via `isinstance()`
  - Test `ResourceRegistry` satisfies `IResourceReader` via `isinstance()`
  - Test all required properties are accessible on a Ship instance
- [ ] Verify: `pytest tests/unit/core/test_protocols_boundary.py -v`

**Notes:**

---

### Task 4.6: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] `pytest tests/ -n 12` — all tests pass
- [ ] Verify `ship_instance.py` no longer TYPE_CHECKING imports Ship
- [ ] Verify `fleet.py` no longer TYPE_CHECKING imports Ship

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ship_instance.py` uses `IPostBattleShip` not `Ship` for type hints
- [ ] `fleet.py` uses `IPostBattleShip` not `Ship` for type hints
- [ ] `BattleResult` uses `List[IPostBattleShip]` not `List[Any]`
- [ ] Protocol conformance tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
