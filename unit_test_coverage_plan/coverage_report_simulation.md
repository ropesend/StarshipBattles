# Simulation Engine Coverage Report

**Agent:** Agent 2 (Physics & Combat)
**Date:** 2026-01-02
**Scope:** `ship_physics.py`, `ship_combat.py`, `projectiles.py`, `collision_system.py`, `battle_engine.py`

## 1. Coverage Summary

The Simulation Engine has a solid baseline of tests for core mechanics (Movement, Damage Application, Projectile Life), but lacks depth in "Game Loop Integration" and "Edge Case Logic".

| File | Estimated Coverage | Key Strengths | Critical Gaps |
| :--- | :--- | :--- | :--- |
| `ship_physics.py` | 60% | Basic `PhysicsBody` movement (velocity, drag). | `ShipPhysicsMixin` integration with **Abilities** (Thrust/Turn calculations), Throttle logic, Mass-based acceleration scaling. |
| `ship_combat.py` | 70% | Damage distribution (Armor, Layers, overflow). Shield Regen. | **Firing Logic** (`fire_weapons` branches), Target Selection priority, Lead calculation math, Emissive/Crystalline armor specific mechanics. |
| `projectiles.py` | 80% | Lifecycle (Range/Endurance), Basic Homing. | **Oscillation Damping** for guidance, complex turn logic, specific Missile/Beam type differentiation in constructors. |
| `collision_system.py` | 90% | Raycasting math, Ramming logic. | Hit Chance RNG edge cases, ECM/Sensor score integration. |
| `battle_engine.py` | 50% | Core Loop delegation (Update/Grid). | **Fighter Launching** (`AttackType.LAUNCH`), Start/Win conditions, Team management details. |

---

## 2. Missing Tests

### Physics (`ship_physics.py`)
- **Ability Integration:** No test verifies that `update_physics_movement` actually calls `get_total_ability_value('CombatPropulsion')`. The current tests only check raw `PhysicsBody` math.
- **Throttle & Mass:** Logic for `engine_throttle` scaling and `mass` affecting acceleration force is present in code but not explicitly verified with asserted values.
- **Turn Throttle:** `rotate()` accounts for `turn_throttle` and `turn_speed`, but this combination isn't tested.

### Combat (`ship_combat.py`)
- **Firing Solution:** `_calculate_firing_solution` (Quadratic Solver) has no direct unit tests. Deviations in lead calculation logic would go unnoticed.
- **Target Selection:** `fire_weapons` logic for choosing Primary vs Secondary vs PDC targets is untested.
- **Seeker vs Direct:** The branching logic for creating a `Projectile` (Direct) vs `Seeker` (Guided) vs `Beam` (Hitscan) inside `fire_weapons` needs finding.
- **Armor Specialties:** `EmissiveArmor` (flat reduction) and `CrystallineArmor` (absorption/recharge) logic in `take_damage` is not covered by `TestDamageLayerLogic`.

### Projectiles (`projectiles.py`)
- **Guidance Stability:** The code contains specific logic to prevent "oscillation" (flip-flopping turn direction). `TestMissileGuidance` only checks "it turns roughly towards target", not this stability fix.
- **Beam Types:** Construction of Beam "projectiles" (dicts) is handled in combat, but `Projectiles.py` handles the class.

### Battle Engine (`battle_engine.py`)
- **Fighter Launch:** `update()` handles `AttackType.LAUNCH` by creating a new `Ship` and adding it to `self.ships`. This critical feature is completely untested.
- **Win Conditions:** `is_battle_over` and `get_winner` logic is untested.

---

## 3. Plan

To achieve 100% Coverage, we need to add the following test cases.

### Step 3.1: Enhance `test_physics.py`
- [ ] **`test_physics_ability_integration`**: Mock a Ship with `CombatPropulsion` abilities and verify `current_speed` increases appropriately when `thrust_forward()` is called.
- [ ] **`test_mass_dampens_acceleration`**: Compare acceleration of a 100-mass ship vs 1000-mass ship with same thrust.

### Step 3.2: Enhance `test_combat.py`
- [ ] **`test_firing_solution_lead`**: Direct test of `solve_lead` with known vectors (e.g., target moving perpendicular).
- [ ] **`test_fire_weapons_creates_projectiles`**: Mock `WeaponAbility` and call `fire_weapons`, asserting that the returned list contains Projectiles with correct properties (Damage, Type).
- [ ] **`test_special_armor_mechanics`**: Test `take_damage` on a ship with `emissive_armor` (flat reduction) and `crystalline_armor` (shield recharge).

### Step 3.3: Enhance `test_projectiles.py`
- [ ] **`test_guidance_damping`**: Setup a missile directly behind a target (180 deg) and verify it commits to a turn direction rather than oscillating.

### Step 3.4: Enhance `test_battle_engine_core.py`
- [ ] **`test_fighter_launch_execution`**: Mock a ship returning `AttackType.LAUNCH` in `fire_weapons`. Run `engine.update()` and assert `len(engine.ships)` increases and the new ship has correct properties (Name, Team).
- [ ] **`test_win_conditions`**: Create scenario with Team 0 dead, assert `engine.get_winner() == 1`.
