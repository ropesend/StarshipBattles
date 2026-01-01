# Component Test Specifications

> [!IMPORTANT]
> These are **simulation-based behavioral tests**, not unit tests. Every test:
> - Runs through the **actual battle simulator**
> - Loads ships from **JSON files** in `tests/data/ships/`
> - Uses **AI behaviors** to control ship actions
> - **Logs results** to output files for verification
> - Uses **toggleable logging** (on for tests, off for normal play)

---

## Table of Contents
1. [Directory Structure](#directory-structure)
2. [Test Philosophy](#1-test-philosophy)
3. [Test Harness Infrastructure](#2-test-harness-infrastructure)
4. [Test Data Requirements](#3-test-data-requirements)
5. [AI Behavior Policies](#4-ai-behavior-policies)
6. [Ship Templates](#5-ship-templates)
7. [Engine Components](#6-engine-components)
8. [Weapons: 360° Firing Arc](#7-weapons-360-firing-arc)
9. [Weapons: 90° Firing Arc](#8-weapons-90-firing-arc)
10. [Implementation Checklist](#9-implementation-checklist)

---

## Directory Structure

> [!IMPORTANT]
> Simulation tests are kept in a **separate subdirectory** from unit tests because they are computationally intensive and take longer to run.

```
tests/
├── simulation/              # Simulation-based component tests (this spec)
│   ├── __init__.py
│   ├── run_component_tests.py   # Test runner script
│   ├── test_log_parser.py       # Log parsing utilities
│   ├── test_configs/            # Test configuration JSONs
│   │   ├── ENG-001.json
│   │   ├── PROJ360-001.json
│   │   └── ...
│   └── output/
│       └── logs/                # Generated log files
├── data/                    # Test data (shared)
│   ├── ships/               # Ship JSON files
│   ├── test_components.json
│   ├── test_vehicleclasses.json
│   └── ...
├── data_driven/             # Existing data-driven unit tests
└── *.py                     # Other unit tests
```

### Running Tests Separately

```bash
# Run ONLY simulation tests (compute intensive)
python -m unittest discover tests/simulation -v

# Run ONLY unit tests (fast)
python -m unittest discover tests -v --ignore-patterns "simulation/*"

# Run ALL tests
python -m unittest discover tests -v
```

---

## 1. Test Philosophy

> [!CAUTION]
> These are **NOT unit tests**. They are full-simulation behavioral tests that validate the combat engine by running actual battles and analyzing logged output.

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Full Simulation** | Every test runs through the battle simulator, not isolated code paths |
| **JSON Ship Loading** | All test ships are defined in JSON files and loaded at runtime |
| **AI-Controlled Behavior** | Ships use test-specific AI behaviors for repeatable scenarios |
| **Log-Based Verification** | Test results are verified by parsing simulation log files |
| **Toggleable Logging** | Logging is enabled for tests, disabled for normal gameplay |
| **Minimal Ships** | Each test ship has only the components needed for that test |
| **Separate Simulations** | Use separate simulations for each test case (one variable at a time) |

### Test Execution Flow

```
1. Load test ship(s) from JSON file(s) in tests/data/ships/
2. Configure AI behaviors for each ship
3. Enable test logging mode
4. Run simulation for specified duration/ticks
5. Parse log file for expected events
6. Assert logged values match expected outcomes
7. Clean up and report results
```

### Ship Roles

| Role | When to Use | Components |
|------|-------------|------------|
| **Attacker** | Testing offensive systems | Only the weapon being tested |
| **Stationary Target** | Testing weapon accuracy/damage | Armor only (no engines, no movement) |
| **Moving Target** | Testing predictive leading | Armor + Engines (moves in controlled pattern) |
| **Evasive Target** | Testing accuracy degradation | Armor + Engines + Thrusters (erratic movement) |
| **Rotating Attacker** | Testing arc-constrained weapons | Weapon + Thrusters (rotates but no translation) |

---

## 2. Test Harness Infrastructure

### 2.1 Test Logging System

> [!NOTE]
> All logging is **toggleable**. When running normal simulations, logging should be disabled to avoid performance overhead.

#### Log Configuration

```python
# Enable/disable test logging globally
TEST_LOGGING_ENABLED = False  # Set to True when running component tests

# Log output directory
TEST_LOG_DIR = "tests/simulation/output/logs/"
```

#### Log Event Types

| Event Type | Data Logged | Purpose |
|------------|-------------|----------|
| `SHIP_SPAWN` | ship_name, position, class, components | Verify ship loaded correctly |
| `TICK` | tick_number, simulation_time | Track simulation progress |
| `SHIP_VELOCITY` | ship_name, tick, velocity, speed, heading | Engine/movement tests |
| `SHIP_POSITION` | ship_name, tick, x, y | Position tracking |
| `WEAPON_FIRE` | ship_name, weapon_id, target, tick | Weapon activity |
| `PROJECTILE_SPAWN` | proj_id, origin, direction, speed | Projectile tracking |
| `HIT` | attacker, target, weapon, damage, tick | Damage verification |
| `MISS` | attacker, target, weapon, reason, tick | Accuracy testing |
| `SEEKER_LAUNCH` | seeker_id, origin, target, tick | Seeker tracking |
| `SEEKER_IMPACT` | seeker_id, target, tick | Seeker hit confirmation |
| `SEEKER_EXPIRE` | seeker_id, reason, tick | Seeker lifetime tracking |
| `SIM_END` | final_tick, ships_remaining | Simulation completion |

#### Log File Format

```
[TICK:0] SHIP_SPAWN | name=Test_Engine_1x_LowMass | pos=(0,0) | class=TestS_2L
[TICK:0] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | vel=(0,0) | speed=0.0
[TICK:1] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | vel=(5.2,0) | speed=5.2
[TICK:100] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | vel=(312.5,0) | speed=312.5
...
[TICK:1000] SIM_END | final_tick=1000 | ships_remaining=1
```

### 2.2 Test Runner

#### Test Configuration File (JSON)

```json
{
    "test_id": "ENG-001",
    "description": "Base speed/accel calculation",
    "ships": [
        {
            "file": "tests/data/ships/Test_Engine_1x_LowMass.json",
            "position": [0, 0],
            "ai_strategy": "straight_line"
        }
    ],
    "duration_ticks": 1000,
    "assertions": [
        {
            "type": "velocity_at_tick",
            "ship": "Test_Engine_1x_LowMass",
            "tick": 1000,
            "expected_speed": 312.5,
            "tolerance": 0.1
        }
    ]
}
```

#### Test Runner Script

```python
# tests/simulation/run_component_tests.py

def run_test(test_config_path):
    """Execute a single simulation test and verify results."""
    # 1. Load test configuration
    # 2. Enable test logging
    # 3. Load ships from JSON
    # 4. Run simulation
    # 5. Parse log file
    # 6. Verify assertions
    # 7. Return pass/fail
    pass
```

### 2.3 Log Parser

```python
class TestLogParser:
    """Parse simulation logs for test verification."""
    
    def get_velocity_at_tick(self, ship_name: str, tick: int) -> float:
        """Return ship speed at specified tick."""
        pass
    
    def get_hit_count(self, attacker: str, target: str) -> int:
        """Count hits between two ships."""
        pass
    
    def get_shots_fired(self, ship_name: str, weapon_id: str = None) -> int:
        """Count shots fired by ship (optionally filtered by weapon)."""
        pass
    
    def get_damage_dealt(self, attacker: str, target: str) -> float:
        """Sum total damage dealt."""
        pass
```

---

## 3. Test Data Requirements

### 3.1 Test Components (test_components.json)

#### Mass Simulator (Dummy Ballast)
A component that **only adds mass** with no other functionality. Required for testing thrust-to-mass relationships.

| ID | Name | Mass | Status |
|----|------|------|--------|
| `test_mass_sim_1k` | Mass Simulator (1,000t) | 1,000 | ✅ Added |
| `test_mass_sim_10k` | Mass Simulator (10,000t) | 10,000 | ✅ Added |
| `test_mass_sim_100k` | Mass Simulator (100,000t) | 100,000 | ✅ Added |

---

#### Beam Weapon Variants (Low/Medium/High Accuracy)

The existing beam weapon has `base_accuracy: 2.0`. We need 3 variants to test the accuracy system:

| Variant | ID | base_accuracy | accuracy_falloff | Expected Behavior |
|---------|-----|---------------|------------------|-------------------|
| **Low Accuracy** | `test_beam_low_acc` | 0.5 | 0.002 | ~62% at point-blank, degrades rapidly |
| **Medium Accuracy** | `test_beam_med_acc` | 2.0 | 0.001 | ~88% at point-blank, standard falloff |
| **High Accuracy** | `test_beam_high_acc` | 5.0 | 0.0005 | ~99% at point-blank, slow falloff |

---

### 3.2 Ship Classes (test_vehicleclasses.json)

> [!NOTE]
> All layers have `max_mass_pct: 1.0` (100% mass allowed in any layer) for maximum testing flexibility.

#### Naming Convention: `Test[Size]_[Layers]L`
- **Size**: S = 2,000t, M = 20,000t, L = 200,000t
- **Layers**: 2L, 3L, 4L, 5L

| Class | Max Mass | Hull | Layers | Status |
|-------|----------|------|--------|--------|
| `TestS_2L` | 2,000 | 20 | CORE, ARMOR | ✅ |
| `TestS_3L` | 2,000 | 20 | CORE, OUTER, ARMOR | ✅ |
| `TestS_4L` | 2,000 | 20 | CORE, INNER, OUTER, ARMOR | ✅ |
| `TestS_5L` | 2,000 | 20 | CORE, INNER, OUTER, WEAPONS, ARMOR | ✅ |
| `TestM_2L` | 20,000 | 200 | CORE, ARMOR | ✅ |
| `TestM_3L` | 20,000 | 200 | CORE, OUTER, ARMOR | ✅ |
| `TestM_4L` | 20,000 | 200 | CORE, INNER, OUTER, ARMOR | ✅ |
| `TestM_5L` | 20,000 | 200 | CORE, INNER, OUTER, WEAPONS, ARMOR | ✅ |
| `TestL_2L` | 200,000 | 2,000 | CORE, ARMOR | ✅ |
| `TestL_3L` | 200,000 | 2,000 | CORE, OUTER, ARMOR | ✅ |
| `TestL_4L` | 200,000 | 2,000 | CORE, INNER, OUTER, ARMOR | ✅ |
| `TestL_5L` | 200,000 | 2,000 | CORE, INNER, OUTER, WEAPONS, ARMOR | ✅ |
| `TestFighter` | 25 | 5 | CORE, ARMOR | ✅ |
| `TestSatellite` | 500 | 50 | CORE | ✅ |

> [!TIP]
> For mass-scaling tests, use the same ship class and add Mass Simulator components to vary total mass while keeping thrust constant.

---

## 4. AI Behavior Policies

### 4.1 Required Test-Specific AI Policies

These policies are needed for controlled, repeatable test simulations. Defined in `tests/data/test_movement_policies.json`:

| Policy ID | Behavior | Description |
|-----------|----------|-------------|
| `test_do_nothing` | **DoNothing** | No movement, no rotation, no firing. Ship sits completely still. |
| `test_straight_line` | **StraightLine** | Full thrust in initial facing direction. No rotation. No targeting. Moves until sim ends. |
| `test_orbit_target` | **OrbitTarget** | Circles around the target at a fixed distance. Maintains constant speed. |
| `test_erratic_maneuver` | **ErraticManeuver** | Random direction changes at random intervals. For testing accuracy degradation. |
| `test_rotate_in_place` | **RotateInPlace** | No translation. Continuous rotation at max turn rate. For testing arc weapon sweep. |
| `test_pass_through` | **PassThrough** | Moves in a straight line that passes through a specific point (firing arc test). |

> [!IMPORTANT]
> These behaviors are implemented in `ai_behaviors.py`.

---

### 4.2 Strategy Assignments for Test Ships

| Ship Role | Targeting Policy | Movement Policy |
|-----------|------------------|-----------------|
| Attacker (stationary) | `test_policy_1` | `test_do_nothing` |
| Attacker (rotating) | `test_policy_1` | `test_rotate_in_place` |
| Target (stationary) | `test_policy_1` | `test_do_nothing` |
| Target (linear) | `test_policy_1` | `test_straight_line` |
| Target (orbiting) | `test_policy_1` | `test_orbit_target` |
| Target (erratic) | `test_policy_1` | `test_erratic_maneuver` |

---

## 5. Ship Templates

### 5.1 Engine Test Ships

> Ship JSON files in `tests/data/ships/`. Contain **ONLY engines and mass simulators**.

| Ship Name | Class | Total Engines | Total Mass Simulators | Expected Thrust | Expected Mass | Expected Speed | Expected Accel |
|-----------|-------|---------------|----------------------|-----------------|---------------|----------------|----------------|
| `Test_Engine_1x_LowMass` | `TestS_2L` | 1× `test_engine_std` (500 thrust) | 0 | 500 | 40 | 312.5 | 78,125 |
| `Test_Engine_1x_MedMass` | `TestS_2L` | 1× `test_engine_std` | 2× Mass Sim 1k | 500 | 2040 | 6.13 | 0.30 |
| `Test_Engine_1x_HighMass` | `TestM_2L` | 1× `test_engine_std` | 10× Mass Sim 1k | 500 | 10220 | 1.22 | 0.012 |
| `Test_Engine_3x_LowMass` | `TestM_3L` | 3× `test_engine_std` | 0 | 1500 | 260 | 144.2 | 55,473 |
| `Test_Engine_3x_HighMass` | `TestL_3L` | 3× `test_engine_std` | 2× Mass Sim 10k | 1500 | 22060 | 1.70 | 7.70 |

#### Formulas (from `ship_stats.py`)

```python
K_SPEED = 25
K_THRUST = 2500

max_speed = (total_thrust * K_SPEED) / mass
acceleration = (total_thrust * K_THRUST) / (mass * mass)
```

---

### 5.2 Weapon Test Ships (Attackers)

> Ship JSON files in `tests/data/ships/`. Contain **ONLY the weapon being tested**.

| Ship Name | Weapon | Purpose |
|-----------|--------|---------|
| `Test_Attacker_Proj360` | `test_weapon_proj_omni` | Projectile, 360° arc tests |
| `Test_Attacker_Proj90` | `test_weapon_proj_fixed` | Projectile, 90° arc tests |
| `Test_Attacker_Beam360_Low` | `test_beam_low_acc` | Beam, 360°, low accuracy |
| `Test_Attacker_Beam360_Med` | `test_beam_med_acc` | Beam, 360°, medium accuracy |
| `Test_Attacker_Beam360_High` | `test_beam_high_acc` | Beam, 360°, high accuracy |
| `Test_Attacker_Beam90` | `test_weapon_beam_fixed` | Beam, 90° arc tests |
| `Test_Attacker_Seeker360` | `test_weapon_missile_omni` | Seeker missile tests |

---

### 5.3 Target Ships

> Ship JSON files in `tests/data/ships/`. Need **armor** (to absorb damage) and optionally **engines/thrusters**.

| Ship Name | Components | Movement Pattern |
|-----------|------------|------------------|
| `Test_Target_Stationary` | Armor only | None (DoNothing AI) |
| `Test_Target_Linear_Slow` | Armor + 1 Engine | Straight line, slow |
| `Test_Target_Linear_Fast` | Armor + 3 Engines | Straight line, fast |
| `Test_Target_Erratic_Small` | Armor + Engine + Thruster (small ship) | Erratic, high maneuverability |
| `Test_Target_Erratic_Large` | Armor + Engine + Thruster (large ship) | Erratic, low maneuverability |
| `Test_Target_Orbiting` | Armor + Engine + Thruster | Circular orbit around attacker |

---

## 6. Engine Components

### 6.1 Test Cases

| Test ID | Test Description | Ship JSON | Logged Verification |
|---------|------------------|-----------|---------------------|
| `ENG-001` | Base speed/accel calculation | `Test_Engine_1x_LowMass.json` | `SHIP_VELOCITY speed=312.5` at convergence |
| `ENG-002` | Speed decreases with mass | 3 separate sims: Low/Med/High mass | Log speeds show 1/mass relationship |
| `ENG-003` | Accel decreases with mass² | Same 3 ships | Log accelerations show 1/mass² relationship |
| `ENG-004` | Speed increases with engines | 1x vs 3x engine ships | 3x engines → ~3x speed in log |
| `ENG-005` | Ship reaches max speed | Any engine ship | `SHIP_VELOCITY` converges to `max_speed` |

### 6.2 Simulation Parameters

- **Simulation Duration**: 1000 ticks (10 seconds)
- **Log Events**: `SHIP_VELOCITY` at tick 0, 100, 500, 1000
- **Assertion Tolerance**: ±0.1% on final values
- **AI Behavior**: `straight_line` (full thrust forward)

### 6.3 Log Verification Example (ENG-001)

```
# Expected log output for Test_Engine_1x_LowMass (thrust=500, mass=40)
[TICK:0] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | speed=0.0
[TICK:100] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | speed=312.5  # max_speed reached
[TICK:1000] SHIP_VELOCITY | name=Test_Engine_1x_LowMass | speed=312.5  # sustained
```

**Verification**:
```python
parser = TestLogParser("tests/output/logs/ENG-001.log")
final_speed = parser.get_velocity_at_tick("Test_Engine_1x_LowMass", 1000)
assert abs(final_speed - 312.5) < 0.5, f"Expected 312.5, got {final_speed}"
```

---

## 7. Weapons: 360° Firing Arc

### 7.1 Projectile Weapons

#### 7.1.1 Accuracy Tests

| Test ID | Attacker | Target | AI Policy | Expected Log |
|---------|----------|--------|-----------|--------------|
| `PROJ360-001` | `Test_Attacker_Proj360` | `Test_Target_Stationary` | Both: `do_nothing` | All `HIT` events, no `MISS` |
| `PROJ360-002` | `Test_Attacker_Proj360` | `Test_Target_Linear_Slow` | Target: `straight_line` | All `HIT` (predictive leading) |
| `PROJ360-003` | `Test_Attacker_Proj360` | `Test_Target_Linear_Fast` | Target: `straight_line` | All `HIT` (predictive leading) |
| `PROJ360-004` | `Test_Attacker_Proj360` | `Test_Target_Erratic_Small` | Target: `erratic` | Mix of `HIT`/`MISS` (measure ratio) |
| `PROJ360-005` | `Test_Attacker_Proj360` | `Test_Target_Erratic_Large` | Target: `erratic` | Higher `HIT` ratio than small target |
| `PROJ360-006` | `Test_Attacker_Proj360` | Target at max_range + 100 | Both: `do_nothing` | `WEAPON_FIRE` events but 0 `HIT` events |

> [!IMPORTANT]
> Out-of-range test (PROJ360-006): The weapon **should fire** (log shows `WEAPON_FIRE`), but **no `HIT` should appear in log**.

#### 7.1.2 Damage Tests

| Test ID | Range | Expected Log |
|---------|-------|--------------|
| `PROJ360-DMG-10` | 10% of max range (100 px) | Sum of `HIT` damage == shots × weapon_damage |
| `PROJ360-DMG-50` | 50% of max range (500 px) | Sum of `HIT` damage == shots × weapon_damage |
| `PROJ360-DMG-90` | 90% of max range (900 px) | Sum of `HIT` damage == shots × weapon_damage |
| `PROJ360-DMG-BEYOND` | 110% of max range (1100 px) | 0 `HIT` events, 0 damage |

---

### 7.2 Beam Weapons

#### 7.2.1 Accuracy Formula (from `components.py`)

```python
def calculate_hit_chance(distance, attack_score_bonus=0.0, defense_score_penalty=0.0):
    """
    Sigmoid accuracy formula:
    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    """
    range_penalty = accuracy_falloff * distance
    net_score = (base_accuracy + attack_score_bonus) - (range_penalty + defense_score_penalty)
    clamped_score = max(-20.0, min(20.0, net_score))
    chance = 1.0 / (1.0 + math.exp(-clamped_score))
    return chance
```

#### 7.2.2 Accuracy Test Matrix

| Test ID | Beam Weapon | Target | Distance | Defense Score | Expected Hit Chance |
|---------|-------------|--------|----------|---------------|---------------------|
| `BEAM360-001` | Low Acc (0.5) | Stationary, Large | 0 | ~-2.5 (size) | **95.3%** |
| `BEAM360-002` | Low Acc (0.5) | Stationary, Large | 400 | ~-2.5 | **73.1%** |
| `BEAM360-003` | Low Acc (0.5) | Stationary, Large | 800 (max) | ~-2.5 | **31.0%** |
| `BEAM360-004` | Med Acc (2.0) | Stationary, Large | 0 | ~-2.5 | **98.9%** |
| `BEAM360-005` | Med Acc (2.0) | Stationary, Large | 400 | ~-2.5 | **96.8%** |
| `BEAM360-006` | Med Acc (2.0) | Stationary, Large | 800 (max) | ~-2.5 | **90.0%** |
| `BEAM360-007` | High Acc (5.0) | Stationary, Large | 0 | ~-2.5 | **99.9%** |
| `BEAM360-008` | High Acc (5.0) | Stationary, Large | 800 | ~-2.5 | **99.7%** |
| `BEAM360-009` | Med Acc (2.0) | Moving, Small (high maneuver) | 400 | ~+1.5 | **59.9%** |
| `BEAM360-010` | Med Acc (2.0) | Moving, Small (high maneuver) | 800 | ~+1.5 | **26.9%** |
| `BEAM360-011` | Any | Any at max_range + 100 | 900 | N/A | `WEAPON_FIRE` but no `HIT` (out of range) |

> [!NOTE]
> Run each test for **100+ shots**. Parse the log for `HIT` and `MISS` events to calculate empirical hit rate. Compare against expected probability (within ±5% tolerance).

---

### 7.3 Seeker Weapons

#### 7.3.1 Seeker Properties (from `projectiles.py` and `test_components.json`)

| Property | Value | Source |
|----------|-------|--------|
| `projectile_speed` | 1000 | Component definition |
| `turn_rate` | 90°/sec | Component definition |
| `endurance` | 5.0 sec | Component definition |
| `range` | 3000 | Component definition |
| `damage` | 100 | Component definition |

#### 7.3.2 Lifetime Tests

| Test ID | Target Distance | Expected Log |
|---------|-----------------|--------------|
| `SEEK360-001` | 500 (close) | `SEEKER_IMPACT` before t=1s |
| `SEEK360-002` | 2500 (mid) | `SEEKER_IMPACT` before lifetime (t≈2.5s) |
| `SEEK360-003` | 5000 (beyond) | `SEEKER_EXPIRE` at t=5s, no `SEEKER_IMPACT` |
| `SEEK360-004` | 4500 (edge) | Either `SEEKER_IMPACT` or `SEEKER_EXPIRE` |

#### 7.3.3 Point Defense Resistance Tests

| Test ID | Target PD Level | Number of Seekers | Expected Log |
|---------|-----------------|-------------------|--------------|
| `SEEK360-PD-001` | None | 10 | 10 `SEEKER_IMPACT` events |
| `SEEK360-PD-002` | 1× `test_weapon_pd_omni` | 10 | Measure `SEEKER_IMPACT` vs `SEEKER_DESTROYED` |
| `SEEK360-PD-003` | 3× `test_weapon_pd_omni` | 10 | Higher `SEEKER_DESTROYED` count |

#### 7.3.4 Tracking Tests

| Test ID | Target Behavior | Expected Log |
|---------|-----------------|--------------|
| `SEEK360-TRACK-001` | Stationary | `SEEKER_IMPACT` (direct flight) |
| `SEEK360-TRACK-002` | Linear movement | `SEEKER_IMPACT` (lead correction) |
| `SEEK360-TRACK-003` | Orbiting | `SEEKER_IMPACT` (curved pursuit) |
| `SEEK360-TRACK-004` | Erratic (high maneuverability) | May see `SEEKER_EXPIRE` if out-turned |

---

## 8. Weapons: 90° Firing Arc

### 8.1 Firing Constraint

> **Arc-constrained weapons fire ONLY if the predicted lead point falls within the firing arc.**

### 8.2 Scenario Matrix

All scenarios must be tested at **4 facing angles**:
- **0°** (Forward)
- **90°** (Starboard)
- **180°** (Rear)
- **270°** (Port)

---

### 8.3 Projectile Weapons (90° Arc)

#### 8.3.1 Pass-Through Scenario

**Setup**: Attacker is stationary (no rotation). Target moves in straight line that passes through attacker's firing arc.

| Test ID | Facing | Target Path | Expected Log |
|---------|--------|-------------|--------------|
| `PROJ90-PASS-F` | 0° (Forward) | Crosses in front | `WEAPON_FIRE` only when in arc |
| `PROJ90-PASS-S` | 90° (Starboard) | Crosses on right | `WEAPON_FIRE` only when in arc |
| `PROJ90-PASS-R` | 180° (Rear) | Crosses behind | `WEAPON_FIRE` only when in arc |
| `PROJ90-PASS-P` | 270° (Port) | Crosses on left | `WEAPON_FIRE` only when in arc |

**Log Measurements**:
- Count `WEAPON_FIRE` events
- Count `HIT` vs total shots
- Sum damage from `HIT` events

---

#### 8.3.2 Circling Target Scenario

**Setup**: Attacker is stationary, **cannot rotate** (`test_do_nothing`). Target orbits around attacker.

| Test ID | Facing | Expected Log |
|---------|--------|--------------|
| `PROJ90-CIRC-F` | 0° (Forward) | `WEAPON_FIRE` only in forward 90° |
| `PROJ90-CIRC-S` | 90° (Starboard) | `WEAPON_FIRE` only in starboard 90° |
| `PROJ90-CIRC-R` | 180° (Rear) | `WEAPON_FIRE` only in rear 90° |
| `PROJ90-CIRC-P` | 270° (Port) | `WEAPON_FIRE` only in port 90° |

**Assertions (from log)**:
- Weapon fires for ~25% of orbit time (90° of 360°)
- No `WEAPON_FIRE` when target is outside arc

---

#### 8.3.3 Rotating Ship Scenario

**Setup**: Target is stationary. Attacker rotates continuously (`test_rotate_in_place`).

> [!NOTE]
> This scenario requires the attacker to have **Thrusters** for rotation capability.

| Test ID | Weapon Facing | Expected Log |
|---------|---------------|--------------|
| `PROJ90-ROT-F` | 0° (Forward) | `WEAPON_FIRE` when arc sweeps over target |
| `PROJ90-ROT-S` | 90° (Starboard) | `WEAPON_FIRE` when arc sweeps over target |
| `PROJ90-ROT-R` | 180° (Rear) | `WEAPON_FIRE` when arc sweeps over target |
| `PROJ90-ROT-P` | 270° (Port) | `WEAPON_FIRE` when arc sweeps over target |

**Log Measurements**:
- Time between `WEAPON_FIRE` events
- Should be consistent with rotation speed

---

### 8.4 Beam Weapons (90° Arc)

> Run **identical scenarios** as Projectile 90° tests:
- `BEAM90-PASS-*` (Pass-through, all facings)
- `BEAM90-CIRC-*` (Circling target, all facings)
- `BEAM90-ROT-*` (Rotating ship, all facings)

**Additional Log Measurements**:
- `HIT` vs `MISS` ratio per arc window
- Total damage during arc window

---

### 8.5 Seeker Weapons (90° Arc)

#### 8.5.1 Launch Direction Rules

- Seekers launch with initial direction **consistent with firing arc**
- If target is **outside** the arc, seeker launches at **nearest arc edge**, then turns to track

#### 8.5.2 Launch Angle Tests

| Test ID | Target Position | Expected Log |
|---------|-----------------|--------------|
| `SEEK90-LAUNCH-001` | In arc center | `SEEKER_LAUNCH` direction toward target |
| `SEEK90-LAUNCH-002` | In arc edge | `SEEKER_LAUNCH` direction toward target |
| `SEEK90-LAUNCH-003` | 10° outside arc | `SEEKER_LAUNCH` at arc edge |
| `SEEK90-LAUNCH-004` | 90° outside arc | `SEEKER_LAUNCH` at closest arc edge |
| `SEEK90-LAUNCH-005` | 180° outside arc | `SEEKER_LAUNCH` at arc edge, long pursuit |

#### 8.5.3 Tracking from Arc Edge

| Test ID | Target Behavior | Expected Log |
|---------|-----------------|--------------|
| `SEEK90-EDGE-001` | Stationary at 45° outside arc | `SEEKER_IMPACT` (seeker turns and tracks) |
| `SEEK90-EDGE-002` | Moving away at 45° outside arc | May see `SEEKER_EXPIRE` |
| `SEEK90-EDGE-003` | Evasive at 45° outside arc | Possibly `SEEKER_EXPIRE` |

---

## 9. Implementation Checklist

### Phase 0: Infrastructure (Data)
- [x] Create mass simulator components (1000t, 10000t, 100000t) ✅
- [x] Create `test_beam_low_acc` component ✅
- [x] Create `test_beam_med_acc` component ✅  
- [x] Create `test_beam_high_acc` component ✅
- [x] Update `test_vehicleclasses.json` with 12 ship classes (3 sizes × 4 layer configs) ✅
- [x] Implement `test_do_nothing` AI policy ✅
- [x] Implement `test_straight_line` AI policy ✅
- [x] Implement `test_orbit_target` AI policy ✅
- [x] Implement `test_erratic_maneuver` AI policy ✅
- [x] Implement `test_rotate_in_place` AI policy ✅

### Phase 0.5: Test Harness (in `tests/simulation/`)
- [x] Create `tests/simulation/` directory structure ✅
- [x] Implement toggleable test logging system (`test_logger.py`) ✅
- [x] Create log event types (SHIP_SPAWN, SHIP_VELOCITY, WEAPON_FIRE, HIT, MISS, etc.) ✅
- [x] Integrate logging into test runner (disabled by default) ✅
- [x] Create `tests/simulation/test_log_parser.py` for log verification ✅
- [x] Create `tests/simulation/run_component_tests.py` ✅
- [x] Create test configuration format (JSON in `tests/simulation/test_configs/`) ✅
- [x] Create `tests/simulation/output/logs/` directory ✅
- [x] Fix fuel requirement to be data-driven (engines with fuel_cost=0 don't require fuel) ✅

### Phase 1: Engine Tests
- [ ] Create engine test ship JSON files (see Section 5.1)
- [ ] Create test configs for `ENG-001` through `ENG-005`
- [ ] Add velocity logging to ship update loop
- [ ] Verify logged speeds match formulas from `ship_stats.py`

### Phase 2: 360° Weapon Tests
- [ ] Create attacker ships (Section 5.2)
- [ ] Create target ships (Section 5.3)
- [ ] Add weapon fire/hit/miss logging
- [ ] Implement `PROJ360-001` through `PROJ360-006`
- [ ] Implement `PROJ360-DMG-*` damage tests
- [ ] Implement `BEAM360-001` through `BEAM360-011`
- [ ] Implement `SEEK360-*` lifetime tests
- [ ] Implement `SEEK360-PD-*` point defense tests
- [ ] Implement `SEEK360-TRACK-*` tracking tests

### Phase 3: 90° Arc Weapon Tests
- [ ] Implement `PROJ90-PASS-*` (4 facings)
- [ ] Implement `PROJ90-CIRC-*` (4 facings)
- [ ] Implement `PROJ90-ROT-*` (4 facings)
- [ ] Implement `BEAM90-*` (mirror of PROJ90)
- [ ] Implement `SEEK90-LAUNCH-*` launch angle tests
- [ ] Implement `SEEK90-EDGE-*` tracking from edge tests

---

## Appendix A: Quick Reference Formulas

### Engine Physics
```python
K_SPEED = 25
K_THRUST = 2500

max_speed = (total_thrust * K_SPEED) / mass
acceleration = (total_thrust * K_THRUST) / (mass ** 2)
turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)  # K_TURN = 25000
```

### Beam Weapon Accuracy (Sigmoid)
```python
import math

def hit_chance(base_accuracy, accuracy_falloff, distance, attack_bonus, defense_penalty):
    range_penalty = accuracy_falloff * distance
    net_score = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    clamped = max(-20.0, min(20.0, net_score))
    return 1.0 / (1.0 + math.exp(-clamped))
```

### Defense Score
```python
import math

def defense_score(diameter, acceleration, turn_speed, ecm_bonus):
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)  # Larger = negative = easier to hit
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))
    return size_score + maneuver_score + ecm_bonus
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-01 | Initial specification |
| 2.0 | 2026-01-01 | Major revision: Added test philosophy, AI policies, detailed ship templates, beam accuracy formula, seeker mechanics, 90° arc scenarios, and implementation checklist |
| 2.1 | 2026-01-01 | Infrastructure update: Mass simulators (1k/10k/100k), 12 ship classes (S/M/L × 2/3/4/5 layers), all with 100% layer mass allowance |
| 3.0 | 2026-01-01 | **Architecture change**: Converted from unit tests to simulation-based behavioral tests. Added test harness infrastructure (Section 2), toggleable logging system, log event types, test runner, log parser. All test cases now specify expected log output rather than direct assertions. Added Phase 0.5 checklist for test harness implementation. |
