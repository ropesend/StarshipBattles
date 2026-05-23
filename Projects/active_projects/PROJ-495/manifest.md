# PROJ-495 File Manifest

> Used by /proj-parallel for conflict detection.
> All paths re-verified against the live tree on 2026-05-23.
> No production-code changes expected; this project edits test files only.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/simulation/combat/test_weapon_firing_system.py | Test | Phase 1 (T1.16 _make_ship_mock factory) |
| tests/unit/simulation/combat/test_damage_calculator.py | Test | Phase 1 (T1.21 use existing mock_ship factory in later test classes) |
| tests/unit/ai/test_ai_controller_unit.py | Test | Phase 2 (T2.5 3+4 nested patches + _make_ai_controller helper) |
| tests/unit/simulation/entities/test_ship_stats.py | Test | Phase 2 (T2.8 43-line setup → fixture) |
| tests/unit/strategy/data/test_container.py | Test | Phase 2 (T2.11 inline 5 wrapper functions); path retargeted from `tests/unit/strategy/test_container.py` |
| tests/unit/strategy/engine/test_resupply_engine.py | Test | Phase 2 (T2.12 9 mock factories → conftest); coordinates with DUP-005/HLP-006 in PROJ-479 |
| tests/unit/strategy/services/test_fleet_navigation_action_timing.py | Test | Phase 2 (T2.23 2-level nested patch helper) |
| tests/unit/simulation/systems/test_tech_preset_loader.py | Test | Phase 2 (T2.29 identical patch wrapper → autouse fixture); path retargeted from `tests/unit/strategy/data/` |
| tests/regression/test_deprecated_code_removed.py | Test | Phase 3 (T3.3 4+4 hasattr-deletion parametrize) |
| tests/unit/strategy/test_engine_event_emission.py | Test | Phase 3 (T3.6 9 event-emission parametrize) |
| tests/unit/strategy/data/test_squadron_characterization.py | Test | Phase 3 (T3.7 5 roundtrip parametrize) |
| tests/unit/simulation/entities/test_ship_physics.py | Test | Phase 3 (T3.8 4 velocity-by-angle parametrize) |
| tests/unit/simulation/ship_combat_engine/test_cooldowns.py | Test | Phase 3 (T3.9 5 shield-regen parametrize) |
| tests/unit/modifiers/test_invalid_operation_handling.py | Test | Phase 3 (T3.11 4 operation-type parametrize) |
| tests/unit/simulation/entities/test_ship_fleet_attrs.py | Test | Phase 3 (T3.17 2 test pairs parametrize) |
| tests/unit/strategy/fleet_navigation/test_destination_path.py | Test | Phase 3 (T3.18 NavigationState parametrized fixture) |
| tests/unit/strategy/engine/test_production_engine_queue.py | Test | Phase 3 (T3.24 2 resources_consumed parametrize) |
| tests/unit/strategy/engine/test_planet_energy_engine.py | Test | Phase 3 (T3.25 4 generator/cap/no-gen/shield-drain parametrize) |
| tests/unit/strategy/facade/test_fleet_dto.py | Test | Phase 3 (T3.27 2 immutable-tuple parametrize) |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | Phase 3 (T3.28 5 roundtrip parametrize); coordinates with DUP-003 in PROJ-479 |
| tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py | Test | Phase 3 (T3.35 3 setup-shared parametrize); path retargeted from `tests/unit/strategy/services/` |
| tests/unit/strategy/fleet/test_warp_resources.py | Test | Phase 3 (T3.39 3 warp_resource_costs parametrize) |
| tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py | Test | Phase 3 (T3.42 5 TestStabilizerCancellation parametrize) |
| tests/unit/simulation/systems/test_tick_phases.py | Test | Phase 3 (T3.44 3 registry-read parametrize) |
| tests/unit/strategy/engine/test_superweapon_command_handlers.py | Test | Phase 3 (T3.46 5 handler-class parametrize) |
| tests/unit/strategy/validation/test_superweapon_validator.py | Test | Phase 3 (T3.47 5 validator-class clusters parametrize) |
| tests/unit/strategy/empire/test_empire_validation.py | Test | Phase 3 (T3.48 3 missing-field PersistenceException parametrize) |
| tests/unit/strategy/engine/test_base_command_handler.py | Test | Phase 3 (T3.49 2 resolve_fleet parametrize) |
| tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py | Test | Phase 4 (T4.3 exact 7-key dict → key-presence) |
| tests/unit/builder/test_ship_loading.py | Test | Phase 4 (T5.1 logic-heavy validation body → parametrize) |
| tests/unit/strategy/services/test_empire_economy_caching.py | Test | Phase 4 (T5.2 repeated scenario unpack → fixture) |
| tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py | Test | Phase 4 (T5.15 remove meta-test imports) |
| tests/unit/strategy/engine/conftest.py | Test infra | READ-ONLY — verify before adding helpers (already has `make_mock_empire`, `mock_empire_factory`) |
| tests/conftest.py | Test infra | READ-ONLY — verify before adding helpers (already has `_make_mock_fleet`, `_assert_roundtrip_property`, `make_mock_ship_instance`) |

## Dropped from PROJ-480 deferred list

| Task | File | Reason |
|------|------|--------|
| (none at scaffold time) | — | All tasks in this scope verified live by Codex spot-check 2026-05-23. Phase 0 may surface additional drops after re-grep. |
