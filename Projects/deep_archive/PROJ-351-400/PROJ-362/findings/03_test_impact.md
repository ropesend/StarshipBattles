# Test Impact Analysis: system_effects_collector Decomposition

## 1. Test Files Importing system_effects_collector

| File | Import Type | Key Tests |
|------|-------------|-----------|
| tests/unit/strategy/services/test_system_effects_collector.py | Direct import | 41 tests covering collect_system_effects, collect_sector_effects, helpers, activation states |
| tests/integration/strategy/test_fleet_sector_effects_end_to_end.py | Direct import | 6 scenarios: fleet flagship effects, enemy/ally filtering, fleet mobility |
| tests/integration/strategy/test_fleet_through_unstable_warp_point.py | Via system iteration | Fleet effects across warp boundaries |
| tests/integration/strategy/test_stabilizer_blocks_superweapon.py | Via system iteration | Stabilizer integration with combat engine |
| tests/unit/strategy/engine/test_environmental_hazard_engine.py | Via environmental_damage | Storm damage rate application |
| tests/unit/strategy/engine/test_owned_sector_effects_filter.py | Via sector filtering | Owner-aware scopes (allied/enemy/player) |
| tests/unit/strategy/fleet_movement_engine/test_characterization.py | Via fleet abilities | Fleet-at-hex effect rendering |

**Total:** 41 tests in dedicated module.

## 2. _aggregate() Branch Coverage

### A. Owner Filtering (Lines 297-299)
**Status:** COVERED - test_no_owned_colonies_returns_empty, test_facility_provider_has_universal_fields
**Gap:** No explicit test for mismatched empire_id rejection

### B. Hex Affinity Check (Lines 304-312)
**Status:** COVERED (partial) - test_collect_sector_effects_returns_storm_abilities_with_nonzero_system_origin
**Gap:** No test for affects_hex exception handling or False return

### C. get_abilities() Error Path (Lines 314-320)
**Status:** NOT COVERED
**Gap:** Must add test for exception catch & logging; currently implicit in integration tests

### D. PROJ-300 D17 Ownerless Scope Validation (Lines 333-346)
**Status:** COVERED - test_ownerless_storm_with_enemy_sector_scope_skipped (line 530), test_ownerless_storm_with_neutral_sector_scope_passes (line 558)

### E. Activation State Phases (Lines 354-361)
**Status:** PARTIALLY COVERED
- ACTIVE: test_activatable_ability_active (line 102)
- ACTIVATING: test_activatable_ability_activating_shows_progress (line 136)
- INACTIVE: test_activatable_ability_inactive (line 125)
**Gap:** No DEACTIVATING phase test

### F. Rate vs Multiplier Kind (Lines 364-367, 424-459)
**Status:** COVERED - test_multiplier_ability_kind, test_rate_ability_kind_via_storm

### G. PROJ-300 D16 Mixed-Kind Validation (Lines 429-448)
**Status:** COVERED - test_rate_group_with_multiplier_only_entry_skipped (line 583)

### H. Status Aggregation (Lines 400-416)
**Status:** INCOMPLETE
- any_active: test_two_facilities_same_ability_both_shown asserts Active
- any_activating: no isolated test
- any_deactivating: no isolated test
**Gap:** No tests for multiple activating/deactivating providers or mixed states

## 3. Characterization Sufficiency

Are existing tests sufficient for safe refactoring of _aggregate?

**NO** - Critical gaps prevent safe refactoring:
1. get_abilities() exception handling untested in isolation
2. DEACTIVATING phase never exercised
3. affects_hex exception handling never tested
4. Mixed activation state precedence rules untested
5. Owned source filtering with empire_id mismatch untested

Risk: Refactoring lines 400-416 without these tests may silently change behavior in error paths.

## 4. Recommended Characterization Test File

**Path:** tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py

**Required Tests (9 new):**

1. test_get_abilities_exception_skips_source_and_logs
2. test_affects_hex_exception_skips_source_and_logs
3. test_deactivating_ability_shows_progress_remaining
4. test_multiple_deactivating_providers_shows_deactivating_status
5. test_activating_overrides_deactivating_in_mixed_group
6. test_mismatched_empire_id_owned_source_skipped
7. test_affects_hex_false_return_skips_source
8. test_improvement_rate_field_fallback
9. test_mixed_activating_deactivating_precise_status_ordering

## 5. Combat Modifier Collector Overlap

File: tests/unit/strategy/services/test_combat_modifier_collector.py

**Shared consumption:**
- Both walk IAbilitySource adapters
- Both handle ShieldModifier, DamageModifier
- Both use aggregate_multipliers() from strategic_ability_scanner
- Both respect ownership/scope filtering

**Analysis:**
- NO direct test overlap (different query paths: iter_ability_sources_* vs find_abilities_in_scope)
- Shared aggregator coverage via test_strategic_ability_scanner.py (713 lines)
- Recommendation: No new tests needed; concerns are complementary

## 6. Existing IAbilitySource Fixtures

Location: test_system_effects_collector.py:16-48

**Reusable mocks:**
- _make_facility(instance_id, design_data, component_states, is_operational)
- _make_planet(name, planet_id, facilities, owner_id)
- _make_system(name, planets)
- _stabilizer_design(comp_id, ability_name, scope)
- _harvest_booster_design(comp_id, resource_type, multiplier)
- _StormWithBadScope (line 538) for affects_hex testing

**New fixtures needed:**
- _make_source_with_bad_get_abilities() - raises exception
- _make_source_with_affects_hex_exception() - raises exception
- _make_source_owned(owner_id) - for empire filtering tests

## Summary Table

| Category | Status | Details |
|----------|--------|---------|
| Existing coverage | 41/50 major paths | Most branches covered; exception paths and error handling incomplete |
| Characterization gaps | 9 critical | Exception paths, DEACTIVATING phase, mixed-state aggregation untested |
| Refactoring safety | AT RISK | Cannot safely refactor _aggregate without new tests |
| Recommended test file | test_system_effects_collector_aggregate_characterization.py | 9 tests using existing + 3 new fixtures |
| Combat overlap | None | Separate concerns; aggregator tested separately |

**Action:** Land 9 characterization tests before refactoring _aggregate to establish safe green baseline.
