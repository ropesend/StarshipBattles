# Phase 3 Checklist: Fix `add_ship_mid_battle()` and Fighter Launch
**Status:** Not Started

## Task 3.1: Write failing tests for mid-battle ship initialization [Medium]
**File:** `tests/unit/simulation/systems/test_add_ship_mid_battle.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_add_ship_mid_battle.py`
- [ ] Write test: ship added via `add_ship_mid_battle()` has `combat_engine._event_bus` set to `engine.combat_events`
- [ ] Write test: ship added via `add_ship_mid_battle()` has had `recalculate_stats()` called
- [ ] Write test: ship added via `add_ship_mid_battle()` has had `update_derelict_status()` called
- [ ] Write test: ship added via `add_ship_mid_battle()` is registered with aura manager (`aura_manager.register_ship` called)
- [ ] Write test: ship added via `add_ship_mid_battle()` receives existing fleet bonuses (check `fleet_attack_bonus`)
- [ ] Run tests -- confirm they fail (missing init steps)
**Notes:** These tests use a real or minimally-mocked `BattleEngine` with mock ships. Verify `_initialize_ship` is called by checking its side effects.

## Task 3.2: Fix `add_ship_mid_battle()` [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [ ] Add two lines after the AI controller setup block (after line 352, before the logger.log call at line 354):
  ```python
  # Initialize ship (event bus, components, stats, derelict check)
  self._initialize_ship(ship)
  # Register with aura manager (scan abilities, recalculate bonuses)
  self.aura_manager.register_ship(ship, self.ships)
  ```
- [ ] Run new tests from Task 3.1 -- confirm they pass
- [ ] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The `self.ships.append(ship)` at line 337 happens before the AI block, so `self.ships` already contains the new ship when `register_ship(ship, self.ships)` is called.

## Task 3.3: Write failing test for fighter launch using `add_ship_mid_battle()` [Medium]
**File:** `tests/unit/simulation/systems/test_fighter_launch_init.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_fighter_launch_init.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_fighter_launch_init.py`
- [ ] Write test: fighter launched via LAUNCH attack type has `combat_engine._event_bus` set
- [ ] Write test: fighter launched via LAUNCH attack type is in `engine.ships`
- [ ] Write test: fighter launched via LAUNCH attack type has an AI controller in `engine.ai_controllers`
- [ ] Run tests -- confirm event bus test fails (fighter launch skips init)
**Notes:** This requires setting up a LAUNCH attack in `just_fired_projectiles` and calling `engine.update()`.

## Task 3.4: Refactor fighter launch to use `add_ship_mid_battle()` [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_fighter_launch_init.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [ ] Replace lines 497-509 (direct append + AI creation) with a call to `add_ship_mid_battle()`:
  ```python
  # Was:
  #   self.ships.append(new_ship)
  #   enemy_team = 1 - new_ship.team_id
  #   if self._ai_factory is not None:
  #       ai = self._ai_factory.create_for_ship(new_ship, enemy_team)
  #       self.ai_controllers.append(ai)
  #   else:
  #       raise ValidationException(...)
  # Now:
  enemy_team = 1 - new_ship.team_id
  self.add_ship_mid_battle(new_ship, new_ship.team_id)
  ```
  Note: `add_ship_mid_battle()` already sets `team_id`, appends to `self.ships`, creates AI controller, and (after Phase 3.2) runs full initialization.
- [ ] Remove the now-dead `else: raise ValidationException(...)` block for fighter launch (was lines 504-509)
- [ ] Run new tests from Task 3.3 -- confirm they pass
- [ ] Run all battle engine tests: `pytest tests/unit/simulation/systems/ -v && pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The `new_ship.team_id` is already set to `source_ship.team_id` via the Ship constructor (line 483: `team_id=source_ship.team_id`). `add_ship_mid_battle()` will overwrite it with the same value. The `new_ship.velocity` and `new_ship.angle` assignments (lines 490-494) must remain BEFORE the `add_ship_mid_battle()` call since `_initialize_ship` may use position/velocity for stats.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
