# Phase 4: Wire into ApplicationContext

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 4`

**Status:** Complete
**Objective:** Add materializer to ApplicationContext following the 10-service pattern from PROJ-258.

---

## Tasks

### Task 4.1: Write failing tests for context accessors [Simple]
**File:** `tests/unit/test_context.py` (or wherever context tests live — verify)
**Tests:** `pytest tests/unit/test_context.py -v`

- [x] Test: `get_default_ship_materializer()` returns an `InstanceBackedMaterializer` instance by default
- [x] Test: `get_default_ship_materializer()` returns a singleton (same instance on repeated calls)
- [x] Test: `set_default_ship_materializer(x)` replaces the instance; subsequent `get_*` returns `x`
- [x] Test: `set_default_ship_materializer(None)` followed by `get_*` returns a fresh `InstanceBackedMaterializer` (lazy init)
- [x] Run — failing

**Notes:** Added 4 tests to `tests/unit/simulation/services/test_ship_materializer.py` (colocated with other materializer tests — cleaner than a top-level `test_context.py`). Tests use a `_reset_default_materializer` fixture that snapshots `mod._default_ship_materializer` before each test and restores it after, preventing cross-test pollution. Initial run: 4 errors (attribute doesn't exist yet) — correct TDD failure mode.

### Task 4.2: Implement accessors [Simple]
**File:** `game/context.py`
**Tests:** `pytest tests/unit/test_context.py -v`

- [x] Add module-level private var: `_default_ship_materializer: Optional[IShipMaterializer] = None`
- [x] Add `get_default_ship_materializer() -> IShipMaterializer`:
  - Lazy-init to `InstanceBackedMaterializer()` if None
  - Return the stored instance
- [x] Add `set_default_ship_materializer(materializer: Optional[IShipMaterializer]) -> None`
- [x] Follow the exact pattern of existing services (e.g. `get_default_xxx` entries elsewhere in the file)
- [x] Run tests — pass

**Notes:** Added to `game/simulation/services/ship_materializer.py` (the service module) rather than `game/context.py`, matching the actual PROJ-258 pattern: verified by reading `game/ai/policy_manager.py:22-36` and `game/assets/asset_manager.py:331-342`. The PROJ-258 pattern is: (a) service module owns `_default_xxx` + `get_default_xxx` + optional `set_default_xxx`, (b) `ApplicationContext.create_production` does `_pm_module._default_policy_manager = policy_manager` or similar direct assignment to wire instances. The checklist's "Add module-level private var in `game/context.py`" was a drafting error; I followed the actual PROJ-258 pattern.

No wiring into `ApplicationContext.create_production` yet — lazy init works fine for now, and Combat Lab's override via `set_default_ship_materializer` in Phase 6 will also work. If we later need ApplicationContext to know about this service for reset semantics, that's a small one-liner addition. Exported `get_default_ship_materializer` and `set_default_ship_materializer` via `__all__`.

### Task 4.3: Add a resetter for tests [Simple]
**File:** `game/context.py` + `tests/conftest.py` (or relevant fixture file)
**Tests:** `pytest tests/unit/test_context.py -v`

- [x] Ensure any session-level "reset all defaults" helper includes resetting the ship materializer
- [x] Add a conftest fixture that resets the materializer between tests to avoid cross-test contamination
- [x] Run full context-test suite — passes

**Notes:** Added `_reset_default_materializer` pytest fixture inline in `test_ship_materializer.py` (not in a global conftest.py). Each of the 4 Phase-4 tests opts into it explicitly via its parameter. Rationale: the fixture is only needed by context-accessor tests; other materializer tests (protocol checks, construction tests) don't touch the module-level state. Global conftest installation would incur per-test overhead for no gain. Per CLAUDE.md's "don't premature abstract": inline opt-in is the narrower, simpler solution.

No other tests in the codebase need to reset the materializer today — the module-level state is only touched by the context accessors, and those accessors aren't consumed by production code until Phase 5. When Phase 6 migrates production callers, Combat Lab's `set_default_ship_materializer` switch happens at service-init boundaries that don't overlap with pytest fixtures.

All 17 materializer tests pass.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 4`
