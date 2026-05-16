# Phase 3: Deferred items — fleet_id field, view=None branch

**Status:** Complete
**Objective:** Close PROJ-393's 2 deferred items (LEG-03-023 already covered by Phase 1).

---

## Background

PROJ-393's `findings/verification_report.md` "Deferred During Implementation" section records 3 items:
- LEG-02-004 (`fleet_id` field full deletion) — partial fix shipped (tag removed only)
- LEG-02-006 (`view=None` branch) — `PlanetSelectionWindow` lacks facade access
- LEG-03-023 (Combat Lab vars) — **handled in Phase 1 of this project**

Phase 3 closes the remaining two.

---

## Tasks

### Task 3.1: `fleet_id` Path B simplification (LEG-02-004) — IMPLEMENTED

**Decision (Path B, 2026-05-08; clarified by PROJ-406 reconciliation):**
`fleet_id` is the canonical command field on `ClearOrdersCommand` /
`DeleteOrderCommand` / `ReorderOrderCommand`. Rather than introduce a parallel
`entity_id`/`entity_type` shape, the forward-dead `entity_type: str = "fleet"`
field was deleted (no handler ever read it; the sibling planet path uses
dedicated `ClearPlanetOrdersCommand` etc.). Closed in commit `6b8ee8c8f`
(PROJ-397 Phase 2 F-02..F-04). Path A (rename to `entity_id`) was retired —
Path B is sufficient because these commands strictly handle the fleet path.
The earlier "~20 callers" estimate was a fabrication; actual call-site count
is 1 per command.

**File:** `game/strategy/engine/commands/__init__.py`
**Tests:** `pytest tests/ -k "command or order"`

- [x] Audited callers — actual count is 1 per command (the "~20 callers" estimate was incorrect).
- [x] Path B chosen: delete forward-dead `entity_type` field; keep `fleet_id` as canonical (no parallel `entity_id` introduced).
- [x] Decision recorded in `decisions.md` and PROJ-406 reconciliation Note above.
- [x] Implemented in commit `6b8ee8c8f` (Phase 2 F-04).
- [x] Verified: focused tests pass; downstream `ClearOrdersCommand` docstring rewritten (Phase 2 F-02/F-03).

### Task 3.2: `view=None` branch deletion (LEG-02-006)
**File:** `game/ui/screens/strategy_detail_fmt.py:254-256` + `PlanetSelectionWindow`
**Tests:** `pytest tests/ -k "strategy_detail_fmt or planet_selection"`

- [x] Identify every caller of `format_planet_info()` that passes `view=None`.
- [x] For `PlanetSelectionWindow`: thread the strategy facade through to it so it can construct a `ColonyDemographicView`.
- [x] For any uncolonized-planet path: ensure the new code path produces the same output the legacy `view is None` branch did.
- [x] Delete the `view is None` branch at lines 254-256 (15 LOC).
- [x] Verify: focused test passes; uncolonized-planet rendering unchanged.

### Task 3.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes

---

## Phase Completion Checklist
- [x] LEG-02-004 fully closed (field deleted, callers migrated)
- [x] LEG-02-006 closed (branch deleted, callers updated)
- [x] Update plan.md phase table row to `Complete`

_Source: `Projects/active_projects/PROJ-393/findings/verification_report.md` "Deferred During Implementation"_
