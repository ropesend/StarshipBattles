# PROJ-298 — Phase 1 Rename Plan

**Generated:** 2026-04-26 (Phase 1 Task 1.3)
**Source:** `usage_inventory.md`
**Methodology:** Word-boundary regex grep across `game/` + `tests/`. Use the rules in `usage_inventory.md` § "[KEEP]" to skip non-rename hits.

---

## Standard rename mapping

| Old | New |
|-----|-----|
| `FleetOrder` | `Order` |
| `PlanetOrder` | `Order` |
| `ClearFleetOrdersCommand` | `ClearOrdersCommand` |
| `DeleteFleetOrderCommand` | `DeleteOrderCommand` |
| `ReorderFleetOrderCommand` | `ReorderOrderCommand` |
| `FleetOrdersWindow` | `OrdersWindow` |
| **`FleetOrderSerializer`** (Phase 1 discovery) | `OrderSerializer` |
| `FleetOrderProcessor` (only line 770 log message) | `OrderProcessor` |

For module-path imports: `from game.ui.screens.fleet_orders_window import X` → `from game.ui.screens.orders_window import X`.

For `from game.strategy import ...`: drop `FleetOrder` from the import list (the `__init__.py` re-export is removed in Phase 4).

---

## Per-area execution order

Phases 2 (production) and 3 (tests) follow the order below. Within each subsection, work top-to-bottom.

### Phase 2: Production renames

#### 2.1 Strategy data layer
1. `game/strategy/data/order_serializer.py` — replace 2 internal class self-references (`FleetOrderSerializer._deserialize_*`) with `OrderSerializer._deserialize_*`. The alias declaration at line 235 is kept until Phase 4.
2. `game/strategy/data/fleet.py` — rename 7 `FleetOrderSerializer` usages (imports + calls) and the FleetOrder mention in line 23/4 docstring.

#### 2.2 Strategy engine layer
3. `game/strategy/engine/commands.py` — alias declarations stay (Phase 4); the class definition docstrings already use the new names.
4. `game/strategy/engine/command_handlers.py` — replace 5x each of `Clear/Delete/ReorderFleetOrders*Command`.
5. `game/strategy/engine/order_processor.py` — line 770 log message: `FleetOrderProcessor` → `OrderProcessor`. Module docstring at line 4 is historical — KEEP.
6. `game/strategy/engine/planet_command_handlers.py` — replace 2x `PlanetOrder`.
7. `game/strategy/engine/planet_action_engine.py` — replace 6x `PlanetOrder`.

#### 2.3 Strategy facade + validation
8. `game/strategy/facade/strategy_session_facade.py` — `PlanetOrder` references.
9. `game/strategy/validation/__init__.py` — `PlanetOrder` references.
10. `game/strategy/validation/planet_order_validator.py` — `PlanetOrder` references. Filename stays.

#### 2.4 UI screens
11. `game/ui/screens/strategy_window_manager.py` — 2x each of Clear/Delete/Reorder + 2x FleetOrdersWindow.
12. `game/ui/screens/orders_window.py` — 3x internal `FleetOrdersWindow` references.
13. `game/ui/screens/strategy_event_router.py` — `PlanetOrder` references.
14. `game/ui/screens/strategy_screen.py` — old-name references.
15. `game/ui/screens/strategy_fleet_command_router.py` — `PlanetOrder` references.
16. `game/ui/screens/planet_abilities_window.py` — `PlanetOrder` references.
17. `game/ui/screens/fleet_orders_window.py` — DO NOT EDIT. Whole file is deleted in Phase 4.

#### 2.5 Strategy package init
18. `game/strategy/__init__.py` — remove the `FleetOrder` import (line 34), the `'FleetOrder'` entry in `__all__` (line 64), and the docstring mention (line 13).

After Phase 2: only the alias declarations themselves and the `fleet_orders_window.py` shim should still reference the old names in production source.

---

### Phase 3: Test renames

Group test renames by directory; tests in the same directory share imports and fixtures.

#### 3.1 Unit/strategy core
- `tests/unit/strategy/test_fleet_order_processor.py` (15)
- `tests/unit/strategy/test_fleet_orders_logic.py` (13) — class symbols rename; filename stays
- `tests/unit/strategy/test_advanced_fleet_orders.py` (5)
- `tests/unit/strategy/test_engine_event_emission.py` (8)
- `tests/unit/strategy/conflict_resolution/test_core.py` (2)
- `tests/unit/strategy/turn_engine/test_turn_processing.py` (1)
- `tests/unit/strategy/turn_engine/test_tick_mechanics.py` (9)
- `tests/unit/strategy/turn_engine/conftest.py` (1)
- `tests/unit/strategy/data/test_empire_fleet_registration.py` (7)
- `tests/unit/strategy/data/test_fleet_order_resolution.py` (5)
- `tests/unit/strategy/data/test_superweapon_orders.py` (8)

#### 3.2 Unit/strategy engine
- `tests/unit/strategy/engine/test_action_execution_engine.py` (22)
- `tests/unit/strategy/engine/test_superweapon_order_processor.py` (28)
- `tests/unit/strategy/engine/test_superweapon_edge_cases.py` (21)
- `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (1)
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (1)
- `tests/unit/strategy/engine/test_transfer_order.py` (10)
- `tests/unit/strategy/engine/test_fleet_order_transfer.py` (3)
- `tests/unit/strategy/engine/test_fleet_movement_engine.py` (5)
- `tests/unit/strategy/engine/test_process_colonize_validation.py` (7)
- `tests/unit/strategy/engine/test_colonize_population.py` (7)
- `tests/unit/strategy/engine/test_colonize_mission_handler.py` (2)
- `tests/unit/strategy/engine/test_build_order_processor.py` (6)
- `tests/unit/strategy/engine/test_movement_build_blocking.py` (5)
- `tests/unit/strategy/engine/test_build_order_command_handler.py` (4)
- `tests/unit/strategy/engine/test_planet_action_engine.py` (20 — `PlanetOrder`)
- `tests/unit/strategy/engine/test_commands.py` (4 — `ClearFleetOrdersCommand`)

#### 3.3 Unit/strategy fleet/services/facade/movement
- `tests/unit/strategy/fleet/test_basics.py` (31)
- `tests/unit/strategy/fleet/test_serialization.py` (17)
- `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py` (31)
- `tests/unit/strategy/fleet/test_build_order.py` (10)
- `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` (20)
- `tests/unit/strategy/services/test_action_time_resolver.py` (10)
- `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` (7)
- `tests/unit/strategy/fleet_navigation/test_projection.py` (10)
- `tests/unit/strategy/fleet_navigation/test_navigation_pure.py` (6)
- `tests/unit/strategy/fleet_navigation/test_destination_path.py` (10)
- `tests/unit/strategy/fleet_navigation/test_data_structures.py` (2)
- `tests/unit/strategy/fleet_movement_engine/test_warp.py` (5)
- `tests/unit/strategy/fleet_movement_engine/test_batch.py` (6)
- `tests/unit/strategy/fleet_movement_engine/test_basics.py` (5)
- `tests/unit/strategy/facade/test_empire_dto.py` (2)
- `tests/unit/strategy/facade/test_fleet_dto_build.py` (4)
- `tests/unit/strategy/facade/test_fleet_dto.py` (4)

#### 3.4 Unit/UI screens
- `tests/unit/ui/screens/test_fleet_orders_refresh.py` (11 FleetOrder + 8 FleetOrdersWindow)
- `tests/unit/ui/screens/test_sub_window_hotkeys.py` (7 FleetOrdersWindow)
- `tests/unit/ui/screens/test_strategy_window_manager.py` (1 FleetOrdersWindow)

#### 3.5 Unit/strategy commands
- `tests/unit/strategy/test_command_handlers.py` (1 each of Clear/Delete/Reorder)

#### 3.6 Integration
- `tests/integration/strategy/test_command_handlers.py` (8 + 9 Clear)
- `tests/integration/strategy/test_commands.py` (1 + 6 Clear)
- `tests/integration/strategy/test_fleet_navigation_consistency.py` (19)
- `tests/integration/strategy/test_fleet_join_redirect.py` (16)
- `tests/integration/strategy/test_superweapon_integration.py` (13)
- `tests/integration/strategy/test_strategy_scene.py` (5)
- `tests/integration/strategy/test_warp_orders.py` (5)
- `tests/integration/strategy/test_system_destruction.py` (5)
- `tests/integration/strategy/test_stabilizer_blocks_superweapon.py` (4)
- `tests/integration/strategy/test_fleet_registration_lifecycle.py` (6)
- `tests/integration/strategy/test_path_projection.py` (3)
- `tests/integration/strategy/turn_engine/test_resupply.py` (1)
- `tests/integration/strategy/turn_engine/test_resources.py` (5)
- `tests/integration/strategy/turn_engine/test_basics.py` (11)
- `tests/integration/strategy/production/test_fleet_save_load.py` (4)
- `tests/integration/strategy/production/test_fleet_production_e2e.py` (5)
- `tests/integration/strategy/facade/test_facade_integration.py` (1)
- `tests/integration/ui/test_fleet_build_button.py` (4 FleetOrder + 3 FleetOrdersWindow)
- `tests/integration/ui/test_colonization_facade.py` (1)
- `tests/integration/save_load/test_roundtrip_orders.py` (11 FleetOrder + 9 FleetOrderSerializer)
- `tests/integration/save_load/test_reference_integrity.py` (5)
- `tests/integration/colonization/test_planet_specific_colonization.py` (11)
- `tests/integration/colonization/test_explicit_orders.py` (4)
- `tests/integration/colonization/test_edge_cases.py` (7)
- `tests/integration/gameplay_loop/test_turn_execution.py` (6)
- `tests/integration/gameplay_loop/test_fleet_operations.py` (9)
- `tests/integration/gameplay_loop/test_commands_colonization.py` (6)

#### 3.7 Fixtures
- `tests/fixtures/strategy_entities.py` (4)

#### 3.8 Repro / experimental
- `tests/repro_warp_bug.py` (3)
- `tests/repro_issues/test_bug_27_ordertype.py` (5)

#### 3.9 Notable filename observations (NO RENAME — class symbols only)
- `test_fleet_order_processor.py`, `test_fleet_order_transfer.py`, `test_fleet_order_resolution.py` — describe domain (testing OrderProcessor for fleet orders); filenames stay.
- `test_fleet_orders_logic.py`, `test_fleet_orders_refresh.py`, `test_advanced_fleet_orders.py` — same.

---

## Phase 4: Alias / shim deletions

Order matters — delete only after the matching old-name usages are migrated.

| # | File | Action |
|---|------|--------|
| 1 | `game/strategy/data/order_types.py` | Delete lines 169-171: comment + `FleetOrder = Order` + `PlanetOrder = Order` |
| 2 | `game/strategy/engine/commands.py` | Delete lines 99-100, 288-289, 304-305: 3 comment + alias pairs |
| 3 | `game/strategy/data/order_serializer.py` | Delete lines 234-235: comment + `FleetOrderSerializer = OrderSerializer` |
| 4 | `game/strategy/__init__.py` | Remove `FleetOrder` from import (line 34) and `__all__` (line 64); update docstring (line 13) |
| 5 | `game/ui/screens/fleet_orders_window.py` | DELETE the entire file |

---

## Phase 5: Documentation updates

- `docs/03_CONVENTIONS.md` — § 1.8 already documents the rename; the table reads correctly. Verify "Old backward compatibility alias modules have been deleted" is now factually true (post-Phase 4); no edit needed.
- `docs/systems/orders_system.md` — already uses `Order`/`OrderType`/`OrderProcessor`; no edit needed.
- Other docs — sweep for stragglers via grep in Phase 5.

---

## Recommended execution approach

For each file in the plan:

1. Open the file
2. Use IDE find-and-replace with **Match Case** + **Whole Word**:
   - `FleetOrder` → `Order` (most files)
   - `PlanetOrder` → `Order`
   - `ClearFleetOrdersCommand` → `ClearOrdersCommand`
   - `DeleteFleetOrderCommand` → `DeleteOrderCommand`
   - `ReorderFleetOrderCommand` → `ReorderOrderCommand`
   - `FleetOrdersWindow` → `OrdersWindow`
   - `FleetOrderSerializer` → `OrderSerializer`
3. Skim the diff to confirm no `[KEEP]` comments were modified accidentally
4. Run targeted tests for the file's directory: `pytest tests/<dir>/ --testmon`
5. Move to next file

Alternative: scripted bulk replacement via Python with word-boundary regex, then manual review of the diff. Faster but riskier; use only after the manual approach has been done on a few files to confirm no surprises.

The "manual via IDE find-and-replace" approach is **strongly preferred** — the cost of corrupting 1 of 600 occurrences is far higher than the cost of doing 85 file edits.
