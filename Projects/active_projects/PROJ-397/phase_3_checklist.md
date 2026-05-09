# Phase 3: Deferred items — fleet_id field, view=None branch

**Status:** Not Started
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

### Task 3.1: Full `fleet_id` field deletion (LEG-02-004)
**File:** `game/strategy/engine/commands/__init__.py` + ~20 callers
**Tests:** `pytest tests/ -k "command or order"`

- [ ] Audit the ~20 callers of `fleet_id=` on `ClearOrdersCommand`/`DeleteOrderCommand`/`ReorderOrderCommand`.
- [ ] Two design paths:
  - **Path A:** Migrate every caller to `entity_id`/`entity_type` (introduces a bigger DI shape but cleaner).
  - **Path B:** Delete `fleet_id` and require callers to construct the command differently. Simpler if `fleet_id` is the only entity_type the commands handle.
- [ ] Decide and document in `decisions.md`.
- [ ] Implement.
- [ ] Verify: focused test passes.

### Task 3.2: `view=None` branch deletion (LEG-02-006)
**File:** `game/ui/screens/strategy_detail_fmt.py:254-256` + `PlanetSelectionWindow`
**Tests:** `pytest tests/ -k "strategy_detail_fmt or planet_selection"`

- [ ] Identify every caller of `format_planet_info()` that passes `view=None`.
- [ ] For `PlanetSelectionWindow`: thread the strategy facade through to it so it can construct a `ColonyDemographicView`.
- [ ] For any uncolonized-planet path: ensure the new code path produces the same output the legacy `view is None` branch did.
- [ ] Delete the `view is None` branch at lines 254-256 (15 LOC).
- [ ] Verify: focused test passes; uncolonized-planet rendering unchanged.

### Task 3.3: Verify
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes

---

## Phase Completion Checklist
- [ ] LEG-02-004 fully closed (field deleted, callers migrated)
- [ ] LEG-02-006 closed (branch deleted, callers updated)
- [ ] Update plan.md phase table row to `Complete`

_Source: `Projects/active_projects/PROJ-393/findings/verification_report.md` "Deferred During Implementation"_
