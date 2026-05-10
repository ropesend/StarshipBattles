# PROJ-345 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/engine/test_production_engine_queue.py` | Test (rewrite line 293) | T3.1 — `<= 10` → `== 10` plus counter assertion |
| `tests/unit/strategy/engine/test_consumable_management_engine/test_characterization.py` | Test (add) | T3.2 — multi-component auto-disable test |
| `tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py` | Test (NEW or extend) | T3.3 — direct-coverage characterization |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test (rewrite lines 54-101) | T3.4 — un-patch `_load_and_create_ship`/`_create_and_place_facility`/`_spawn_fleet_ship`; assert per-method outputs |
| `tests/unit/strategy/engine/test_production_engine*.py` | Test (add) | T3.5 — fleet-context 3rd branch in `_log_resource_shortage` and `_apply_resource_consumption` |
| `Projects/active_projects/PROJ-345/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 1 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/strategy/engine/ -x -q` then `python Tools/lint_test_files.py` |
