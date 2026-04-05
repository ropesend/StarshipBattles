# Phase 4 Checklist: Integration Tests
**Status:** Not Started

## Task 4.1: Write integration test for reinforcements [Medium]
**File:** `tests/integration/simulation/test_mid_battle_reinforcement.py` (new)
**Tests:** `pytest tests/integration/simulation/test_mid_battle_reinforcement.py -v`
- [ ] Create test file `tests/integration/simulation/test_mid_battle_reinforcement.py`
- [ ] Set up a minimal battle with real Ship objects and a real BattleEngine (use test ship data from `simulation_tests/data/ships/`)
- [ ] Run N ticks to establish baseline
- [ ] Add reinforcement ship via `engine.add_ship_mid_battle()`
- [ ] Assert: reinforcement ship's `combat_engine._event_bus is engine.combat_events`
- [ ] Assert: reinforcement ship's stats are populated (e.g., `ship.mass > 0`, `ship.max_hp > 0`)
- [ ] Assert: if reinforcement has a fleet-scope ability, teammates' `fleet_attack_bonus` or `fleet_defense_bonus` reflects it
- [ ] Assert: reinforcement receives existing fleet bonuses from teammates
- [ ] Run more ticks and assert: reinforcement fires weapons (check `total_shots_fired > 0` or events in combat bus)
**Notes:** This is the key test proving the entire fix works end-to-end with real objects.

## Task 4.2: Final verification [Simple]
**Tests:** `python scripts/test_sharded.py`
- [ ] Run full test suite: `python scripts/test_sharded.py` -- all pass
- [ ] Grep for any other callers of `add_ship_mid_battle`: `grep -rn "add_ship_mid_battle" game/` -- verify all callers benefit
- [ ] Grep for any other direct `self.ships.append` in `battle_engine.py` -- verify no other uninitialized additions remain
- [ ] Verify `start()` still calls `self.aura_manager.initialize(self.ships)` (line 300) -- this is correct for battle start (full init), not `register_ship()`
- [ ] Update docs if battle engine lifecycle is documented in `docs/`
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
