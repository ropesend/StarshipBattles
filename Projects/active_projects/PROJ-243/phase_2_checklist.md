# Phase 2 Checklist: Extract `_initialize_ship()` Helper and Add `register_ship()`
**Status:** Not Started

## Task 2.1: Write failing tests for `_initialize_ship()` [Medium]
**File:** `tests/unit/simulation/systems/test_battle_engine_init_ship.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_battle_engine_init_ship.py`
- [ ] Write test: `_initialize_ship(ship)` wires `ship.combat_engine._event_bus` to `self.combat_events`
- [ ] Write test: `_initialize_ship(ship)` calls `comp.update()` for all active components
- [ ] Write test: `_initialize_ship(ship)` calls `ship.recalculate_stats()`
- [ ] Write test: `_initialize_ship(ship)` calls `ship.update_derelict_status()`
- [ ] Run tests -- confirm they fail (`_initialize_ship` does not exist yet)
**Notes:** Use mock ships with mock components. Verify via `assert_called_once` on mocks.

## Task 2.2: Extract `_initialize_ship()` from `start()` [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [ ] Add new method after `_log_initial_status()` (after line 318):
  ```python
  def _initialize_ship(self, ship: 'Ship') -> None:
      """Run per-ship initialization: event bus, components, stats, derelict check.

      Called from start() for initial ships and add_ship_mid_battle() for
      reinforcements. Extracted to ensure parity between both paths.
      """
      ship.combat_engine._event_bus = self.combat_events
      for comp in ship.get_all_components():
          if comp.is_active:
              comp.update()
      ship.recalculate_stats()
      ship.update_derelict_status()
  ```
- [ ] Replace lines 286-297 in `start()` with a call to `_initialize_ship()`:
  ```python
  # Was:
  #   for s in self.ships:
  #       s.combat_engine._event_bus = self.combat_events
  #   for s in self.ships:
  #       for comp in s.get_all_components():
  #           if comp.is_active:
  #               comp.update()
  #       s.recalculate_stats()
  #       s.update_derelict_status()
  # Now:
  for s in self.ships:
      self._initialize_ship(s)
  ```
- [ ] Run new tests from Task 2.1 -- confirm they pass
- [ ] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The two separate `for s in self.ships` loops (lines 286-287 and 292-297) collapse into one loop calling `_initialize_ship(s)`. This is safe because event bus wiring has no dependency on other ships' event buses.

## Task 2.3: Write failing test for `FleetAuraManager.register_ship()` [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_register.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_register.py -v`
- [ ] Create test file `tests/unit/simulation/combat/test_fleet_aura_register.py`
- [ ] Write test: `register_ship(ship, all_ships)` calls `_scan_ship(ship)` (new ship's abilities scanned)
- [ ] Write test: `register_ship(ship, all_ships)` calls `_recalculate(all_ships)` (bonuses updated)
- [ ] Write test: after `register_ship()`, the new ship has correct `fleet_attack_bonus`
- [ ] Write test: after `register_ship()`, existing ships receive bonuses from the new ship's fleet-scope abilities
- [ ] Run tests -- confirm they fail (`register_ship` does not exist yet)
**Notes:** Use mock ships with mock abilities for unit tests. Integration test in Phase 4 covers real components.

## Task 2.4: Add `register_ship()` to FleetAuraManager [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_register.py -v`
- [ ] Add new method after `_scan_ship()` (after line 113):
  ```python
  def register_ship(self, ship: Any, all_ships: List[Any]) -> None:
      """Register a ship added mid-battle.

      Scans the new ship for fleet-scope abilities and recalculates
      all team bonuses so that:
      1. The new ship's abilities contribute to teammates
      2. The new ship receives existing fleet bonuses

      Args:
          ship: The newly added ship
          all_ships: All ships currently in battle (including the new one)
      """
      if ship.is_alive:
          self._scan_ship(ship)
      self._recalculate(all_ships)
  ```
- [ ] Run new tests from Task 2.3 -- confirm they pass
- [ ] Run existing aura tests (if any): `pytest tests/unit/simulation/combat/ -v`
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
