# Phase 1: IRaceRegistry protocol + CachedRaceRegistry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define the `IRaceRegistry` protocol and implement `CachedRaceRegistry` wrapping the existing file-backed `RaceLibrary`. Full test coverage for cache hits, misses, invalidation, and None-result caching.

---

## Tasks

### Task 1.1: Define `IRaceRegistry` protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] Add `@runtime_checkable` protocol with `get_race(race_id: str) -> Optional['RaceConfig']`.
- [ ] Import `RaceConfig` under `TYPE_CHECKING` guard (to avoid runtime import cycle).
- [ ] Update `docs/01_ARCHITECTURE.md` Protocols table with the new entry.

**Notes:**

### Task 1.2: Write failing tests for `CachedRaceRegistry` [Medium]
**File:** `tests/unit/strategy/systems/test_race_library.py` (add `TestCachedRaceRegistry` class)
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistry`

- [ ] Test: first `get_race("foo")` call delegates to backing library.
- [ ] Test: second `get_race("foo")` call does NOT hit backing (use MagicMock to count calls).
- [ ] Test: `get_race` for a missing race returns None AND caches the None (second call doesn't re-query).
- [ ] Test: `invalidate("foo")` clears one entry; next `get_race("foo")` re-queries.
- [ ] Test: `invalidate()` (no args) clears all entries.
- [ ] Test: protocol conformance — `isinstance(CachedRaceRegistry(mock_library), IRaceRegistry)` is True.

**Notes:**

### Task 1.3: Implement `CachedRaceRegistry` [Medium]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistry`

- [ ] Add class (see design.md § CachedRaceRegistry for full sketch):
  ```python
  class CachedRaceRegistry:
      """PROJ-287: Session-scoped in-memory cache over RaceLibrary.
      Implements IRaceRegistry. Caches None results along with hits."""
      def __init__(self, backing): ...
      def get_race(self, race_id): ...
      def invalidate(self, race_id=None): ...
  ```
- [ ] Add module docstring paragraph describing the caching contract.

**Notes:**

### Task 1.4: Verify protocol conformance [Simple]
**Tests:** `pytest tests/unit/strategy/systems/test_race_library.py`

- [ ] All `TestCachedRaceRegistry` tests green.
- [ ] Existing `RaceLibrary` tests still green (no changes to backing class).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: facade exposure)
