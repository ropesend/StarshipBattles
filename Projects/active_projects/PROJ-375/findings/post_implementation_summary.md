# PROJ-375 Post-Implementation Summary

All 3 phases completed 2026-05-05. 10 of 10 verified-safe items consolidated.

## LOC Delta by Cluster

| ID | Cluster | Files Touched | Delta (approx) |
|----|---------|---------------|----------------|
| DEEP-01-001 | `_find_shield_component_id` deletion | 1 | -4 |
| DUP-X-02 + DUP-X-06 | `iter_facility_ability_entries` helper + 5-engine + planet_action_engine migration | 7 | helper +60 (with tests +110), call sites -90 net |
| DUP-X-01 | `_resolve_player_planet` helper + 7 handler refactor | 3 | helper +25 (with tests +60), handlers -14 |
| Cluster 5 | 4 SetXTarget handlers via `_apply_planet_environmental_target` | 1 | -25 |
| DUP-X-07 + Cluster 11 | 4 superweapon mission handlers via `_emit_validated_order` | 1 | -16 |
| DUP-X-05 | `RaceDescriptionLLMController` `_fields` dict + parameterized methods | 1 | -55 |
| Cluster 29+30 | `_get_ability_info` + `_get_ability_data_from_registry` in harvesting_engine | 1 | -55 |
| DUP-X-03 | 5 workshop dropdown handlers via 2 shared strategy helpers | 1 | -25 |
| DUP-X-04 | `DataListWindowMixin._run_update_template` + filter helpers shared | 3 | -55 |
| Cluster 6 | `_rebuild_modifier_icons_for_item` module-level helper | 1 | -55 |

Net code reduction: roughly **-440 LOC** in production code, partially offset
by shared helper bodies (~+150 LOC across `component_inspector.py`,
`handlers/base.py`, `data_list_window_mixin.py`, `harvesting_engine.py`,
`structure_list_items.py`, and the 2 workshop dispatch helpers). Test coverage
expanded by ~+170 LOC across `test_component_inspector.py` and
`test_base_command_handler.py`.

## Test Verification

Per-phase focused tests:

| Phase | Suites | Result |
|-------|--------|--------|
| 1 | `test_planet_action_engine.py` | 20 passed |
| 2 | `tests/unit/strategy/engine/`, `tests/unit/strategy/services/`, `tests/unit/strategy/test_component_inspector.py` | 1762 passed |
| 3 | `tests/unit/ui/screens/` (excluding race_setup, widgets) | 2907 passed, 1 skipped |

Full sharded suite was **not** run during the project — focused-test
discipline was used per the phase-worker rules to avoid the prior Wave A
hang on `test_sharded.py`.

## Out-of-Scope Discoveries

None. The `Dict` import in `atmosphere_engine.py` was already unused before
the migration; left untouched to avoid drift outside the project's scope.

## Skipped Clusters

None. All 10 verified-safe items consolidated as planned. The two excluded
items (DUP-X-08, DEEP-01-004) were excluded by design before phase work
started; nothing was abandoned mid-phase.
