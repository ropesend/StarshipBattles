# PROJ-298 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

> **NOTE:** Phase 1 produces the precise per-file inventory in `findings/usage_inventory.md`. The list below is the projected scope based on initial grep evidence.

### DELETE (Phase 4)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/fleet_orders_window.py` | Production | DELETE — re-export shim (8 lines) |

### EDIT (alias declarations removed)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/order_types.py` | Production | EDIT — delete lines 169-171 (`FleetOrder` and `PlanetOrder` aliases + comment) |
| `game/strategy/engine/commands.py` | Production | EDIT — delete 3 alias declarations (lines 99-100, 288-289, 304-305) + comments |
| `game/strategy/data/order_serializer.py` | Production | EDIT — delete lines 234-235 (`FleetOrderSerializer = OrderSerializer` + comment). Phase 1 discovery |
| `game/strategy/__init__.py` | Production | EDIT — remove `FleetOrder` from import (line 34), `__all__` (line 64), docstring (line 13). Phase 1 discovery |

### EDIT (production renames)

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_window_manager.py` | Production | RENAME `PlanetOrder` → `Order` (and any other old names) |
| `game/ui/screens/strategy_event_router.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/ui/screens/orders_window.py` | Production | RENAME any internal old-name uses |
| `game/ui/screens/strategy_screen.py` | Production | RENAME |
| `game/ui/screens/strategy_fleet_command_router.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/ui/screens/planet_abilities_window.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/strategy/engine/command_handlers.py` | Production | RENAME `PlanetOrder` → `Order` (and any command-name old uses) |
| `game/strategy/engine/order_processor.py` | Production | RENAME log message at line 770 (`FleetOrderProcessor` → `OrderProcessor`). Module docstring at line 4 is historical, KEEP |
| `game/strategy/data/order_serializer.py` | Production | RENAME 2 internal class self-references (`FleetOrderSerializer._deserialize_*` → `OrderSerializer._deserialize_*`). Phase 1 discovery |
| `game/strategy/data/fleet.py` | Production | RENAME 7 `FleetOrderSerializer` usages (imports + calls) and 1 `FleetOrder` mention in module docstring |
| `game/strategy/engine/planet_action_engine.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/strategy/engine/planet_command_handlers.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/strategy/facade/strategy_session_facade.py` | Production | RENAME `PlanetOrder` → `Order` |
| `game/strategy/validation/planet_order_validator.py` | Production | RENAME `PlanetOrder` → `Order` (filename stays — see decisions.md) |
| `game/strategy/validation/__init__.py` | Production | RENAME `PlanetOrder` → `Order` |

### EDIT (test renames)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/test_fleet_orders_logic.py` | Test | RENAME class symbols (filename stays) |
| `tests/unit/strategy/engine/test_planet_action_engine.py` | Test | RENAME `PlanetOrder` → `Order` |
| `tests/unit/strategy/engine/test_planet_command_handlers.py` | Test | RENAME |
| `tests/unit/strategy/facade/test_facade_dispatch.py` | Test | RENAME |
| `tests/unit/ui/screens/test_strategy_ui_menu.py` | Test | RENAME `PlanetOrder` → `Order` |
| `tests/unit/ui/screens/test_sub_window_hotkeys.py` | Test | RENAME |
| `tests/unit/ui/screens/test_strategy_window_manager.py` | Test | RENAME |
| `tests/unit/ui/screens/test_strategy_event_router.py` | Test | RENAME |
| `tests/unit/ui/screens/test_fleet_orders_refresh.py` | Test | RENAME class symbols (filename stays) |
| `tests/unit/ui/screens/test_event_log_window.py` | Test | RENAME |
| `tests/unit/ui/screens/test_click_gate_integration.py` | Test | RENAME |
| `tests/integration/ui/test_fleet_build_button.py` | Test | RENAME |
| `tests/integration/save_load/test_roundtrip_orders.py` | Test | RENAME — includes 9 `FleetOrderSerializer` usages plus 11 `FleetOrder`. Phase 1 scope addition |
| `tests/repro_warp_bug.py`, `tests/repro_issues/test_bug_27_ordertype.py` | Test (repro) | RENAME class symbols. Ad-hoc reproducers; low effort |
| Additional test files | Test | Per `findings/rename_plan.md` (phase 1 deliverable). 76 files match `\bFleetOrder\b` alone |

### EDIT (docs)

| File | Type | Notes |
|------|------|-------|
| `docs/03_CONVENTIONS.md` | Docs | Update or remove old-name examples |
| Any other doc flagged by Phase 1 | Docs | Update per `findings/rename_plan.md` |

### NEW (Phase 1 outputs)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-298/findings/usage_inventory.md` | Project artifact | Phase 1 deliverable |
| `Projects/active_projects/PROJ-298/findings/rename_plan.md` | Project artifact | Phase 1 deliverable |

### EXPLICITLY EXCLUDED

- `Projects/deep_archive/**` — historical record, do not modify
- `Reviews/results/**` — frozen review snapshots
- `Tracking/bugs/archived/**`, `Tracking/features/archived/**`, `Tracking/solved_bugs.md` — historical bug/feature records
- `coverage.json` and any other generated reports
- `commands.py:95` `fleet_id` field — see `decisions.md` (out of scope: data-model rename)
- `*.py` files where `fleet_orders` appears only as a lowercase variable/function/file name (e.g., `test_fleet_orders_logic.py` filename, `get_fleet_orders()` method) — these are domain terms, not the deprecated class
