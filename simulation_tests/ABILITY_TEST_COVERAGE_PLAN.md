> **Status: In Progress**
> Scenario classes live in `simulation_tests/scenarios/*_scenarios.py` and are
> run via `python -m simulation_tests.run_tests`.
> Current baseline: **113 passed, 1 failed (RESOURCE-002 game bug), 0 skipped (114 total)**.
> Note: `defense_scenarios.py` was deleted — its 8 tests were redundant with
> dedicated ability files or replaced by the EmissiveArmor category.

# Comprehensive Ability Test Coverage Plan

## Objective

Create a **dedicated test category for every combat-relevant ability** in the
simulator. Each category is a scenario file named after the ability it tests
(e.g., `tohit_attack_scenarios.py` for `ToHitAttackModifier`). Tests within a
category capture both **expected** and **unexpected** behaviors, including:

- The ability's basic effect (positive and negative values)
- Stacking rules: same group does NOT stack (intra-group MAX), different groups DO stack (inter-group SUM)
- Edge cases specific to the ability

### One Category Per Ability

Every combat ability gets its own category with a test ID prefix matching the
ability name. The test file contains only tests for that one ability. Other
components are included only when necessary to create the test scenario (e.g., a
beam weapon is needed to measure the effect of a sensor on hit rate).

### Stacking Must Always Be Tested

Different abilities may stack differently. Currently all numeric abilities use
**intra-group MAX, inter-group SUM**. Marker abilities use boolean OR. Each
ability category must include stacking tests to lock in the correct behavior:

| Scenario | What it proves |
|----------|---------------|
| 1 component | Basic effect works |
| 2 components, same group | Intra-group MAX (no extra benefit) |
| 2 components, different groups | Inter-group SUM (additive stacking) |
| Negative value | Ability works bidirectionally |
| No resource | Component without power/ammo provides no benefit |
| 50% resource | Component stops functioning when resource depletes mid-battle |
| Full resource (control) | Identical setups produce identical results |

### Comparison Scenarios

Ability tests use the `ComparisonScenario` template which runs two battles (A/B)
and compares measured outcomes. This proves the ability actually changes combat
results, not just that a formula computes the right number.

### Isolation Principle

Each test tests ONE thing. Minimal components — only what's needed to observe the
ability under test.

---

## Design Philosophy

1. **Minimal Components**: Each test component has ONLY the ability being tested + minimal required support
2. **No Resource Pollution**: Unless testing resource consumption, use no-resource variants
3. **Dedicated Test File Per Ability Category**: Group related abilities into focused test files
4. **Consistent Naming**: `test_<ability>_no_resource` for isolated components

---

## Ability Inventory (from ABILITY_REGISTRY)

### Category A: Resource System (3 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `ResourceConsumption` | Constant/activation triggers, depletion stops component | HIGH |
| `ResourceStorage` | Capacity tracking, fill/consume cycle | HIGH |
| `ResourceGeneration` | Energy regen rate, regeneration occurs each tick | MEDIUM |

### Category B: Weapons (3 types)
| Ability | Test File | Status | Tests |
|---------|-----------|--------|-------|
| `BeamWeaponAbility` | `beam_scenarios.py` | Partial (23 tests: 11 base + 7 high-tick + 5 resource) | BEAMWEAPON-*, BEAMWEAPON-RES-* |
| `ProjectileWeaponAbility` | `projectile_scenarios.py` | Partial (14 tests: 6 base + 3 damage + 5 resource) | PROJECTILE-*, PROJECTILE-RES-* |
| `SeekerWeaponAbility` | `seeker_scenarios.py` | **Complete** (11 tests: speed, endurance, turn×2, damage, HP, resource, PDC) | SEEKER-* |

### Category C: Propulsion (2 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `CombatPropulsion` | Thrust applied, acceleration, mass relationship | HIGH |
| `ManeuveringThruster` | Turn rate, rotation behavior | HIGH |

### Category D: Defense Systems (4 abilities)
| Ability | Test File | Status | Tests |
|---------|-----------|--------|-------|
| `ShieldProjection` | `shield_projection_scenarios.py` | **Complete** (10 tests) | SHIELD-PROJ-001 to 007, 005B, METALS-001/002 |
| `ShieldRegeneration` | `shield_regen_scenarios.py` | **Complete** (6 tests) | SHIELD-REGEN-001 to 006 |
| `ToHitDefenseModifier` | `tohit_defense_scenarios.py` | **Complete** (4 tests) | TOHIT-DEF-001/002/003/004 |
| `ArmorLayer` | `armor_layer_scenarios.py` | **Complete** (3 tests) | ARMOR-LAYER-001 to 003 |
| `EmissiveArmor` | `emissive_armor_scenarios.py` | **Complete** (5 tests) | EMISSIVE-001 to 005 |

### Category E: Combat Modifiers (1 ability)
| Ability | Test File | Status | Tests |
|---------|-----------|--------|-------|
| `ToHitAttackModifier` | `tohit_attack_scenarios.py` | **Complete** (4 tests) | TOHIT-ATK-001/002/003/004 |

### Category F: Carrier Operations (1 ability)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `VehicleLaunch` | Fighter launch, cycle time, capacity | LOW |

### Category G: Support Systems (3 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `CrewCapacity` | Crew limit aggregation | LOW |
| `LifeSupportCapacity` | Life support limit aggregation | LOW |
| `CrewRequired` | Crew requirement aggregation | LOW |

### Category H: Marker Abilities (6 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `CommandAndControl` | Ship operational check | LOW |
| `RequiresCommandAndControl` | Dependency validation | LOW |
| `RequiresCombatMovement` | Dependency validation | LOW |
| `StructuralIntegrity` | Hull marker presence | LOW |
| `Armor` | Armor layer component marker | LOW |

---

## Execution Order

### Completed (weapon/system-level test files)
1. **Phase 1** (Complete): Beam weapon tests — 23 scenarios in `beam_scenarios.py`
2. **Phase 2** (Complete): Propulsion tests — 9 scenarios in `propulsion_scenarios.py`
3. **Phase 3** (Complete → Deleted): Shield/Armor/ECM/Sensor tests — `defense_scenarios.py` (redundant, replaced by ability-specific files)
4. **Phase 4** (Complete): Stat modifier tests — 6 scenarios in `modifier_scenarios.py`
5. **Phase 5** (Complete): Projectile weapon tests — 14 scenarios in `projectile_scenarios.py`
6. **Phase 6** (Rewritten): Seeker weapon tests — 11 ComparisonScenario tests in `seeker_scenarios.py`
7. **Phase 7** (Complete): Resource system tests — 9 scenarios in `resource_scenarios.py`

### Completed (ability-specific categories using ComparisonScenario)
8. **ToHitAttackModifier** (Complete): 4 scenarios in `tohit_attack_scenarios.py`
9. **ToHitDefenseModifier** (Complete): 4 scenarios in `tohit_defense_scenarios.py`
10. **ShieldProjection** (Complete): 10 scenarios in `shield_projection_scenarios.py`

### Completed (ability-specific categories, continued)
11. **ShieldRegeneration** (Complete): 6 scenarios in `shield_regen_scenarios.py`
12. **ArmorLayer** (Complete): 3 scenarios in `armor_layer_scenarios.py`
13. **EmissiveArmor** (Complete): 5 scenarios in `emissive_armor_scenarios.py`

### Cleanup
- Deleted `defense_scenarios.py` — 8 tests removed (SHIELD-001/002/003, ECM-001, SENSOR-001/002, ARMOR-001/002)
  - SHIELD-001/002 redundant with SHIELD-PROJ-001/002
  - SHIELD-003 redundant with SHIELD-REGEN-001 to 006
  - ECM-001 redundant with TOHIT-DEF-001
  - SENSOR-001/002 redundant with TOHIT-ATK-001
  - ARMOR-001/002 replaced by EMISSIVE-001 to 005 (better tests with ComparisonScenario + stacking)

14. **CommandAndControl** (Complete): 5 scenarios in `cnc_scenarios.py`

15. **ShieldRegeneratingArmor** (Complete): 5 scenarios in `sra_scenarios.py`

### Pending (ability-specific categories)
16. **VehicleLaunch**: Carrier/hangar tests

---

## Test Design Best Practices

These practices were established through iterative development of the test suite:

### Weapon & Target Setup
1. **Damage = 1 per hit** for accuracy tests: `damage_dealt == hits`, simple counting
2. **Reload = 0.0** for accuracy tests: fires every tick, high sample counts for statistical validity
3. **Extreme HP targets** (1 billion HP): targets never die during tests
4. **Zero-mass components**: ship mass comes only from hull, keeps physics predictable
5. **Point-blank distance ≥ 100px**: ships with mass=400 have radius ~29.5px; center distance must exceed sum of radii to avoid visual overlap
6. **Use game-realistic values**: projectile speed=20000 matches the actual railgun in the game (200 px/tick after PROJECTILE_SPEED_SCALE division)

### Moving Target Design
7. **Moving targets start out of range**: place at (100, -1200) heading up so they reach full speed before entering the engagement zone
8. **Same starting position for comparable tests**: PROJ-002 (slow) and PROJ-003 (fast) both start at (100, -1200), isolating target speed as the only variable
9. **Erratic target thruster sizing**: calculate overshoot = max_speed * (180 / effective_turn_rate); must be well under leash radius. Use `test_thruster_high` (raw=500); large ships may need multiple thrusters
10. **Enable position tracking** (`track_positions=True`) on erratic/moving tests to verify the leash works and targets stay in the engagement zone
11. **Turn speed is per 100 ticks**: `rotate()` divides by 100. When sizing thrusters, use `turn_speed / 100` as the actual deg/tick rotation rate

### Instrumentation & Metrics
12. **Track shots_fired and hits**: templates auto-collect per-weapon stats via `_collect_weapon_stats()`; scenarios can add `_collect_extra_results()` to expose `shots_fired`, `hits`, `hit_rate` in results
13. **Use resolved hit rate**: exclude in-flight projectiles from hit/miss counting — `resolved_shots = fired - in_flight`. Without this, long-range tests show false accuracy dropoff from travel-time artifacts

### Validation Rigour (CRITICAL)
14. **Verify ALL assumptions in preconditions, not just outcomes.** A test that depends on a moving target MUST verify the target actually moved. A test that depends on weapon range MUST verify the distance. If a precondition fails silently, the outcome check becomes meaningless — a "pass" on a broken test is worse than a failure.
15. **Verify target movement in precondition phase**: check `target.velocity.length()` matches expected `max_speed`, check displacement from start position is substantial, check position tracking `ticks_in_range` and `max_distance` for erratic targets
16. **Pass criteria must be hard to game**: use both upper AND lower bounds on hit rate for erratic tests (too high = target didn't evade, too low = weapon broken). Require minimum shot counts so a single lucky hit can't pass the test. Require 100% resolved hit rate for stationary targets — not just "damage > 0"
17. **Validate every weapon stat in data phase**: damage, range, projectile_speed, reload_time. If a modifier silently overwrites a value (like the arc_set bug), data-phase checks catch it before the outcome phase runs
18. **Verify the weapon actually fired** (or didn't): PROJ-006 checks `shots_fired == 0` to confirm the weapon correctly refused to fire at an out-of-range target. Without this, the test would pass if the weapon was broken for any reason

## Speed Unit Reference

Ship speed, projectile speed, and turn speed all use **different scales**:

| Entity | Config/Formula | Actual (px/tick or deg/tick) |
|--------|---------------|----------------------------|
| Ship speed | `(thrust * 25) / mass` | px/tick directly |
| Projectile speed | `projectile_speed / 100` | px/tick after PROJECTILE_SPEED_SCALE |
| Turn speed | `(raw_turn * 25000) / mass^1.5` | degrees per 100 ticks; `rotate()` divides by 100 |

Examples:
- Ship: thrust=1500, mass=1000 → max_speed=37.5 px/tick
- Projectile: speed=20000 → 200 px/tick (5.3x faster than ship)
- Turn: raw=500, mass=400 → turn_speed=1562.5 → effective 15.6 deg/tick

## Success Criteria

- Each combat ability has its own test category (scenario file + test ID prefix)
- Each category includes: basic effect, same-group stacking, different-group stacking, negative value
- Tests use ComparisonScenario template for measured A/B comparisons
- Tests use minimal components (no unnecessary batteries/generators)
- All tests pass: `python -m simulation_tests.run_tests`
- New components follow naming: `test_<type>_<variant>`
- Use `test_armor_extreme_hp` for targets that should not die

---

## Reference Files

- **Abilities**: `game/simulation/components/abilities/` (weapons.py, defense.py, propulsion.py, etc.)
- **Test Components**: `simulation_tests/data/components.json`
- **Test Ships**: `simulation_tests/data/ships/`
- **Test Scenarios**: `simulation_tests/scenarios/*_scenarios.py`
- **Test Constants**: `simulation_tests/test_constants.py`
- **Templates**: `simulation_tests/scenarios/templates.py`
