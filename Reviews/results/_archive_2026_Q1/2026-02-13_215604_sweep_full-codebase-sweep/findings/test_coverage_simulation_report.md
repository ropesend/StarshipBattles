# Test Coverage Analysis Report: `game/simulation/`

**Generated**: 2026-02-13
**Shard**: `game/simulation/`
**Analyzer**: Sweep Agent

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Production files scanned | 67 |
| Test files found | 98 |
| Untested modules identified | 3 |
| Undertested public APIs | 8 |
| Critical path gaps | 4 |
| Test quality issues | 3 |
| Integration gaps | 2 |

---

## Findings

### Phase 1: Untested Modules

#### INFO: All Core Simulation Modules Have Test Coverage

Good news: The simulation shard has comprehensive test coverage for most modules. All major subsystems have corresponding test files:

- `combat/` - All 4 files tested (damage_calculator, targeting_system, weapon_firing_system, battle_mode_handler)
- `entities/` - All 9 files tested (ship, projectile, ability_aggregator, combat_endurance, layer_data, ship_combat_engine, ship_formation, ship_physics, ship_serialization)
- `services/` - All 5 files tested (battle_service, design_loader, modifier_service, registry_loader, vehicle_design_service)
- `managers/` - Both files tested (battle_state_manager, retreat_manager)
- `systems/` - battle_engine and battle_end_conditions fully tested
- `validation/` - ship_validator tested

---

### Phase 2: Undertested Public APIs

#### MAJOR: Propulsion Abilities Lack Direct Unit Tests

**File**: `C:\Dev\Starship Battles\game\simulation\components\abilities\propulsion.py`

**Details**: The propulsion module contains 4 ability classes (CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump) with critical ship movement functionality. While these abilities are exercised indirectly through ship stats tests, they lack dedicated unit tests for:

- `sync_data()` method behavior on data changes
- `recalculate()` modifier application
- `get_ui_rows()` output format
- `WarpJump.can_jump()` mass validation logic

**Impact**: Propulsion bugs could cause ships to have incorrect movement stats or fail warp validation silently.

**Recommendation**: Add `tests/unit/simulation/components/abilities/test_propulsion.py` with tests for each ability class.

---

#### MAJOR: AbilityManager Instantiation Logic Undertested

**File**: `C:\Dev\Starship Battles\game\simulation\components\ability_manager.py`

**Details**: The `instantiate_abilities()` method (lines 145-205) handles critical ability lifecycle management but `tests/unit/simulation/components/test_ability_manager.py` primarily tests query methods (`get_abilities`, `has_ability`). Missing tests:

- Preserving existing instances during sync
- Handling `sync_data()` callback on existing abilities
- Registry miss handling (line 178-179)
- List vs single item ability data handling

**Impact**: Ability state could be lost during component updates, causing cooldowns to reset or weapon states to corrupt.

**Recommendation**: Expand test_ability_manager.py with instantiation lifecycle tests.

---

#### MINOR: ShipStatsCalculator Phase Methods Not Individually Tested

**File**: `C:\Dev\Starship Battles\game\simulation\entities\ship_stats.py`

**Details**: While `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` exists, the internal phase methods are not individually unit tested:

- `_phase_damage_check_and_supply()` - Phase 1
- `_phase_resource_allocation()` - Phase 2
- `_phase_stats_aggregation()` - Phase 3
- `_phase_physics_and_limits()` - Phase 4
- `_phase_sensor_defense_scores()` - Phase 5

**Impact**: Phase ordering tests exist, but individual phase logic is tested implicitly through integration.

**Recommendation**: Low priority - current integration testing is adequate, but unit tests per phase would aid debugging.

---

#### MINOR: BattleStateManager Serialization Edge Cases

**File**: `C:\Dev\Starship Battles\game\simulation\managers\battle_state_manager.py`

**Details**: The test file `tests/unit/simulation/managers/test_battle_state_manager.py` exists but could benefit from additional edge case coverage:

- Handling corrupt/malformed save data
- Large battle state serialization (many ships, many projectiles)
- Concurrent state access patterns

**Impact**: Save/load could fail silently on edge cases.

---

### Phase 3: Critical Path Coverage

#### CRITICAL: Damage Pipeline Armor Calculations Sparsely Tested

**File**: `C:\Dev\Starship Battles\game\simulation\combat\damage_calculator.py`

**Details**: The armor damage reduction formulas in `tests/unit/simulation/armor_mechanics/` exist but the interaction between `EmissiveArmor`, `CrystallineArmor`, and the damage calculator's `apply_damage()` method has limited integration testing.

Specifically:
- `emissive_armor` damage type filtering (beam weapons)
- `crystalline_armor` threshold clamping
- Combined armor + shield damage absorption order

**Impact**: Ships could take incorrect damage when multiple defensive layers interact.

**Recommendation**: Add armor+shield integration tests to `tests/unit/simulation/combat/test_damage_calculator.py`.

---

#### MAJOR: Hit/Miss Resolution RNG Seeding Not Verified

**File**: `C:\Dev\Starship Battles\game\simulation\combat\targeting_system.py`

**Details**: The targeting system uses random number generation for hit/miss calculations. Tests verify hit probability calculations but do not verify:

- Deterministic outcomes with fixed seeds
- RNG state isolation between targeting calls
- Statistical distribution over many samples

**Impact**: Battle replays may not be deterministic; balance tuning could be affected by RNG clustering.

**Recommendation**: Add seeded RNG tests to verify deterministic hit/miss sequences.

---

#### MAJOR: Seeker Weapon Guidance State Not Tested Across Retargeting

**File**: `C:\Dev\Starship Battles\game\simulation\entities\projectile.py`

**Details**: While `tests/unit/simulation/projectile_guidance/` has extensive tests, the retargeting scenario (original target dies mid-flight) has limited coverage:

- Seeker acquires new target from candidates
- Seeker with no valid targets (all enemies dead)
- Target switching preserving missile velocity/heading

**Impact**: Missiles could become unguided or target allies on retarget.

---

#### MINOR: Component Stat Aggregation Order Dependencies

**File**: `C:\Dev\Starship Battles\game\simulation\entities\ability_aggregator.py`

**Details**: The `calculate_ability_totals()` function aggregates values with different stacking rules (sum, max, replace). Tests exist but don't verify:

- Order-dependent stacking when multiple components have same ability
- Empty component list handling
- Mixed active/inactive component aggregation

**Impact**: Stats could vary based on component installation order.

---

### Phase 4: Test Quality Issues

#### MAJOR: Heavy Mock Usage in BattleEngine Tests

**File**: `C:\Dev\Starship Battles\tests\unit\simulation\systems\test_battle_engine_tick.py`

**Details**: The test file uses extensive mocking (Mock, MagicMock, patch) which:

- Creates tight coupling to implementation details
- May not catch integration regressions
- Tests pass even if real components break

Example: Lines 24-66 create fully mocked ships that don't exercise real Ship behavior.

**Recommendation**: Add integration-level tick tests using real Ship instances to complement mocked tests.

---

#### MINOR: Combat Endurance Tests Use Manual Ability Setup

**File**: `C:\Dev\Starship Battles\tests\unit\simulation\entities\test_combat_endurance.py`

**Details**: Tests manually construct ability instances and attach them to mocks rather than using component fixtures. This:

- Doesn't test the actual ability instantiation path
- May have stale mock structures if ability signatures change

**Impact**: Tests could pass while real components fail.

---

#### MINOR: Missing Parametrization in Weapon Tests

**File**: `C:\Dev\Starship Battles\tests\unit\simulation\combat\test_weapon_firing_system.py`

**Details**: Test file is 1294+ lines with many similar test patterns. Using `@pytest.mark.parametrize` for weapon type variations would:

- Reduce code duplication
- Ensure consistent coverage across weapon types
- Make adding new weapon types easier

**Impact**: Maintenance burden; potential for drift between weapon type test coverage.

---

### Phase 5: Integration Test Gaps

#### MAJOR: No End-to-End Battle Simulation Tests

**File**: `C:\Dev\Starship Battles\tests\integration\fleet_combat\`

**Details**: While `test_service_integration.py` tests BattleService, there are no full battle simulation tests that:

- Run battles to completion (not just N ticks)
- Verify battle outcomes match expected winners
- Test multi-ship fleet engagements
- Verify replay determinism with seeds

**Impact**: Full battle regressions may not be caught until manual testing.

**Recommendation**: Add `test_battle_e2e.py` with parametrized fleet configurations.

---

#### MINOR: Fighter Launch Integration Not Tested

**File**: `C:\Dev\Starship Battles\tests\unit\combat\test_fighter_launch.py`

**Details**: Fighter launch mechanics are unit tested but integration with:

- Hangar resource depletion
- AI controller assignment
- Fighter surviving to next tick

...is not verified in integration tests.

**Impact**: Fighter launches could partially succeed (fighter spawned but AI broken).

---

### Phase 6: Missing Test Categories

#### INFO: Simulation Tests Directory Well Organized

The `simulation_tests/` directory provides scenario-based testing:

- `test_beam_weapons.py` - Beam weapon scenarios
- `test_projectile_weapons.py` - Projectile scenarios
- `test_seeker_weapons.py` - Missile/seeker scenarios
- `test_defense.py` - Shield/armor scenarios
- `test_engine_physics.py` - Movement physics
- `test_modifiers.py` - Modifier system

**Note**: This complements unit tests well. Consider adding:

- `test_retreat_escape.py` - Retreat mechanic scenarios
- `test_fighter_combat.py` - Carrier/fighter scenarios
- `test_resource_exhaustion.py` - Ammo/fuel depletion scenarios

---

## Prioritized Recommendations

### High Priority (Critical/Major)

1. **Add armor damage pipeline integration tests** - Critical path gap
2. **Add propulsion ability unit tests** - Major API gap
3. **Add seeker retargeting scenario tests** - Critical path gap
4. **Add end-to-end battle simulation tests** - Integration gap
5. **Expand ability manager instantiation tests** - Major API gap

### Medium Priority (Minor/Quality)

6. **Add deterministic RNG seeding tests** - Hit/miss verification
7. **Reduce mock coupling in BattleEngine tests** - Test quality
8. **Parametrize weapon firing tests** - Maintenance
9. **Add ShipStatsCalculator phase unit tests** - Coverage depth

### Low Priority (Polish)

10. **Add retreat/escape simulation scenarios** - Scenario coverage
11. **Add fighter combat scenarios** - Scenario coverage
12. **Add combat endurance integration fixtures** - Test quality

---

## Coverage Heat Map

| Subsystem | Unit Coverage | Integration Coverage | Scenario Coverage |
|-----------|--------------|---------------------|-------------------|
| combat/ | HIGH | MEDIUM | HIGH |
| entities/ | HIGH | HIGH | MEDIUM |
| components/ | MEDIUM | MEDIUM | LOW |
| services/ | HIGH | HIGH | N/A |
| systems/ | HIGH | MEDIUM | HIGH |
| managers/ | HIGH | LOW | LOW |
| validation/ | HIGH | MEDIUM | N/A |

---

*Report generated by Sweep Agent for test coverage analysis.*
