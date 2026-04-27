# Phase 1: Survey & Inventory

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build a precise, filtered inventory of every old-name usage in production+test source. Do this BEFORE any renames so later phases can be checked off file-by-file.

---

## Tasks

### Task 1.1: Build per-symbol usage inventory [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/usage_inventory.md` (NEW)
**Tests:** None — this is a pure investigation task.

For each old-name symbol, run a word-boundary grep scoped to source directories and record every hit. Exclude archives, reviews, tracking, and generated files.

- [ ] Create `findings/usage_inventory.md` with one section per symbol below
- [ ] Run for each symbol — record every (file, line, kind-of-use) tuple in the inventory:
  - [ ] `\bFleetOrder\b` (the class type, not `fleet_orders` variables) — `grep -rn "\bFleetOrder\b" game/ tests/`
  - [ ] `\bPlanetOrder\b` — `grep -rn "\bPlanetOrder\b" game/ tests/`
  - [ ] `\bClearFleetOrdersCommand\b` — `grep -rn "\bClearFleetOrdersCommand\b" game/ tests/`
  - [ ] `\bDeleteFleetOrderCommand\b` — `grep -rn "\bDeleteFleetOrderCommand\b" game/ tests/`
  - [ ] `\bReorderFleetOrderCommand\b` — `grep -rn "\bReorderFleetOrderCommand\b" game/ tests/`
  - [ ] `\bFleetOrdersWindow\b` — `grep -rn "\bFleetOrdersWindow\b" game/ tests/`
  - [ ] `from game.ui.screens.fleet_orders_window` (module-path imports of the shim) — `grep -rn "fleet_orders_window" game/ tests/` (excluding the shim file itself)
- [ ] Categorize each hit as one of:
  - **Import line** — `from X import OldName`
  - **Type annotation** — `def f(x: OldName)`, `: OldName =`
  - **Instance check** — `isinstance(x, OldName)`
  - **Class reference** — `OldName(...)`, `OldName.method`
  - **String literal** — old name in a docstring/comment/error message
- [ ] Total tally: target the actual production+test count (will be much less than the 109/14 raw greps)

**Notes:** [Filled with totals during execution]

---

### Task 1.2: Identify non-rename hits to leave alone [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/usage_inventory.md` (EDIT)
**Tests:** None.

Mark hits that should NOT be renamed:

- [ ] **Variable/function names containing `fleet_orders`** (lowercase) — these refer to "orders attached to a fleet," not the `FleetOrder` class. Leave alone. Examples: `fleet_orders_logic`, `get_fleet_orders()`, `test_fleet_orders_refresh.py`
- [ ] **Module/file names** — `fleet_orders_window.py` itself is a shim being deleted; don't rename it. Test files like `test_fleet_orders_logic.py` should stay (they test the orders-of-a-fleet domain, not the FleetOrder class)
- [ ] **The `planet_order_validator.py` filename** — the file's class probably doesn't reference `PlanetOrder` anymore (it operates on `Order` instances with planet entity_type). The filename hints at the domain, similar to `fleet_orders_*` conventions. Leave alone for this project; capture as a follow-up if desired
- [ ] **Comments/docstrings explaining migration history** (e.g., `# PROJ-238: Backward compatibility alias`) — the comments themselves will be removed when the alias is removed in Phase 4. Don't pre-edit
- [ ] Annotate the inventory with `[KEEP]` for these hits

**Notes:**

---

### Task 1.3: Build the rename plan [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/rename_plan.md` (NEW)
**Tests:** None.

Translate the inventory into a per-file action plan.

- [ ] For each file with `[RENAME]` hits, list:
  - File path
  - Symbol(s) to rename and the new name
  - Hit count (so the implementer knows what to expect)
- [ ] Order the rename plan by area: production-strategy → production-ui → tests-strategy → tests-ui → docs
- [ ] Save to `findings/rename_plan.md`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `findings/usage_inventory.md` exists with per-symbol sections
- [ ] `findings/rename_plan.md` exists with per-file actions
- [ ] Total `[RENAME]` count documented in `plan.md` Current State
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: Production Rename)
