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
| 1. Declare Fleet Bonus Attributes on Ship | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract `_initialize_ship()` Helper and Add `register_ship()` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix `add_ship_mid_battle()` and Fighter Launch | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration Tests | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-10
**Current Phase:** Complete
**Last Agent Action:** Project review (Protocol 09) completed — 17 findings addressed, Key Files table updated, decisions.md populated, design.md annotated, minor observations recorded. PROJ-268 filed for remove_ship() aura cleanup.
**Next Action:** Archive project. Separately, implement PROJ-268 (FleetAuraManager.unregister_ship).
**Blockers:** None
**Context for Next Agent:** Plan reviewed and updated on 2026-04-10. All references verified against current codebase. Key changes: line numbers corrected for post-PROJ-253/259 drift, Ship.__init__ annotation updated to reflect fix, decisions.md backfilled. One scope gap identified → PROJ-268.

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
| Battle engine | `game/simulation/systems/battle_engine.py` | `BattleEngine` | `start()`: 237-315, `_initialize_ship()`: 329-340, `add_ship_mid_battle()`: 342-381, `_process_launch_attack()` fighter launch: 505-534 |
| Ship entity | `game/simulation/entities/ship.py` | `Ship.__init__` | Lines 48-189 (fleet_attack_bonus and fleet_defense_bonus declared at lines 138-139) |
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` | `FleetAuraManager` | `initialize()`: 64-97, `_scan_ship()`: 99-119, `register_ship()`: 121-135, `_recalculate()`: 171-235 |
| Battle controller | `game/simulation/battle_controller.py` | `BattleController.add_reinforcements()` | Lines 336-380 (calls `engine.add_ship_mid_battle()` at line 371) |
| Collision system | `game/engine/collision.py` | `CollisionSystem.process_beam_attack()` | Lines 115, 120 (getattr fallback for fleet bonuses) |
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
**Status:** Complete

#### Task 1.1: Write failing tests for attribute existence [Simple]
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [x] Create test file `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
- [x] Write test: freshly constructed Ship has `fleet_attack_bonus == 0.0` (use minimal Ship constructor with mock registries)
- [x] Write test: freshly constructed Ship has `fleet_defense_bonus == 0.0`
- [x] Write test: `fleet_attack_bonus` can be set to a float and read back
- [x] Write test: `fleet_defense_bonus` can be set to a float and read back
- [x] Run tests — confirm they fail with `AttributeError` (attributes not declared yet)
**Notes:** Tests confirmed to fail with AttributeError before implementation.

#### Task 1.2: Declare attributes in Ship.__init__ [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py -v`
- [x] Add the following two lines after line 165 (`self.baseline_to_hit_offense: float = 0.0`):
  ```python
  self.fleet_attack_bonus: float = 0.0   # Set by FleetAuraManager._recalculate()
  self.fleet_defense_bonus: float = 0.0  # Set by FleetAuraManager._recalculate()
  ```
- [x] Run new tests — confirm they pass
- [x] Run existing ship tests: `pytest tests/unit/simulation/entities/ -v`
**Notes:** All 458 entity tests pass.

#### Task 1.3: Verify no regressions [Simple]
**Tests:** `pytest tests/unit/simulation/ -v`
- [x] Run: `pytest tests/unit/simulation/ -v` — all pass
- [x] Confirm `FleetAuraManager._recalculate()` still sets the attributes correctly (no behavior change — it overwrites declared defaults)
**Notes:** 2775 tests pass.

---

### Phase 2: Extract `_initialize_ship()` Helper and Add `register_ship()` [Medium]
**Objective:** Create the reusable helper methods that Phase 3 will use to fix `add_ship_mid_battle()`.
**Status:** Complete

#### Task 2.1: Write failing tests for `_initialize_ship()` [Medium]
- [x] All subtasks complete
**Notes:** 4 tests, all failed with AttributeError before implementation.

#### Task 2.2: Extract `_initialize_ship()` from `start()` [Simple]
- [x] All subtasks complete
**Notes:** Collapsed two for-loops into one calling _initialize_ship(). 374 tests pass.

#### Task 2.3: Write failing test for `FleetAuraManager.register_ship()` [Simple]
- [x] All subtasks complete
**Notes:** 5 tests (incl. dead ship edge case), all failed before implementation.

#### Task 2.4: Add `register_ship()` to FleetAuraManager [Simple]
- [x] All subtasks complete
**Notes:** All 173 combat tests pass.

---

### Phase 3: Fix `add_ship_mid_battle()` and Fighter Launch [Medium]
**Objective:** Apply the helpers from Phase 2 to fix both the reinforcement path and the fighter launch path.
**Status:** Complete

#### Task 3.1: Write failing tests for mid-battle ship initialization [Medium]
- [x] All subtasks complete
**Notes:** 5 tests, all failed before implementation. Mock components needed is_operational and ability_instances for _scan_ship compatibility.

#### Task 3.2: Fix `add_ship_mid_battle()` [Simple]
- [x] All subtasks complete
**Notes:** Added _initialize_ship() + aura_manager.register_ship() after AI controller setup.

#### Task 3.3: Write failing test for fighter launch using `add_ship_mid_battle()` [Medium]
- [x] All subtasks complete
**Notes:** 3 tests, event bus test failed before implementation as expected.

#### Task 3.4: Refactor fighter launch to use `add_ship_mid_battle()` [Medium]
- [x] All subtasks complete
**Notes:** Replaced direct ships.append + AI block with add_ship_mid_battle(). Updated 6 existing mock fighters in test_battle_engine_tick.py.

---

### Phase 4: Integration Tests [Simple]
**Objective:** End-to-end test proving reinforcement ships and fighters work correctly in a running battle with real (not mocked) components.
**Status:** Complete

#### Task 4.1: Write integration test for reinforcements [Medium]
- [x] All subtasks complete
**Notes:** 4 integration tests: full initialization, fleet bonus propagation, combat participation, derelict detection. All pass with real objects.

#### Task 4.2: Final verification [Simple]
- [x] All subtasks complete
**Notes:** 14370 passed, 2 skipped, 0 failures. Docs updated. No uninitialized ship additions remain.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `python Tools/test_sharded/test_sharded.py` — establish baseline

### After Each Phase
- [x] Run targeted tests for changed files
- [x] Run `pytest tests/unit/simulation/battle_controller/ -v` — existing battle tests pass
- [x] Run `pytest tests/unit/simulation/systems/ -v` — battle engine tests pass

### Final Verification
- [x] `pytest tests/unit/simulation/ -v` — all pass
- [x] `pytest tests/integration/simulation/ -v` — all pass
- [x] `python Tools/test_sharded/test_sharded.py` — full suite green (14370 passed)
- [x] `add_ship_mid_battle()` calls `_initialize_ship()` and `aura_manager.register_ship()`
- [x] `start()` uses `_initialize_ship()` in its per-ship loop (DRY)
- [x] Fighter launch calls `add_ship_mid_battle()` instead of duplicating logic
- [x] `Ship.__init__` declares `fleet_attack_bonus` and `fleet_defense_bonus` with `0.0` default
- [x] `FleetAuraManager.register_ship()` exists and is called for mid-battle additions
- [x] No direct `self.ships.append()` in fighter launch path (uses `add_ship_mid_battle()` instead)
- [x] Docs updated if battle engine lifecycle is documented

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-04-10 | 17 findings: 10 stale refs, 1 scope gap (High), 2 doc gaps, 4 minor observations | Line refs updated, decisions.md populated, design.md annotated, PROJ-268 filed for remove_ship() aura cleanup, minor observations recorded in decisions.md |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All tests passing (14370 passed, 2 skipped, 0 failures)
- [x] No regressions in existing battle controller tests (125 pass)
- [x] Audit passed (review 2026-04-10: no blocking issues, 1 scope gap → PROJ-268)
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
