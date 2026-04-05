# PROJ-243: Mid-Battle Ship Addition Fix

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-243` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-243 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Declare Fleet Bonus Attributes on Ship | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract `_initialize_ship()` Helper and Add `register_ship()` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix `add_ship_mid_battle()` and Fighter Launch | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Current Phase:** Planning
**Last Action:** Full protocol-compliant plan written with line numbers and code snippets
**Next Action:** Begin Phase 1 — write failing tests for fleet bonus attribute declaration
**Blockers:** None
**Context for Next Agent:** All line numbers verified against current source. No pre-existing test failures related to this area. The `collision.py` getattr fallback (lines 110, 115) is a defensive workaround for the undeclared attributes — once Phase 1 declares them, the getattr is still safe but no longer necessary (out of scope to change).

## Overview
`BattleEngine.add_ship_mid_battle()` (lines 320-355 of `battle_engine.py`) is incomplete compared to `start()` (lines 285-300). Ships added mid-battle (reinforcements, launched fighters) are missing five critical initialization steps: combat event bus wiring, initial component updates, stat recalculation, derelict status check, and aura manager registration. Additionally, `fleet_attack_bonus` and `fleet_defense_bonus` are dynamically set on Ship by `FleetAuraManager._recalculate()` (lines 193-194) but never declared in `Ship.__init__`, which is a latent `AttributeError` if any code reads these attributes before the aura manager runs.

The fighter launch path in `BattleEngine.update()` (lines 478-511) has the same problem — it appends the new ship directly to `self.ships` and creates an AI controller but skips all initialization steps.

## Goals
- **Parity with `start()`:** `add_ship_mid_battle()` runs the same initialization sequence as `start()` for each added ship
- **Declared attributes:** `fleet_attack_bonus` and `fleet_defense_bonus` declared in `Ship.__init__` with default `0.0`
- **Aura re-scan:** New ship's fleet-scope abilities are picked up by `FleetAuraManager`
- **Fighter launch fix:** Fighter launch path uses `add_ship_mid_battle()` instead of duplicating ship-addition logic
- **Full test coverage:** Integration tests prove reinforcement ships fire events, have correct stats, and receive fleet bonuses

## Scope
**In Scope:**
- `game/simulation/systems/battle_engine.py` — extract `_initialize_ship()`, fix `add_ship_mid_battle()`, refactor fighter launch
- `game/simulation/entities/ship.py` — declare `fleet_attack_bonus` and `fleet_defense_bonus`
- `game/simulation/combat/fleet_aura_manager.py` — add `register_ship()` method
- Unit tests for each change
- Integration test proving end-to-end reinforcement correctness

**Out of Scope:**
- `remove_ship()` (already works — removes from ships list and AI controllers)
- `FleetAuraManager` internal aggregation logic (already correct, just needs re-scan trigger)
- `collision.py` getattr fallback cleanup (lines 110, 115 — defensive code, still valid)
- Any UI changes

## Key Files Reference
| Component | File Path | Class/Function | Key Lines |
|-----------|-----------|----------------|-----------|
| Battle engine | `game/simulation/systems/battle_engine.py` | `BattleEngine` | `start()`: 221-306, `add_ship_mid_battle()`: 320-355, `update()` fighter launch: 462-511 |
| Ship entity | `game/simulation/entities/ship.py` | `Ship.__init__` | Lines 34-192 (no fleet_attack/defense_bonus declared) |
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` | `FleetAuraManager` | `initialize()`: 60-91, `_scan_ship()`: 93-113, `_recalculate()`: 121-197 |
| Battle controller | `game/simulation/battle_controller.py` | `BattleController.add_reinforcements()` | Lines 327-372 (calls `engine.add_ship_mid_battle()` at line 362) |
| Collision system | `game/engine/collision.py` | `CollisionSystem.process_beam_attack()` | Lines 110, 115 (getattr fallback for fleet bonuses) |
| Existing edge case tests | `tests/unit/simulation/battle_controller/test_edge_cases.py` | `TestAddReinforcementsEdgeCases` | Lines 82-143 (3 tests, none verify init steps) |
| Test conftest | `tests/unit/simulation/battle_controller/conftest.py` | Fixtures | Lines 1-67 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Declare fleet bonus attributes in `Ship.__init__` with default `0.0` | Dynamically-set attributes are fragile. Declaring makes the contract explicit and prevents `AttributeError` if accessed before aura manager runs. |
| 2026-04-05 | Extract `_initialize_ship()` helper from `start()` | The 5-step init sequence (event bus, component update, recalculate, derelict check) is shared between `start()` and `add_ship_mid_battle()`. Extract once, call from both. DRY. |
| 2026-04-05 | Add `register_ship()` method to `FleetAuraManager` | `initialize()` clears all state and rescans everything — too heavy for adding one ship. A targeted `register_ship()` that scans one ship and triggers `_recalculate()` is the clean solution. |
| 2026-04-05 | Refactor fighter launch to use `add_ship_mid_battle()` | Fighter launch (lines 478-511) duplicates ship-addition logic and skips all init. It should call `add_ship_mid_battle()` to inherit the fix. |
| 2026-04-05 | 4 phases instead of 3 | Separating the helper extraction (Phase 2) from the fix application (Phase 3) keeps each phase focused and testable. Fighter launch refactor folded into Phase 3. |

## Initial Analysis

### What `start()` does (lines 285-300) that `add_ship_mid_battle()` skips:

| Step | `start()` Line(s) | `add_ship_mid_battle()` | Impact of Missing |
|------|-------------------|------------------------|-------------------|
| Wire event bus | 286-287: `s.combat_engine._event_bus = self.combat_events` | **Missing** | Damage/destruction events not logged; UI won't see hits |
| Component update | 292-295: `for comp in s.get_all_components(): if comp.is_active: comp.update()` | **Missing** | RequiresCommandAndControl not checked; components may be incorrectly operational |
| Recalculate stats | 296: `s.recalculate_stats()` | **Missing** | Ship stats stale; max_shields, speed, etc. may be wrong |
| Derelict check | 297: `s.update_derelict_status()` | **Missing** | Ship could be derelict but not flagged |
| Aura registration | 300: `self.aura_manager.initialize(self.ships)` | **Missing** | New ship's fleet-scope abilities not contributing; new ship not receiving fleet bonuses |

### Undeclared attribute problem:

`FleetAuraManager._recalculate()` (lines 193-194 of `fleet_aura_manager.py`) sets:
```python
ship.fleet_attack_bonus = team.get('ToHitAttackModifier', 0.0)
ship.fleet_defense_bonus = team.get('ToHitDefenseModifier', 0.0)
```

But `Ship.__init__` (lines 34-192 of `ship.py`) never declares these attributes. `collision.py` (lines 110, 115) uses `getattr(..., None)` as a defensive workaround:
```python
fleet_atk = getattr(source_ship, 'fleet_attack_bonus', None)
fleet_def = getattr(target, 'fleet_defense_bonus', None)
```

### Fighter launch duplication:

`BattleEngine.update()` (lines 478-511) creates a fighter ship and does:
```python
self.ships.append(new_ship)          # line 497 - direct append
ai = self._ai_factory.create_for_ship(new_ship, enemy_team)  # line 502
self.ai_controllers.append(ai)       # line 503
```

This skips all 5 initialization steps. It should call `add_ship_mid_battle()` instead.

## Swarm Findings Summary

### Architecture
- `BattleEngine` is the simulation core — it must not depend on UI or strategy layers
- Ship initialization is a clear "extract method" opportunity: the 4-line sequence in `start()` (lines 286-297) is a cohesive unit
- `FleetAuraManager.register_ship()` is the natural API: scan one ship, recalculate all bonuses
- Fighter launch in `update()` is a code duplication smell — it reinvents `add_ship_mid_battle()`

### Key Patterns to Reuse
- **Facade/Delegate**: `Ship.combat_engine` is a lazy property (line 253-262) — event bus wiring happens post-construction
- **Two-phase aggregation**: FleetAuraManager already implements intra-group MAX, inter-group SUM (line 168-174)
- **Factory injection**: AI controllers created via `_ai_factory` (PROJ-43 pattern) — both `start()` and `add_ship_mid_battle()` already use this

### Risks Identified
1. **Fighter launch refactor may change timing** — Currently fighter is appended to `self.ships` mid-tick (during attack processing). After refactor, `add_ship_mid_battle()` will also wire event bus + run component update + recalculate stats + register auras during the same tick. This is correct behavior but could surface latent bugs if any component assumes stats are not recalculated mid-tick. **Mitigation:** Integration test verifying fighter works after refactor.
2. **Aura recalculation cost** — `register_ship()` calls `_recalculate(all_ships)` which iterates all providers and ships. For mid-battle additions this is fine (small fleet sizes), but worth noting. **Mitigation:** No action needed — fleet sizes are small.
3. **Test mocks in `test_edge_cases.py`** — Existing tests (lines 82-143) mock `engine.add_ship_mid_battle` entirely. They won't break from our changes, but they also won't verify the new behavior. **Mitigation:** New integration tests in Phase 4 cover real behavior.

---

## Phases

### Phase 1: Declare Fleet Bonus Attributes on Ship [Simple]
**Objective:** Add `fleet_attack_bonus` and `fleet_defense_bonus` to `Ship.__init__` with default `0.0`, eliminating the undeclared attribute risk.
**Status:** Not Started

#### Task 1.1: Write failing tests for attribute existence [Simple]
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [ ] Create test file `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
- [ ] Write test: freshly constructed Ship has `fleet_attack_bonus == 0.0` (use minimal Ship constructor with mock registries)
- [ ] Write test: freshly constructed Ship has `fleet_defense_bonus == 0.0`
- [ ] Write test: `fleet_attack_bonus` can be set to a float and read back
- [ ] Write test: `fleet_defense_bonus` can be set to a float and read back
- [ ] Run tests — confirm they fail with `AttributeError` (attributes not declared yet)
**Notes:**

#### Task 1.2: Declare attributes in Ship.__init__ [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [ ] Add the following two lines after line 165 (`self.baseline_to_hit_offense: float = 0.0`):
  ```python
  self.fleet_attack_bonus: float = 0.0   # Set by FleetAuraManager._recalculate()
  self.fleet_defense_bonus: float = 0.0  # Set by FleetAuraManager._recalculate()
  ```
- [ ] Run new tests — confirm they pass
- [ ] Run existing ship tests: `pytest tests/unit/simulation/entities/ -v`
**Notes:**

#### Task 1.3: Verify no regressions [Simple]
**Tests:** `pytest tests/unit/simulation/ -v`
- [ ] Run: `pytest tests/unit/simulation/ -v` — all pass
- [ ] Confirm `FleetAuraManager._recalculate()` still sets the attributes correctly (no behavior change — it overwrites declared defaults)
**Notes:**

---

### Phase 2: Extract `_initialize_ship()` Helper and Add `register_ship()` [Medium]
**Objective:** Create the reusable helper methods that Phase 3 will use to fix `add_ship_mid_battle()`.
**Status:** Not Started

#### Task 2.1: Write failing tests for `_initialize_ship()` [Medium]
**File:** `tests/unit/simulation/systems/test_battle_engine_init_ship.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_battle_engine_init_ship.py`
- [ ] Write test: `_initialize_ship(ship)` wires `ship.combat_engine._event_bus` to `self.combat_events`
- [ ] Write test: `_initialize_ship(ship)` calls `comp.update()` for all active components
- [ ] Write test: `_initialize_ship(ship)` calls `ship.recalculate_stats()`
- [ ] Write test: `_initialize_ship(ship)` calls `ship.update_derelict_status()`
- [ ] Run tests — confirm they fail (`_initialize_ship` does not exist yet)
**Notes:** Use mock ships with mock components. Verify via `assert_called_once` on mocks.

#### Task 2.2: Extract `_initialize_ship()` from `start()` [Simple]
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
- [ ] Run new tests from Task 2.1 — confirm they pass
- [ ] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The two separate `for s in self.ships` loops (lines 286-287 and 292-297) collapse into one loop calling `_initialize_ship(s)`. This is safe because event bus wiring has no dependency on other ships' event buses.

#### Task 2.3: Write failing test for `FleetAuraManager.register_ship()` [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_register.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_register.py -v`
- [ ] Create test file `tests/unit/simulation/combat/test_fleet_aura_register.py`
- [ ] Write test: `register_ship(ship, all_ships)` calls `_scan_ship(ship)` (new ship's abilities scanned)
- [ ] Write test: `register_ship(ship, all_ships)` calls `_recalculate(all_ships)` (bonuses updated)
- [ ] Write test: after `register_ship()`, the new ship has correct `fleet_attack_bonus`
- [ ] Write test: after `register_ship()`, existing ships receive bonuses from the new ship's fleet-scope abilities
- [ ] Run tests — confirm they fail (`register_ship` does not exist yet)
**Notes:** Use mock ships with mock abilities for unit tests. Integration test in Phase 4 covers real components.

#### Task 2.4: Add `register_ship()` to FleetAuraManager [Simple]
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
- [ ] Run new tests from Task 2.3 — confirm they pass
- [ ] Run existing aura tests (if any): `pytest tests/unit/simulation/combat/ -v`
**Notes:**

---

### Phase 3: Fix `add_ship_mid_battle()` and Fighter Launch [Medium]
**Objective:** Apply the helpers from Phase 2 to fix both the reinforcement path and the fighter launch path.
**Status:** Not Started

#### Task 3.1: Write failing tests for mid-battle ship initialization [Medium]
**File:** `tests/unit/simulation/systems/test_add_ship_mid_battle.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_add_ship_mid_battle.py`
- [ ] Write test: ship added via `add_ship_mid_battle()` has `combat_engine._event_bus` set to `engine.combat_events`
- [ ] Write test: ship added via `add_ship_mid_battle()` has had `recalculate_stats()` called
- [ ] Write test: ship added via `add_ship_mid_battle()` has had `update_derelict_status()` called
- [ ] Write test: ship added via `add_ship_mid_battle()` is registered with aura manager (`aura_manager.register_ship` called)
- [ ] Write test: ship added via `add_ship_mid_battle()` receives existing fleet bonuses (check `fleet_attack_bonus`)
- [ ] Run tests — confirm they fail (missing init steps)
**Notes:** These tests use a real or minimally-mocked `BattleEngine` with mock ships. Verify `_initialize_ship` is called by checking its side effects.

#### Task 3.2: Fix `add_ship_mid_battle()` [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_add_ship_mid_battle.py -v && pytest tests/unit/simulation/battle_controller/ -v`
- [ ] Add two lines after the AI controller setup block (after line 352, before the logger.log call at line 354):
  ```python
  # Initialize ship (event bus, components, stats, derelict check)
  self._initialize_ship(ship)
  # Register with aura manager (scan abilities, recalculate bonuses)
  self.aura_manager.register_ship(ship, self.ships)
  ```
- [ ] Run new tests from Task 3.1 — confirm they pass
- [ ] Run existing battle controller tests: `pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The `self.ships.append(ship)` at line 337 happens before the AI block, so `self.ships` already contains the new ship when `register_ship(ship, self.ships)` is called.

#### Task 3.3: Write failing test for fighter launch using `add_ship_mid_battle()` [Medium]
**File:** `tests/unit/simulation/systems/test_fighter_launch_init.py` (new)
**Tests:** `pytest tests/unit/simulation/systems/test_fighter_launch_init.py -v`
- [ ] Create test file `tests/unit/simulation/systems/test_fighter_launch_init.py`
- [ ] Write test: fighter launched via LAUNCH attack type has `combat_engine._event_bus` set
- [ ] Write test: fighter launched via LAUNCH attack type is in `engine.ships`
- [ ] Write test: fighter launched via LAUNCH attack type has an AI controller in `engine.ai_controllers`
- [ ] Run tests — confirm event bus test fails (fighter launch skips init)
**Notes:** This requires setting up a LAUNCH attack in `just_fired_projectiles` and calling `engine.update()`.

#### Task 3.4: Refactor fighter launch to use `add_ship_mid_battle()` [Medium]
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
- [ ] Run new tests from Task 3.3 — confirm they pass
- [ ] Run all battle engine tests: `pytest tests/unit/simulation/systems/ -v && pytest tests/unit/simulation/battle_controller/ -v`
**Notes:** The `new_ship.team_id` is already set to `source_ship.team_id` via the Ship constructor (line 483: `team_id=source_ship.team_id`). `add_ship_mid_battle()` will overwrite it with the same value. The `new_ship.velocity` and `new_ship.angle` assignments (lines 490-494) must remain BEFORE the `add_ship_mid_battle()` call since `_initialize_ship` may use position/velocity for stats.

---

### Phase 4: Integration Tests [Simple]
**Objective:** End-to-end test proving reinforcement ships and fighters work correctly in a running battle with real (not mocked) components.
**Status:** Not Started

#### Task 4.1: Write integration test for reinforcements [Medium]
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

#### Task 4.2: Final verification [Simple]
**Tests:** `python scripts/test_sharded.py`
- [ ] Run full test suite: `python scripts/test_sharded.py` — all pass
- [ ] Grep for any other callers of `add_ship_mid_battle`: `grep -rn "add_ship_mid_battle" game/` — verify all callers benefit
- [ ] Grep for any other direct `self.ships.append` in `battle_engine.py` — verify no other uninitialized additions remain
- [ ] Verify `start()` still calls `self.aura_manager.initialize(self.ships)` (line 300) — this is correct for battle start (full init), not `register_ship()`
- [ ] Update docs if battle engine lifecycle is documented in `docs/`
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python scripts/test_sharded.py` — establish baseline

### After Each Phase
- [ ] Run targeted tests for changed files
- [ ] Run `pytest tests/unit/simulation/battle_controller/ -v` — existing battle tests pass
- [ ] Run `pytest tests/unit/simulation/systems/ -v` — battle engine tests pass

### Final Verification
- [ ] `pytest tests/unit/simulation/ -v` — all pass
- [ ] `pytest tests/integration/simulation/ -v` — all pass
- [ ] `python scripts/test_sharded.py` — full suite green
- [ ] `add_ship_mid_battle()` calls `_initialize_ship()` and `aura_manager.register_ship()`
- [ ] `start()` uses `_initialize_ship()` in its per-ship loop (DRY)
- [ ] Fighter launch calls `add_ship_mid_battle()` instead of duplicating logic
- [ ] `Ship.__init__` declares `fleet_attack_bonus` and `fleet_defense_bonus` with `0.0` default
- [ ] `FleetAuraManager.register_ship()` exists and is called for mid-battle additions
- [ ] No direct `self.ships.append()` in fighter launch path (uses `add_ship_mid_battle()` instead)
- [ ] Docs updated if battle engine lifecycle is documented

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing (`python scripts/test_sharded.py`)
- [ ] No regressions in existing battle controller tests
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
