# Phase 4: Delete Aliases & Shim Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** With production and tests fully migrated to new names, eradicate the alias declarations and the shim module per System Migration Policy.

**Prerequisites:** Phases 2 and 3 complete; full sharded suite passes with 15112+; ALL old-name references in `game/` and `tests/` have been replaced (alias declarations + shim are the only remaining mentions).

---

## Tasks

### Task 4.1: Delete `FleetOrder` and `PlanetOrder` aliases [Simple]
**File:** `game/strategy/data/order_types.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] Read `game/strategy/data/order_types.py` lines 165-175 to confirm current state
- [ ] Delete lines 169-171 (the two `# PROJ-238: Backward compatibility aliases (will be removed after full migration)` comment + `FleetOrder = Order` + `PlanetOrder = Order`)
- [ ] If the file ends abruptly with the deletion, ensure trailing newline
- [ ] **Verification:** `python -c "from game.strategy.data.order_types import FleetOrder"` raises `ImportError`
- [ ] **Verification:** `python -c "from game.strategy.data.order_types import PlanetOrder"` raises `ImportError`
- [ ] Run targeted tests

**Notes:**

---

### Task 4.2: Delete command aliases in `commands.py` [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Read `game/strategy/engine/commands.py` lines 95-105 to confirm `ClearFleetOrdersCommand` alias is at line 100
- [ ] Delete line 100 + its `# PROJ-238: Backward compatibility alias` comment (line 99)
- [ ] Find and delete the `DeleteFleetOrderCommand = DeleteOrderCommand` alias (~line 289) + its comment line
- [ ] Find and delete the `ReorderFleetOrderCommand = ReorderOrderCommand` alias (~line 305) + its comment line
- [ ] **Verification:** `python -c "from game.strategy.engine.commands import ClearFleetOrdersCommand"` raises `ImportError`
- [ ] **Verification:** Same for `DeleteFleetOrderCommand` and `ReorderFleetOrderCommand`
- [ ] Run targeted tests

**Notes:**

---

### Task 4.3: Delete `fleet_orders_window.py` shim module [Simple]
**File:** `game/ui/screens/fleet_orders_window.py` (DELETE)
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Confirm zero internal importers: `grep -rn "from game.ui.screens.fleet_orders_window\|import fleet_orders_window" game/ tests/`
- [ ] Expected: zero results (Phase 3 should have migrated all of them)
- [ ] If any remain, STOP — fix them first, then return here
- [ ] Delete `game/ui/screens/fleet_orders_window.py` outright
- [ ] **Verification:** `python -c "from game.ui.screens.fleet_orders_window import OrdersWindow"` raises `ModuleNotFoundError`
- [ ] **Verification:** `python -c "from game.ui.screens.fleet_orders_window import FleetOrdersWindow"` raises `ModuleNotFoundError`
- [ ] Run targeted tests

**Notes:**

---

### Task 4.4: Update CLAUDE.md / docs to drop "FleetOrder backward compat" mentions [Simple]
**File:** Any docs that reference the alias as a known issue
**Tests:** Manual grep verification

- [ ] `grep -rn "FleetOrder\|PlanetOrder\|FleetOrdersWindow" CLAUDE.md docs/`
- [ ] **Expected hits:**
  - `docs/03_CONVENTIONS.md` (will be updated in Phase 5)
  - Any other docs flagged in Phase 1
- [ ] If CLAUDE.md mentions FleetOrder backward compat anywhere as a known-issue or migration-pending note, remove it
- [ ] **Verification:** `grep -rn "PROJ-238: Backward compatibility" .` returns zero source-tree results (only `Projects/deep_archive/` mentions allowed)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/ tests/` returns ZERO results
- [ ] `python -c "from game.strategy.data.order_types import FleetOrder"` raises `ImportError`
- [ ] `python -c "from game.ui.screens.fleet_orders_window import OrdersWindow"` raises `ModuleNotFoundError`
- [ ] Full sharded suite at 15112+ passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 5: Documentation & Verification)
