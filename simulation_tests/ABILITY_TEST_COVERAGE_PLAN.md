> **Status: Partially Implemented**
> Scenario classes live in `simulation_tests/scenarios/*_scenarios.py` and are
> run via `python -m simulation_tests.run_tests`.
> Current baseline: **64 passed, 2 failed (game bugs), 3 skipped (69 total)**.

# Comprehensive Ability Test Coverage Plan

## Objective

Create minimal component/ship designs to test **every ability** in the combat simulator, following the isolation principle: **each test tests ONE thing**.

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
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `BeamWeaponAbility` | Accuracy formula, range falloff, firing arc, damage | HIGH |
| `ProjectileWeaponAbility` | Projectile spawning, speed, travel time, damage | HIGH |
| `SeekerWeaponAbility` | Tracking behavior, endurance, turn rate, PDC interaction | HIGH |

### Category C: Propulsion (2 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `CombatPropulsion` | Thrust applied, acceleration, mass relationship | HIGH |
| `ManeuveringThruster` | Turn rate, rotation behavior | HIGH |

### Category D: Defense Systems (4 abilities)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `ShieldProjection` | Shield capacity, damage absorption, overflow to hull | HIGH |
| `ShieldRegeneration` | Regeneration rate, energy consumption coupling | MEDIUM |
| `ToHitDefenseModifier` | Defense bonus applies to hit calculations | MEDIUM |
| `EmissiveArmor` | Damage reduction threshold | MEDIUM |

### Category E: Combat Modifiers (1 ability)
| Ability | What to Test | Priority |
|---------|--------------|----------|
| `ToHitAttackModifier` | Attack bonus applies to beam hit calculations | MEDIUM |

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

## Sub-Agent Task Breakdown

### Task 1: Propulsion Tests (HIGH PRIORITY)
**File**: `simulation_tests/tests/test_propulsion.py`

**Goal**: Verify CombatPropulsion and ManeuveringThruster work correctly in isolation.

**Sub-agent Prompt**:
```
Create minimal propulsion tests in simulation_tests/.

1. Add to components.json:
   - `test_engine_no_fuel` (already exists, verify no ResourceConsumption)
   - `test_thruster_std` (already exists, verify no ResourceConsumption)

2. Create `test_propulsion.py` with tests:
   - PROP-001: Engine provides thrust, ship accelerates
   - PROP-002: Thrust/mass ratio affects max speed
   - PROP-003: Thruster provides turn rate
   - PROP-004: Turn rate allows rotation

3. Ships: Use minimal ships with ONLY engine/thruster + hull
```

---

### Task 2: Shield Tests (HIGH PRIORITY)
**File**: `simulation_tests/tests/test_shields.py`

**Sub-agent Prompt**:
```
Create shield system tests in simulation_tests/.

1. Add to components.json:
   - `test_shield_no_regen` (ShieldProjection only, no energy cost)
   - `test_shield_regen_no_energy` (ShieldRegeneration without energy dep)

2. Create `test_shields.py` with tests:
   - SHIELD-001: Shield absorbs damage before hull
   - SHIELD-002: Damage overflow goes to hull
   - SHIELD-003: Shield regenerates over time
   - SHIELD-004: Multiple shields stack capacity

3. Ships: Minimal defender with shield + hull, attacker with beam weapon
```

---

### Task 3: Defense Modifier Tests (MEDIUM PRIORITY)
**File**: `simulation_tests/tests/test_defense_modifiers.py`

**Sub-agent Prompt**:
```
Create defense modifier tests in simulation_tests/.

1. Add to components.json:
   - `test_ecm_no_energy` (ToHitDefenseModifier without power req)
   - `test_emissive_armor` (EmissiveArmor component)

2. Create `test_defense_modifiers.py` with tests:
   - DEF-001: ToHitDefenseModifier reduces enemy hit chance
   - DEF-002: Multiple ECMs don't stack (same stack_group)
   - DEF-003: EmissiveArmor ignores small damage hits
   - DEF-004: Stacking rules for different defense types

3. Ships: Target with defense components, attacker with beam
```

---

### Task 4: Attack Modifier Tests (MEDIUM PRIORITY)
**File**: `simulation_tests/tests/test_attack_modifiers.py`

**Sub-agent Prompt**:
```
Create attack modifier tests in simulation_tests/.

1. Add to components.json:
   - `test_sensor_no_energy` (ToHitAttackModifier without power req)

2. Create `test_attack_modifiers.py` with tests:
   - ATK-001: ToHitAttackModifier improves hit chance
   - ATK-002: Multiple sensors don't stack (same stack_group)
   - ATK-003: Different sensor types stack

3. Ships: Attacker with sensor + beam, stationary target
```

---

### Task 5: Point Defense Tests (HIGH PRIORITY)
**File**: `simulation_tests/tests/test_point_defense.py`

**Sub-agent Prompt**:
```
Create point defense interaction tests in simulation_tests/.

1. Add to components.json:
   - `test_pd_no_energy` (BeamWeaponAbility with "pdc" tag, no energy)

2. Create `test_point_defense.py` with tests:
   - PDC-001: PDC targets incoming seekers
   - PDC-002: PDC destroys seekers before impact
   - PDC-003: PDC ignores non-seeker projectiles
   - PDC-004: Multiple PDCs intercept more seekers

3. Ships: Target with PDC + hull, attacker with seeker launcher
```

---

### Task 6: Carrier Operations Tests (LOW PRIORITY)
**File**: `simulation_tests/tests/test_carriers.py`

**Sub-agent Prompt**:
```
Create carrier/hangar tests in simulation_tests/.

1. Add to components.json:
   - `test_hangar_simple` (VehicleLaunch with basic fighter)

2. Create `test_carriers.py` with tests:
   - CARRIER-001: Hangar launches fighter
   - CARRIER-002: Cycle time limits launches
   - CARRIER-003: Fighter attacks enemy

3. Ships: Carrier with hangar, target ship
```

---

## Execution Order

1. **Phase 1** (Complete): Beam weapon tests (21 scenarios)
2. **Phase 2** (Complete): Propulsion tests (9 scenarios)
3. **Phase 3** (Complete): Shield tests (3 scenarios)
4. **Phase 4** (Complete): Defense/Attack modifier tests (9 scenarios: armor, ECM, sensor, stat modifiers)
5. **Phase 5** (Complete): Projectile weapon tests (9 scenarios)
6. **Phase 6** (Complete): Seeker weapon tests (8 scenarios + 3 PDC placeholders)
7. **Phase 7** (Complete): Resource system tests (9 scenarios)
8. **Phase 8** (Pending): Point Defense tests - flesh out SEEKER-PD-001/002/003
9. **Phase 9** (Pending): Carrier/VehicleLaunch tests
10. **Phase 10** (Pending): Crystalline armor, component damage, derelict detection

---

## Test Design Best Practices

These practices were established through iterative development of the test suite:

1. **Damage = 1 per hit** for accuracy tests: `damage_dealt == hits`, simple counting
2. **Reload = 0.0** for accuracy tests: fires every tick, high sample counts for statistical validity
3. **Extreme HP targets** (1 billion HP): targets never die during tests
4. **Zero-mass components**: ship mass comes only from hull, keeps physics predictable
5. **Point-blank distance ≥ 100px**: ships with mass=400 have radius ~29.5px; center distance must exceed sum of radii to avoid visual overlap
6. **Moving targets start out of range**: place at (100, -1200) heading up so they reach full speed before entering the engagement zone
7. **Same starting position for comparable tests**: PROJ-002 (slow) and PROJ-003 (fast) both start at (100, -1200), isolating target speed as the only variable
8. **Use game-realistic values**: projectile speed=20000 matches the actual railgun in the game (200 px/tick after PROJECTILE_SPEED_SCALE division)
9. **Track shots_fired and hits**: templates auto-collect per-weapon stats via `_collect_weapon_stats()`; scenarios can add `_collect_extra_results()` to expose `shots_fired`, `hits`, `hit_rate` in results

## Speed Unit Reference

Ship speed and projectile speed use **different scales**:

| Entity | Config/Formula | Actual (px/tick) |
|--------|---------------|-----------------|
| Ship | `(thrust * 25) / mass` | Direct |
| Projectile | `projectile_speed / 100` | After PROJECTILE_SPEED_SCALE |

Example: A ship with thrust=1500, mass=1000 has max_speed=37.5 px/tick.
A projectile with speed=20000 moves at 200 px/tick (5.3x faster).

## Success Criteria

- Each ability has at least one dedicated test
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
