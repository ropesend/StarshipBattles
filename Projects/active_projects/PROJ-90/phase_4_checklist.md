# Phase 4: Strategy-Simulation Boundary Protocol

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Define `IPostBattleShip` protocol in Core to formalize the strategy-simulation boundary. Update ShipInstance, Fleet, and BattleResult to use protocol instead of concrete Ship type.

---

## Tasks

### Task 4.1: Define IPostBattleShip and IResourceReader protocols [Medium]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/ -v`

- [x] Add new section after Combat Entity Protocols (~line 287):
  ```
  # =============================================================================
  # Strategy-Simulation Boundary Protocols (PROJ-90)
  # =============================================================================
  ```
- [x] Add `IResourceReader` protocol
- [x] Add `IPostBattleShip` protocol
- [x] Add TypeGuard functions `is_post_battle_ship()` and `is_resource_reader()`
- [x] Verify: `python -c "from game.core.protocols import IPostBattleShip, IResourceReader; print('OK')"`

**Notes:** Protocols added at end of file after IScene section.

---

### Task 4.2: Update ShipInstance to use protocol [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

- [x] Add import: `from game.core.protocols import IPostBattleShip`
- [x] Modify TYPE_CHECKING block: Remove `from game.simulation.entities.ship import Ship`, keep `Empire` and `GameRegistries`
- [x] Change `update_from_ship(self, ship: 'Ship')` → `update_from_ship(self, ship: IPostBattleShip)`
- [x] Change `from_ship(cls, ship: 'Ship', ...)` → `from_ship(cls, ship: IPostBattleShip, ...)`
  - Added docstring note: "Also calls ShipSerializer.to_dict() internally, which requires a full simulation Ship instance."
- [x] Verify: `pytest tests/unit/strategy/ -n 4` - 1537 passed

**Notes:** Ship import completely removed from TYPE_CHECKING block.

---

### Task 4.3: Update Fleet to use protocol [Medium]
**File:** `game/strategy/data/fleet.py` and `game/strategy/data/fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

- [x] Add import: `from game.core.protocols import IPostBattleShip`
- [x] `fleet_battle_adapter.py`: Change `update_from_battle_results(surviving_ships: List['Ship'])` → `List[IPostBattleShip]`
- [x] `fleet.py`: Change `update_from_battle_results(surviving_ships: List['Ship'])` → `List[IPostBattleShip]`
- [x] Verify: `pytest tests/unit/strategy/ -n 4` - 1537 passed

**Notes:** Ship import kept in TYPE_CHECKING for `to_battle_ships` return type (returns actual Ships). The protocol replaces the input type only.

---

### Task 4.4: Strengthen BattleResult DTO typing [Simple]
**File:** `game/strategy/interfaces/battle_resolver.py`
**Tests:** `pytest tests/unit/strategy/adapters/ tests/unit/strategy/conflict_resolution/ -v`

- [x] Add import: `from game.core.protocols import IPostBattleShip`
- [x] Change `team0_survivors: List[Any]` → `List[IPostBattleShip]`
- [x] Change `team1_survivors: List[Any]` → `List[IPostBattleShip]`
- [x] Verify: `pytest tests/unit/strategy/adapters/ -v` - 41 passed

**Notes:** Removed Any import, now uses typed protocol.

---

### Task 4.5: Add protocol conformance tests [Simple]
**New File:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py -v`

- [x] Create test file with conformance tests:
  - Test `Ship` satisfies `IPostBattleShip` via `isinstance()` - 9 tests
  - Test `ResourceRegistry` satisfies `IResourceReader` via `isinstance()` - 6 tests
  - Test negative cases (dict, None don't satisfy) - 2 tests
- [x] Verify: `pytest tests/unit/core/test_protocols_boundary.py -v` - 17 passed

**Notes:** Created comprehensive conformance test suite.

---

### Task 4.6: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] `pytest tests/ -n 12` — 7557 passed
- [x] Verify `ship_instance.py` no longer TYPE_CHECKING imports Ship - CONFIRMED
- [x] Verify `fleet.py` update_from_battle_results uses IPostBattleShip - CONFIRMED

**Notes:** 17 new tests added (7540 → 7557)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `ship_instance.py` uses `IPostBattleShip` not `Ship` for type hints
- [x] `fleet.py` uses `IPostBattleShip` not `Ship` for type hints (for update_from_battle_results)
- [x] `BattleResult` uses `List[IPostBattleShip]` not `List[Any]`
- [x] Protocol conformance tests pass (17 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
