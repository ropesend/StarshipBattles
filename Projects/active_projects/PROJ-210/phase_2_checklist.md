# Phase 2: Facade Bloat & Pass-Through Elimination

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-210 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Task 2.1 Complete, Tasks 2.2-2.3 Remaining
**Objective:** Remove zero-value pass-through facade methods, expose delegates via properties
**Priority:** Critical — removes ~120 lines of maintenance burden, clarifies API
**Findings:** CQ-01, CQ-02, AR-001, ROF-006, DC-004

---

## Tasks

### Task 2.1: Expose Fleet Delegates as Public Properties [Complex] - COMPLETE
**Findings:** CQ-01 (28 pass-through methods, 120 lines of pure delegation)
**Files:** `game/strategy/data/fleet.py`, all callers of Fleet pass-through methods
**Tests:** `pytest tests/ -n 12`

- [x] Inventory all pass-through methods on Fleet (expected: ~28) — Found 20+
- [x] Expose `_resource_agg` as public `resources` property
- [x] Expose `_capabilities` as public `capabilities` property (already partially done)
- [x] Expose `_battle` as public `battle` property
- [x] Search codebase for all callers of each pass-through method
- [x] Update callers: `fleet.can_use_warp()` → `fleet.capabilities.can_use_warp()`
- [x] Update callers: `fleet.get_fleet_cargo_capacity()` → `fleet.resources.get_fleet_cargo_capacity()`
- [x] Update callers: `fleet.to_battle_ships()` → `fleet.battle.to_battle_ships()`
- [x] Remove all pass-through methods from Fleet class
- [x] Run full suite: `pytest tests/ -n 12` — **12929 passed, 4 failed (pre-existing), 1 skipped**
- [x] Verify: Fleet.py line count reduced by ~120 lines — **320 lines (was 552)**

**Notes:** Task complete. 65+ files modified. All test mock updates done. 4 pre-existing bug_13 failures (missing asset files).

### Task 2.2: Decouple Delegates from Fleet Internals [Medium]
**Findings:** AR-001 (delegates store `_fleet` reference, access internals directly)
**Files:** `fleet_resource_aggregator.py`, `fleet_capability_calculator.py`, `fleet_battle_adapter.py`
**Tests:** `pytest tests/unit/strategy/test_fleet*.py -v`

- [ ] Audit each delegate for `self._fleet.*` access patterns
- [ ] Identify which Fleet attributes each delegate needs
- [ ] Refactor delegates to accept needed data via method parameters instead of `self._fleet`
- [ ] OR: Define a minimal interface/protocol that Fleet implements for delegates
- [ ] Run targeted tests
- [ ] Run full suite: `pytest tests/ -n 12`

**Notes:** Full decoupling may be too aggressive — consider interface-based approach where delegates depend on a protocol, not the concrete Fleet class.

### Task 2.3: Remove Dead Pass-Through _default_formation_positions [Simple]
**Findings:** DC-004
**Files:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v`

- [ ] Verify _default_formation_positions on Fleet is only called through delegate
- [ ] Remove Fleet._default_formation_positions() method
- [ ] Update any callers to use FleetBattleAdapter directly
- [ ] Run tests

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero pass-through facade methods remain on Fleet
- [x] Fleet.py < 350 lines (320 lines)
- [ ] All tests passing (baseline: 12929)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
