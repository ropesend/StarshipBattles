# Phase 12: UI-Battle Interface (AR-06)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 12`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create clean interface between UI and battle layer

---

## Prerequisites
- [ ] Phase 2C complete (workshop/battle decoupling)
- [ ] Phase 8 complete (BattleEngine-AI decoupling)

## Background

**Problem (AR-06):**
- UI battle code imports directly from simulation
- Battle panels directly access ship objects
- Battle UI tightly coupled to simulation internals
- Cannot mock for UI testing

**Target:** Create IBattleUI service interface exposing only what UI needs.

---

## Tasks

### Task 12.1: Analyze Battle UI Requirements [Simple]
**Files:** `game/ui/screens/battle_scene.py`, `game/ui/hud/panels.py`
**Tests:** N/A (analysis)

- [ ] Document what data UI needs from battle:
  - Ships (position, health, team, status)
  - Projectiles (position, type)
  - Battle state (is_over, winner, tick_count)
  - AI controllers state
- [ ] Document what actions UI performs:
  - Start/pause/resume battle
  - Select ship
  - Camera control
- [ ] Add to findings/phase_12_analysis.md

**Notes:**

---

### Task 12.2: Create IBattleUI Protocol [Medium]
**File:** `game/ui/interfaces/battle_ui.py` (NEW)
**Tests:** `pytest tests/unit/ui/interfaces/`

- [ ] Create `IBattleUI` protocol with query methods:
  ```python
  class IBattleUI(Protocol):
      def get_ships(self) -> List[ShipDTO]:
          ...
      def get_projectiles(self) -> List[ProjectileDTO]:
          ...
      def is_battle_over(self) -> bool:
          ...
      def get_winner(self) -> Optional[int]:
          ...
      def get_tick_count(self) -> int:
          ...
  ```
- [ ] Create DTOs for UI consumption:
  - ShipDTO (id, position, health, team, is_alive, etc.)
  - ProjectileDTO (id, position, type, etc.)
- [ ] Create unit tests

**Notes:**

---

### Task 12.3: Create BattleUIService Implementation [Medium]
**File:** `game/ui/services/battle_ui_service.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_battle_ui_service.py`

- [ ] Create `BattleUIService` implementing IBattleUI:
  - Wraps BattleService/BattleEngine
  - Converts internal objects to DTOs
  - Exposes only what UI needs
- [ ] Inject BattleService via constructor
- [ ] Create unit tests

**Notes:**

---

### Task 12.4: Update battle_scene.py [Medium]
**File:** `game/ui/screens/battle_scene.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle*.py`

- [ ] Inject BattleUIService via constructor
- [ ] Replace direct BattleEngine access with service calls
- [ ] Replace direct Ship access with ShipDTO
- [ ] Replace direct Projectile access with ProjectileDTO
- [ ] Verify rendering still works with DTOs
- [ ] Run battle scene tests

**Notes:**

---

### Task 12.5: Update HUD Panels [Medium]
**File:** `game/ui/hud/panels.py`
**Tests:** `pytest tests/unit/ui/hud/`

- [ ] Identify panels that access battle data
- [ ] Update to receive DTOs instead of domain objects
- [ ] Update rendering to use DTO properties
- [ ] Run panel tests

**Notes:**

---

### Task 12.6: Create Mock BattleUIService [Simple]
**File:** `tests/unit/ui/mocks/mock_battle_ui_service.py` (NEW)
**Tests:** N/A (test utility)

- [ ] Create `MockBattleUIService` implementing IBattleUI:
  - Returns configurable mock data
  - Tracks method calls
  - Simulates battle progression
- [ ] Document usage for UI tests

**Notes:**

---

### Task 12.7: Update UI Tests to Use Mock [Medium]
**Files:** Battle-related UI tests
**Tests:** Self-referential

- [ ] Update battle scene tests to use MockBattleUIService
- [ ] Update HUD panel tests to use mock
- [ ] Verify tests are faster with mock
- [ ] Verify tests are more isolated

**Notes:**

---

### Task 12.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/test_battle*.py`

- [ ] Run battle integration tests
- [ ] Verify battle rendering works
- [ ] Verify ship selection works
- [ ] Verify battle completion works
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] IBattleUI protocol created
- [ ] BattleUIService implementation created
- [ ] ShipDTO and ProjectileDTO created
- [ ] battle_scene.py uses BattleUIService
- [ ] HUD panels use DTOs
- [ ] Mock service available for testing
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
