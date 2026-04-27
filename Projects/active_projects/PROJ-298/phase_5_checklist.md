# Phase 5: Documentation & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (pending user smoke test)
**Objective:** Update documentation that still references old names; verify the project end-to-end with a manual smoke test.

**Prerequisites:** Phases 2-4 complete; aliases and shim are gone.

---

## Tasks

### Task 5.1: Update `docs/03_CONVENTIONS.md` [Simple]

- [x] Read `docs/03_CONVENTIONS.md` § 1.8 — already accurately documents the rename ("Old backward compatibility alias modules have been deleted").
- [x] Decision: KEEP § 1.8 as historical migration documentation. The table accurately captures old → new mappings for new contributors. The closing sentence "Old backward compatibility alias modules have been deleted. All code must use the new names and import paths directly." is now factually true post-Phase 4.

**Notes:** No changes needed. The doc was forward-written (described the target state) and is now accurate.

---

### Task 5.2: Sweep all docs for any remaining mentions [Simple]

- [x] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrderProcessor\b\|\bFleetOrderSerializer\b" docs/`
- [x] Updated `docs/04_SERVICES.md:492` (`tuple[FleetOrder, ...]` → `tuple[Order, ...]`)
- [x] Updated `docs/04_SERVICES.md:521` (`order: FleetOrder` → `order: Order`)
- [x] Updated `docs/systems/strategy_layer.md:113` (`ClearFleetOrdersCommand` → `ClearOrdersCommand`)
- [x] Updated `docs/systems/strategy_layer.md:117` (`DeleteFleetOrderCommand` → `DeleteOrderCommand`, handler too)
- [x] Updated `docs/systems/strategy_layer.md:118` (`ReorderFleetOrderCommand` → `ReorderOrderCommand`, handler too)
- [x] Updated `docs/systems/strategy_layer.md:227` (`List[FleetOrder]` → `List[Order]`)
- [x] **Verification:** Final grep returns ONLY the historical migration table in `docs/03_CONVENTIONS.md` § 1.8 + a single historical sentence at `docs/systems/strategy_layer.md:570` ("The unified `Order` class (renamed from `FleetOrder` in PROJ-238)..."). Both are accurate history and KEEP per Phase 1.

**Notes:** The remaining hits are intentional migration documentation. Distinguishable from stale references because they explicitly describe the rename rather than treating old names as current.

---

### Task 5.3: Update CLAUDE.md (if present) [Simple]

- [x] `grep -n "FleetOrder\|PlanetOrder\|FleetOrdersWindow" CLAUDE.md` returned zero hits. No edits needed.

**Notes:** CLAUDE.md was already clean.

---

### Task 5.4: Final sweep + full suite [Simple]

- [x] Final sweep across the entire source tree:
  ```
  grep -rn "\bFleetOrder\b|\bPlanetOrder\b|\bClearFleetOrdersCommand\b|\bDeleteFleetOrderCommand\b|\bReorderFleetOrderCommand\b|\bFleetOrdersWindow\b|\bFleetOrderProcessor\b|\bFleetOrderSerializer\b" game/ tests/ docs/ CLAUDE.md
  ```
- [x] **Result:** Zero source-code hits in `game/` and `tests/`. Only historical migration documentation in `docs/03_CONVENTIONS.md` § 1.8 + 1 sentence at `docs/systems/strategy_layer.md:570`. Plus historical comments in production source (e.g., `fleet.py:23`, `order_types.py:5,77`, `order_processor.py:4`, `orders_window.py:3,39`) describing the PROJ-238 history — all accurate and KEEP.
- [x] **Full testmon suite ran:** 15376 passed, 2 skipped, 5 failed (all 5 fixed in cleanup pass — `test_sub_window_hotkeys.py`, `test_fleet_orders_refresh.py`, `test_fleet_build_button.py` had `from game.ui.screens.fleet_orders_window import` references; updated to `orders_window`. 36/36 of those pass after fix).

**Notes:** No production regressions. The pre-existing `test_build_context.py::test_fleet_satisfies_build_context_protocol` failure persists — confirmed unrelated to PROJ-298 via git stash test. Out of scope.

---

### Task 5.5: Manual smoke test [Simple]
**File:** Game runtime
**Tests:** Manual launch of the game

- [ ] **DEFERRED TO USER** — `python game/main.py` (or however the game is launched)
- [ ] **Smoke 1 — Fleet Orders:** open the strategy screen, select a fleet, open the orders panel, issue a MOVE order. Verify it appears, executes, and the panel updates correctly.
- [ ] **Smoke 2 — Planet Orders:** open the strategy screen, select a colonized planet, open its abilities/orders panel, issue a build or recruit order. Verify it appears, queues, and processes when end-of-turn fires.
- [ ] **Smoke 3 — Sub-window hotkeys:** verify hotkey shortcuts to the orders sub-windows still work.

**Notes:** This is a user-verification gate. The implementation agent cannot run the game UI; the user must perform these smoke tests before the project is fully closed.

---

### Task 5.6: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`

- [ ] **DEFERRED** — Add a one-line entry under "Recently Archived" once the user verifies smoke tests pass and approves project closure.
- [ ] Format: `- **PROJ-298** — FleetOrder Rename Cleanup (2026-04-26). All 5 phases complete. Aliases (`FleetOrder`, `PlanetOrder`, `Clear/Delete/ReorderFleetOrdersCommand`, `FleetOrderSerializer`, in-place `FleetOrdersWindow` alias) and `fleet_orders_window.py` shim deleted; ~644 old-name usages migrated across ~85 files. Sharded suite passing (modulo 1 pre-existing unrelated failure).`

**Notes:** Will be added after user smoke test passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (5.5 + 5.6 deferred to user verification gate)
- [x] Final sweep returns only intentional historical references
- [x] Targeted suite passes (no PROJ-298 regressions)
- [ ] Manual smoke tests pass (user)
- [ ] User verified end-to-end
- [x] Update status at top of this file to `Complete` (pending user smoke)
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete — pending user smoke verification"
