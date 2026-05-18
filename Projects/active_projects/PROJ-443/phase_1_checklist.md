# Phase 1: Triage `test_cargo_tracking.py`

**Status:** Complete (2026-05-17, HEAD pending commit)
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):** `tests/unit/strategy/data/test_cargo_tracking.py`

**Objective:** Triage the 30 failures in `test_cargo_tracking.py`. Classify each: (a) now passing; (b) test assertion wrong against current contract — fix test; (c) test exposes real bug — fix production; (d) obsolete — delete with rationale in `decisions.md`.

**Result:** All 30 failures classified as **(b)**. No production bugs surfaced; no obsolete tests. Single commit covering both clusters because the fix is one logical change (fixture priming) and one mechanical sweep (`.resources.` prefix).

---

## Tasks

### 1a — Capture current failure list and root-cause [Simple]

- [x] Re-ran `pytest tests/unit/strategy/data/test_cargo_tracking.py -q --no-header --tb=short`; 30F/2P matches Phase 0 inventory.
- [x] Two distinct root causes identified:
  - **Cluster A (29/30)**: `ValueError: ShipInstance requires registries for stats calculation` raised from `ShipStatsCache.calculate` ([game/strategy/data/ship_stats_cache.py:41-45](../../../../game/strategy/data/ship_stats_cache.py#L41-L45)). Tests construct `ShipInstance(...)` directly via `__init__` (no registries) then call cargo-capacity methods which route through `_cargo_mgr.get_cargo_capacity` → `ship.get_calculated_stats()` → `ShipStatsCache.calculate(ship)`. The fixtures had a `mock_registries` fixture parameter that was never actually wired to the instance via `set_registries(...)`. Tests predate PROJ-211's mandatory-registry contract.
  - **Cluster B (5/30, overlapping with A)**: `AttributeError: 'Fleet' object has no attribute 'get_fleet_cargo_X'`. Per [game/strategy/data/fleet.py:281-282](../../../../game/strategy/data/fleet.py#L281-L282) ("PROJ-210 Phase 2 removed pass-through methods. Use fleet.capabilities.\*, fleet.resources.\*, fleet.battle.\* directly."), the four Fleet cargo methods moved onto `FleetConsumableAggregator` accessible via `fleet.resources`. The one already-passing Fleet test (`test_fleet_load_to_empty_fleet`) uses the canonical `fleet.resources.load_cargo_to_fleet(...)` form, confirming the migration target.

### 1b — Apply fixes [Simple]

- [x] Added `_prime_stats(ship)` module-level helper that hydrates `ship._cached_stats` from `ship.design_data['expected_stats']`, so `ShipStatsCache.get_or_compute` returns the cached dict and skips `calculate`. The cargo manager only reads `stats['cargo_storage']`, so a minimal expected_stats dict satisfies all paths under test.
- [x] Updated both fixtures (`ship_with_cargo_capacity`, `ship_without_cargo`) and the inline `ship2` / `test_fleet_load_to_empty_fleet` ship to prime stats before use.
- [x] Updated `test_ship_instance_cargo_serialization_roundtrip` to re-prime the `restored` instance returned by `from_dict` (which carries `design_data` but starts with `_cached_stats=None`).
- [x] Updated `test_clone_preserves_cargo` to re-prime the cloned instance (clone path uses the dataclass `__init__`; `_cached_stats` is `init=False` and defaults to `None`).
- [x] Swept the 5 Fleet pass-through method calls to use `fleet.resources.<method>` prefix: `get_fleet_cargo_capacity`, `get_fleet_cargo_current`, `load_cargo_to_fleet`, `unload_cargo_from_fleet`.
- [x] Removed unused `mock_registries` fixture (the `unittest.mock` import is no longer needed; trimmed).
- [x] Updated class docstrings on `TestFleetCargoCapacity` / `TestFleetLoadCargo` / `TestFleetUnloadCargo` / `TestFleetCargoCurrent` to reference the `.resources.` prefix.

### 1c — Verify and commit [Simple]

- [x] `python -m pytest tests/unit/strategy/data/test_cargo_tracking.py -q --no-header` → **32 passed in 1.40s**, zero failures.
- [x] Sharded suite green (no visible-tests regression).
- [x] Commit message: `PROJ-443 Phase 1: triage test_cargo_tracking.py (30 failures → green; all category-b test-contract fixes)`.

---

## Phase Completion Checklist
- [x] All test_cargo_tracking.py failures resolved (30 fixed; 0 deletions; 0 production changes)
- [x] `pytest tests/unit/strategy/data/test_cargo_tracking.py -q -n 4` returns zero failures (32/32 green)
- [x] Sharded suite still green (no regression in visible tests)
- [x] `plan.md` updated; `phase_state.json` not used (03c dropped per Phase 0)
