# Phase 4: Integration test migration (9+ direct `.append`/`.extend` sites in `test_fms_planet_*`)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 4`
> 2. Sharded suite green
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_3 (typed substrate + typed write services + UI reader migration complete)
**Objective:** Migrate the 10 direct `planet.staging_yard.append(dict_literal)` / `.extend(...)` / `.clear()` mutations in the 4 integration test files at the `tests/integration/` root. Either construct typed instances directly or replace direct list mutation with `planet.add_to_staging_yard(typed_instance)` calls.

**File ownership rule:** Phase 4 owns the integration test cluster that was "unowned" in the old PROJ-444..447 partition (Stage 3 preflight §2.2). No production changes in this phase.

**Source-of-truth findings:** Stage 3 preflight §2.2 BLOCKER #2 — see [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

---

## Tasks

### Task 4.1: Migrate `test_fms_planet_recovery.py:59` [Simple]
**File:** `tests/integration/test_fms_planet_recovery.py`
**Tests:** `pytest tests/integration/test_fms_planet_recovery.py -q`

- [x] Locate the `.append(item)` at line 59. Identify what dict shape is being constructed (e.g. `{"name": ..., "vehicle_type": "fighter", "design_id": ..., "mass": ...}`)
- [x] Replace with typed construction:
  ```python
  # OLD:
  planet.staging_yard.append({
      "name": "Mk1 Fighter",
      "vehicle_type": "fighter",
      "design_id": "fighter_01",
      "mass": 10.0,
  })
  # NEW:
  planet.add_to_staging_yard(CarriedVehicle(
      design_id="fighter_01",
      vehicle_type="fighter",
      design_data={"name": "Mk1 Fighter"},
      mass=10.0,
  ))
  ```
- [x] Run focused test; verify green

**Why use `add_to_staging_yard` instead of direct list mutation?** It exercises the public API and the `max_staging_mass` invariant — closer to how production code paths behave.

### Task 4.2: Migrate `test_fms_planet_lay_mines.py:82, 139, 155, 171` [Medium]
**File:** `tests/integration/test_fms_planet_lay_mines.py`
**Tests:** `pytest tests/integration/test_fms_planet_lay_mines.py -q`

- [x] Locate each of the 4 mutation sites at lines 82, 139, 155, 171
- [x] Migrate each — typical shape:
  ```python
  # OLD:
  planet.staging_yard.append(_mine_dict())
  # NEW:
  planet.add_to_staging_yard(CarriedVehicle(
      design_id="mine_01",
      vehicle_type="mine",
      design_data={"name": "Mk1 Mine"},
      mass=5.0,
  ))
  ```
- [x] If `_mine_dict()` is a helper used in multiple places, refactor it to `_mine_typed() -> CarriedVehicle` and update all callers
- [x] Run focused test

### Task 4.3: Migrate `test_fms_planet_launch.py:92, 121, 157, 192` [Medium]
**File:** `tests/integration/test_fms_planet_launch.py`
**Tests:** `pytest tests/integration/test_fms_planet_launch.py -q`

- [x] Locate each of the 4 mutation sites
- [x] Migrate `.append`/`.extend` calls; typical pattern (per Stage 3 preflight):
  ```python
  # OLD:
  planet.staging_yard.extend(_fighter_dict(hp=80 - i * 5) for i in range(3))
  # NEW:
  for i in range(3):
      planet.add_to_staging_yard(CarriedVehicle(
          design_id="fighter_01",
          vehicle_type="fighter",
          design_data={"name": "Mk1 Fighter", "hp": 80 - i * 5},
          mass=10.0,
      ))
  ```
- [x] Run focused test

### Task 4.4: Migrate `test_fms_a_e2e.py:305` [Simple]
**File:** `tests/integration/test_fms_a_e2e.py`
**Tests:** `pytest tests/integration/test_fms_a_e2e.py -q`

- [x] The mutation at line 305 is `.clear()` (per Stage 3 preflight §1.2 table). `.clear()` works on both dict-typed and object-typed lists — it just empties the list. Verify the call site still does what the test intends.
- [x] If the test asserts post-clear behavior (e.g. "after clear, planet has empty staging yard"), the assertion may still work; verify by running the focused test
- [x] Per Stage 3 preflight, this is the most innocuous of the 10 sites

### Task 4.5: Run all integration tests + commit [Medium]
**Tests:** `pytest tests/integration/test_fms_planet_*.py tests/integration/test_fms_a_e2e.py -n 4 -q`

- [x] All 4 integration test files green
- [x] Sharded suite green
- [x] Commit message: `PROJ-450 Phase 4: migrate 10 direct staging-yard mutations in integration tests to typed inputs via public API`

---

## Phase Completion Checklist
- [x] All 10 direct `.append`/`.extend`/`.clear()` sites migrated
- [x] Helper functions (`_mine_dict`, `_fighter_dict`, etc.) refactored to typed equivalents where appropriate
- [x] All 4 integration test files green via direct invocation
- [x] Sharded suite green
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **`tests/integration/test_fms_*` was unowned in PROJ-444..447.** Codex r4 redesign explicitly assigns this cluster to PROJ-450. The Stage 3 preflight §2.2 documented why: it sits between bucket-A (data/facade), bucket-B (engine), and bucket-C (UI).
- **Mutations via `add_to_staging_yard` exercise the public API.** This is the cleaner migration path and aligns with the "saves are disposable + production goes through the public surface" principle.
- **Risk: capacity invariant.** Direct `.append` bypassed `max_staging_mass`. After migration, `add_to_staging_yard` returns `False` on capacity exceeded. Verify the test fixtures don't rely on overflow injection; if they do, set `max_staging_mass=0.0` (unlimited) on the test planet.
- **Helper renaming.** If `_mine_dict()` becomes `_mine_typed()` (returning `CarriedVehicle`), update all callers in the same file. Keep the helper signature pattern (kwargs for variation).
