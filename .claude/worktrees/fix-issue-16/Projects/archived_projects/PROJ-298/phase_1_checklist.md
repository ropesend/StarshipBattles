# Phase 1: Survey & Inventory

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Build a precise, filtered inventory of every old-name usage in production+test source. Do this BEFORE any renames so later phases can be checked off file-by-file.

---

## Tasks

### Task 1.1: Build per-symbol usage inventory [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/usage_inventory.md` (NEW)
**Tests:** None — this is a pure investigation task.

For each old-name symbol, run a word-boundary grep scoped to source directories and record every hit. Exclude archives, reviews, tracking, and generated files.

- [x] Create `findings/usage_inventory.md` with one section per symbol below
- [x] Run for each symbol — record every (file, line, kind-of-use) tuple in the inventory:
  - [x] `\bFleetOrder\b` (the class type, not `fleet_orders` variables) — `grep -rn "\bFleetOrder\b" game/ tests/`
  - [x] `\bPlanetOrder\b` — `grep -rn "\bPlanetOrder\b" game/ tests/`
  - [x] `\bClearFleetOrdersCommand\b` — `grep -rn "\bClearFleetOrdersCommand\b" game/ tests/`
  - [x] `\bDeleteFleetOrderCommand\b` — `grep -rn "\bDeleteFleetOrderCommand\b" game/ tests/`
  - [x] `\bReorderFleetOrderCommand\b` — `grep -rn "\bReorderFleetOrderCommand\b" game/ tests/`
  - [x] `\bFleetOrdersWindow\b` — `grep -rn "\bFleetOrdersWindow\b" game/ tests/`
  - [x] `from game.ui.screens.fleet_orders_window` (module-path imports of the shim) — `grep -rn "fleet_orders_window" game/ tests/` (excluding the shim file itself)
- [x] Categorize each hit as one of:
  - **Import line** — `from X import OldName`
  - **Type annotation** — `def f(x: OldName)`, `: OldName =`
  - **Instance check** — `isinstance(x, OldName)`
  - **Class reference** — `OldName(...)`, `OldName.method`
  - **String literal** — old name in a docstring/comment/error message
- [x] Total tally: target the actual production+test count (will be much less than the 109/14 raw greps)

**Notes:**
- Counted 6 alias declarations + 1 shim module + 1 package re-export.
- Real production+test totals: `FleetOrder`=582 occurrences/76 files, `PlanetOrder`=29/4, `ClearFleetOrdersCommand`=29/7, `DeleteFleetOrderCommand`=10/4, `ReorderFleetOrderCommand`=10/4, `FleetOrdersWindow`=24/6, `FleetOrderSerializer`=~22/4. Total ~684 occurrences across ~85 unique files.
- **Phase 1 discovery:** A SIXTH alias `FleetOrderSerializer = OrderSerializer` exists at `game/strategy/data/order_serializer.py:235`. NOT in original code review report or initial PROJ-298 scope. Added to scope; plan.md and decisions.md updated accordingly.
- **Phase 1 discovery:** `game/strategy/__init__.py` re-exports `FleetOrder` (lines 13, 34, 64). Added to Phase 4 deletion scope.
- The 76-file `FleetOrder` count includes a long tail of test files with low hit density. `findings/rename_plan.md` orders them by area + density for execution.

---

### Task 1.2: Identify non-rename hits to leave alone [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/usage_inventory.md` (EDIT)
**Tests:** None.

Mark hits that should NOT be renamed:

- [x] **Variable/function names containing `fleet_orders`** (lowercase) — these refer to "orders attached to a fleet," not the `FleetOrder` class. Leave alone. Examples: `fleet_orders_logic`, `get_fleet_orders()`, `test_fleet_orders_refresh.py`
- [x] **Module/file names** — `fleet_orders_window.py` itself is a shim being deleted; don't rename it. Test files like `test_fleet_orders_logic.py` should stay (they test the orders-of-a-fleet domain, not the FleetOrder class)
- [x] **The `planet_order_validator.py` filename** — the file's class probably doesn't reference `PlanetOrder` anymore (it operates on `Order` instances with planet entity_type). The filename hints at the domain, similar to `fleet_orders_*` conventions. Leave alone for this project; capture as a follow-up if desired
- [x] **Comments/docstrings explaining migration history** (e.g., `# PROJ-238: Backward compatibility alias`) — the comments themselves will be removed when the alias is removed in Phase 4. Don't pre-edit
- [x] Annotate the inventory with `[KEEP]` for these hits

**Notes:**
- All `[KEEP]` items consolidated into the "[KEEP] — Hits NOT to rename" section of `usage_inventory.md`.
- Special case: `order_processor.py:770` log-message string contains `FleetOrderProcessor` — this IS in scope (a runtime emission, not a history note). The matching docstring at line 4 of the same file is historical and stays.

---

### Task 1.3: Build the rename plan [Simple]
**File:** `Projects/active_projects/PROJ-298/findings/rename_plan.md` (NEW)
**Tests:** None.

Translate the inventory into a per-file action plan.

- [x] For each file with `[RENAME]` hits, list:
  - File path
  - Symbol(s) to rename and the new name
  - Hit count (so the implementer knows what to expect)
- [x] Order the rename plan by area: production-strategy → production-ui → tests-strategy → tests-ui → docs
- [x] Save to `findings/rename_plan.md`

**Notes:**
- `rename_plan.md` orders Phase 2 production work as: data layer → engine → facade/validation → UI screens → strategy `__init__.py`.
- Phase 3 test work is split by directory: unit/strategy core → unit/strategy engine → unit/strategy fleet/services/facade → unit/UI screens → integration → fixtures → repro.
- Recommended approach (in `rename_plan.md`): IDE find-and-replace with **Match Case + Whole Word**, file-by-file. Not bulk sed — risk of corrupting the 1-of-684 substring overlap is too high.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `findings/usage_inventory.md` exists with per-symbol sections
- [x] `findings/rename_plan.md` exists with per-file actions
- [x] Total `[RENAME]` count documented in `plan.md` Current State
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: Production Rename)
