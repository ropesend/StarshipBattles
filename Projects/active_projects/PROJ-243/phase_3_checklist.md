# Phase 3 Checklist: Fix `add_ship_mid_battle()` and Fighter Launch
**Status:** Complete

## Task 3.1: Write failing tests for mid-battle ship initialization [Medium]
**File:** `tests/unit/simulation/systems/test_add_ship_mid_battle.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v`
- [x] Create test file `tests/unit/simulation/systems/test_add_ship_mid_battle.py`
- [x] Write test: ship added via `add_ship_mid_battle()` has `combat_engine._event_bus` set to `engine.combat_events`
- [x] Write test: ship added via `add_ship_mid_battle()` has had `recalculate_stats()` called
- [x] Write test: ship added via `add_ship_mid_battle()` has had `update_derelict_status()` called
- [x] Write test: ship added via `add_ship_mid_battle()` is registered with aura manager (`aura_manager.register_ship` called)
- [x] Write test: ship added via `add_ship_mid_battle()` receives existing fleet bonuses (check `fleet_attack_bonus`)
- [x] Run tests -- confirm they fail (missing init steps)
**Notes:** All 5 tests failed for the right reasons before implementation. Mock components need is_operational and ability_instances for _scan_ship compatibility.

## Task 3.2: Fix `add_ship_mid_battle()` [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [x] Add `self._initialize_ship(ship)` and `self.aura_manager.register_ship(ship, self.ships)` after AI controller setup
- [x] Run new tests from Task 3.1 -- confirm they pass
- [x] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** All 5 new tests pass, 125 battle controller tests pass.

## Task 3.3: Write failing test for fighter launch using `add_ship_mid_battle()` [Medium]
**File:** `tests/unit/simulation/systems/test_fighter_launch_init.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_fighter_launch_init.py -v`
- [x] Create test file `tests/unit/simulation/systems/test_fighter_launch_init.py`
- [x] Write test: fighter launched via LAUNCH attack type has `combat_engine._event_bus` set
- [x] Write test: fighter launched via LAUNCH attack type is in `engine.ships`
- [x] Write test: fighter launched via LAUNCH attack type has an AI controller in `engine.ai_controllers`
- [x] Run tests -- confirm event bus test fails (fighter launch skips init)
**Notes:** Event bus test failed (None vs CombatEventBus), ships-list and AI tests passed (existing code already does those).

## Task 3.4: Refactor fighter launch to use `add_ship_mid_battle()` [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_fighter_launch_init.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [x] Replace direct ships.append + AI creation block with `self.add_ship_mid_battle(new_ship, new_ship.team_id)`
- [x] Remove the now-dead `else: raise ValidationException(...)` block for fighter launch
- [x] Run new tests from Task 3.3 -- confirm they pass
- [x] Run all battle engine tests: `pytest tests/unit/simulation/systems/ -v && pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** 6 existing tests in test_battle_engine_tick.py needed mock fighter updates (added combat_engine, get_all_components, recalculate_stats, update_derelict_status, fleet_attack/defense_bonus). All 382 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
