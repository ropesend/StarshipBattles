# Phase 3: Task 5.4 deferred — `superweapon_order_processor.py` 723 LOC decomposition

**Status:** Not Started
**Objective:** Close PROJ-382's deferred Task 5.4. The file is 723 LOC and exceeds the 500-LOC ceiling.

---

## Background

PROJ-382 deferred this with rationale (verified in `Projects/active_projects/PROJ-382/findings/verification_report.md` Deferred During Implementation):

> The 5 `process_*` dispatchers carry `_precheck`/`_effect` closures over `self._get_empire_mutator()` / `self._event_bus` / `self._registries`. Extracting them as free functions either threads engine refs through every closure or requires a state-bag type. Audit's "register effect closures on `SuperweaponSpec`" path is a registry-restructuring project.

Two paths forward:
- **Option A (registry-restructuring):** Move `precheck`/`effect` callables onto `SuperweaponSpec` itself. Each spec then owns its dispatch shape. The processor becomes a thin loop. Cleaner architecturally but bigger refactor.
- **Option B (state-bag class):** Extract a `_SuperweaponDispatcher` class with `engine_refs` as instance fields. The 5 dispatchers become methods on it. Less ambitious but unblocks the LOC ceiling.

PROJ-382's review will weigh in on which is preferred (read it before starting).

---

## Tasks

### Task 3.1: Decide Option A vs Option B
**File:** N/A — design decision

- [ ] Read PROJ-382's review for any preference on this finding
- [ ] Decide which option to pursue. Document in `decisions.md`.

### Task 3.2: Implement chosen option
**File:** `game/strategy/engine/superweapon_order_processor.py` (+ possibly `game/simulation/components/abilities/superweapons.py` if Option A)
**Tests:** `pytest tests/ -k "superweapon" -v`

- [ ] Implement the decomposition.
- [ ] Verify: file ends ≤ 500 LOC.
- [ ] Verify: all 5 superweapon types still process correctly via end-to-end test.
- [ ] Verify: focused test passes.

### Task 3.3: Final regression
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved.

---

## Phase Completion Checklist
- [ ] `superweapon_order_processor.py` ≤ 500 LOC
- [ ] All 5 superweapon process_* paths exercised by tests
- [ ] Update plan.md phase table row to `Complete`

_Source: `Projects/active_projects/PROJ-382/findings/verification_report.md` "Deferred During Implementation"_
