# Phase 1: IRaceRegistry protocol + CachedRaceRegistry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Define the `IRaceRegistry` protocol and implement `CachedRaceRegistry` wrapping the existing file-backed `RaceLibrary`. Full test coverage for cache hits, misses, invalidation, and None-result caching.

---

## Tasks

### Task 1.1: Define `IRaceRegistry` protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [x] Add `@runtime_checkable` protocol with `get_race(race_id: str) -> Optional['RaceConfig']`.
- [x] Import `RaceConfig` under `TYPE_CHECKING` guard (to avoid runtime import cycle).
- [x] Update `docs/01_ARCHITECTURE.md` Protocols table with the new entry.

**Notes:** Also added `IRaceRegistry` to `game/core/__init__.py` exports (`__all__` + module docstring) and bumped `game.core` export count in `docs/01_ARCHITECTURE.md` from 45 to 46.

### Task 1.2: Write failing tests for `CachedRaceRegistry` [Medium]
**File:** `tests/unit/strategy/systems/test_race_library.py` (add `TestCachedRaceRegistry` class)
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistry`

- [x] Test: first `get_race("foo")` call delegates to backing library.
- [x] Test: second `get_race("foo")` call does NOT hit backing (use MagicMock to count calls).
- [x] Test: `get_race` for a missing race returns None AND caches the None (second call doesn't re-query).
- [x] Test: `invalidate("foo")` clears one entry; next `get_race("foo")` re-queries.
- [x] Test: `invalidate()` (no args) clears all entries.
- [x] Test: protocol conformance — `isinstance(CachedRaceRegistry(mock_library), IRaceRegistry)` is True.

**Notes:** Added a 7th test (`test_invalidate_unknown_id_is_noop`) to lock in that invalidating an uncached id is a safe no-op. Verified the suite failed for the right reason (ImportError on `CachedRaceRegistry`) before implementing.

### Task 1.3: Implement `CachedRaceRegistry` [Medium]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistry`

- [x] Add class (see design.md § CachedRaceRegistry for full sketch):
  ```python
  class CachedRaceRegistry:
      """PROJ-287: Session-scoped in-memory cache over RaceLibrary.
      Implements IRaceRegistry. Caches None results along with hits."""
      def __init__(self, backing): ...
      def get_race(self, race_id): ...
      def invalidate(self, race_id=None): ...
  ```
- [x] Add module docstring paragraph describing the caching contract.

**Notes:** Implementation matches design.md sketch exactly; module docstring documents the cache + invalidation discipline.

### Task 1.4: Verify protocol conformance [Simple]
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py`

- [x] All `TestCachedRaceRegistry` tests green.
- [x] Existing `RaceLibrary` tests still green (no changes to backing class).

**Notes:** 35/35 in `test_race_library.py` pass; 54/54 in `test_protocols.py` + `test_protocols_boundary.py` pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: facade exposure)
