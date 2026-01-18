# BeamWeaponAbility Test Suite

## Ability Under Test

`BeamWeaponAbility` - Instant-hit weapon with accuracy-based hit probability.

Beam weapons fire instantaneously and resolve hits immediately based on a sigmoid probability formula. Unlike projectile weapons, beams have no travel time.

---

## Core Formulas

### Hit Probability (Sigmoid)

```
P_hit = 1 / (1 + e^(-x))

where:
  x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
  range_penalty = accuracy_falloff × surface_distance
  surface_distance = center_distance - target_radius
  target_radius = 40 × (mass / 1000)^(1/3)
```

### Defense Score

```
defense_score = size_score + maneuver_score + ecm_score

where:
  size_score = -2.5 × log₁₀(diameter / 80)
  diameter = radius × 2
  maneuver_score = sqrt(acceleration / 20 + turn_speed / 360)
  ecm_score = sum of ToHitDefenseModifier abilities
```

### Example Calculation (BEAMWEAPON-001)

```
Given:
  center_distance = 50 px
  target_mass = 400
  base_accuracy = 0.5
  accuracy_falloff = 0.002

Step 1: target_radius = 40 × (400/1000)^(1/3) = 29.47 px
Step 2: surface_distance = 50 - 29.47 = 20.53 px
Step 3: range_penalty = 0.002 × 20.53 = 0.0411
Step 4: defense_score = -2.5 × log₁₀(58.94/80) = 0.3316
Step 5: net_score = 0.5 - 0.0411 - 0.3316 = 0.1273
Step 6: P_hit = 1/(1 + e^(-0.1273)) = 0.5318 (53.18%)
```

---

## Behaviors to Test

### Expected Behaviors

| ID | Behavior | Test ID | Status |
|----|----------|---------|--------|
| E1 | Beam hits target based on sigmoid formula | BEAMWEAPON-001 to 008 | ✓ |
| E2 | Hit rate decreases with distance (range penalty) | BEAMWEAPON-001,002,003 | ✓ |
| E3 | Higher base_accuracy = higher hit rate | BEAMWEAPON-001,004,007 | ✓ |
| E4 | Lower accuracy_falloff = better long-range accuracy | BEAMWEAPON-003,006,008 | ✓ |
| E5 | Moving targets harder to hit (defense penalty) | BEAMWEAPON-009,010 | ✓ |
| E6 | Damage dealt equals hits × damage_per_hit | BEAMWEAPON-001 | ✓ |
| E7 | Beam fires every tick (reload=0) | BEAMWEAPON-001 | ✓ |

### Unexpected Behaviors (Negative Tests)

| ID | Behavior | Test ID | Status |
|----|----------|---------|--------|
| U1 | Beam does NOT hit beyond max range | BEAMWEAPON-011 | ✓ |
| U2 | Beam does NOT hit outside firing arc | TODO | - |
| U3 | Beam does NOT fire without energy (if applicable) | TODO | - |
| U4 | Beam does NOT damage friendly ships | TODO | - |

---

## Test Matrix

### By Accuracy Level

| Accuracy | base_accuracy | accuracy_falloff | Tests |
|----------|---------------|------------------|-------|
| Low | 0.5 | 0.002 | BEAMWEAPON-001, 002, 003 |
| Medium | 2.0 | 0.001 | BEAMWEAPON-004, 005, 006, 009, 010 |
| High | 5.0 | 0.0005 | BEAMWEAPON-007, 008 |

### By Distance

| Distance Type | Surface Distance | Tests |
|---------------|------------------|-------|
| Point Blank | ~20 px | BEAMWEAPON-001, 004, 007 |
| Mid Range | ~370 px | BEAMWEAPON-002, 005, 009 |
| Max Range | ~720 px | BEAMWEAPON-003, 006, 008, 010 |
| Beyond Range | >800 px | BEAMWEAPON-011 |

### By Target Type

| Target | Behavior | Tests |
|--------|----------|-------|
| Stationary (mass=400) | No defense from maneuverability | BEAMWEAPON-001 to 008, 011 |
| Erratic (mass=65) | High defense from movement | BEAMWEAPON-009, 010 |

---

## Test Components

### Beam Weapons

| Component ID | base_accuracy | accuracy_falloff | damage | range | arc |
|--------------|---------------|------------------|--------|-------|-----|
| `test_beam_low_acc_1dmg` | 0.5 | 0.002 | 1 | 800 | 360 |
| `test_beam_med_acc_1dmg` | 2.0 | 0.001 | 1 | 800 | 360 |
| `test_beam_high_acc_1dmg` | 5.0 | 0.0005 | 1 | 800 | 360 |

**Design Notes**:
- All beams do 1 damage per hit for easy statistical counting (hits = damage_dealt)
- Range of 800 is sufficient for all tests (simplest single variant)
- Arc of 360 is simplest (no targeting complexity)
- Reload of 0 means beam fires every tick

### Test Ships

| Ship | Component | Mass | Purpose |
|------|-----------|------|---------|
| `Test_Attacker_Beam360_Low.json` | test_beam_low_acc_1dmg | 25 | Low accuracy tests |
| `Test_Attacker_Beam360_Med.json` | test_beam_med_acc_1dmg | 25 | Medium accuracy tests |
| `Test_Attacker_Beam360_High.json` | test_beam_high_acc_1dmg | 25 | High accuracy tests |
| `Test_Target_Stationary.json` | test_armor_extreme_hp | 400 | Standard stationary target |
| `Test_Target_Erratic_Small.json` | - | 65 | Moving target with evasion |

---

## Expected Hit Rates Reference

### Stationary Target (mass=400, defense=0.3316)

| Test ID | Accuracy | Surface Dist | Range Penalty | Net Score | Expected P |
|---------|----------|--------------|---------------|-----------|------------|
| BEAMWEAPON-001 | Low (0.5) | 20.53 px | 0.0411 | 0.1273 | 53.18% |
| BEAMWEAPON-002 | Low (0.5) | 370.53 px | 0.7411 | -0.5727 | 36.07% |
| BEAMWEAPON-003 | Low (0.5) | 720.53 px | 1.4411 | -1.2727 | 21.86% |
| BEAMWEAPON-004 | Med (2.0) | 20.53 px | 0.0205 | 1.6479 | 83.85% |
| BEAMWEAPON-005 | Med (2.0) | 370.53 px | 0.3705 | 1.2979 | 78.55% |
| BEAMWEAPON-006 | Med (2.0) | 720.53 px | 0.7205 | 0.9479 | 72.07% |
| BEAMWEAPON-007 | High (5.0) | 20.53 px | 0.0103 | 4.6581 | 99.06% |
| BEAMWEAPON-008 | High (5.0) | 720.53 px | 0.3603 | 4.3081 | 98.66% |

### Erratic Target (mass=65, defense=3.1408)

| Test ID | Accuracy | Surface Dist | Range Penalty | Net Score | Expected P |
|---------|----------|--------------|---------------|-----------|------------|
| BEAMWEAPON-009 | Med (2.0) | 383.92 px | 0.3839 | -1.5247 | 4.84% |
| BEAMWEAPON-010 | Med (2.0) | 733.92 px | 0.7339 | -1.8747 | 3.47% |

---

## Statistical Validation

### Standard Tests (500 ticks, ±6% margin)

Minimum ticks calculation:
```
n_min = (z² × p × (1-p)) / ε²
n_min = (1.96² × 0.5 × 0.5) / 0.06²  (worst case p=0.5)
n_min ≈ 267 ticks

With 2x buffer: 500 ticks
```

### High-Tick Tests (100k ticks, ±1% margin)

For precise validation (p < 0.001 significance):
```
n_min = (2.58² × 0.5 × 0.5) / 0.01²
n_min ≈ 16,641 ticks

With buffer: 100,000 ticks
```

---

## Validation Rules

Each test should have TWO validation layers:

1. **Formula Validation** (DeterministicMatchRule)
   - Verifies the expected hit probability is calculated correctly
   - Catches bugs in test setup or formula implementation

2. **Outcome Validation** (StatisticalTestRule)
   - Verifies actual hit rate matches expected statistically
   - Catches bugs in game engine hit resolution

Example:
```python
validation_rules=[
    DeterministicMatchRule(
        name='Expected Hit Chance',
        path='results.expected_hit_chance',
        expected=0.5318,
        description='P = 1/(1+e^-0.1273) from sigmoid formula'
    ),
    StatisticalTestRule(
        name='Hit Rate',
        test_type='binomial',
        expected_probability=0.5318,
        equivalence_margin=0.06,
        trials_expr='ticks_run',
        successes_expr='damage_dealt'
    )
]
```

---

## Source Files

- **Scenario Code**: `simulation_tests/scenarios/beam_scenarios.py`
- **Test Constants**: `simulation_tests/test_constants.py`
- **Production Code**: `game/simulation/components/abilities/weapons.py`
- **Hit Resolution**: `game/engine/collision.py`
- **Defense Calculation**: `game/simulation/entities/ship_stats.py`
