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
| 1. Survey & Inventory | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Production Rename | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test Rename | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete Aliases & Shim Module | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation & Verification | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for implementation)
**Last Action:** Project created (split out from PROJ-297 due to scope — 726+ usages of old names)
**Next Action:** Begin Phase 1 — survey all alias usages, build a per-symbol manifest before any renames
**Blockers:** None — depends on no other work
**Context for Next Agent:** PROJ-238 (in `Projects/deep_archive/PROJ-201-250/PROJ-238/`) was the original Fleet/Planet*Order → Order migration. It introduced backward-compat aliases that were never cleaned up. This project finishes that migration. **Do not start renaming until Phase 1 inventory is complete** — the symbol surface is wider than the original code review noted (PlanetOrder + FleetOrdersWindow are also aliased; review missed them).

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
- Same renames in test source under `tests/`
- Module-path renames where callers still use `from game.ui.screens.fleet_orders_window import ...`
- Deletion of the alias declarations:
  - `game/strategy/data/order_types.py:170-171` (`FleetOrder`, `PlanetOrder`)
  - `game/strategy/engine/commands.py:100` (`ClearFleetOrdersCommand`)
  - `game/strategy/engine/commands.py:289` (`DeleteFleetOrderCommand`)
  - `game/strategy/engine/commands.py:305` (`ReorderFleetOrderCommand`)
- Deletion of `game/ui/screens/fleet_orders_window.py` (whole-file re-export shim)
- Updates to any docs that still use the old names (mainly `docs/03_CONVENTIONS.md` per the grep results)

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
| `DeleteFleetOrderCommand = DeleteOrderCommand` | `game/strategy/engine/commands.py` | ~289 |
| `ReorderFleetOrderCommand = ReorderOrderCommand` | `game/strategy/engine/commands.py` | ~305 |
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
