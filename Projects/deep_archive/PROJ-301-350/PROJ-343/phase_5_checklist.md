# Phase 5: T1.3 — owned sector effects empire_id propagation

**Status:** Not Started
**Objective:** Pass the querying empire's id (the fleet owner) to `collect_sector_effects` at both call sites so the collector's owner filter activates.

---

## Tasks

### Task 5.1: Confirm ripple via grep [Simple]
**File:** read-only

- [ ] `git grep -n "collect_sector_effects" game/strategy/` — list every call site.
- [ ] For each, decide whether `empire_id=None` is correct (ownerless ambient query) or a leak.
- [ ] Document each in [decisions.md](../PROJ-343/decisions.md).

**Notes:**

### Task 5.2: Fix env-hazard call site [Simple]
**File:** `game/strategy/engine/environmental_hazard_engine.py:111-113`
**Tests:** `pytest tests/unit/strategy/engine/test_owned_sector_effects_filter.py -x` — must PASS

- [ ] Replace `empire_id=None` with `empire_id=fleet.owner_id`.
- [ ] Update the misleading comment at lines 109-110 — the owner filter NOW applies.
- [ ] Run Phase 1 task-1.4 test → passes.

**Notes:**

### Task 5.3: Fix combat call site [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py:508-511`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_engine* -x`

- [ ] Read lines 508-511 to identify the querying empire's id (probably the attacker or a current-fleet variable).
- [ ] Replace `empire_id=None` with the appropriate id.
- [ ] If the call is per-fleet inside a loop, use that fleet's `owner_id`; if per-team, use the team's empire id.

**Notes:**

### Task 5.4: Update pinning tests for cross-team leak [Medium]
**File:** `tests/unit/strategy/engine/test_environmental_hazard_engine*.py`, `tests/unit/strategy/engine/test_conflict_resolution_engine*.py`
**Tests:** `pytest tests/unit/strategy/engine/test_environmental_hazard_engine* tests/unit/strategy/engine/test_conflict_resolution_engine* -x`

- [ ] `git grep -n "empire_id=None\|cross.*team\|leak" tests/unit/strategy/engine/test_environmental_hazard_engine* tests/unit/strategy/engine/test_conflict_resolution_engine*` — find tests that pin the leak.
- [ ] For each: rewrite to assert empires now correctly filtered (owner-only damage), or delete with rationale.
- [ ] Verify ownerless-storm regression: add or confirm a test that ownerless storms still apply to all empires (because `owner_id is None` short-circuits the collector filter).

**Notes:**

### Task 5.5: Commit
- [ ] Stage env-hazard + combat fixes + test updates + Phase 1 task-1.4 test
- [ ] Commit: `fix(sector-effects): pass querying empire_id so owned hazards don't leak across teams (PROJ-343 T1.3)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.3 commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 6
