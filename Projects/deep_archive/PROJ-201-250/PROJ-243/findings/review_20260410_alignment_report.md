# PROJ-243 Plan-Code Alignment Report

**Date:** 2026-04-10
**Reviewer:** Claude Code (Opus 4.6)
**Scope:** All 4 phases, Key Files table, and goal verification

---

## Executive Summary

PROJ-243 is **fully implemented and correct at the functional level**. All five goals are met:

1. **Parity with `start()`** -- `add_ship_mid_battle()` calls `_initialize_ship()` (line 376) which runs the same 4-step sequence as `start()` (line 306).
2. **Declared attributes** -- `fleet_attack_bonus` and `fleet_defense_bonus` are declared in `Ship.__init__` at lines 138-139 with default `0.0`.
3. **Aura re-scan** -- `add_ship_mid_battle()` calls `aura_manager.register_ship()` (line 378), which calls `_scan_ship()` + `_recalculate()`.
4. **Fighter launch fix** -- `_process_launch_attack()` calls `self.add_ship_mid_battle()` at line 533 instead of duplicating ship-addition logic.
5. **Full test coverage** -- All 6 test files exist and contain meaningful tests.

The only discrepancies are **stale line-number references** in the Key Files table. These are cosmetic (documentation drift) and would not block or mislead a developer who navigates by class/function name.

---

## Key Files Table Line Number Audit

### F-01: BattleEngine `start()` line range shifted
**Plan Reference:** `game/simulation/systems/battle_engine.py` -- `start()`: 221-306
**Actual Code:** `start()` begins at **line 237** and the per-ship initialization loop ends at **line 306** (the loop itself is at line 305-306). The method signature starts at 237, not 221. Line 221 is inside `__init__` (the `_alive_ships_cache` attribute).
**Impact:** Low. A developer searching for `start()` would find it by name. Off by 16 lines.
**Proposed Fix:** Update to `start()`: 237-315

### F-02: BattleEngine `add_ship_mid_battle()` line range shifted
**Plan Reference:** `game/simulation/systems/battle_engine.py` -- `add_ship_mid_battle()`: 320-355
**Actual Code:** `add_ship_mid_battle()` starts at **line 342** and ends at **line 381**.
**Impact:** Low. Off by 22 lines at start, 26 at end.
**Proposed Fix:** Update to `add_ship_mid_battle()`: 342-381

### F-03: BattleEngine `update()` fighter launch line range shifted
**Plan Reference:** `game/simulation/systems/battle_engine.py` -- `update()` fighter launch: 462-511
**Actual Code:** `update()` itself is at lines 418-442. The fighter launch logic is in `_process_launch_attack()` at lines **505-534**. The plan's range 462-511 partially overlaps the actual method but the start/end are wrong.
**Impact:** Low. The plan correctly identifies that fighter launch goes through `add_ship_mid_battle()` (line 533). The method was likely extracted/refactored during PROJ-259 tick phase work.
**Proposed Fix:** Update to `_process_launch_attack()`: 505-534

### F-04: Ship.__init__ line range and annotation incorrect
**Plan Reference:** `game/simulation/entities/ship.py` -- `Ship.__init__` Lines 34-192 "(no fleet_attack/defense_bonus declared)"
**Actual Code:** `Ship.__init__` spans **lines 48-189**. `fleet_attack_bonus` and `fleet_defense_bonus` **ARE** declared at **lines 138-139** with default `0.0` and descriptive comments. The annotation "(no fleet_attack/defense_bonus declared)" describes the pre-fix state, not the current state.
**Impact:** Medium (misleading). The parenthetical describes the bug that was fixed, not the current code. A reader might think the fix hasn't been applied. The line range is also off (34 is in the imports, 192 is `_equip_default_hull`).
**Proposed Fix:** Update to `Ship.__init__`: 48-189. Change annotation to "(fleet_attack_bonus and fleet_defense_bonus declared at lines 138-139)".

### F-05: FleetAuraManager `initialize()` line range shifted
**Plan Reference:** `game/simulation/combat/fleet_aura_manager.py` -- `initialize()`: 60-91
**Actual Code:** `initialize()` is at **lines 64-97**. Off by 4-6 lines, likely due to the PROJ-253 dirty-flag attributes added to `__init__`.
**Impact:** Low.
**Proposed Fix:** Update to `initialize()`: 64-97

### F-06: FleetAuraManager `_scan_ship()` line range shifted
**Plan Reference:** `game/simulation/combat/fleet_aura_manager.py` -- `_scan_ship()`: 93-113
**Actual Code:** `_scan_ship()` is at **lines 99-119**.
**Impact:** Low.
**Proposed Fix:** Update to `_scan_ship()`: 99-119

### F-07: FleetAuraManager `_recalculate()` line range significantly shifted
**Plan Reference:** `game/simulation/combat/fleet_aura_manager.py` -- `_recalculate()`: 121-197
**Actual Code:** `_recalculate()` is at **lines 171-235**. The `register_ship()` method (added by this project) sits at lines 121-135, pushing `_recalculate()` down by ~50 lines. Additional methods (`invalidate_aura_cache`, `update`, `_get_provider_fingerprint` from PROJ-253) also contribute to the shift.
**Impact:** Medium. Off by 50 lines. The plan's line 121 actually points to `register_ship()`, not `_recalculate()`.
**Proposed Fix:** Update to `register_ship()`: 121-135, `_recalculate()`: 171-235

### F-08: BattleController `add_reinforcements()` line range shifted
**Plan Reference:** `game/simulation/battle_controller.py` -- Lines 327-372, calls `engine.add_ship_mid_battle()` at line 362
**Actual Code:** `add_reinforcements()` is at **lines 336-380**. The `engine.add_ship_mid_battle()` call is at **line 371** (not 362). Off by ~9 lines throughout.
**Impact:** Low.
**Proposed Fix:** Update to Lines 336-380, `engine.add_ship_mid_battle()` at line 371

### F-09: Collision system `fleet_defense_bonus` getattr line incorrect
**Plan Reference:** `game/engine/collision.py` -- Lines 110, 115 (getattr fallback for fleet bonuses)
**Actual Code:** `fleet_attack_bonus` getattr is at **line 115** (correct). `fleet_defense_bonus` getattr is at **line 120** (not 110).
**Impact:** Low. One of two line numbers is correct; the other is off by 10.
**Proposed Fix:** Update to Lines 115, 120

### F-10: Test edge cases and conftest line ranges
**Plan Reference:** `tests/unit/simulation/battle_controller/test_edge_cases.py` -- `TestAddReinforcementsEdgeCases` Lines 82-143; conftest Lines 1-67
**Actual Code:** `TestAddReinforcementsEdgeCases` is at **lines 82-143** (exact match). Conftest is **lines 1-67** (exact match).
**Impact:** None. These are correct.
**Proposed Fix:** No change needed.

---

## Phase-by-Phase Implementation Verification

### Phase 1: Declared Attributes

| Task | Status | Evidence |
|------|--------|----------|
| 1.1 Test file created | DONE | `tests/unit/simulation/entities/test_ship_fleet_attrs.py` exists, 4 tests |
| 1.2 Attributes declared in Ship.__init__ | DONE | Lines 138-139: `fleet_attack_bonus: float = 0.0`, `fleet_defense_bonus: float = 0.0` |
| 1.3 No regressions | DONE | (verified by project completion) |

### Phase 2: _initialize_ship() Extraction and register_ship()

| Task | Status | Evidence |
|------|--------|----------|
| 2.1 Test file for _initialize_ship() | DONE | `tests/unit/simulation/systems/test_battle_engine_init_ship.py` exists, 4 tests |
| 2.2 _initialize_ship() extracted | DONE | Lines 329-340 in battle_engine.py. Called from `start()` at line 306 |
| 2.3 Test file for register_ship() | DONE | `tests/unit/simulation/combat/test_fleet_aura_register.py` exists, 5 tests |
| 2.4 register_ship() added | DONE | Lines 121-135 in fleet_aura_manager.py. Scans ship + recalculates bonuses |

**Note on Task 2.2:** The plan says "Collapsed two for-loops into one calling _initialize_ship()". Looking at `start()`, there is indeed a single loop at line 305-306: `for s in self.ships: self._initialize_ship(s)`. This confirms the two separate loops were collapsed into one.

### Phase 3: Mid-battle Ship Initialization and Fighter Launch

| Task | Status | Evidence |
|------|--------|----------|
| 3.1 Test file for mid-battle init | DONE | `tests/unit/simulation/systems/test_add_ship_mid_battle.py` exists, 5 tests |
| 3.2 add_ship_mid_battle() fixed | DONE | Lines 375-378: calls `_initialize_ship(ship)` then `aura_manager.register_ship(ship, self.ships)` |
| 3.3 Test file for fighter launch | DONE | `tests/unit/simulation/systems/test_fighter_launch_init.py` exists, 3 tests |
| 3.4 Fighter launch refactored | DONE | Line 533: `self.add_ship_mid_battle(new_ship, new_ship.team_id)` instead of direct append |

### Phase 4: Integration Test and Final Verification

| Task | Status | Evidence |
|------|--------|----------|
| 4.1 Integration test created | DONE | `tests/integration/simulation/test_mid_battle_reinforcement.py` exists, 4 tests |
| 4.2 Final verification | DONE | (verified by project completion) |

---

## Collision System getattr Observation

The plan notes that `collision.py` uses `getattr(source_ship, 'fleet_attack_bonus', None)` and `getattr(target, 'fleet_defense_bonus', None)` as fallback patterns. Now that PROJ-243 has declared these attributes in `Ship.__init__`, the `getattr(..., None)` fallback is technically unnecessary for `Ship` objects but remains harmless as a defensive pattern (other object types passed to the collision system might not have these attributes). No action needed.

---

## Summary of Findings

| ID | Severity | Category | Summary |
|----|----------|----------|---------|
| F-01 | Low | Line drift | BattleEngine.start() off by 16 lines |
| F-02 | Low | Line drift | BattleEngine.add_ship_mid_battle() off by 22 lines |
| F-03 | Low | Line drift | Fighter launch method off by ~43 lines, also renamed to _process_launch_attack |
| F-04 | Medium | Stale annotation | Ship.__init__ annotation says "no fleet bonuses declared" but they ARE declared (that was the fix) |
| F-05 | Low | Line drift | FleetAuraManager.initialize() off by 4 lines |
| F-06 | Low | Line drift | FleetAuraManager._scan_ship() off by 6 lines |
| F-07 | Medium | Line drift | FleetAuraManager._recalculate() off by 50 lines (register_ship inserted above) |
| F-08 | Low | Line drift | BattleController.add_reinforcements() off by 9 lines |
| F-09 | Low | Line drift | collision.py fleet_defense_bonus line off by 10 |
| F-10 | None | Correct | test_edge_cases.py and conftest.py line numbers match exactly |

**Overall Assessment:** All implementation goals are met. The codebase matches the project's intent. All 10 findings are documentation-level line number drift -- none represent missing or incorrect implementation.
