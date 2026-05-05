# Phase 4: Delete Aliases & Shim Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** With production and tests fully migrated to new names, eradicate the alias declarations and the shim module per System Migration Policy.

**Prerequisites:** Phases 2 and 3 complete; full sharded suite passes with 15112+; ALL old-name references in `game/` and `tests/` have been replaced (alias declarations + shim are the only remaining mentions).

---

## Tasks

### Task 4.1: Delete `FleetOrder` and `PlanetOrder` aliases [Simple]
**File:** `game/strategy/data/order_types.py`

- [x] Read `order_types.py` lines 165-175 to confirm current state
- [x] Delete lines 169-171 (comment + `FleetOrder = Order` + `PlanetOrder = Order`)
- [x] **Verification:** `python -c "from game.strategy.data.order_types import FleetOrder"` raises `ImportError` ✓
- [x] **Verification:** `python -c "from game.strategy.data.order_types import PlanetOrder"` raises `ImportError` ✓

**Notes:** Both aliases plus the boilerplate comment cleanly removed.

---

### Task 4.2: Delete command aliases in `commands.py` [Simple]
**File:** `game/strategy/engine/commands.py`

- [x] Delete `ClearFleetOrdersCommand = ClearOrdersCommand` (line 100) + comment
- [x] Delete `DeleteFleetOrderCommand = DeleteOrderCommand` (line 289) + comment
- [x] Delete `ReorderFleetOrderCommand = ReorderOrderCommand` (line 305) + comment
- [x] **Verification:** `python -c "from game.strategy.engine.commands import ClearFleetOrdersCommand"` raises `ImportError` ✓

**Notes:** All 3 alias declarations + their boilerplate comments removed.

---

### Task 4.3: Delete `fleet_orders_window.py` shim module + extra alias [Simple]
**File:** `game/ui/screens/fleet_orders_window.py` (DELETE), `game/ui/screens/orders_window.py` (EDIT)

- [x] Confirm zero internal importers: grep returned zero
- [x] Delete `game/ui/screens/fleet_orders_window.py` outright
- [x] **Verification:** `python -c "from game.ui.screens.fleet_orders_window import OrdersWindow"` raises `ModuleNotFoundError` ✓
- [x] **Phase 1 scope addition:** Delete `FleetOrdersWindow = OrdersWindow` alias at `orders_window.py:353`

**Notes:** Both the shim module AND the redundant in-place alias at `orders_window.py:353` removed.

---

### Task 4.4: Phase 1 scope additions — `FleetOrderSerializer` alias + `__init__.py` re-export [Simple]
**File:** `game/strategy/data/order_serializer.py`, `game/strategy/__init__.py`

- [x] Delete `FleetOrderSerializer = OrderSerializer` alias at `order_serializer.py:235` + comment
- [x] **Verification:** `python -c "from game.strategy.data.order_serializer import FleetOrderSerializer"` raises `ImportError` ✓
- [x] Remove `FleetOrder` import from `game/strategy/__init__.py` (line 34: drop `, FleetOrder` from import; update docstring at line 13)
- [x] Remove `'FleetOrder'` entry from `__all__` (line 64)
- [x] **Verification:** `python -c "from game.strategy import FleetOrder"` raises `ImportError`

**Notes:** Both Phase 1 discovery aliases removed.

---

### Task 4.5: Update CLAUDE.md / docs to drop "FleetOrder backward compat" mentions [Simple]

- [x] `grep -rn "PROJ-238: Backward compatibility" --include="*.py" game/ tests/` returns zero results ✓
- [x] No CLAUDE.md migration-pending notes about FleetOrder; nothing to remove there.
- [x] `docs/03_CONVENTIONS.md` § 1.8 already documents the rename as complete (preserved as accurate now)

**Notes:** All "backward compatibility" boilerplate removed alongside the aliases. `docs/03_CONVENTIONS.md` was already factually correct ("Old backward compatibility alias modules have been deleted") — that statement is now true post-Phase 4.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/ tests/` returns ZERO results (only historical docstring comments in `fleet.py:23`, `order_types.py:5,77`, `order_processor.py:4`, `commands.py:93,281,296`, `orders_window.py:3,39` — these describe the rename history, are accurate, and are KEEP-list per Phase 1)
- [x] All ImportError verifications above pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 5: Documentation & Verification)
