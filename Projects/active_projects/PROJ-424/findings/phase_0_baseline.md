# Phase 0 Preflight Baseline (2026-05-17)

## Grep #1: duplicated metadata constants

`rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES|ORDER_TO_ABILITY_MAP" game tests docs`

### Production reader inventory (game/)

`MOVEMENT_ORDER_TYPES` — production readers:
- `game/strategy/services/cargo_transfer_service.py:12,37`
- `game/strategy/services/action_time_resolver.py:24,86`
- `game/strategy/services/fleet_path_projection.py:22,76`
- `game/strategy/services/fleet_navigation_service.py:21`
- `game/strategy/engine/action_execution_engine.py:24,169`
- `game/strategy/data/fleet.py:27` (re-export)
- (definition: `game/strategy/data/order_types.py:70`)

`ACTION_ORDER_TYPES` — production readers:
- `game/strategy/services/fleet_navigation_service.py:21`
- `game/strategy/engine/action_execution_engine.py:25,181`
- `game/strategy/engine/fleet_movement_engine.py:21,275`
- `game/strategy/data/fleet.py:28` (re-export)
- (definition: `game/strategy/data/order_types.py:79`)

`PLANET_ACTION_ORDER_TYPES` — production readers:
- `game/strategy/services/action_time_resolver.py:26,114`
- `game/strategy/engine/planet_action_engine.py:19,131`
- (definition: `game/strategy/data/order_types.py:105`)

`PLANET_FMS_ACTION_ORDER_TYPES` — production readers:
- `game/strategy/engine/action_execution_engine.py:27,268` — only production consumer (confirmed)
- (definition: `game/strategy/data/order_types.py:115`)

`ORDER_TO_ABILITY_MAP` — production readers:
- `game/strategy/services/action_time_resolver.py:35,50,101` — definition + only reader inside same module
- (no other production reader)

`registry.py` references the constant *names* only in docstrings and the `IMPLICIT_ACTION_ORDER_TYPES` (a distinct entity, retained).

### Test imports of duplicated constants

- `tests/unit/strategy/fleet_movement_engine/test_characterization.py:18,108` — `ACTION_ORDER_TYPES`
- `tests/unit/strategy/test_fleet_order_processor.py:431,436,439` — `ACTION_ORDER_TYPES`
- `tests/unit/strategy/services/test_action_time_resolver.py:209,233` — comment refs only (no live import via these names; covered by Phase 3)
- `tests/unit/strategy/data/test_order_types_characterization.py:29-31,74,77,81,84` — all four (`ACTION_ORDER_TYPES`, `MOVEMENT_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, plus assertions)
- `tests/unit/strategy/engine/test_command_specs_contract.py:15-18,28,166,171,176,181` — `ACTION_ORDER_TYPES`, `MOVEMENT_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, `ORDER_TO_ABILITY_MAP`
- `tests/unit/strategy/engine/test_command_registry_contract.py:26-34,90,95-196` — all four constants + `ORDER_TO_ABILITY_MAP`
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py:11-12,24,29` — `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`
- `tests/unit/strategy/engine/test_action_execution_engine.py:507` — comment only

The manifest's 8 test modules cover all of these. No new test files outside the manifest need touches.

### Docs

- `docs/04_SERVICES.md:440-441,884`
- `docs/systems/satellites.md:195,258`
- `docs/systems/orders_system.md:58,66,74,84,109,153,157,343`

## Grep #2: `subcategories=` and `@command_spec(` distribution

`rg -n "subcategories\s*=" game/strategy/engine`:
- only definition site in `game/strategy/engine/commands/registry.py:82,97` (`CommandSpec.subcategories` field).
- **No** handler currently sets `subcategories=`. Phase 1 introduces them.

`@command_spec(` count by file (real decorators at line start, total 40):
- `handlers/build.py`: 2
- `handlers/construction_queue.py`: 4
- `handlers/launch_fighters.py`: 1  (FMS — Phase 1 tag target)
- `handlers/launch_satellites.py`: 1  (FMS — Phase 1 tag target)
- `handlers/lay_mines.py`: 1  (FMS — Phase 1 tag target)
- `handlers/movement.py`: 5
- `handlers/order_queue.py`: 5
- `handlers/recover_fighters.py`: 1  (FMS — Phase 1 tag target)
- `handlers/recover_satellites.py`: 1  (FMS — Phase 1 tag target)
- `handlers/transfer.py`: 1
- `planet_command_handlers.py`: 7
- `superweapon_command_handlers.py`: 11
- TOTAL: 40 specs

TD-03 audit cited 41 DTOs; the 1-spec drift is informational only — Phase 1's "exactly five planet_fms specs" assertion remains correct because the 5 FMS handlers are unambiguously enumerated above.

## Conclusions

- Per-constant reader counts match TD-03 design.md "Consumer Inventory" exactly.
- `PLANET_FMS_ACTION_ORDER_TYPES` has exactly one production consumer (`action_execution_engine.py`).
- No untracked test modules import the duplicated constants — manifest is a superset of the test grep result.
- No `subcategories=` overlap to worry about; the 5 FMS handlers are clean Phase 1 targets.
- Total `@command_spec` count is 40, not 41 — `manifest.md` already documents "exactly 5 planet_fms specs"; that count is correct regardless.

**No production edits this phase.** Inventory only.
