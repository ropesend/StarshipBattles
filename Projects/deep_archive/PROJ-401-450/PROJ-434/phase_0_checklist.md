# Phase 0: API extension on `DesignRepository` + `DesignCatalog`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-434 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):**
- `game/strategy/systems/design_repository.py`
- `game/strategy/systems/design_catalog.py`
- `game/strategy/facade/slices/_facade_state.py`
- `tests/unit/strategy/design_repository/test_scan_designs.py`
- `tests/unit/strategy/design_repository/test_save_design.py`
- `tests/unit/strategy/design_repository/test_load_design_data.py`
- `tests/unit/strategy/design_catalog/test_search_designs.py`
- `tests/unit/strategy/design_catalog/test_filter_designs.py`
- `tests/unit/strategy/design_catalog/test_cache_invalidation.py`
- `tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py`

**Objective:** Add every method on `DesignRepository` / `DesignCatalog` that the deferred Phase 6 UI callers depend on, byte-compatible with the corresponding `DesignLibrary` method. Wire the QA-Obs-3 cache invalidation contract through `FacadeSessionState.designs_by_empire` so the catalog (not `DesignLibrary`) is the source of truth for the per-empire UI cache. Additive only — no caller migration this phase; the existing `DesignLibrary` UI flow stays live alongside the new methods so the tree stays green.

---

## Tasks

### Task 0.1: Characterization pin on `DesignLibrary` UI surface [Standard]
**Files:** `tests/unit/strategy/design_library/` (extend existing tests as needed)
**Tests:** `pytest tests/unit/strategy/design_library/ -q`

- [ ] Audit the current `DesignLibrary` public API consumed by UI: `scan_designs`, `search_designs`, `filter_designs`, `load_design_data`, `get_design_path`, `save_design(ship, name, built_designs)`, `mark_obsolete`.
- [ ] Confirm each has a focused test that pins its current behavior (ordering, error cases, side effects). Backfill where coverage is thin.
- [ ] Record any behavior subtleties (e.g. overwrite-protection rules, search match semantics) in `findings_ledger.md` as Phase 0 baseline.

### Task 0.2: Extend `DesignRepository` API [Medium]
**File:** `game/strategy/systems/design_repository.py`
**Tests:** `pytest tests/unit/strategy/design_repository/ -q`

- [ ] Add `scan_designs(empire_id: int)` matching `DesignLibrary.scan_designs` byte-for-byte (same ordering, same caching policy: repository scans on every call, the cache lives on the catalog).
- [ ] Add `load_design_data(design_id: str)` matching `DesignLibrary.load_design_data`.
- [ ] Add `get_design_path(design_id: str)` matching `DesignLibrary.get_design_path`.
- [ ] Add the rich `save_design(ship, name, built_designs)` — metadata embedding + overwrite-protection (raises the same exception type as `DesignLibrary` on conflict with a built design) + on-disk write through the existing low-level `save_design_data`. Does NOT invalidate the catalog cache (the catalog wrapper does that).
- [ ] Add `mark_obsolete(design_id: str)` matching `DesignLibrary.mark_obsolete`.
- [ ] Write red tests first per the strict TDD rule, then implement. Every new method needs a focused test that mirrors the characterization test from Task 0.1.

### Task 0.3: Extend `DesignCatalog` API + cache hook [Medium]
**File:** `game/strategy/systems/design_catalog.py`
**Tests:** `pytest tests/unit/strategy/design_catalog/ -q`

- [ ] Add `search_designs(query: str)` matching `DesignLibrary.search_designs` (match semantics — substring vs prefix — confirmed in Task 0.1).
- [ ] Add `filter_designs(predicate)` matching `DesignLibrary.filter_designs`.
- [ ] Add `invalidate(design_id: str | None = None)` cache hook — single-design invalidation when an id is supplied, full-cache invalidation when `None`.
- [ ] Add a `save_design(...)` orchestration method that delegates to `DesignRepository.save_design`, then calls `invalidate(design_id)` to clear the per-turn cache. This is the QA-Obs-3 contract surface for the workshop migration in Phase 2.
- [ ] Write red tests first; cover cache invalidation parity with a regression test in `test_cache_invalidation.py`.

### Task 0.4: Wire `FacadeSessionState.designs_by_empire` through the catalog [Standard]
**File:** `game/strategy/facade/slices/_facade_state.py`
**Tests:** `pytest tests/unit/strategy/facade/test_designs_by_empire_through_catalog.py -q`

- [ ] Re-point the `designs_by_empire` accessor to resolve through `session.services.design_catalogs_by_empire[empire_id]` rather than constructing a `DesignLibrary`.
- [ ] Add a focused regression test: workshop save → same-empire viewer sees the new design on the next `designs_by_empire[empire_id]` access without a turn advance.
- [ ] Verify the existing `DesignLibrary`-based callers still work — this slice migration is additive, not subtractive. Any UI caller that still constructs its own `DesignLibrary` instance continues to do so until its own Phase 1/2 migration. Document any subtlety in `findings_ledger.md`.

### Task 0.5: Phase close [Simple]
**Tests:** focused suites + sharded smoke.

- [ ] `pytest tests/unit/strategy/design_repository/ tests/unit/strategy/design_catalog/ tests/unit/strategy/facade/ tests/unit/strategy/design_library/ -q` green.
- [ ] `python Tools/test_sharded/test_sharded.py` green.
- [ ] `rg -n "DesignLibrary" game tests` still has hits — the deletion gate is NOT met this phase by design.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-434 phase_0 --repo .worktrees/phases/PROJ-434/phase_0`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `DesignRepository` exposes `scan_designs`, `load_design_data`, `get_design_path`, rich `save_design`, `mark_obsolete`
- [ ] `DesignCatalog` exposes `search_designs`, `filter_designs`, `invalidate`, `save_design` (orchestration)
- [ ] `FacadeSessionState.designs_by_empire` resolves through the catalog
- [ ] QA-Obs-3 regression test green
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
