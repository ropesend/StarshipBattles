# Test Coverage Gaps Sweep: Simulation

## Summary
- **Shard:** Simulation (`game/simulation/` and all subdirectories)
- **Production Files Scanned:** 76
- **Test Files Cross-Referenced:** 46 (unit) + 32 (simulation_tests) + relevant integration tests
- **Total Issues Found:** 27
- **Critical:** 5 | **Major:** 11 | **Minor:** 8 | **Info:** 3

## Production-to-Test Mapping

### Files WITH test coverage:
| Production File | Test File(s) |
|---|---|
| `battle_controller.py` | `battle_controller/test_config.py`, `test_initialization.py`, `test_execution.py`, `test_mechanics.py`, `test_state.py`, `test_utilities.py` |
| `battle_config.py` | `test_battle_config.py` |
| `battle_state.py` | `test_battle_state_manager.py` (partial) |
| `formula_system.py` | `test_formula_exceptions.py` |
| `physics_constants.py` | `test_physics_constants.py` |
| `combat/damage_calculator.py` | `combat/test_damage_calculator.py` |
| `combat/targeting_system.py` | `combat/test_targeting_system.py` |
| `combat/weapon_firing_system.py` | `combat/test_weapon_firing_system.py` |
| `combat/battle_mode_handler.py` | `combat/test_battle_mode_handlers.py` |
| `managers/retreat_manager.py` | `test_retreat_manager.py` |
| `managers/battle_state_manager.py` | `test_battle_state_manager.py` |
| `entities/ship_combat_engine.py` | `ship_combat_engine/test_creation_and_lead.py`, `test_targeting.py`, `test_combat_ops.py` |
| `entities/projectile.py` | `projectile_guidance/test_guidance_core.py`, `test_guidance_behavior.py` |
| `services/design_loader.py` | `test_simulation_design_loader.py` |
| `services/registry_loader.py` | `services/test_registry_loader.py` |
| `factories/ai_factory.py` | `factories/test_ai_factory.py` |
| `interfaces/ai_controller.py` | `interfaces/test_ai_controller_interface.py` |
| `validation/base.py` | `validation/test_base_rule.py` |
| `validation/ship_validator.py` | `test_layer_restriction_rule_refactor.py` |
| `systems/battle_end_conditions.py` | `systems/test_battle_end_conditions.py`, `test_battle_engine_end_conditions.py` |
| `systems/battle_engine.py` | `systems/test_battle_engine_end_conditions.py` |
| `systems/resource_manager.py` | `systems/test_resource_manager_edge_cases.py` |
| `entities/ship_stats.py` | `systems/test_ship_stats_calculator_phases.py`, `test_ship_stats_phase_ordering.py` |
| `components/ability_manager.py` | `components/test_ability_manager.py` |
| `components/modifier_manager.py` | `components/test_modifier_manager.py` |
| `components/modifiers.py` | `components/test_modifiers.py` |
| `components/modifier_schema.py` | `components/test_modifier_schema.py` |
| `components/modifier_effects.py` | `components/test_modifier_effects.py` |
| `components/component_constants.py` | `components/test_component_constants.py` |
| `components/component_stats_calculator.py` | `components/test_component_stats_calculator.py` |
| `components/abilities/markers.py` | `components/abilities/test_markers.py` |
| `components/abilities/stat_keys.py` | `components/abilities/test_stat_keys.py` |
| `components/abilities/superweapons.py` | `components/abilities/test_superweapons.py` |

### Files with NO dedicated test file:
| Production File | Public API Size | Severity |
|---|---|---|
| `entities/ship.py` | Very large (god class, ~500+ lines) | Via integration tests only |
| `entities/ship_physics.py` | 3 public methods | MAJOR |
| `entities/ship_formation.py` | 8 public methods | MAJOR |
| `entities/ship_loader.py` | 4 public functions | MAJOR |
| `entities/ship_serialization.py` | 6 public methods | MAJOR |
| `entities/ship_stat_querier.py` | 5 public methods | MAJOR |
| `entities/ship_validator_helper.py` | 3 public methods | MINOR |
| `entities/ability_aggregator.py` | 4 public functions | CRITICAL |
| `entities/combat_endurance.py` | 2 public functions | MAJOR |
| `entities/layer_data.py` | 4 public methods | MINOR |
| `projectile_manager.py` | 6 public methods | CRITICAL |
| `services/battle_service.py` | 12 public methods | CRITICAL |
| `services/vehicle_design_service.py` | 8 public methods | MAJOR |
| `services/modifier_service.py` | 7 public methods | MAJOR |
| `systems/persistence.py` | 2 public methods | MINOR |
| `systems/tech_preset_loader.py` | 6 public methods | MINOR |
| `designs.py` | 2 factory functions | MINOR |
| `components/modifier_introspection.py` | 5 public methods | MINOR |
| `components/component_health_manager.py` | 3 public methods | MINOR |
| `components/component_resource_manager.py` | 4 public methods | MINOR |
| `components/abilities/base.py` | Large base class | Via subclass tests |
| `components/abilities/weapons.py` | 4 weapon classes | Via simulation_tests |
| `components/abilities/defense.py` | 6 defense classes | Via simulation_tests |
| `components/abilities/propulsion.py` | 3 propulsion classes | Via simulation_tests |
| `components/abilities/resources.py` | 3 resource classes | Via simulation_tests |
| `components/abilities/crew.py` | 3 crew classes | Via simulation_tests |
| `components/abilities/cargo.py` | 2 cargo classes | Partial (test_cargo_storage) |
| `components/abilities/colonize.py` | 1 class | No direct test |
| `components/abilities/harvester.py` | 1 class | No direct test |

---

## Findings

#### CRITICAL: BattleService has no unit tests
**ID:** TCG-SIM-001
**Location:** `game/simulation/services/battle_service.py` (production) / No test file exists
**Issue:** BattleService is the primary abstraction between UI and BattleEngine, with 12 public methods (create_battle, add_ship, remove_ship, start_battle, update, run_ticks, is_battle_over, get_winner, get_battle_state, get_all_ships, get_alive_ships, reset). It has zero dedicated unit tests. The class is only exercised indirectly through BattleController tests and integration tests.
**Impact:** Regressions in battle creation flow, ship management, or state queries could go undetected. Error paths (e.g., creating battle after engine exists, adding ships after start, null engine handling) are not verified.
**Recommendation:** Create `tests/unit/simulation/services/test_battle_service.py` covering: create_battle success/failure, add_ship before/after start, remove_ship, start_battle with no ships, update when not started, run_ticks with battle-over short circuit, get_battle_state with/without engine, reset.
**Effort:** Medium

#### CRITICAL: ProjectileManager has no unit tests
**ID:** TCG-SIM-002
**Location:** `game/simulation/projectile_manager.py` (production) / No test file exists
**Issue:** ProjectileManager handles projectile updates, collision detection (ship collisions, missile interception), and damage application. Its `_check_ship_collisions` method contains a complete dynamic collision detection algorithm (sweep test with relative velocity). None of this is unit-tested. The only coverage is via full simulation_tests which exercise it indirectly.
**Impact:** Collision detection bugs, missed hits, phantom hits, incorrect damage application, and projectile lifetime bugs could all go undetected. The sweep collision math is particularly fragile and untested.
**Recommendation:** Create `tests/unit/simulation/test_projectile_manager.py` covering: add/get/clear projectiles, update with expired projectiles, ship collision detection (direct hit, near miss, relative velocity), missile interception, damage application via _apply_hit, record_hit weapon stat updates.
**Effort:** Complex

#### CRITICAL: AbilityAggregator has no unit tests
**ID:** TCG-SIM-003
**Location:** `game/simulation/entities/ability_aggregator.py` (production) / No test file exists
**Issue:** The ability aggregation system (`calculate_ability_totals`, `get_ability_total`, `get_ability_instances_by_class`, `_aggregate_ability_groups`) is a foundational piece of the stat calculation pipeline. It implements a two-phase aggregation (MAX within group, SUM/MULTIPLY across groups) that is critical to correct stat computation. There are NO dedicated unit tests for these functions.
**Impact:** Incorrect ability stacking (e.g., shield capacity, sensor scores, ECM) would cascade through all ship stats. The MULTIPLICATIVE_ABILITIES and MARKER_ABILITIES special cases are completely untested at the unit level. Layer filtering and scope filtering paths are untested.
**Recommendation:** Create `tests/unit/simulation/entities/test_ability_aggregator.py` covering: single component simple ability, multiple components same ability summing, stack_group MAX within group, stack_group SUM across groups, MULTIPLICATIVE_ABILITIES multiply behavior, MARKER_ABILITIES boolean behavior, layer filtering, scope filtering, empty components list, mixed dict/instance abilities.
**Effort:** Medium

#### CRITICAL: ShipPhysicsMixin has no unit tests
**ID:** TCG-SIM-004
**Location:** `game/simulation/entities/ship_physics.py` (production) / No test file exists
**Issue:** ShipPhysicsMixin implements core ship movement physics including `update_physics_movement` (thrust/coast physics with dynamic thrust calculation from operational engines), `thrust_forward`, and `rotate`. The physics formulas involve K_SPEED, K_THRUST constants and mass-based calculations. None of these are unit-tested.
**Impact:** Physics bugs (e.g., ships not decelerating properly, incorrect max speed calculation from dynamic thrust, division by zero with zero mass) would affect all combat gameplay. The dynamic thrust path where `get_total_ability_value('CombatPropulsion', operational_only=True)` is called is untested at the mixin level.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship_physics.py` covering: thrust_forward sets flag, update_physics_movement with thrust (verify acceleration, max speed capping), update_physics_movement coasting (deceleration to zero), rotate left/right, physics with zero mass, throttle effects, position update from velocity.
**Effort:** Medium

#### CRITICAL: ShipFormation has no unit tests
**ID:** TCG-SIM-005
**Location:** `game/simulation/entities/ship_formation.py` (production) / No test file exists
**Issue:** ShipFormation manages formation relationships (master/member, join/leave, add_member/remove_member) with 8 public methods and properties. Only covered by `tests/integration/test_formation_flight.py` and `test_formation_attack.py` integration tests, but those test the full formation-in-combat pipeline, not individual formation state management.
**Impact:** Formation state corruption (e.g., member not removed from master's list on leave, double-join creating duplicates) could cause combat AI errors. The bidirectional references (member.master -> master, master.members -> [member]) are particularly error-prone without isolated tests.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship_formation.py` covering: is_master/is_member properties, join adds to master.members, leave removes from master.members, add_member/remove_member, double-join idempotency, leave when not in formation.
**Effort:** Simple

#### MAJOR: ShipSerializer has no dedicated unit tests
**ID:** TCG-SIM-006
**Location:** `game/simulation/entities/ship_serialization.py` (production) / No dedicated test file
**Issue:** ShipSerializer handles to_dict/from_dict for Ship objects including layer serialization, component loading with modifiers, resource restoration, and stat verification. While indirectly tested via simulation_tests and save/load integration tests, there are no unit tests for individual methods like `_load_components`, `_restore_resources`, `_verify_stats`, or round-trip serialization.
**Impact:** Serialization bugs (e.g., missing modifiers during load, incorrect stat verification tolerances, layer skipping logic) could cause design corruption or silent data loss.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship_serialization.py` covering: to_dict produces expected structure, from_dict creates valid ship, round-trip (to_dict -> from_dict) preserves all data, modifier persistence, resource restoration, stat verification with mismatches, error handling for invalid data.
**Effort:** Medium

#### MAJOR: VehicleDesignService has no unit tests
**ID:** TCG-SIM-007
**Location:** `game/simulation/services/vehicle_design_service.py` (production) / No test file exists
**Issue:** VehicleDesignService (formerly ShipBuilderService) provides 8 public methods: create_ship, add_component, add_component_instance, add_component_bulk, remove_component, change_class, validate_design, get_available_components, get_layer_info, get_ship_summary. This is the primary service for the ship design workshop UI. Zero unit tests exist.
**Impact:** Design operations (add/remove components, class changes, validation) could break without detection. The add_component_bulk partial-success path and change_class migration logic are untested.
**Recommendation:** Create `tests/unit/simulation/services/test_vehicle_design_service.py` covering all public methods with success and error paths.
**Effort:** Medium

#### MAJOR: ModifierService has no unit tests
**ID:** TCG-SIM-008
**Location:** `game/simulation/services/modifier_service.py` (production) / No test file exists
**Issue:** ModifierService has 7 public methods (is_modifier_allowed, get_mandatory_modifiers, is_modifier_mandatory, get_initial_value, ensure_mandatory_modifiers, get_local_min_max) plus MANDATORY_MODIFIERS constant. These control modifier validation and auto-application during ship design. No unit tests exist.
**Impact:** Modifiers could be incorrectly allowed/denied, mandatory modifiers might not auto-apply, and turret_mount min/max constraints could be wrong. The complex get_initial_value logic with different modifier types is completely untested.
**Recommendation:** Create `tests/unit/simulation/services/test_modifier_service.py` covering: is_modifier_allowed with various restriction types, get_mandatory_modifiers returns all applicable, get_initial_value for each modifier type, ensure_mandatory_modifiers auto-applies, get_local_min_max turret constraint logic.
**Effort:** Medium

#### MAJOR: CombatEndurance calculations have no unit tests
**ID:** TCG-SIM-009
**Location:** `game/simulation/entities/combat_endurance.py` (production) / No test file exists
**Issue:** `calculate_combat_endurance` and `_calculate_cached_summary` compute fuel/ammo/energy endurance times, net energy rates, DPS, and cached summary stats. These calculations are critical for ship comparison and combat balance. No unit tests exist.
**Impact:** Incorrect endurance calculations would mislead players about ship capabilities and affect AI decision-making. The edge cases (zero consumption, infinite endurance, negative energy net) are particularly important.
**Recommendation:** Create `tests/unit/simulation/entities/test_combat_endurance.py` covering: fuel endurance with/without consumption, ammo endurance, energy endurance (draining vs sustainable), DPS calculation, inf handling, zero-division protection, cached summary structure.
**Effort:** Simple

#### MAJOR: ShipStatQuerier has no unit tests
**ID:** TCG-SIM-010
**Location:** `game/simulation/entities/ship_stat_querier.py` (production) / No test file exists
**Issue:** ShipStatQuerier provides get_ability_total, get_total_ability_value, get_total_sensor_score, get_total_ecm_score, max_weapon_range, and cached_summary. These are the primary stat query methods used throughout the codebase. No unit tests.
**Impact:** Stat queries returning wrong values would cascade through combat resolution, UI displays, and AI decisions. The max_weapon_range calculation with SeekerWeaponAbility fallback (speed * endurance) is untested.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship_stat_querier.py` testing each method with mock ships/components.
**Effort:** Simple

#### MAJOR: ShipLoader functions have no dedicated unit tests
**ID:** TCG-SIM-011
**Location:** `game/simulation/entities/ship_loader.py` (production) / No test file exists
**Issue:** `load_vehicle_classes_data`, `load_vehicle_classes`, `initialize_ship_data`, and `get_or_create_validator` are critical bootstrap functions. `load_vehicle_classes_data` handles JSON loading, layer configuration resolution, and deep copy. Only exercised via conftest fixtures.
**Impact:** Vehicle class loading bugs (e.g., layer_config resolution, missing files, malformed JSON) could cause game startup failures that are hard to diagnose.
**Recommendation:** Create `tests/unit/simulation/entities/test_ship_loader.py` covering: load_vehicle_classes_data with valid file, missing file, layer_config resolution, get_or_create_validator singleton behavior.
**Effort:** Simple

#### MAJOR: DamageCalculator _damage_layer weighted random selection untested
**ID:** TCG-SIM-012
**Location:** `game/simulation/combat/damage_calculator.py:93-129` / `tests/unit/simulation/combat/test_damage_calculator.py`
**Issue:** The `_damage_layer` method uses `random.choices` with weights based on component HP for random damage distribution. While tests exist for the overall damage pipeline, the weighted random selection behavior is not statistically tested. There are no tests verifying that: (a) higher-HP components are more likely to be hit, (b) destroyed components are skipped, (c) damage continues to next component when one is depleted.
**Impact:** Could silently change damage distribution without detection. Weighted selection is a core combat mechanic.
**Recommendation:** Add statistical tests with fixed random seed verifying damage distribution follows HP weighting, and tests with multiple components at various HP levels.
**Effort:** Simple

#### MAJOR: BattleState serialization round-trip not tested
**ID:** TCG-SIM-013
**Location:** `game/simulation/battle_state.py` (production) / `tests/unit/simulation/test_battle_state_manager.py` (partial coverage)
**Issue:** BattleState, ShipState, ProjectileState, ComponentState, and BattleResults all have to_dict/from_dict/to_json/from_json methods. While BattleStateManager has tests for capture/restore config, there are NO tests for the round-trip serialization of these state objects: to_dict -> from_dict should produce identical objects. ShipState.from_ship() and ProjectileState.from_projectile() are also untested.
**Impact:** Save/load corruption could go undetected. The complex nested state (BattleState -> ShipState -> ComponentState) with projectile references makes this particularly fragile.
**Recommendation:** Create comprehensive round-trip tests for all state dataclasses, particularly ComponentState modifiers, ShipState position/velocity tuples, and ProjectileState ship reference resolution.
**Effort:** Medium

#### MINOR: Abilities base class (Ability) has no isolated unit tests
**ID:** TCG-SIM-014
**Location:** `game/simulation/components/abilities/base.py` (production) / No test file for base class
**Issue:** The Ability base class defines the interface all abilities implement (get_primary_value, get_consumed_stats, get_effect_summary, recalculate, applies_to_layer, etc.) plus STAT_BINDINGS processing. Only tested through concrete subclasses in simulation_tests. The STAT_BINDINGS machinery (get_effective_stat, apply_stat_bindings) is not independently verified.
**Impact:** Changes to the base class could break all abilities without triggering specific subclass tests.
**Recommendation:** Create `tests/unit/simulation/components/abilities/test_base_ability.py` testing: get_primary_value default, STAT_BINDINGS processing, applies_to_layer filtering, get_consumed_stats enumeration.
**Effort:** Simple

#### MINOR: ColonizeAbility and HarvesterAbility have no tests
**ID:** TCG-SIM-015
**Location:** `game/simulation/components/abilities/colonize.py`, `harvester.py` / No test files
**Issue:** ColonizeAbility and HarvesterAbility are strategic-layer abilities with no dedicated tests. While they may be exercised through integration tests, their individual behavior (resource type, rate, capacity) is not verified.
**Impact:** Low risk since these are simple data-carrying abilities, but changes to their constructor or get_primary_value could break strategy integration.
**Recommendation:** Add minimal tests in `tests/unit/simulation/components/abilities/` for each.
**Effort:** Simple

#### MINOR: ModifierIntrospection has no unit tests
**ID:** TCG-SIM-016
**Location:** `game/simulation/components/modifier_introspection.py` / No test file exists
**Issue:** ModifierIntrospection provides 5 static methods for UI introspection (get_modifier_affects, get_component_modifier_summary, get_ability_modifier_summary, generate_modifier_tooltip, generate_ability_stats_display). No unit tests.
**Impact:** UI tooltip and modifier display bugs. Lower severity since it's presentation-only, not game logic.
**Recommendation:** Create basic tests verifying output structure of each method.
**Effort:** Simple

#### MINOR: ComponentHealthManager has no unit tests
**ID:** TCG-SIM-017
**Location:** `game/simulation/components/component_health_manager.py` / No test file exists
**Issue:** Extracted health management (take_damage, reset_hp, hp_ratio caching) has no dedicated tests. The damage threshold status update and hp_ratio cache invalidation are untested at this level.
**Impact:** Low since the Component class tests exercise these paths, but the extracted helper should have its own tests for isolation.
**Recommendation:** Create `tests/unit/simulation/components/test_component_health_manager.py`.
**Effort:** Simple

#### MINOR: ComponentResourceManager has no unit tests
**ID:** TCG-SIM-018
**Location:** `game/simulation/components/component_resource_manager.py` / No test file exists
**Issue:** Extracted resource management (can_afford_activation, consume_activation, try_activate, get_resource_cost) has no dedicated tests. The formula-based resource cost calculation is untested at this level.
**Impact:** Resource consumption bugs could affect combat pacing and weapon firing.
**Recommendation:** Create `tests/unit/simulation/components/test_component_resource_manager.py`.
**Effort:** Simple

#### MINOR: TechPresetLoader has no unit tests
**ID:** TCG-SIM-019
**Location:** `game/simulation/systems/tech_preset_loader.py` / No test file exists
**Issue:** TechPresetLoader provides 6 static methods for managing tech presets in standalone workshop mode. No unit tests exist.
**Impact:** Low since this is only used in standalone workshop mode, not core gameplay.
**Recommendation:** Create minimal tests with mock preset JSON files.
**Effort:** Simple

#### MINOR: LayerData has no unit tests
**ID:** TCG-SIM-020
**Location:** `game/simulation/entities/layer_data.py` / No test file exists
**Issue:** LayerData dataclass with create_hull, from_definition, and clear methods has no dedicated tests. Used everywhere layers are initialized.
**Impact:** Low since it's a simple dataclass, but from_definition defaults could silently change.
**Recommendation:** Create simple tests for factory methods and clear behavior.
**Effort:** Simple

#### INFO: Weapon ability classes tested primarily through simulation_tests
**ID:** TCG-SIM-021
**Location:** `game/simulation/components/abilities/weapons.py` (WeaponAbility, BeamWeaponAbility, ProjectileWeaponAbility, SeekerWeaponAbility)
**Issue:** Weapon abilities have no dedicated unit tests. Coverage comes from `simulation_tests/tests/test_beam_weapons.py`, `test_projectile_weapons.py`, `test_seeker_weapons.py`, and `test_defense.py`. These are good integration-level tests but don't test individual ability methods in isolation (e.g., `get_damage` with formula evaluation, `check_firing_solution` with various angles, `can_fire` cooldown logic).
**Impact:** Individual method bugs are harder to isolate. Formula-based damage (`=50 + range_to_target * 0.1`) is only tested through full battle simulation.
**Recommendation:** Consider adding unit tests for edge cases: zero range, formula evaluation errors, firing arc boundary conditions, negative damage formulas.
**Effort:** Medium

#### INFO: Defense ability classes tested primarily through simulation_tests
**ID:** TCG-SIM-022
**Location:** `game/simulation/components/abilities/defense.py` (ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor, CrystallineArmor, Armor, ShipRepair)
**Issue:** Defense abilities have no dedicated unit tests in `tests/unit/`. Coverage from `simulation_tests/tests/test_defense.py` and `tests/unit/simulation/armor_mechanics/`. Individual ability constructor parsing and recalculate methods are not individually tested.
**Impact:** Changes to defense ability calculations could produce subtly wrong values.
**Recommendation:** Consider unit tests for ability constructors with various input formats (dict, number, shortcut).
**Effort:** Simple

#### INFO: ShipIO (persistence.py) inherently difficult to unit test
**ID:** TCG-SIM-023
**Location:** `game/simulation/systems/persistence.py`
**Issue:** ShipIO uses Tkinter file dialogs which cannot be unit tested without complex mocking. The Tkinter initialization at module load time also causes issues in test environments.
**Impact:** Low since this is UI-bound I/O code. Integration testing through save/load tests provides adequate coverage.
**Recommendation:** No action needed. Consider extracting the serialization logic (already done in ShipSerializer) from the file-dialog logic if refactoring.
**Effort:** N/A

#### MAJOR: No tests for BattleEngine.update tick processing
**ID:** TCG-SIM-024
**Location:** `game/simulation/systems/battle_engine.py` / `tests/unit/simulation/systems/test_battle_engine_end_conditions.py`
**Issue:** BattleEngine's `update()` method processes a full combat tick: spatial grid update, AI controller updates, ship physics/weapons/abilities, attack processing (beams, projectiles, launches), collision handling, and projectile management. The existing test file only tests end conditions, not the core tick loop. The full tick processing is only exercised through simulation_tests.
**Impact:** Individual tick processing bugs (e.g., order-of-operations issues between AI, weapons, and movement) would only surface in full simulation scenarios, making them hard to isolate.
**Recommendation:** Add unit tests for BattleEngine.update() covering: AI update called for each ship, ship update called, attacks processed, projectiles updated, spatial grid refreshed. Mock subsystems to test orchestration logic.
**Effort:** Complex

#### MAJOR: No boundary tests for physics formula calculations
**ID:** TCG-SIM-025
**Location:** `game/simulation/entities/ship_stats.py:220-246` (_phase_physics_and_limits)
**Issue:** Physics formulas (`acceleration = thrust * K_THRUST / mass^2`, `turn_speed = raw_turn * K_TURN / mass^1.5`, `max_speed = thrust * K_SPEED / mass`) are tested via `test_ship_stats_calculator_phases.py` and `test_ship_stats_phase_ordering.py` but lack boundary tests. Edge cases not tested: very small mass (near-zero causing extreme acceleration), very large mass (potential float overflow in mass^1.5), zero thrust with non-zero mass, zero mass (division by zero), extremely high thrust values.
**Impact:** Edge case physics bugs could cause ships to teleport, have infinite speed, or NaN values in combat.
**Recommendation:** Add boundary test cases in existing test file or new `test_ship_stats_boundaries.py`: mass=0, mass=0.001, mass=999999, thrust=0, thrust=999999, all zeros.
**Effort:** Simple

#### MAJOR: No tests for resource consumption during combat ticks
**ID:** TCG-SIM-026
**Location:** `game/simulation/components/abilities/resources.py` (ResourceConsumption.update), `game/simulation/systems/resource_manager.py` (ResourceRegistry.update)
**Issue:** While `test_resource_manager_edge_cases.py` tests edge cases of ResourceRegistry, and `simulation_tests/tests/test_resource_consumption.py` runs full simulations, there are no unit tests for the per-tick resource consumption flow: Component.update() -> ResourceConsumption.update() -> check has_sufficient -> consume. The interaction between consumption triggers (constant, activation, strategic_per_hex) and the resource registry is untested at the unit level.
**Impact:** Resource consumption bugs would affect combat pacing (ships running out of fuel too fast/slow, weapons firing without ammo).
**Recommendation:** Create unit tests for ResourceConsumption.update with each trigger type, testing the full flow from ability to registry consumption.
**Effort:** Medium

#### MAJOR: ShipCombatEngine combat cooldowns only partially tested
**ID:** TCG-SIM-027
**Location:** `game/simulation/entities/ship_combat_engine.py:161-232` / `tests/unit/simulation/ship_combat_engine/test_combat_ops.py`
**Issue:** `update_combat_cooldowns` handles shield regeneration (with energy cost check) and repair application. While test_combat_ops.py exists, it doesn't comprehensively test: shield regen with insufficient energy, repair targeting most-damaged component, repair restoring component status when HP exceeds threshold, repair with zero repair_rate, regen capping at max_shields.
**Impact:** Shield/repair imbalance in combat. Energy-gated shield regen is a key balancing mechanic that needs thorough testing.
**Recommendation:** Add specific tests for each branch in update_combat_cooldowns and _apply_repair to test_combat_ops.py.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-SIM-001 (CRITICAL): BattleService has no unit tests** - Primary battle management service with 12 public methods and zero tests. This is the gateway for all battle operations and should be the first service to get comprehensive tests.

2. **TCG-SIM-002 (CRITICAL): ProjectileManager has no unit tests** - Contains a collision detection algorithm (sweep test with relative velocity) that is mathematically complex and completely untested. Collision bugs directly affect combat outcomes.

3. **TCG-SIM-003 (CRITICAL): AbilityAggregator has no unit tests** - Foundational stat aggregation with two-phase logic (MAX within group, SUM/MULTIPLY across groups). Affects every ship stat calculation in the game.

4. **TCG-SIM-004 (CRITICAL): ShipPhysicsMixin has no unit tests** - Core movement physics with dynamic thrust calculations. Physics bugs affect all combat gameplay and are notoriously subtle.

5. **TCG-SIM-024 (MAJOR): BattleEngine.update tick processing has no tests** - The main combat loop orchestrating AI, weapons, movement, and collisions is only tested through full simulations, making individual bugs extremely hard to isolate.
