# PROJ-298: FleetOrder Rename Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-298` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-298 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Survey & Inventory | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Production Rename | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test Rename | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete Aliases & Shim Module | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation & Verification | Complete (pending user smoke) | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Complete — pending user smoke verification
**Last Action:** All 5 phases code-complete. Total: 8 alias declarations deleted (`FleetOrder`, `PlanetOrder`, `ClearFleetOrdersCommand`, `DeleteFleetOrderCommand`, `ReorderFleetOrderCommand`, `FleetOrderSerializer`, in-place `FleetOrdersWindow` at `orders_window.py:353`, plus the `FleetOrder` re-export in `game/strategy/__init__.py`). 1 shim module deleted (`game/ui/screens/fleet_orders_window.py`). ~644 old-name usages migrated across ~85 files. Stale doc references in `docs/04_SERVICES.md` and `docs/systems/strategy_layer.md` updated. Two scope expansions discovered + fixed: handler classes `DeleteFleetOrderCommandHandler`/`ReorderFleetOrderCommandHandler` were also old-named (PROJ-238 missed them); 3 redundant compat dispatch registrations in `command_handlers.py` deleted as dead code.

**Phase 5 (full testmon) caught and fixed 5 test failures referencing the deleted shim path** (`tests/unit/ui/screens/test_sub_window_hotkeys.py`, `test_fleet_orders_refresh.py`, `tests/integration/ui/test_fleet_build_button.py` — all updated to import from `game.ui.screens.orders_window`).

**Next Action:** **USER VERIFICATION**. Run the game, exercise fleet orders + planet orders + sub-window hotkeys per Phase 5 Task 5.5 smoke checklist. After smoke passes, update MEMORY.md (Task 5.6) and archive PROJ-298.

**Blockers:** Manual smoke test required (cannot be performed by implementation agent).

**Context for Next Agent (or audit):**
- One pre-existing test failure persists: `tests/unit/strategy/data/test_build_context.py::TestBuildContextProtocolCompliance::test_fleet_satisfies_build_context_protocol`. Confirmed unrelated to PROJ-298 via `git stash` test. Out of scope.
- Historical migration documentation (e.g., `docs/03_CONVENTIONS.md` § 1.8, `docs/systems/strategy_layer.md:570`, production docstrings like `order_types.py:5,77`) intentionally retained — they accurately describe the PROJ-238 rename history.
- All `Order` / `OrdersWindow` / `OrderSerializer` / `OrderProcessor` / command-handler names are now canonical with no aliases.
- Total source-code hits for old names: **zero** in `game/` and `tests/`.

## Overview
Complete the Fleet/Planet*Order → Order rename started in PROJ-238 by replacing all old-name usages with their canonical new-name equivalents, then deleting the alias declarations and the `fleet_orders_window.py` re-export shim. Per System Migration Policy (CLAUDE.md), the goal is full eradication — no aliases, no shims, no deprecated comments.

## Goals
- Replace every old-name reference in production and test code with the canonical new name
- Delete all alias declarations (`FleetOrder = Order`, `PlanetOrder = Order`, `ClearFleetOrdersCommand = ClearOrdersCommand`, `DeleteFleetOrderCommand = DeleteOrderCommand`, `ReorderFleetOrderCommand = ReorderOrderCommand`)
- Delete the `game/ui/screens/fleet_orders_window.py` re-export shim (only consumed by external/legacy callers — verify zero internal callers first)
- Remove the wildcard import noted in the code review (collapses naturally with the shim deletion)
- Maintain the 15112 test baseline throughout

## Scope

**In:**
- Symbol renames in production source under `game/`:
  - `FleetOrder` → `Order`
  - `PlanetOrder` → `Order`
  - `ClearFleetOrdersCommand` → `ClearOrdersCommand`
  - `DeleteFleetOrderCommand` → `DeleteOrderCommand`
  - `ReorderFleetOrderCommand` → `ReorderOrderCommand`
  - `FleetOrdersWindow` (when imported as a class symbol) → `OrdersWindow`
  - **`FleetOrderSerializer` → `OrderSerializer`** (Phase 1 discovery)
  - `FleetOrderProcessor` log-message string at `order_processor.py:770` → `OrderProcessor`
- Same renames in test source under `tests/`
- Module-path renames where callers still use `from game.ui.screens.fleet_orders_window import ...`
- Deletion of the alias declarations:
  - `game/strategy/data/order_types.py:170-171` (`FleetOrder`, `PlanetOrder`)
  - `game/strategy/engine/commands.py:100` (`ClearFleetOrdersCommand`)
  - `game/strategy/engine/commands.py:289` (`DeleteFleetOrderCommand`)
  - `game/strategy/engine/commands.py:305` (`ReorderFleetOrderCommand`)
  - **`game/strategy/data/order_serializer.py:235` (`FleetOrderSerializer`) — Phase 1 discovery**
- Deletion of `game/ui/screens/fleet_orders_window.py` (whole-file re-export shim)
- Removal of `FleetOrder` re-export from `game/strategy/__init__.py` (lines 13, 34, 64)
- Updates to any docs that still use the old names — most docs already use new names; minimal action required (verify in Phase 5)

**Out:**
- The `fleet_id: int  # Kept for backward compat; use entity_id for new code` field rename in `commands.py:95` — that's a data-model rename, deeper scope, separate project
- Tracking/Bugs archive rewrites — historical context should remain in `Tracking/bugs/archived/*`, `Tracking/features/archived/*`, `Reviews/results/*`, and `Projects/deep_archive/*`
- Coverage and other generated artifacts (`coverage.json`, etc.)

## Key Files

### Alias Declaration Sites (DELETE in Phase 4)
| Component | File Path | Lines |
|-----------|-----------|-------|
| `FleetOrder = Order` | `game/strategy/data/order_types.py` | 170 |
| `PlanetOrder = Order` | `game/strategy/data/order_types.py` | 171 |
| `ClearFleetOrdersCommand = ClearOrdersCommand` | `game/strategy/engine/commands.py` | 100 |
| `DeleteFleetOrderCommand = DeleteOrderCommand` | `game/strategy/engine/commands.py` | 289 |
| `ReorderFleetOrderCommand = ReorderOrderCommand` | `game/strategy/engine/commands.py` | 305 |
| **`FleetOrderSerializer = OrderSerializer`** (Phase 1 discovery) | `game/strategy/data/order_serializer.py` | 235 |
| `FleetOrder` re-export | `game/strategy/__init__.py` | 13, 34, 64 |
| Re-export shim module | `game/ui/screens/fleet_orders_window.py` | whole file (8 lines) |

### Production Files Known to Use Old Names (renames in Phase 2)
Initial grep evidence (full inventory in Phase 1):
- `game/ui/screens/strategy_window_manager.py` (PlanetOrder)
- `game/ui/screens/strategy_event_router.py` (PlanetOrder)
- `game/ui/screens/orders_window.py`
- `game/ui/screens/strategy_screen.py`
- `game/ui/screens/strategy_fleet_command_router.py` (PlanetOrder)
- `game/ui/screens/planet_abilities_window.py` (PlanetOrder)
- `game/strategy/engine/command_handlers.py` (PlanetOrder)
- `game/strategy/engine/planet_action_engine.py` (PlanetOrder)
- `game/strategy/engine/planet_command_handlers.py` (PlanetOrder)
- `game/strategy/facade/strategy_session_facade.py` (PlanetOrder)
- `game/strategy/validation/planet_order_validator.py` (PlanetOrder)
- `game/strategy/validation/__init__.py` (PlanetOrder)

### Documentation
| File | Why |
|------|-----|
| `docs/03_CONVENTIONS.md` | Contains old-name examples (per grep) — update or note as historical |

## Related Documents
- [design.md](design.md) - Verification evidence and design rationale
- [decisions.md](decisions.md) - Decisions log
- [PROJ-297](../PROJ-297/plan.md) - The companion code-review-cleanup project
- [Projects/deep_archive/PROJ-201-250/PROJ-238/](../../deep_archive/PROJ-201-250/PROJ-238/) - The original migration that introduced the aliases

## Verification
- [ ] All phase checklists complete
- [ ] `grep -rn "FleetOrder\b\|PlanetOrder\b\|ClearFleetOrdersCommand\|DeleteFleetOrderCommand\|ReorderFleetOrderCommand\|FleetOrdersWindow" game/ tests/` returns zero source matches (archive/Tracking/Reviews are exempt)
- [ ] `python -c "from game.strategy.data.order_types import FleetOrder"` raises `ImportError`
- [ ] `python -c "from game.ui.screens.fleet_orders_window import OrdersWindow"` raises `ModuleNotFoundError`
- [ ] Full sharded suite at 15112+ passing
- [ ] Manual smoke: launch game, open a fleet, issue an order, verify the orders panel works
- [ ] Manual smoke: launch game, open a planet, issue a planet order (build/recruit), verify the planet orders panel works
- [ ] User verified
