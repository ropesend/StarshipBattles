# PROJ-452 Phase 1: Container.remove non-negative guard (DI-005)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-452 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close DI-2026-05-18-005 by mirroring the existing `Container.add` non-negative guard onto `Container.remove`. This is the smallest finding in the project; Phase 1 establishes the TDD recipe (RED-then-GREEN with a focused unit test) that Phases 2-4 follow.

**Cross-bucket file-ownership rule:** This phase touches only `game/strategy/data/container.py` and `tests/unit/strategy/data/test_container.py`. Do NOT touch any file PROJ-453 / PROJ-454 / PROJ-455 owns.

**Source-of-truth findings:** [`findings/PROJ-452_findings.md`](findings/PROJ-452_findings.md) — read DI-005's full text (Codex reproduction at PROJ-436 Phase 11 consult) before starting.

---

## Tasks

### Task 1.1: DI-005 — Mirror Container.add non-negative guards onto Container.remove [Simple]
**File:** `game/strategy/data/container.py:225` (`Container.remove`)
**Tests:** `pytest tests/unit/strategy/data/test_container.py -v`

- [ ] Read the existing `Container.add` guards at `container.py:191` (resource: `if quantity < 0: raise ValueError("resource quantity must be non-negative")`) and `:213-214` (population: `if quantity < 0: raise ValueError("population quantity must be non-negative")`). The wording matters — Phase 1 must use the exact same phrases so the symmetry is visible from `git grep`.
- [ ] Read the current `Container.remove` block at `container.py:225-256`. Note the three branches: `ResourceContainable` (lines 226-235), `ItemContainable` (lines 237-243), `PopulationContainable` (lines 245-254).
- [ ] **RED**: Add three unit tests to `tests/unit/strategy/data/test_container.py`:
  1. `test_remove_rejects_negative_resource_quantity` — call `container.remove(ResourceContainable("metals"), -3.0)`, assert `ValueError` raised with message containing `"non-negative"`.
  2. `test_remove_rejects_negative_population_quantity` — call `container.remove(PopulationContainable("human"), -2)`, assert `ValueError` raised.
  3. `test_remove_does_not_grow_storage_on_negative_quantity` — pre-populate the container with `add(...)`, attempt `remove(..., -3.0)`, assert the storage value is unchanged (defends against future regression where the guard is removed but the reproduce-the-bug behaviour returns).
  
  Run the new tests; confirm all three FAIL before the production change (the `remove` body currently subtracts a negative number → growth → no exception).
- [ ] **GREEN**: Add the guard at the top of the `ResourceContainable` branch in `Container.remove` (immediately after the `isinstance` check at line 226):
  ```python
  if quantity < 0:
      raise ValueError("resource quantity must be non-negative")
  ```
  Add the parallel guard at the top of the `PopulationContainable` branch (after the `isinstance` check at line 245):
  ```python
  if quantity < 0:
      raise ValueError("population quantity must be non-negative")
  ```
  The `ItemContainable` branch (lines 237-243) does not need a guard — `quantity` is unused there (item removal is by `instance_id`).
- [ ] Run targeted tests; confirm all three RED tests now pass.
- [ ] Run `pytest tests/unit/strategy/data/test_container.py -v` (full file) — confirm no existing tests regress.
- [ ] **Verify symmetry**: `git diff game/strategy/data/container.py` should show only the two new guard blocks; the `ResourceContainable` block at line 226 and the `PopulationContainable` block at line 245 should mirror the wording at line 191 and 213-214 exactly.
- [ ] Update DI-2026-05-18-005 in `AgentCoordination/discovered_issues/log.jsonl` with `"status": "resolved"` and a `"resolution_note"` pointing at the PR (use the existing PROJ-444 / PROJ-445 resolution_note style).

**Notes:** [Filled during implementation. Sample shape: `2026-XX-XX: guard landed at container.py:228 (resource) and :248 (population). RED → GREEN cycle verified manually.`]

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] DI-2026-05-18-005 marked `resolved` in `log.jsonl`
- [ ] All three new tests in `test_container.py` green
- [ ] `pytest tests/unit/strategy/data/test_container.py -v` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-452 1` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

## Notes / Deferrals

- **BayInventory mirror** — `BayInventory.remove_resource` / `remove_population` got the parallel non-negative guards in archived PROJ-444 Phase 1 Task 1.1 (F-A-001). Phase 1 here closes the container-level mirror that the same DI entry (DI-005) named as the canonical fix site.
- **`ItemContainable` branch** — no quantity-based guard needed; items remove by `instance_id`.
