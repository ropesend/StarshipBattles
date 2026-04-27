# PROJ-298 — Phase 1 Usage Inventory

**Generated:** 2026-04-26 (Phase 1 Task 1.1)
**Methodology:** Word-boundary regex grep across `game/` + `tests/`. Excluded `.venv/`, `Projects/deep_archive/`, `Reviews/`, `Tracking/`, `coverage.json`, and any `__pycache__/`.

---

## Symbol Counts (production + test source)

| Symbol | Files | Occurrences | Notes |
|--------|-------|-------------|-------|
| `\bFleetOrder\b` | 76 | 582 | Largest surface — bulk of the rename work |
| `\bPlanetOrder\b` | 4 | 29 | Confined to planet-action code paths |
| `\bClearFleetOrdersCommand\b` | 7 | 29 | Production + test mix |
| `\bDeleteFleetOrderCommand\b` | 4 | 10 | Production + test mix |
| `\bReorderFleetOrderCommand\b` | 4 | 10 | Production + test mix |
| `\bFleetOrdersWindow\b` | 6 | 24 | UI screen class symbol; tests + the shim itself |
| `\bFleetOrderSerializer\b` | 4 | ~22 | **DISCOVERED Phase 1** — additional alias in `order_serializer.py:235`. Not in original plan scope but required for completeness |
| `\bFleetOrderProcessor\b` | 1 (file: `order_processor.py`) | 2 | One docstring comment (history; KEEP) + one log-message string at line 770 (rename to `OrderProcessor`) |

**Approximate total source-tree old-name occurrences:** ~684 across ~85 unique files (some files match multiple symbols).

---

## Alias Declarations to Delete (revised — 6 sites, not 5)

| # | Symbol | File | Line | Notes |
|---|--------|------|------|-------|
| 1 | `FleetOrder = Order` | `game/strategy/data/order_types.py` | 170 | Original scope |
| 2 | `PlanetOrder = Order` | `game/strategy/data/order_types.py` | 171 | Original scope |
| 3 | `ClearFleetOrdersCommand = ClearOrdersCommand` | `game/strategy/engine/commands.py` | 100 | Original scope |
| 4 | `DeleteFleetOrderCommand = DeleteOrderCommand` | `game/strategy/engine/commands.py` | 289 | Original scope |
| 5 | `ReorderFleetOrderCommand = ReorderOrderCommand` | `game/strategy/engine/commands.py` | 305 | Original scope |
| 6 | **`FleetOrderSerializer = OrderSerializer`** | `game/strategy/data/order_serializer.py` | **235** | **NEW — discovered Phase 1** |

Plus the package-level re-export in `game/strategy/__init__.py`:
- Line 13 — docstring mention "OrderType, FleetOrder - Fleet movement orders"
- Line 34 — `from game.strategy.data.order_types import OrderType, Order, FleetOrder  # FleetOrder alias for compat`
- Line 64 — `'FleetOrder',  # PROJ-238: backward compat alias` in `__all__`

These three lines are removed when the `FleetOrder` symbol is fully migrated.

---

## Modules to Delete

| File | Lines | Notes |
|------|-------|-------|
| `game/ui/screens/fleet_orders_window.py` | 8 | Re-export shim. `from game.ui.screens.orders_window import *  # noqa: F401,F403` + `FleetOrdersWindow = OrdersWindow` |

---

## Production Files to Edit (RENAME)

Sorted by symbol density. Each file's specific rename targets are listed.

### Heavy hitters (multiple symbols / many occurrences)

| File | FleetOrder | PlanetOrder | Clear* | Delete* | Reorder* | FleetOrdersWindow | FleetOrderSerializer | Notes |
|------|-----------|-------------|--------|---------|----------|-------------------|---------------------|-------|
| `game/strategy/data/order_types.py` | 3 | 1 | – | – | – | – | 1 (docstring) | Alias declarations + historical docstrings |
| `game/strategy/data/order_serializer.py` | – | – | – | – | – | – | 3 | Alias declaration + 2 self-references in class methods |
| `game/strategy/data/fleet.py` | 1 | – | – | – | – | – | 7 | All `FleetOrderSerializer` usages |
| `game/strategy/engine/order_processor.py` | – | – | – | – | – | – | – + 2 (FleetOrderProcessor) | Comment + log-message string |
| `game/strategy/engine/commands.py` | – | – | 2 | 2 | 2 | – | – | Alias declarations + comments |
| `game/strategy/engine/command_handlers.py` | – | – | 5 | 5 | 5 | – | – | All three command-name old uses |
| `game/strategy/engine/planet_command_handlers.py` | – | 2 | – | – | – | – | – | PlanetOrder usage |
| `game/strategy/engine/planet_action_engine.py` | – | 6 | – | – | – | – | – | PlanetOrder usage |
| `game/strategy/__init__.py` | 3 | – | – | – | – | – | – | Re-export (lines 13, 34, 64) |
| `game/ui/screens/strategy_window_manager.py` | – | – | 2 | 2 | 2 | – | – | UI command refs |
| `game/ui/screens/orders_window.py` | – | – | – | – | – | 3 | – | Internal `FleetOrdersWindow` reference |
| `game/ui/screens/fleet_orders_window.py` | – | – | – | – | – | 2 | – | The shim itself (DELETE) |
| `game/strategy/data/fleet.py` (header docstring) | 1 | – | – | – | – | – | inc above | History note in module docstring |

### Other production files (lower density — see grep for specifics)

`game/ui/screens/strategy_event_router.py`, `game/ui/screens/strategy_screen.py`, `game/ui/screens/strategy_fleet_command_router.py`, `game/ui/screens/planet_abilities_window.py`, `game/strategy/facade/strategy_session_facade.py`, `game/strategy/validation/planet_order_validator.py`, `game/strategy/validation/__init__.py` — each has 1–10 hits, mostly `PlanetOrder` references.

---

## Test Files to Edit (RENAME)

The grep returned 76 files matching `\bFleetOrder\b`, mostly in tests. Top hits:

### Highest density (15+ occurrences)
- `tests/unit/strategy/engine/test_superweapon_order_processor.py` — 28
- `tests/unit/strategy/engine/test_superweapon_edge_cases.py` — 21
- `tests/unit/strategy/engine/test_action_execution_engine.py` — 22
- `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` — 20
- `tests/integration/strategy/test_fleet_navigation_consistency.py` — 19
- `tests/unit/strategy/test_fleet_order_processor.py` — 15
- `tests/unit/strategy/fleet/test_serialization.py` — 17
- `tests/integration/strategy/test_fleet_join_redirect.py` — 16
- `tests/unit/strategy/test_fleet_orders_logic.py` — 13
- `tests/integration/strategy/test_superweapon_integration.py` — 13
- `tests/unit/strategy/turn_engine/test_turn_processing.py` — (count from grep)
- `tests/integration/strategy/test_warp_orders.py` — 5
- `tests/unit/strategy/fleet/test_basics.py` — 31
- `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py` — 31
- `tests/integration/strategy/test_strategy_scene.py` — 5
- `tests/integration/strategy/turn_engine/test_basics.py` — 11
- `tests/unit/strategy/data/test_superweapon_orders.py` — 8

### Test files with `FleetOrderSerializer`
- `tests/integration/save_load/test_roundtrip_orders.py` — 9 usages

### Test files with `FleetOrdersWindow`
- `tests/unit/ui/screens/test_sub_window_hotkeys.py` — 7
- `tests/unit/ui/screens/test_fleet_orders_refresh.py` — 8
- `tests/unit/ui/screens/test_strategy_window_manager.py` — 1
- `tests/integration/ui/test_fleet_build_button.py` — 3

### Test files with `PlanetOrder`
- `tests/unit/strategy/engine/test_planet_action_engine.py` — 20

### Test files with the command aliases
- `tests/integration/strategy/test_command_handlers.py` — 9 (Clear) + 1 (Delete?) + 1 (Reorder?)
- `tests/integration/strategy/test_commands.py` — 6
- `tests/unit/strategy/test_command_handlers.py` — 1 each
- `tests/unit/strategy/engine/test_commands.py` — 4 (Clear)

### `repro_*` files (root-level test reproducers)
- `tests/repro_warp_bug.py` — 3 hits (FleetOrder)
- `tests/repro_issues/test_bug_27_ordertype.py` — 5 hits (FleetOrder)

---

## [KEEP] — Hits NOT to rename

These match the search but should NOT be touched:

### Variable / function / lowercase domain names containing `fleet_orders`
- Test filenames: `test_fleet_orders_logic.py`, `test_fleet_orders_refresh.py`, `test_fleet_order_processor.py`, `test_fleet_order_resolution.py`, `test_fleet_order_transfer.py`, `test_advanced_fleet_orders.py`, `test_build_order.py`, `test_build_order_processor.py`, `test_build_order_command_handler.py` — these test domains, not the deprecated class. Filenames stay.
- Production files: nothing under this rule applies (the `fleet_orders_window.py` is itself the shim being deleted).
- Variable names like `fleet.orders`, `fleet_orders`, method names — domain term. Keep.

### Historical docstring comments (PROJ-238 rename history)
- `game/strategy/data/order_types.py:5` — `PROJ-238: Renamed FleetOrder -> Order. Unified with PlanetOrderType.` — historical, KEEP
- `game/strategy/data/order_types.py:77` — `PROJ-238: Renamed from FleetOrder. Used by both fleets and planets.` — historical, KEEP
- `game/strategy/data/fleet.py:23` — `# PROJ-238: FleetOrder renamed to Order` — historical, KEEP
- `game/strategy/engine/commands.py:93, 281, 296` — `PROJ-238: Renamed from ClearFleetOrdersCommand` etc. — historical, KEEP

### Files referencing `FleetOrderProcessor` historically only
- `game/strategy/engine/order_processor.py:4` — module docstring `PROJ-238: Renamed from FleetOrderProcessor.` — historical, KEEP
- `game/strategy/engine/order_processor.py:770` — `logger.debug(f"FleetOrderProcessor [Instant]: ...")` — RENAME this log message to `OrderProcessor` (it's a runtime log, not a history note)

### Filename `planet_order_validator.py`
- The file's class operates on `Order` instances. The filename describes the *domain* (validates planet orders). KEEP filename per decisions.md.

---

## Repro / experimental file decisions

`tests/repro_warp_bug.py` and `tests/repro_issues/test_bug_27_ordertype.py` are not under `tests/unit/` or `tests/integration/`. They appear to be ad-hoc reproducers. Phase 3 decision: rename old-name imports to new-name (low effort). If they're scheduled for deletion in some future cleanup, that's a separate issue.

---

## Out-of-Scope Reminders

Per decisions.md:
- `commands.py:95` `fleet_id: int  # Kept for backward compat; use entity_id for new code` — DATA-MODEL backward-compat marker. Out of scope.
- `Tracking/`, `Reviews/results/`, `Projects/deep_archive/`, `coverage.json` — historical record. Do not modify.
- `*.py` files where `fleet_orders` appears only as a lowercase variable/function/file name — domain term, KEEP.

---

## Phase 1 Outcome

**Total `[RENAME]` files:** ~85
**Total `[RENAME]` occurrences:** ~684
**Aliases to delete:** 6 (was 5 in original scope; +1 discovered: `FleetOrderSerializer`)
**Modules to delete:** 1 (`fleet_orders_window.py`)
**Package re-exports to remove:** 1 (`game/strategy/__init__.py` `FleetOrder`)
**Filename renames:** 0 (decisions.md scopes class symbols only)
