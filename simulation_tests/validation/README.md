# Validation System Documentation

## Overview

The validation system provides two types of rules for verifying test correctness:

1. **ExactMatchRule** - Validates test metadata matches actual component data
2. **StatisticalTestRule** - Validates observed outcomes match expected outcomes using TOST equivalence testing

## ExactMatchRule - Data Verification

### Purpose

Ensures that test expectations accurately reflect the actual component definitions in the game data.

### Why This Matters

Tests calculate expected outcomes based on component stats (damage, accuracy, range, etc.). If the component data changes but the test isn't updated, the test will fail or give misleading results.

ExactMatchRule **catches these mismatches automatically**.

### Syntax

```python
ExactMatchRule(
    name='Human Readable Name',       # Displayed in results
    path='dot.notation.path',         # Path to value on scenario object
    expected=value                    # Expected value (any type)
)
```

### Common Paths

| Path | Accesses | Example Value |
|------|----------|---------------|
| `attacker.weapon.damage` | Weapon damage | `1` |
| `attacker.weapon.base_accuracy` | Base accuracy | `0.5` |
| `attacker.weapon.accuracy_falloff` | Falloff per pixel | `0.002` |
| `attacker.weapon.range` | Maximum range | `800` |
| `target.mass` | Target ship mass | `400.0` |
| `attacker.mass` | Attacker ship mass | `25.0` |
| `target.max_hp` | Target max HP | `1000000500` |

### How It Works

1. **Parse Path**: Splits `'attacker.weapon.damage'` into `['attacker', 'weapon', 'damage']`
2. **Navigate Object**:
   ```python
   obj = scenario
   for attr in ['attacker', 'weapon', 'damage']:
       obj = getattr(obj, attr)
   actual_value = obj  # Value found
   ```
3. **Compare Values**:
   - Integers: `actual == expected`
   - Floats: `abs(actual - expected) < 1e-9`
   - Strings: `actual == expected`
4. **Result**: PASS if values match, FAIL if different

### Example

```python
ExactMatchRule(
    name='Beam Weapon Damage',
    path='attacker.weapon.damage',
    expected=1
)
```

**Execution**:
```python
# 1. Navigate path
scenario.attacker                              # Ship object
scenario.attacker.weapon                       # Component with BeamWeaponAbility
scenario.attacker.weapon.damage                # = 1

# 2. Compare
actual = 1
expected = 1
actual == expected  # True

# 3. Result
{
    'name': 'Beam Weapon Damage',
    'status': 'PASS',
    'message': 'Expected: 1, Actual: 1, Difference: 0.0',
    'p_value': None,
    'tolerance': None
}
```

### Path Resolution for Weapons

Weapons are accessed via a property that finds the component with the weapon ability:

```python
# In TestScenario or Ship class:
@property
def weapon(self):
    """Get first weapon component."""
    for component in self.components:
        if hasattr(component, 'abilities'):
            for ability_name in ['BeamWeaponAbility', 'ProjectileWeaponAbility']:
                if ability_name in component.abilities:
                    return component.get_ability(ability_name)
    return None

# This allows:
# attacker.weapon.damage  # Works!
```

### Standard Validation Rules for Beam Tests

Every beam test should include these 5 ExactMatchRules:

```python
validation_rules=[
    ExactMatchRule(
        name='Beam Weapon Damage',
        path='attacker.weapon.damage',
        expected=1
    ),
    ExactMatchRule(
        name='Base Accuracy',
        path='attacker.weapon.base_accuracy',
        expected=0.5  # Or 0.8, 0.99 depending on weapon
    ),
    ExactMatchRule(
        name='Accuracy Falloff',
        path='attacker.weapon.accuracy_falloff',
        expected=0.002  # Or 0.001, 0.0001 depending on weapon
    ),
    ExactMatchRule(
        name='Weapon Range',
        path='attacker.weapon.range',
        expected=800
    ),
    ExactMatchRule(
        name='Target Mass',
        path='target.mass',
        expected=400.0  # Or 600.0, 65.0 depending on target
    )
]
```

## StatisticalTestRule - TOST Equivalence Testing

### Purpose

Proves that observed probabilistic outcomes (like hit rates) are **statistically equivalent** to expected outcomes within a specified margin.

### Traditional vs TOST

**Traditional Hypothesis Testing**:
- Null hypothesis: μ = θ (no difference)
- Alternative: μ ≠ θ (significant difference)
- p < 0.05 means "significantly **different**"
- **Cannot prove equivalence**

**TOST (Two One-Sided Tests)**:
- Tests two hypotheses simultaneously
- H₁: μ - θ > -ε (not too low)
- H₂: μ - θ < +ε (not too high)
- p < 0.05 means "proven **equivalent** within ±ε"
- **Can prove equivalence**

### Why TOST?

Game mechanics are probabilistic. We need to prove:
- 50% hit rate weapon actually hits ~50% of the time
- Not 45% (too low)
- Not 55% (too high)
- But somewhere in ±ε margin around 50%

Traditional testing can only say "not significantly different" (weak statement).
TOST says "**proven equivalent within margin**" (strong statement).

### Syntax

```python
StatisticalTestRule(
    name='Hit Rate',                          # Rule name
    test_type='binomial',                     # Test type (currently only binomial)
    expected_probability=0.5318,              # Expected outcome (0.0-1.0)
    equivalence_margin=0.06,                  # ±6% margin (0.06 for 500-tick, 0.01 for 100k)
    trials_expr='ticks_run',                  # Expression for number of trials
    successes_expr='damage_dealt',            # Expression for number of successes
    description='Each beam hit = 1 damage'    # Human-readable explanation
)
```

### Parameters Explained

#### expected_probability

The theoretical probability calculated from game formulas.

**For beam weapons**:
```python
# Example: Low accuracy beam at point blank
base_acc = 0.5
falloff = 0.002
surface_distance = 20.53  # NOT center distance!
attack_bonus = 0.0
defense_penalty = 0.3316

range_penalty = surface_distance * falloff  # 0.0411
net_score = (base_acc + attack_bonus) - (range_penalty + defense_penalty)  # 0.1589
expected_probability = 1 / (1 + exp(-net_score))  # 0.5396

# More precise calculation gives 0.5318
```

#### equivalence_margin

How close is "close enough"?

| Test Duration | Ticks | Standard Error | Recommended Margin | Rationale |
|---------------|-------|----------------|-------------------|-----------|
| **Standard** | 500 | ~2.2% | ±6% | 3× SE, quick validation |
| **High-Tick** | 100,000 | ~0.16% | ±1% | 6× SE, precise validation |

**Standard Error Formula** (for binomial at p≈0.5):
```
SE ≈ 0.5 / √n

Examples:
n=500    → SE ≈ 2.2%
n=1000   → SE ≈ 1.6%
n=10000  → SE ≈ 0.5%
n=100000 → SE ≈ 0.16%
```

**Choosing Margin**:
- Margin should be ≥3× SE for reliable testing
- Tighter margins require more samples
- Game design consideration: ±6% is acceptable gameplay variance

#### trials_expr and successes_expr

Expressions evaluated on `scenario.results` dict to get trial count and success count.

**Common patterns**:

```python
# Pattern 1: Direct beam hits (1 damage per hit)
trials_expr='ticks_run'        # Number of ticks = number of firing opportunities
successes_expr='damage_dealt'  # Damage dealt = number of hits (since damage=1)

# Pattern 2: Counted projectiles
trials_expr='projectiles_fired'   # Track projectiles fired
successes_expr='projectiles_hit'  # Track projectiles that hit

# Pattern 3: Boolean events
trials_expr='shields_tested'       # Number of shield activations
successes_expr='shields_blocked'   # Number of successful blocks
```

### How TOST Works (Detailed)

Given:
- `n` = trials (e.g., 500 ticks)
- `k` = successes (e.g., 260 hits)
- `p̂` = k/n = observed proportion (260/500 = 0.52 = 52%)
- `θ` = expected proportion (0.5318 = 53.18%)
- `ε` = equivalence margin (0.06 = ±6%)

**Step 1: Calculate Standard Error**
```
SE = √(θ(1-θ)/n)
SE = √(0.5318 × 0.4682 / 500)
SE = √(0.000498)
SE = 0.0223 = 2.23%
```

**Step 2: Test Hypothesis 1 (Not Too Low)**
```
H₁: p̂ - θ > -ε
    0.52 - 0.5318 > -0.06
    -0.0118 > -0.06  ✓ TRUE

Z₁ = (p̂ - θ + ε) / SE
Z₁ = (0.52 - 0.5318 + 0.06) / 0.0223
Z₁ = 0.0482 / 0.0223
Z₁ = 2.161

p₁ = CDF(Z₁) = CDF(2.161) = 0.9846
# This is the one-sided test, we want lower tail
p₁ = 0.0154
```

**Step 3: Test Hypothesis 2 (Not Too High)**
```
H₂: p̂ - θ < +ε
    0.52 - 0.5318 < +0.06
    -0.0118 < +0.06  ✓ TRUE

Z₂ = (p̂ - θ - ε) / SE
Z₂ = (0.52 - 0.5318 - 0.06) / 0.0223
Z₂ = -0.0718 / 0.0223
Z₂ = -3.220

p₂ = 1 - CDF(Z₂) = 1 - CDF(-3.220) = 1 - 0.0006 = 0.9994
# Upper tail
p₂ = 0.0006
```

**Step 4: Determine Final Result**
```
p_final = max(p₁, p₂)
p_final = max(0.0154, 0.0006)
p_final = 0.0154

Decision:
p_final < 0.05  →  PASS (equivalence proven)
```

### Interpreting P-Values

| P-Value | Interpretation | Action |
|---------|----------------|--------|
| **< 0.01** | Strong evidence of equivalence | Excellent! |
| **0.01 - 0.05** | Equivalence proven at 95% confidence | PASS |
| **0.05 - 0.10** | Weak evidence, not quite proven | Consider re-running or checking expected value |
| **> 0.10** | Not equivalent (or need more samples) | Check calculations, increase sample size, or adjust margin |

### Result Object

```python
{
    'name': 'Hit Rate',
    'status': 'PASS',  # or 'FAIL'
    'message': 'Hit rate 52.00% equivalent to expected 53.18% within ±6.00% (p=0.0154)',
    'p_value': 0.0154,
    'tolerance': 0.05,
    'expected': 0.5318,
    'observed': 0.52,
    'margin': 0.06,
    'lower_bound': 0.4718,  # 53.18% - 6%
    'upper_bound': 0.5918   # 53.18% + 6%
}
```

### Example: Full Validation

```python
# Test: BEAM360-001 (Low Accuracy Point Blank)
# Expected: 53.18% hit rate
# Run: 500 ticks
# Observed: 260 hits = 52.00%

StatisticalTestRule(
    name='Hit Rate',
    test_type='binomial',
    expected_probability=0.5318,
    equivalence_margin=0.06,
    trials_expr='ticks_run',
    successes_expr='damage_dealt',
    description='Each beam hit = 1 damage, so damage = hit count'
)

# Execution:
trials = scenario.results['ticks_run']        # 500
successes = scenario.results['damage_dealt']  # 260
observed = 260 / 500                          # 0.52

# TOST calculation (see above)
# p_final = 0.0154 < 0.05 → PASS

# Result displayed:
[PASS] Hit Rate
  Hit rate 52.00% equivalent to expected 53.18% within ±6.00% (p=0.0154)
  Lower bound: 47.18%, Upper bound: 59.18%
  Observed is within equivalence region.
```

## Validation Execution

### In TestScenario.verify()

```python
def verify(self, engine):
    """Verify test results."""
    # 1. Calculate actual outcomes
    damage_dealt = self.initial_hp - self.target.hp
    hit_rate = damage_dealt / engine.tick_count

    # 2. Store in results dict
    self.results['damage_dealt'] = damage_dealt
    self.results['hit_rate'] = hit_rate
    self.results['ticks_run'] = engine.tick_count
    self.results['initial_hp'] = self.initial_hp
    self.results['final_hp'] = self.target.hp

    # 3. Run validation (base class method)
    self.results['validation_results'] = self.run_validation()

    # 4. Determine overall pass/fail
    self.passed = all(
        r['status'] == 'PASS'
        for r in self.results['validation_results']
    )

    return self.passed
```

### run_validation() Implementation

```python
def run_validation(self) -> List[Dict[str, Any]]:
    """Execute all validation rules."""
    results = []

    for rule in self.metadata.validation_rules:
        if isinstance(rule, ExactMatchRule):
            result = self._run_exact_match_rule(rule)
        elif isinstance(rule, StatisticalTestRule):
            result = self._run_statistical_rule(rule)
        else:
            result = {
                'name': 'Unknown Rule',
                'status': 'FAIL',
                'message': f'Unknown rule type: {type(rule)}'
            }

        results.append(result)

    return results
```

## Standard Test Patterns

### Pattern 1: Beam Weapon Accuracy Test (Standard)

```python
metadata = TestMetadata(
    test_id="BEAM360-XXX",
    max_ticks=500,
    validation_rules=[
        # Data verification (5 rules)
        ExactMatchRule(name='Beam Weapon Damage', path='attacker.weapon.damage', expected=1),
        ExactMatchRule(name='Base Accuracy', path='attacker.weapon.base_accuracy', expected=0.5),
        ExactMatchRule(name='Accuracy Falloff', path='attacker.weapon.accuracy_falloff', expected=0.002),
        ExactMatchRule(name='Weapon Range', path='attacker.weapon.range', expected=800),
        ExactMatchRule(name='Target Mass', path='target.mass', expected=400.0),

        # Statistical validation (1 rule)
        StatisticalTestRule(
            name='Hit Rate',
            test_type='binomial',
            expected_probability=0.5318,  # Calculated from surface distance
            equivalence_margin=0.06,      # ±6% for 500 ticks
            trials_expr='ticks_run',
            successes_expr='damage_dealt',
            description='Each beam hit = 1 damage'
        )
    ]
)
```

### Pattern 2: High-Tick Precision Test

```python
metadata = TestMetadata(
    test_id="BEAM360-XXX-HT",
    max_ticks=100000,
    tags=["high-tick", "precision"],
    validation_rules=[
        # Same 5 ExactMatchRules as standard test...

        # Tighter margin for high sample count
        StatisticalTestRule(
            name='Hit Rate',
            test_type='binomial',
            expected_probability=0.5702,  # Recalculated for mass=600 target
            equivalence_margin=0.01,      # ±1% for 100k ticks
            trials_expr='ticks_run',
            successes_expr='damage_dealt',
            description='High precision test with 100k ticks'
        )
    ]
)
```

### Pattern 3: Deterministic Test (No Statistical Rule)

```python
metadata = TestMetadata(
    test_id="BEAM360-011",
    max_ticks=500,
    validation_rules=[
        # Only ExactMatchRules for deterministic tests
        ExactMatchRule(name='Weapon Range', path='attacker.weapon.range', expected=800),
        ExactMatchRule(name='Actual Distance', path='distance_to_target', expected=900),
        ExactMatchRule(name='Damage Dealt', path='damage_dealt', expected=0),  # Out of range
    ]
)
```

## Common Pitfalls

### 1. Using Center Distance Instead of Surface Distance

```python
# WRONG - Expected value too low
center_distance = 50.0
expected_hit_chance = calculate_hit_chance(0.5, 0.002, 50.0, 0.0, 0.30)
# Result: Test FAILS because actual uses surface distance

# CORRECT - Use surface distance
target_radius = 40 * ((400 / 1000) ** (1/3))  # 29.47px
surface_distance = 50.0 - target_radius        # 20.53px
expected_hit_chance = calculate_hit_chance(0.5, 0.002, 20.53, 0.0, 0.30)
# Result: Test PASSES
```

### 2. Margin Too Tight for Sample Size

```python
# PROBLEMATIC - Margin too tight
StatisticalTestRule(
    name='Hit Rate',
    expected_probability=0.5318,
    equivalence_margin=0.01,  # ±1% with only 500 samples
    trials_expr='ticks_run'   # 500 ticks → SE ≈ 2.2%
)
# Margin < 3×SE, test may fail due to random variance

# BETTER - Appropriate margin
StatisticalTestRule(
    name='Hit Rate',
    expected_probability=0.5318,
    equivalence_margin=0.06,  # ±6% with 500 samples
    trials_expr='ticks_run'   # 500 ticks → SE ≈ 2.2%, 6% ≈ 3×SE
)
```

### 3. Wrong Expression for Successes

```python
# WRONG - Using hit_rate (float) instead of count
StatisticalTestRule(
    trials_expr='ticks_run',     # 500
    successes_expr='hit_rate'    # 0.52 (NOT a count!)
)
# Binomial test expects INTEGER counts

# CORRECT - Use damage_dealt (count)
StatisticalTestRule(
    trials_expr='ticks_run',        # 500
    successes_expr='damage_dealt'   # 260 (count)
)
```

### 4. Forgotten to Store Results

```python
# WRONG - Results not stored
def verify(self, engine):
    damage_dealt = self.initial_hp - self.target.hp
    # Forgot to store!
    self.results['validation_results'] = self.run_validation()
    # StatisticalTestRule can't find 'damage_dealt' in results!

# CORRECT - Store all metrics
def verify(self, engine):
    damage_dealt = self.initial_hp - self.target.hp
    self.results['damage_dealt'] = damage_dealt  # Store!
    self.results['ticks_run'] = engine.tick_count
    self.results['validation_results'] = self.run_validation()
```

## Debugging Validation Failures

### ExactMatchRule Failures

```
[FAIL] Base Accuracy
  Expected: 0.5, Actual: 0.6, Difference: 0.1
```

**Possible causes**:
1. Component JSON was updated but test wasn't
2. Wrong component ID in ship JSON
3. Test expected value is wrong

**Debug steps**:
1. Check component definition in `components.json`
2. Verify ship uses correct component ID
3. Update test expected value if component changed intentionally

### StatisticalTestRule Failures

```
[FAIL] Hit Rate
  Hit rate 45.00% NOT equivalent to expected 53.18% within ±6.00% (p=0.1234)
  Lower bound: 47.18%, Upper bound: 59.18%
  Observed 45.00% is below equivalence region.
```

**Possible causes**:
1. Expected probability calculation is wrong (surface distance issue?)
2. Combat system has a bug
3. Random bad luck (5% chance)

**Debug steps**:

1. **Verify expected calculation**:
   ```python
   print(f"Target radius: {target_radius:.2f}px")
   print(f"Surface distance: {surface_distance:.2f}px")
   print(f"Defense score: {defense_score:.4f}")
   print(f"Expected hit chance: {expected_hit_chance:.4f}")
   ```

2. **Run test multiple times**:
   - If p-value varies significantly, it's random variance
   - If p-value is consistently high, expected value is likely wrong

3. **Enable combat system debug logging**:
   ```python
   # Add to collision.py temporarily
   if random.random() < chance:
       print(f"DEBUG: Hit at distance {hit_dist:.2f}, chance {chance:.4f}")
   ```

4. **Use high-tick test**:
   - 100k ticks reduces random variance dramatically
   - SE ≈ 0.16% vs 2.2% for 500 ticks

## See Also

- `../COMBAT_LAB_DOCUMENTATION.md` - Complete system overview
- `../test_framework/README.md` - Test framework architecture
- `rules.py` - Rule class implementations
- `validators.py` - Validation execution logic
