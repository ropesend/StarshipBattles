# PROJ-333 — File Manifest

All paths are repo-relative.

## Production files (read-only — characterized, not modified)

| File | LOC | Existing test coverage |
|---|---:|---|
| `game/strategy/engine/production_engine.py` | 666 | Partial: `test_production_refactor.py`, `test_production_repro.py`, `test_production_math.py` (math + smoke) |
| `game/strategy/engine/production_spawner.py` | 413 | Partial: `test_production_spawner_staging_yard.py` |
| `game/strategy/engine/consumable_management_engine.py` | 164 | Partial: `tests/unit/strategy/consumable_management_engine/` (initialization / consumption / auto_disable) |
| `game/strategy/engine/fleet_movement_engine.py` | 360 | Partial: `tests/unit/strategy/fleet_movement_engine/` (basics / batch / warp) plus integration `test_fleet_movement.py` |
| `game/strategy/engine/order_processor.py` | 910 | Minimal: only `test_order_processor_fleet_merge.py` — TRANSFER / COLONIZE / staging-yard load-unload paths NOT covered |

**Total in-scope production LOC:** 2,513.

## New test files (created by Phase 1)

| File | Engine covered | Notes |
|---|---|---|
| `tests/unit/strategy/engine/test_production_engine_queue.py` | `production_engine.py` | Queue-tick processing, validation, expenditure, completion. |
| `tests/unit/strategy/engine/test_production_engine_consumption.py` | `production_engine.py` | Affordability routing, resource consumption, shortage logging. |
| `tests/unit/strategy/engine/test_production_spawner.py` | `production_spawner.py` | Spawn dispatch, ship/complex creation, staging yard. |
| `tests/unit/strategy/consumable_management_engine/test_characterization.py` | `consumable_management_engine.py` | Pin remaining surface gaps not covered by the 3 existing files. |
| `tests/unit/strategy/fleet_movement_engine/test_characterization.py` | `fleet_movement_engine.py` | Pin speed-modifier truncation, collect-vs-apply ordering, jump-past filter. |
| `tests/unit/strategy/engine/test_order_processor_colonize.py` | `order_processor.py` | COLONIZE happy / unhappy / drop-pod deploy. |
| `tests/unit/strategy/engine/test_order_processor_transfer.py` | `order_processor.py` | TRANSFER / LOAD / UNLOAD across planet + fleet targets. |
| `tests/unit/strategy/engine/test_order_processor_instant.py` | `order_processor.py` | `process_instant_orders` Phase A/B/C, mutual-pair election, cancellation events. |

**Total new test files:** 8 (production_engine split 2-way; order_processor split 3-way).

## Files NOT modified

- All five production files in `game/strategy/engine/` listed above.
- All existing test files; new tests sit alongside, not in replacement.
- `turn_engine.py`, `action_execution_engine.py`, `superweapon_order_processor.py`, `build_order_processor.py` — out of scope for this project.
