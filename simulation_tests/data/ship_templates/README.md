# Ship Templates

This directory contains reference templates for Combat Lab test ships.

## Purpose

These templates document common patterns and structures for test ships, reducing duplication and making it easier to create new test scenarios.

## Template Files

### base_stationary_target_template.json
Reference template for stationary target ships used in weapon testing.

**Common Variants:**
- `Test_Target_Stationary.json` - Standard target (mass=400, extreme HP)
- `Test_Target_SmallErratic.json` - Small, moving target (mass=50)
- `Test_Target_Large.json` - Large target (mass=8000)

**Key Properties:**
- `mass`: Affects target radius and defense score
- `armor_component`: Determines HP pool
- `ai_strategy`: Usually `test_do_nothing` for stationary targets

### base_attacker_template.json
Reference template for attacker ships with various weapon types.

**Common Variants:**
- `Test_Attacker_Beam360_Low.json` - Low accuracy beam (0.5 base)
- `Test_Attacker_Beam360_Med.json` - Medium accuracy beam (2.0 base)
- `Test_Attacker_Beam360_High.json` - High accuracy beam (5.0 base)
- `Test_Attacker_Projectile360.json` - Projectile weapon (10 damage)
- `Test_Attacker_Seeker360.json` - Seeker/missile weapon (50 damage)

**Key Properties:**
- `weapon_component`: Defines weapon stats (accuracy, damage, range, etc.)
- `mass`: Usually 25.0 for attackers
- `ai_strategy`: Usually `test_do_nothing`

## Usage

These templates serve as documentation and reference when creating new test ships. They are NOT automatically processed by a generator script - they document existing patterns.

When creating a new test ship:
1. Copy the appropriate template
2. Replace `[PLACEHOLDERS]` with actual values
3. Update metadata (description, last_modified)
4. Set appropriate component IDs in layers
5. Update expected_stats to match components
6. Save in `simulation_tests/data/ships/` directory

## Related Files

- **Test Constants**: `simulation_tests/test_constants.py` - Centralized values
- **Ship Files**: `simulation_tests/data/ships/` - Actual test ship definitions
- **Components**: `simulation_tests/data/components.json` - Weapon/armor definitions

## Maintenance

When adding new weapon types or test patterns:
1. Update the relevant template's `_template_info.common_variants`
2. Document key properties and their effects
3. Update this README with new patterns

## Version History

- **1.0** (2026-01-14) - Initial templates created during Phase 4 refactoring
