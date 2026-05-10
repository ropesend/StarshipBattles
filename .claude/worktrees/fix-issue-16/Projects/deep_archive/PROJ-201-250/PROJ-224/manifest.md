# PROJ-224 File Manifest

> Generated during project setup. Used by /proj-parallel for conflict detection.

## Files

| File | Type | Notes |
|------|------|-------|
| **Phase 1: Bug Fixes** | | |
| game/simulation/systems/battle_engine.py | Production | DUP-SYS-004: Extract `_count_alive_teams()` helper, fix derelict counting in `is_battle_over()` and `get_winner()` |
| tests/unit/simulation/systems/test_battle_engine_end_conditions.py | Test | Add/update tests for consistent derelict handling |
| tests/unit/simulation/systems/test_battle_engine_tick.py | Test | May need updates for team-alive counting changes |
| **Phase 2: Shared Utilities** | | |
| game/core/protocols.py | Production | DUP-CEA-001: Keep canonical `_has_attrs()` here; make it importable |
| game/ai/protocols.py | Production | DUP-CEA-001: Remove duplicate `_has_attrs()`, import from core |
| game/simulation/interfaces/entity_protocols.py | Production | DUP-SIM-004: Remove duplicate `_has_attrs()`, import from core |
| game/simulation/interfaces/ability_protocols.py | Production | DUP-SIM-004: Remove duplicate `_has_attrs()`, import from core |
| game/core/string_utils.py | Production | DUP-XL-009: New file — `display_name()` and `slugify()` utilities |
| game/ui/panels/modifier_impact_grid.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/ui/panels/ship_detail_panel.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/ui/screens/strategy_detail_fmt.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/ui/screens/builder/right_panel.py | Production | DUP-XL-009: Replace 4 occurrences of `replace('_', ' ').title()` with `display_name()` |
| game/ui/screens/test_lab/screen.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/ui/screens/test_lab/test_run_details.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/simulation/components/modifier_introspection.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/simulation/components/abilities/colonize.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/core/constants.py | Production | DUP-SCR-009: Add `EARTH_MASS = 5.972e24` constant |
| tests/unit/core/test_protocols.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_build_queue_source.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_build_context.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_galaxy.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_population_model.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_facility_construction_queue.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/unit/strategy/data/test_facility_resource_tracking.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/facade/test_system_queries.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/facade/test_system_dto.py | Test | DUP-SCR-009: Replace 5 hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/facade/test_empire_dto.py | Test | DUP-SCR-009: Replace 2 hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/turn_engine/test_resupply.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/transfer/conftest.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/strategy/test_resupply_system.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| tests/integration/save_load/test_resupply_persistence.py | Test | DUP-SCR-009: Replace hardcoded `5.972e24` with `EARTH_MASS` |
| game/core/hex_math.py | Production | DUP-SD-03: Add `hex_from_dict_safe()` utility for try/except deserialization |
| tests/unit/core/test_hex_math_core.py | Test | DUP-SD-03: Add tests for `hex_from_dict_safe()` |
| game/strategy/systems/race_library.py | Production | DUP-SS-04: Replace `_slugify()` with shared `slugify()` |
| game/strategy/systems/design_library.py | Production | DUP-SS-04: Replace `_sanitize_design_id()` with shared `slugify()` |
| tests/unit/strategy/systems/test_race_library.py | Test | DUP-SS-04: May need updates for slugify refactor |
| tests/unit/strategy/design_library/test_basics.py | Test | DUP-SS-04: May need updates for slugify refactor |
| game/core/math.py | Production | DUP-XL-007: Add `angle_from_vector()` or similar atan2-to-degrees utility |
| game/simulation/components/abilities/weapons.py | Production | DUP-XL-007: Replace inline atan2-to-degrees with utility |
| game/ai/controller.py | Production | DUP-XL-007: Replace inline atan2-to-degrees with utility; DUP-SYS-003: Update BattleConfig import |
| game/ai/combat_utils.py | Production | DUP-XL-007: Replace inline atan2-to-degrees with utility |
| game/simulation/combat/weapon_firing_system.py | Production | DUP-XL-007: Replace inline atan2-to-degrees with utility |
| **Phase 3: Constants & Naming Cleanup** | | |
| game/ai/behaviors.py | Production | DUP-CEA-002: Remove `TICK_DURATION` class constants, use `PhysicsConfig.TICK_RATE` directly |
| tests/unit/ai/test_behavior_units.py | Test | DUP-CEA-002: May need updates for TICK_DURATION removal |
| game/simulation/entities/projectile.py | Production | DUP-CEA-005: Replace inline angle normalization with `angle_diff` or math utility |
| game/core/config.py | Production | DUP-SYS-003: Rename `BattleConfig` class to `CombatConstants` |
| game/core/__init__.py | Production | DUP-SYS-003: Update `BattleConfig` export to `CombatConstants` |
| game/engine/collision.py | Production | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| game/simulation/systems/battle_engine.py | Production | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| game/simulation/projectile_manager.py | Production | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| tests/unit/core/test_config.py | Test | DUP-SYS-003: Update `BattleConfig` references to `CombatConstants` |
| tests/unit/ai/test_ai_controller_unit.py | Test | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| tests/unit/ai/test_ai_controller_interface.py | Test | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| tests/unit/simulation/test_projectile_manager.py | Test | DUP-SYS-003: Update `BattleConfig` import to `CombatConstants` |
| game/strategy/quickstart_builder.py | Production | DUP-CEA-006: Replace raw `json.load()` with `json_utils.load_json()` |
| **Phase 4: Minor Cleanup** | | |
| game/simulation/battle_controller.py | Production | DUP-SYS-007: Route state capture through BattleStateManager |
| game/simulation/managers/battle_state_manager.py | Production | DUP-SYS-007: Ensure state capture is the single source of truth |
| game/simulation/services/battle_service.py | Production | DUP-SYS-008: Extract "no active battle" guard helper (5 occurrences) |
| game/ui/services/ship_io.py | Production | DUP-UIS-004: Extract shared ships folder path property |
| game/ui/screens/strategy_window_manager.py | Production | DUP-SCR-006: Evaluate facade-or-session dispatch dedup |
| game/ui/screens/build_queue_screen.py | Production | DUP-SCR-006: Evaluate facade-or-session dispatch dedup |
| game/ui/screens/empire_build_queue_window.py | Production | DUP-SCR-006: Evaluate facade-or-session dispatch dedup |
| game/ui/screens/strategy_build_queue_manager.py | Production | DUP-SCR-006: Evaluate facade-or-session dispatch dedup |
| tests/unit/simulation/battle_controller/test_state.py | Test | DUP-SYS-007: May need updates for state capture routing |
| tests/unit/simulation/battle_controller/test_execution.py | Test | DUP-SYS-007: May need updates for state capture changes |
| tests/unit/simulation/services/test_battle_service.py | Test | DUP-SYS-008: May need updates for guard refactor |
| **Additional files edited** | | |
| game/ui/panels/race_summary_panel.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/strategy/generation/storm_generator.py | Production | DUP-XL-009: Replace `replace('_', ' ').title()` with `display_name()` |
| game/strategy/data/planet_physics.py | Production | DUP-SCR-009: MASS_EARTH now aliases EARTH_MASS from core |
| game/ui/screens/planet_list_filters.py | Production | DUP-SCR-009: Replace hardcoded 5.97e24 with EARTH_MASS |
| docs/03_CONVENTIONS.md | Documentation | DUP-SYS-003: Update BattleConfig reference to BattleTuning |
| tests/unit/core/test_string_utils.py | Test | NEW: Tests for display_name() and slugify() |
| tests/unit/core/test_constants.py | Test | DUP-SCR-009: Add EARTH_MASS tests |
| tests/unit/core/test_simulation_constants.py | Test | DUP-CEA-003: Add TICKS_PER_SECOND derivation test |
| tests/unit/core/test_math_vector2.py | Test | DUP-XL-007: Add angle_from_vector tests |
