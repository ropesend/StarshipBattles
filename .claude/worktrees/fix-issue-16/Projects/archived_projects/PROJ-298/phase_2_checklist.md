# Phase 2: Production Rename

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace every old-name reference in `game/` (production source) with the canonical new name. Aliases remain intact so tests still pass — they will be deleted in Phase 4 once tests are migrated.

**Prerequisites:** Phase 1 inventory complete (`findings/usage_inventory.md` and `findings/rename_plan.md` populated).

---

## Tasks

Work through `findings/rename_plan.md`, file by file. For each file:
1. Open the file
2. Replace each old-name symbol with its new name (use IDE find-and-replace with whole-word matching, OR `sed -i` with `\b` boundaries)
3. Run the file's targeted tests
4. Check the file off below

### Task 2.1: Strategy data layer renames [Simple]
**File:** Files under `game/strategy/data/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/data/`

- [x] For each file in `findings/rename_plan.md` under `game/strategy/data/`: apply word-boundary rename for the symbols listed
- [x] Run targeted tests
- [x] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b" game/strategy/data/` — all remaining hits are the alias declarations themselves (lines 170-171 of `order_types.py`)

**Notes:**
- `order_serializer.py`: Renamed 2 internal class self-references (`FleetOrderSerializer._deserialize_*` → `OrderSerializer._deserialize_*`). The alias declaration at line 235 stays for Phase 4.
- `fleet.py`: Renamed 7 `FleetOrderSerializer` usages (2 imports, 2 calls, 3 comments, 1 module docstring). Module docstring updated to `OrderSerializer extracted to order_serializer.py (PROJ-210).`
- 28/28 `tests/integration/save_load/test_roundtrip_orders.py` pass after rename.
- 188/188 strategy fleet tests pass.

---

### Task 2.2: Strategy engine renames [Simple]
**File:** Files under `game/strategy/engine/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] For each file in `findings/rename_plan.md` under `game/strategy/engine/`: rename
- [x] Specific known hits (verify in inventory):
  - [x] `command_handlers.py` (PlanetOrder usages)
  - [x] `planet_action_engine.py`
  - [x] `planet_command_handlers.py`
  - [x] `commands.py` — alias declarations remain (deleted in Phase 4)
- [x] Run targeted tests
- [x] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b" game/strategy/engine/` — only the alias declarations themselves remain

**Notes:**
- `command_handlers.py`: SCOPE EXPANSION — also renamed two handler classes that PROJ-238 missed: `DeleteFleetOrderCommandHandler` → `DeleteOrderCommandHandler` and `ReorderFleetOrderCommandHandler` → `ReorderOrderCommandHandler`. The third handler `ClearOrdersCommandHandler` was already on the new name; consistency demanded the other two follow.
- `command_handlers.py`: Removed 3 dead-code dispatch registrations (lines 1022, 1033, 1035 in original). After the alias rename collapsed to identical strings, they were redundant duplicates. The original purpose (registering under the old class string name) was unreachable code from day one — `cmd.name` returns `__class__.__name__` which always resolves to the canonical name.
- Test coupling: `tests/unit/strategy/test_command_handlers.py` had to be updated NOW (not Phase 3) because it imports the renamed handler classes. Updated 22 references (2 imports, 2 test class names, 3 string literals in expected_commands list, 16+ instantiations). 80/80 tests pass.
- `order_processor.py`: Line 770 log-message string `FleetOrderProcessor` → `OrderProcessor`. Module docstring at line 4 (historical migration note) preserved.
- `planet_command_handlers.py`: Removed `as PlanetOrder` import alias; updated direct call at line 90.
- `planet_action_engine.py`: Removed `as PlanetOrder` TYPE_CHECKING import; updated 5 string-literal type annotations (`'PlanetOrder'` → `'Order'`).
- `commands.py`: Class definitions already on new names; only the alias declarations + their `# PROJ-238: Backward compatibility alias` comments remain (Phase 4 cleanup).

---

### Task 2.3: Strategy facade + validation renames [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`, `game/strategy/validation/__init__.py`, `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/unit/strategy/facade/ tests/unit/strategy/validation/`

- [x] Rename per inventory
- [x] Run targeted tests
- [x] **Verification:** grep returns zero non-alias hits in these files

**Notes:**
- Phase 1 rename plan over-scoped this task. Production fresh greps after Task 2.2 confirm:
  - `strategy_session_facade.py`: zero `\bFleetOrder\b`/`\bPlanetOrder\b` hits.
  - `validation/__init__.py`: zero hits.
  - `planet_order_validator.py`: zero hits (filename stays per decisions.md; class is `PlanetOrderValidator` which is a domain term, not the `PlanetOrder` symbol).
- The earlier file list was the unfiltered grep that matched substrings (`PlanetOrderValidator` contains `PlanetOrder` as substring). Word-boundary search after Task 2.2 returns zero. NO ACTION NEEDED.

---

### Task 2.4: UI screens renames [Medium]
**File:** Files under `game/ui/screens/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/ui/screens/`

UI is the largest production surface. Rename systematically.

- [x] Specific known hits (verify in inventory):
  - [x] `strategy_window_manager.py`
  - [x] `strategy_event_router.py` — Phase 1 over-scoped; word-boundary grep returns zero PlanetOrder/FleetOrder symbol hits in this file
  - [x] `strategy_screen.py` — same, zero word-boundary hits
  - [x] `strategy_fleet_command_router.py` — same, zero word-boundary hits
  - [x] `planet_abilities_window.py` — same, zero word-boundary hits
  - [x] `orders_window.py` — only historical docstring lines (3, 39 — KEEP) and the alias declaration at line 353 (Phase 4 deletion). NO RENAMES needed.
- [x] Run targeted tests
- [x] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" game/ui/` — only `fleet_orders_window.py` shim + `orders_window.py:353` alias remain (both Phase 4 deletions)

**Notes:**
- `strategy_window_manager.py`: 6 simple replacements at lines 432-443 (3 imports + 3 instantiations). All command alias names migrated to new names.
- `orders_window.py`: SCOPE ADDITION — line 353 has a SECOND `FleetOrdersWindow = OrdersWindow` alias declaration (separate from the `fleet_orders_window.py` shim). Added to Phase 4 deletion scope.
- All other UI files in the original Phase 1 plan were over-scoped — substring matches that don't refer to renamed symbols.
- 2469 testmon tests pass.

---

### Task 2.5: Sweep for any missed production hits [Simple]
**File:** All of `game/`
**Tests:** `pytest tests/ --testmon`

- [x] Final sweep: `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/`
- [x] **Expected remaining hits ONLY:**
  - 6 alias declaration sites: `order_types.py:170-171`, `commands.py:100, 289, 305`, `order_serializer.py:235`, `orders_window.py:353` (all Phase 4 deletions)
  - The `fleet_orders_window.py` shim file (Phase 4 deletion)
  - The `__init__.py` `FleetOrder` re-export at lines 13, 34, 64 (Phase 4 deletion)
  - Historical migration docstring comments — KEEP
- [x] If any other hits exist, file a Notes entry below describing them and decide rename vs keep
- [x] Run `pytest tests/ --testmon` to catch any production-only regressions

**Notes:**
- Final sweep confirms only Phase 4 deletion targets and historical docstrings remain.
- 2469 testmon tests pass after all Phase 2 production renames. No regressions.
- Total Phase 2 production files modified: 8 (`order_serializer.py`, `fleet.py`, `command_handlers.py`, `order_processor.py`, `planet_command_handlers.py`, `planet_action_engine.py`, `strategy_window_manager.py`, plus `tests/unit/strategy/test_command_handlers.py` for handler-class coupling).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `grep` sweep above produces only the expected residual hits
- [x] `pytest tests/ --testmon` passes (tests still work because aliases are still in place)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: Test Rename)
