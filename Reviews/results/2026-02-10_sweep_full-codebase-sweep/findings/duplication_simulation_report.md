# Duplication & Fragmentation Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 72
- **Total Issues Found:** 10
- **Critical:** 3 | **Major:** 4 | **Minor:** 3 | **Info:** 0

## Findings

#### CRITICAL: Duplicated Ability Aggregation Logic
**ID:** DUP-SIM-001
**Location:** `game/simulation/entities/ability_aggregator.py:70-148` (calculate_ability_totals) AND `game/simulation/entities/ability_aggregator.py:165-229` (calculate_ability_totals_for_layer)
**Issue:** Two functions are ~85% duplicate. Both build identical nested dict structures, iterate components → ability_instances, extract values with get_primary_value(), and call shared _aggregate_ability_groups() helper. The only difference is calculate_ability_totals_for_layer() adds layer/scope filtering before aggregation.
**Impact:** Bug fix in aggregation logic needs to be applied to both functions. Active divergence in layer/scope filtering logic.
**Recommendation:** Refactor to single calculate_ability_totals() with optional layer=None, scope_filter=None parameters.
**Effort:** Medium

#### CRITICAL: Near-Duplicate ResourceConsumption Extraction Pattern
**ID:** DUP-SIM-002
**Location:** `game/simulation/entities/combat_endurance.py:36-79` AND `game/simulation/entities/ship_stats.py:274-295`
**Issue:** Identical pattern for extracting resource consumption abilities from components. Different variable names (ab vs ability, c vs comp) but same logic. combat_endurance.py also has hand-rolled WeaponAbility lookup that needs sharing.
**Impact:** Bug creep in weapon lookup logic. Copy-paste drift with different variable names reduces clarity.
**Recommendation:** Extract ability filtering pattern into utility function: get_ability_instances_by_class(components, class_name).
**Effort:** Simple

#### CRITICAL: Modifier Effect Validation Duplication
**ID:** DUP-SIM-003
**Location:** `game/simulation/components/modifier_schema.py:52-160` AND `game/simulation/components/modifier_effects.py:254-309`
**Issue:** modifier_schema.py contains 4 validation functions for V2 format (52 lines). modifier_effects.py contains validate_formula() and validate_modifier_definition() (50+ lines). Both validate the SAME modifier definitions but use different validation logic. No single source of truth.
**Impact:** Data integrity risk - modifiers may pass one validator but fail the other.
**Recommendation:** Consolidate all modifier validation into modifier_effects.py and have modifier_schema.py delegate.
**Effort:** Medium

#### MAJOR: Ability Instance Retrieval Pattern Duplicated
**ID:** DUP-SIM-004
**Location:** `game/simulation/components/component.py:191-223` AND `game/simulation/components/ability_manager.py:30-104`
**Issue:** Component delegates to AbilityManager for retrieval, but both implement similar caching/fallback logic. AbilityManager has __name__ fallback (lines 57-65) marked as KNOWN_ISSUE/tech debt. Three layers of fallbacks makes debugging hard.
**Impact:** Test infrastructure issues surfaced in production code via __name__ fallback pattern.
**Recommendation:** Fix test module reload issue at source, eliminate __name__ fallback. Simplify to single index → isinstance → error flow.
**Effort:** Complex

#### MAJOR: Component Status Checking Pattern Repeated 8+ Times
**ID:** DUP-SIM-005
**Location:** `game/simulation/combat/weapon_firing_system.py:68,75` AND `game/simulation/entities/ship_stats.py:269,395,424,432,438` AND `game/simulation/entities/ship.py:267` AND `game/simulation/entities/combat_endurance.py:86` AND `game/simulation/combat/damage_calculator.py:43`
**Issue:** Pattern "check if component is active, then process" appears identically in 8+ files. This cross-cutting concern has no central place to modify activation logic.
**Impact:** No central place to modify activation logic. Cognitive overhead from repeated conditional.
**Recommendation:** Create Ship.iter_active_components() iterator method.
**Effort:** Simple

#### MAJOR: Ability Value Extraction Pattern (get_primary_value)
**ID:** DUP-SIM-006
**Location:** `game/simulation/entities/ability_aggregator.py:99-114` AND `game/simulation/entities/ship_stat_querier.py:76-77` AND `game/simulation/entities/combat_endurance.py:144-147`
**Issue:** Three different files extract ability values using get_primary_value() with slightly different aggregation (stack_group handling, simple sum, DPS calculation). No single way to aggregate ability values.
**Impact:** Unclear which aggregation approach is "correct" for different contexts. Risk of inconsistency if ability definitions change.
**Recommendation:** Create AbilityAggregationStrategy with sum_values, max_values_per_group, multiply_across_groups methods.
**Effort:** Medium

#### MAJOR: Serialization Stat Verification Logic
**ID:** DUP-SIM-007
**Location:** `game/simulation/entities/ship_serialization.py:208-241`
**Issue:** 30+ lines of stat verification logic that could drift from expected_stats definition elsewhere. While delegation pattern is good, the stat verification is not centralized.
**Impact:** Stat mismatches could go undetected if verification logic diverges.
**Recommendation:** Ensure integration test coverage for stat mismatch detection.
**Effort:** Simple

#### MINOR: Validation Rule Duplication Pattern
**ID:** DUP-SIM-008
**Location:** `game/simulation/validation/ship_validator.py:54-85`
**Issue:** Three rule classes (LayerConstraintRule, UniqueComponentRule, ExclusiveGroupRule) share identical structure with repeated _should_validate boilerplate.
**Impact:** Low (already using template method pattern well).
**Recommendation:** Extract common _should_validate patterns into base class helper.
**Effort:** Simple

#### MINOR: Distance/Position Calculation Patterns
**ID:** DUP-SIM-009
**Location:** `game/simulation/combat/targeting_system.py:30-77` AND `game/simulation/entities/ship_physics.py`
**Issue:** solve_lead() implements quadratic formula for projectile interception (48 lines). Similar distance calculations appear elsewhere for shield projection, weapon range, proximity targeting.
**Impact:** Low (solve_lead is specialized), but duplicated distance logic elsewhere should be unified.
**Recommendation:** Create physics utility module with common calculations.
**Effort:** Simple

#### MINOR: Resource Consumption Tracking Duplicated
**ID:** DUP-SIM-010
**Location:** `game/simulation/entities/combat_endurance.py:18-99` AND `game/simulation/systems/resource_manager.py`
**Issue:** combat_endurance.py manually calculates fuel/ammo/energy consumption (82 lines). ResourceManager also tracks consumption. The two systems are parallel but not unified.
**Impact:** Dual tracking creates maintenance burden.
**Recommendation:** Delegate consumption calculation to ResourceManager; have combat_endurance query results.
**Effort:** Medium

## Top 5 Priority Issues
1. **DUP-SIM-001: Ability Aggregation Duplication** - Active divergence in calculation logic, affects stats/damage/targeting
2. **DUP-SIM-002: ResourceConsumption Extraction** - Bug creep in combat-critical weapon lookup logic
3. **DUP-SIM-003: Modifier Validation Duplication** - Data integrity issues if validators diverge
4. **DUP-SIM-005: Component Status Checking** - Scattered cross-cutting concern across 8+ call sites
5. **DUP-SIM-004: Ability Retrieval Fallback** - Test infrastructure debt surfaced in production code
