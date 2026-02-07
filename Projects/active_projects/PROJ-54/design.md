# PROJ-54: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Code Quality Audit Findings

The Combat Lab has ~60 scenarios across 5 scenario files. The framework is functional but has significant maintainability issues that will compound as we expand coverage.

**Critical Issues Found:**

1. **Massive verify/results duplication** - `self.results['initial_hp'] = self.initial_hp` appears 50 times across 8 files. Scenarios override `verify()` entirely, bypassing template logic.
2. **Projectile scenarios bypass templates** - All 9 projectile scenarios extend raw `TestScenario`, duplicating the full setup/update/verify cycle that `StaticTargetScenario` already provides.
3. **`_resolve_path` duplicated 3 times** - Identical utility in `ExactMatchRule`, `DeterministicMatchRule`, and `PreRunValidator` with varying error quality.
4. **`_extract_ship_validation_data` hardcoded to beam** - Only extracts `BeamWeaponAbility` data, returns immediately after finding one. Cannot validate projectile, seeker, defense, or propulsion data.
5. **Beam scenarios duplicate hit-chance calc** - Every beam scenario has near-identical `custom_setup()`.
6. **Seeker scenarios hardcode magic numbers** - `self.results['missile_speed'] = 1000` instead of reading from loaded ship data.

### Ability System Architecture

25+ ability types in `ABILITY_REGISTRY`:
- **Weapons:** `BeamWeaponAbility`, `ProjectileWeaponAbility`, `SeekerWeaponAbility`
- **Defense:** `ShieldProjection`, `ShieldRegeneration`, `ToHitAttackModifier`, `ToHitDefenseModifier`, `EmissiveArmor`
- **Propulsion:** `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `WarpJump`
- **Resources:** `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`
- **Crew:** `CrewRequired`, `CrewCapacity`, `LifeSupportCapacity`
- **Markers:** `Armor`, `Engine`, `Generator`, `Weapon`, `Thruster`
- **Other:** `Harvester`, `HarvestStorage`

All abilities use `STAT_BINDINGS` for modifier integration. Modifiers affect abilities through a two-stage aggregation: intra-group MAX (redundancy), inter-group SUM/MULTIPLY (stacking).

### Current Test Coverage

| Ability Type | Combat Lab Coverage |
|---|---|
| BeamWeaponAbility | 18+ scenarios |
| ProjectileWeaponAbility | 9 scenarios |
| SeekerWeaponAbility | 8 scenarios |
| ResourceConsumption/Storage/Gen | 9 scenarios |
| CombatPropulsion | 3 scenarios |
| ShieldProjection | **None** |
| ShieldRegeneration | **None** |
| EmissiveArmor | **None** |
| ToHitDefenseModifier | **None** |
| ToHitAttackModifier | **None** |
| Component Modifiers | **None** |

---

## Key Patterns to Reuse

- **`StaticTargetScenario`**: `simulation_tests/scenarios/templates.py:33-222` - Template with `custom_setup`/`custom_update` hooks, pass-criteria flags
- **`DuelScenario`**: `simulation_tests/scenarios/templates.py:229-398` - Two-ship engagement template
- **`PropulsionScenario`**: `simulation_tests/scenarios/templates.py:405-572` - Movement/physics template
- **`ExactMatchRule`**: `simulation_tests/scenarios/validation.py:100-226` - Exact value validation with path resolution
- **`StatisticalTestRule`**: `simulation_tests/scenarios/validation.py:378+` - TOST equivalence testing for hit rates
- **`DeterministicMatchRule`**: `simulation_tests/scenarios/validation.py:229-375` - Float comparison with tolerance
- **Zero-mass test components**: `simulation_tests/data/components.json` - All non-hull test components have mass=0

---

## Dependencies & Risks

1. **Phase ordering is critical** - Template refactor (Phase 2) must happen before scenario simplification (Phase 3), because scenarios need the new `_collect_results` hook.
2. **Test ID stability** - All existing test IDs and pass/fail behavior MUST remain identical through Phases 1-3. These are refactors, not rewrites.
3. **Backward compat for `data['weapon']`** - When generalizing `_extract_ship_validation_data`, existing beam scenarios must still resolve `attacker.weapon.damage` paths.
4. **Surface distance calculation** - Beam weapons measure range to target surface, not center. This is a critical formula detail that tests depend on.

---

## Modifier Design

Game modifiers (in `data/modifiers.json`) have complex multi-effect formulas with mass/cost side effects. For testing, we create **simplified single-effect versions** in `simulation_tests/data/modifiers.json`:

| Test Modifier | Game Equivalent | Single Effect | No Side Effects |
|---|---|---|---|
| `test_damage_boost` | `simple_size_mount` | `damage_mult` only | No mass/cost |
| `test_range_boost` | `range_mount` | `range_mult` only | No mass/cost |
| `test_turret` | `turret_mount` | `arc_set` only | No mass |
| `test_reload_boost` | `rapid_fire` | `reload_mult` only | No mass/cost |
| `test_accuracy_boost` | `precision_mount` | `accuracy_add` only | No mass/cost |
| `test_thrust_boost` | `simple_size_mount` | `thrust_mult` only | No mass/cost |
| `test_endurance_boost` | `seeker_endurance` | `endurance_mult` only | No mass/cost |
| `test_consumption_reduction` | `efficiency_mount` | `consumption_mult` only | No mass/cost |

This isolates the variable being tested - if a damage modifier test fails, we know the issue is with `damage_mult` application, not a mass/cost side effect.

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
