# Phase 5: Documentation & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update documentation that still references old names; verify the project end-to-end with a manual smoke test.

**Prerequisites:** Phases 2-4 complete; aliases and shim are gone.

---

## Tasks

### Task 5.1: Update `docs/03_CONVENTIONS.md` [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Tests:** Manual verification

The grep evidence flagged `docs/03_CONVENTIONS.md` as containing old-name examples.

- [ ] Read `docs/03_CONVENTIONS.md` and find every old-name mention (`FleetOrder`, `PlanetOrder`, `FleetOrdersWindow`, etc.)
- [ ] For each:
  - If it's an example of a type/symbol → update to `Order` / `OrdersWindow`
  - If it's historical commentary about the migration → either remove or rephrase as past-tense ("formerly `FleetOrder`, now `Order`") only if the historical context aids comprehension; default to removing
- [ ] **Verification:** `grep -n "FleetOrder\|PlanetOrder\|FleetOrdersWindow" docs/03_CONVENTIONS.md` returns zero results

**Notes:**

---

### Task 5.2: Sweep all docs for any remaining mentions [Simple]
**File:** All of `docs/`
**Tests:** Manual verification

- [ ] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b" docs/`
- [ ] For each hit, apply the same rule as Task 5.1
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" docs/` returns zero results

**Notes:**

---

### Task 5.3: Update CLAUDE.md note (if present) [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

- [ ] `grep -n "FleetOrder\|PlanetOrder" CLAUDE.md`
- [ ] If hits exist, update or remove per Task 5.1 rule
- [ ] **Verification:** `grep -n "FleetOrder\|PlanetOrder" CLAUDE.md` returns zero results

**Notes:**

---

### Task 5.4: Final sweep + full suite [Simple]
**File:** Whole repo
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Final sweep across the entire source tree (excluding archives/Tracking/Reviews):
  ```bash
  grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" \
    game/ tests/ docs/ CLAUDE.md
  ```
- [ ] **Expected:** zero results
- [ ] If hits exist, fix and re-sweep
- [ ] **Run full sharded suite — must remain at 15112+ passing**

**Notes:**

---

### Task 5.5: Manual smoke test [Simple]
**File:** Game runtime
**Tests:** Manual launch of the game

- [ ] `python game/main.py` (or however the game is launched)
- [ ] **Smoke 1 — Fleet Orders:** open the strategy screen, select a fleet, open the orders panel, issue a MOVE order. Verify it appears, executes, and the panel updates correctly.
- [ ] **Smoke 2 — Planet Orders:** open the strategy screen, select a colonized planet, open its abilities/orders panel, issue a build or recruit order. Verify it appears, queues, and processes when end-of-turn fires.
- [ ] **Smoke 3 — Sub-window hotkeys:** verify hotkey shortcuts to the orders sub-windows still work (the rename touched `test_sub_window_hotkeys.py`).
- [ ] If any smoke fails: identify root cause, fix, return to relevant earlier task.

**Notes:**

---

### Task 5.6: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md` (auto-memory index)
**Tests:** None.

- [ ] Add a one-line entry under "Recently Archived" or "Completed Projects" once the project is closed (this happens after user verification, not now)
- [ ] Format: `- **PROJ-298** — FleetOrder Rename Cleanup (2026-MM-DD). All 5 phases complete. Aliases (`FleetOrder`, `PlanetOrder`, `Clear/Delete/ReorderFleetOrdersCommand`) and `fleet_orders_window.py` shim deleted; ~N old-name usages migrated. Sharded suite: 15112/15112.`
- [ ] If you started a detail file under `memory/` for this project, link it from MEMORY.md

**Notes:** Do this AFTER user verifies the project is complete; not during implementation.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Final sweep returns zero hits in source tree
- [ ] Full sharded suite at 15112+ passing
- [ ] Manual smoke tests pass
- [ ] User verified end-to-end
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
