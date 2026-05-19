# Phase 1: Migrate `tests/fixtures/strategy_entities.py` (4 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 1`
> 2. Sharded suite must be green (`python Tools/test_sharded/test_sharded.py`)
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0 (audit-verified 4 sites in this file)
**Objective:** Translate the 4 legacy-kwarg sites in `tests/fixtures/strategy_entities.py` to post-PROJ-436 private-field spellings (`_consumable_levels=`, `_cargo_contents=`, `_stockpile=`). Wrappers stay in place; this phase is independently green so it can ship as its own commit.

**File ownership rule:** This project owns wrapper-related test fixtures. Phase 1 touches only one file in `tests/fixtures/`. No `game/` edits.

**Source-of-truth findings:** F-C-020 (4 fixture sites) — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md).

---

## Tasks

### Task 1.1: Verify `create_test_facility` kwarg stays as-is (PlanetaryFacility public field) [Simple]
**File:** `tests/fixtures/strategy_entities.py`
**Tests:** `pytest tests/unit/strategy/data/test_planetary_facility_characterization.py tests/unit/strategy/data/test_facility_resource_tracking.py -n 4 -q`

- [ ] Verify at line 140 the kwarg stays:
  ```python
  consumable_levels={"fuel": 50.0, "energy": 100.0},
  ```
- [ ] **No edit.** `PlanetaryFacility.consumable_levels` is still a public dataclass field at `game/strategy/data/planetary_facility.py:32`; F-A-012's generic consumable API landed but the constructor kwarg was NOT renamed (verified 2026-05-19 codex audit). The PROJ-436 Phase 4f wrapper + property pattern was for Planet + ShipInstance only; PlanetaryFacility never adopted that pattern.
- [ ] Confirm the focused tests pass at current HEAD (they should — no edit was made)
- [ ] Document in `decisions.md` (free-rider with the 2026-05-19 plan-population row): "Facility consumable_levels stays public; F-A-012 constructor-kwarg rename is a separate future project, out of PROJ-449 scope."

**Notes:** This task is a no-op verification step. It remains in the checklist so future agents see the explicit decision rather than wondering why facility line 140 was skipped. The PROJ-449 wrapper-retirement scope is limited to the two classes that actually have wrappers + property clusters: Planet and ShipInstance.

### Task 1.2: Translate `create_test_ship_instance` consumable_levels + cargo_contents kwargs [Simple]
**File:** `tests/fixtures/strategy_entities.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 4 -q`

- [ ] At line 318, change:
  ```python
  consumable_levels={"fuel": 80.0, "energy": 50.0},
  ```
  to:
  ```python
  _consumable_levels={"fuel": 80.0, "energy": 50.0},
  ```
- [ ] At line 320, change:
  ```python
  cargo_contents={"minerals": 10},
  ```
  to:
  ```python
  _cargo_contents={"minerals": 10},
  ```
- [ ] Run the focused tests above; the entire `tests/unit/strategy/ship_instance/` directory should pass (the wrapper still translates `consumable_levels=` / `cargo_contents=` if any downstream caller passes them via this fixture)

### Task 1.3: Translate `create_test_empire` seed-reserve stockpile kwarg [Simple]
**File:** `tests/fixtures/strategy_entities.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py tests/integration/test_empire_resource_aggregation.py -n 4 -q`

- [ ] At line 425, change:
  ```python
  reserve = create_test_planet(
      has_facilities=False,
      has_population=False,
      name="_starting_reserve",
      stockpile=dict(seed_pool),
  )
  ```
  to:
  ```python
  reserve = create_test_planet(
      has_facilities=False,
      has_population=False,
      name="_starting_reserve",
      _stockpile=dict(seed_pool),
  )
  ```
- [ ] Run the focused tests above
- [ ] Verify: `test_empire_resources::test_resource_pool_aggregates_colonies` still reflects the seeded pool

### Task 1.4: Full focused test run + sharded suite [Medium]
**Tests:** `pytest tests/fixtures/ tests/unit/strategy/data/ tests/unit/strategy/ship_instance/ -n 4 -q`, then `python Tools/test_sharded/test_sharded.py`

- [ ] Focused suite green
- [ ] Sharded suite green at the same count as pre-phase
- [ ] If sharded suite regresses, check whether `create_test_planet` accepts `_stockpile=` directly (it doesn't — it calls `Planet(...)`, and Planet's wrapper translates `stockpile=` → `_stockpile=`; if the wrapper does NOT translate `_stockpile=` straight through, fix the fixture helper to use `_stockpile=` only when the call chain supports it)
- [ ] Commit message: `PROJ-449 Phase 1: migrate strategy_entities.py 4 sites to private kwargs`

---

## Phase Completion Checklist
- [ ] All 4 fixture sites migrated to private kwargs
- [ ] Sharded suite green at the pre-phase test count (no regression)
- [ ] Plan.md Quick Status → Complete
- [ ] Plan.md Current State updated; ready for Phase 2

## Notes / Risks / Coordination Touchpoints
- **Wrapper still alive after this phase.** Any downstream caller passing `consumable_levels=` or `stockpile=` directly into `ShipInstance(...)` / `Planet(...)` still works because the wrapper translates. This phase is gating only — it makes the fixture file no longer dependent on the wrapper.
- **No `game/` edits.** Production code untouched.
- **PlanetaryFacility unknown.** If the field rename never happened for PlanetaryFacility (Phase 0 D1 deferred), Task 1.1 may be a no-op — flag in decisions.md and skip cleanly.
- **`create_test_planet` is a helper, not `Planet(...)` directly** — verify it forwards kwargs to `Planet(...)` and that `_stockpile=` survives the forward.
