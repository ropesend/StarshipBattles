# PROJ-264 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/planet_command_handlers.py` | Production (read-only) | Target for coverage; no changes expected |
| `game/strategy/validation/planet_order_validator.py` | Production (read-only) | Target for coverage; no changes expected |
| `game/strategy/engine/order_processor.py` | Production (read-only) | Target for coverage; no changes expected |
| `game/strategy/facade/strategy_session_facade.py` | Production (read-only) | Target for coverage; no changes expected |
| `tests/unit/strategy/engine/test_planet_command_handlers.py` | Test | **New** -- Phase 1: ~22 tests for 4 handler classes |
| `tests/unit/strategy/validation/test_planet_order_validator.py` | Test | **New** -- Phase 1: ~25 tests for validator + _facility_has_ability |
| `tests/unit/strategy/engine/test_fleet_transfer_extended.py` | Test | **New** -- Phase 2: ~20 tests for fleet transfer + resource cargo + BUG-70 |
| `tests/unit/strategy/engine/test_staging_yard_operations.py` | Test | **New** -- Phase 2: ~14 tests for staging yard load/unload |
| `tests/unit/strategy/facade/test_facade_dispatch.py` | Test | **New** -- Phase 3: ~36 tests for 31 dispatch methods + build queue queries |

## Conflict Notes

- This project creates **5 new test files only**; no production files are modified.
- No overlap with any other active project since all files are new.
- The production files are read-only targets -- if another project modifies them, tests here may need updating but the scope of this project does not change.
