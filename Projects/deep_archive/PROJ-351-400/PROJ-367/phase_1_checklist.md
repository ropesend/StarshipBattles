# Phase 1: Typed ability classes (PodStorage, MultiplexTracking, VehicleStorage; extend VehicleLaunchAbility)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-367 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate `comp.abilities.get(...)` raw-dict reads for the five untyped abilities. `PodStorageAbility.capacity_mass: float`, `MultiplexTrackingAbility.slots: int`, `VehicleStorageAbility.capacity: int` are added; `VehicleLaunchAbility` is extended with `max_launch_mass: float`; `Armor` is consumed via `has_ability` only. Golden snapshot bit-identical for the 7 existing designs; carrier + multiplex designs added.

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State
- [ ] Verify `BUILTIN_HANDLED_ABILITIES` is unchanged from PROJ-360 commit `79e79d9e5` baseline (no other in-flight branch has touched it)
- [ ] `grep -rn 'comp\.abilities\.get' game/simulation/entities/stat_contributors/ game/simulation/entities/ship_stats.py` — capture the EXACT set of call sites this phase must eliminate (expected: 7 sites — `command.py:58`, `defense.py:52`, `launch.py:45,46`, `ship_stats.py:201,207,315`)

---

## Tasks

### Task 1.1: AST regression test (TDD-first) [Simple]
**File:** `tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py -v`

- [ ] Write a test that walks `game/simulation/entities/stat_contributors/*.py` and `game/simulation/entities/ship_stats.py` (Phase 3 path, not Phase 5), parses each via `ast`, and asserts no `Subscript`/`Call` matches `comp.abilities.get("...")`. Allow `comp.has_ability("Armor")` and `comp.get_abilities("...")`.
- [ ] Restrict the `ship_stats.py` walk to the Phase 3 region (`_phase_stats_aggregation`, `_aggregate_cargo_and_pod_abilities`, `_aggregate_resource_abilities`); do not flag Phase 5 functions (`_phase_post_physics_aggregation` etc).
- [ ] Run the test; **confirm it fails** on the current code with the 7 expected sites listed.
- [ ] **Verify:** test fails for the right reason (lists every expected call site).

**Notes:**

### Task 1.2: Add `MultiplexTrackingAbility` typed class [Simple]
**File:** `game/simulation/components/abilities/markers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py -v`

- [ ] Add `class MultiplexTrackingAbility(Ability)` with `slots: int = 0` parsed from data
- [ ] `STAT_BINDINGS = []` (no multiplier — value is read directly)
- [ ] `get_primary_value()` returns `float(self.slots)`
- [ ] `get_ui_rows()` returns `[{'label': 'Targets', 'value': str(self.slots), 'color_hint': HINT_NEUTRAL}]`
- [ ] Add `parse + recalculate + ui_rows` unit tests
- [ ] Verify `ability_manager.py` factory routes the new class — add a registration entry if needed
- [ ] **Verify:** new tests pass; existing tests untouched

**Notes:**

### Task 1.3: Add `VehicleStorageAbility` typed class [Simple]
**File:** `game/simulation/components/abilities/markers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py -v`

- [ ] Add `class VehicleStorageAbility(Ability)` with `capacity: int = 0` parsed from data
- [ ] `STAT_BINDINGS = []`
- [ ] `get_primary_value()` returns `float(self.capacity)`
- [ ] **Data shape: accept BOTH scalar (`50`) and dict (`{"capacity": 50}`) forms.** Production data is scalar; the dict form is a forward-compat hedge.
- [ ] Unit tests for both shapes + factory routing
- [ ] **Verify:** parses with both forms; existing tests untouched

**Notes:**

### Task 1.4: Add `PodStorageAbility` typed class (capacity_mass only) [Medium]
**File:** `game/simulation/components/abilities/markers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py -v`

- [ ] Add `class PodStorageAbility(Ability)` with **single attribute `capacity_mass: float = 0.0`** parsed from data
- [ ] **NO `pod_class` attribute** — verified at `data/components.json:2396-2397` and `docs/systems/ability_reference.md:768-786`
- [ ] `STAT_BINDINGS = []`
- [ ] `get_primary_value()` returns `float(self.capacity_mass)`
- [ ] **Data shape: accept BOTH scalar (`5000`) and dict (`{"capacity_mass": 5000}`) forms.** Reference doc says optional dict format.
- [ ] Unit tests for both shapes + factory routing
- [ ] **Verify:** matches today's dict payload at `data/components.json:2396-2397` exactly

**Notes:**

### Task 1.5: Extend `VehicleLaunchAbility` with `max_launch_mass` [Simple]
**File:** `game/simulation/components/abilities/markers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py -v`

- [ ] In `_parse_attrs`, add `self.max_launch_mass = data.get("max_launch_mass", 0.0)` (after the existing `cycle_time` parse)
- [ ] `STAT_BINDINGS unchanged` — `max_launch_mass` is additive, not modifier-scaled
- [ ] Add unit test asserting `VehicleLaunchAbility` parses `max_launch_mass` from `data/components.json:1241-1245`-style data
- [ ] **Verify:** existing `VehicleLaunchAbility` tests still pass; new attribute has correct default

**Notes:**

### Task 1.6: Migrate `MultiplexTracking` call site [Simple]
**File:** `game/simulation/entities/stat_contributors/command.py`
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_command.py -v` and golden snapshot

- [ ] Replace line 58 `mt = comp.abilities.get("MultiplexTracking", 0)` with `mt = sum(getattr(ab, 'slots', 0) for ab in comp.get_abilities("MultiplexTracking"))`
- [ ] Verify: a component without MultiplexTracking returns 0
- [ ] **Verify:** golden snapshot bit-identical (`pytest tests/unit/simulation/entities/test_ship_stats_golden.py -v`)

**Notes:**

### Task 1.7: Migrate `VehicleLaunch` and `VehicleStorage` call sites [Simple]
**File:** `game/simulation/entities/stat_contributors/launch.py`
**Tests:** golden snapshot

- [ ] Replace `vl = comp.abilities.get("VehicleLaunch", {})` (line 45) with `vl = comp.get_abilities("VehicleLaunch")[0]` (assumes Task 1.5's typed class has `max_launch_mass`)
- [ ] Replace the dict-shape reads `vl.get("max_launch_mass", 0)` with typed `vl.max_launch_mass`
- [ ] Replace `comp.abilities.get("VehicleStorage", 0)` (line 46) with `sum(getattr(ab, 'capacity', 0) for ab in comp.get_abilities("VehicleStorage"))`
- [ ] **Verify:** golden snapshot bit-identical

**Notes:**

### Task 1.8: Migrate `PodStorage` call site (capacity_mass) [Simple]
**File:** `game/simulation/entities/ship_stats.py:315`
**Tests:** golden snapshot

- [ ] Replace the `pod_data = comp.abilities.get("PodStorage")` block (lines 315-319) with iteration over `comp.get_abilities("PodStorage")`, reading `.capacity_mass` typed attr
- [ ] Accumulate into the existing `acc["pod_storage_mass"]` key (will become `accumulator.pod_storage_mass` in Phase 3 — keep the key name stable for now)
- [ ] **Verify:** golden snapshot bit-identical

**Notes:**

### Task 1.9: Migrate `Armor` call sites [Simple]
**Files:** `game/simulation/entities/stat_contributors/defense.py:52`, `game/simulation/entities/ship_stats.py:201,207`
**Tests:** golden snapshot

- [ ] Replace all `comp.abilities.get("Armor", False)` with `comp.has_ability("Armor")`
- [ ] **Verify:** behavior identical (the dict access returned truthy/falsy already)
- [ ] **Verify:** golden snapshot bit-identical

**Notes:**

### Task 1.10: Add carrier + multiplex-equipped golden fixtures [Medium]
**File:** `tests/unit/simulation/entities/test_ship_stats_golden.py` and `test_ship_stats_golden_snapshot.json`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats_golden.py -v`

- [ ] Identify a carrier design (something with `VehicleLaunch` + `VehicleStorage`) — `qs_carrier` if it exists, else add a quickstart design entry
- [ ] Identify a multiplex-equipped design (something with `MultiplexTracking`)
- [ ] Add both to the parametrized fixture list
- [ ] Regenerate snapshot ONCE (via `pytest --update-snapshot` or equivalent), then commit the new entries
- [ ] **Verify:** all 7 original designs still match bit-identical; new designs have stable snapshots
- [ ] **Verify:** the new fixtures actually exercise the typed classes from Tasks 1.2-1.5 (assert non-zero values for the relevant fields)

**Notes:** Closes PROJ-360 review FIND-001 / FIND-005 incidentally.

### Task 1.11: Run AST regression test (it should now PASS) [Simple]
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py -v`

- [ ] Run the Task 1.1 test; confirm it now passes (zero `comp.abilities.get(...)` reads in scope)
- [ ] **Verify:** test would fail again if any of Tasks 1.6–1.9 were reverted

**Notes:**

### Task 1.12: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count = baseline + new tests added; zero regressions
- [ ] **Acceptance:** pass count ≥ baseline + Tasks 1.1/1.2/1.3/1.4/1.5/1.10 test additions

**Notes:**

### Task 1.13: Commit Phase 1 [Simple]

- [ ] `git add` only the files listed in this checklist (verify with `git status --short` first)
- [ ] Commit message: `feat(PROJ-367): Phase 1 — typed ability classes (PodStorage capacity_mass, MultiplexTracking, VehicleStorage; extend VehicleLaunchAbility) + dict-access removal`
- [ ] Sign-off: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Do NOT push
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero `comp.abilities.get(...)` reads in `stat_contributors/` + `ship_stats.py:_phase_stats_aggregation` path (Task 1.11 test passes)
- [ ] `VehicleLaunchAbility` has `max_launch_mass` attribute
- [ ] `PodStorageAbility` has only `capacity_mass` (no `pod_class`)
- [ ] Golden snapshot bit-identical for all 7 original designs; carrier + multiplex designs added with stable snapshots
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
