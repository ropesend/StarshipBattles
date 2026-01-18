# Simulation Test Protocol

This document defines the formal protocol for constructing simulation tests in the Combat Lab.

---

## Directory Structure

**Test Data** (isolated from production):
- `simulation_tests/data/` - All test data files
  - `simulation_tests/data/components/` - Test-only components
  - `simulation_tests/data/ships/` - Test ship configurations
  - `simulation_tests/data/vehicle_classes/` - Test hull classes

**Production Data** (never modified by tests):
- `data/` - Production game data

Tests MUST use only test data. This isolation ensures tests don't break production and production changes don't silently break tests.

---

## Component Mass Convention

**Rule**: Test components have 0 mass. Ship mass comes ONLY from:
1. **Hull components** (standardized masses)
2. **Mass Simulators** (when testing mass-dependent mechanics)

### Why Zero-Mass Components?

Without this convention, changing a weapon/armor component changes ship mass, which affects:
- Ship radius (cube root scaling from mass)
- Defense score (based on diameter)
- Expected hit rates in weapon tests
- Acceleration and max speed in propulsion tests

By giving all non-hull components 0 mass:
- Regular and High-Tick test variants have **identical expected hit rates**
- Adding/removing components doesn't accidentally change ship mass
- Mass is explicit and predictable
- Test maintenance is simplified

### Standard Hull Masses

| Hull ID | Mass | Radius | Use Case |
|---------|------|--------|----------|
| `hull_test_xs` | 100 | 18.57 px | Minimum mass (matches physics safeguard) |
| `hull_test_s` | 400 | 29.47 px | Standard small target |
| `hull_test_m` | 1000 | 40.00 px | Reference mass target |
| `hull_test_l` | 4000 | 63.50 px | Large target |
| `hull_test_fighter` | 25 | 11.70 px | Fighter scale |
| `hull_test_satellite` | 100 | 18.57 px | Matches safeguard |

**Radius Formula**: `radius = 40 × (mass/1000)^(1/3)`

### Mass Simulators

When you need specific mass values for testing mass-dependent mechanics:
- `test_mass_sim_1k` - Adds 1,000 mass
- `test_mass_sim_10k` - Adds 10,000 mass
- `test_mass_sim_100k` - Adds 100,000 mass

Use these only when testing how mass affects behavior (e.g., acceleration tests with different mass tiers).

### Physics Safeguard

The physics code uses `max(ship.mass, 100)` for radius calculation, preventing division-by-zero issues with very low mass values.

---

## Test Suite Organization

Tests are organized into **Test Suites** named after the ability class being tested.

### Suite Structure

- **Suite Name**: Matches the ability class name exactly (e.g., `BeamWeaponAbility`, `EngineAbility`, `ManeuveringThruster`)
- **Suite Document**: `simulation_tests/suites/{AbilityClassName}.md`
- **Test ID Format**: `{ABILITYNAME}-NNN` (e.g., `BEAMWEAPON-001`, `ENGINE-001`, `THRUSTER-001`)

### Suite Document Contents

Each suite document (`simulation_tests/suites/{AbilityName}.md`) contains:

1. **Ability Description** - What the ability does
2. **Core Formulas** - Mathematical formulas used by the ability
3. **Expected Behaviors** - What SHOULD happen (positive tests)
4. **Unexpected Behaviors** - What should NOT happen (negative tests)
5. **Test Coverage Matrix** - Which test covers each behavior
6. **Test Components** - Components used by tests in this suite

The Combat Lab UI loads and displays the suite document when a category is selected.

### Suite Document Location

```
simulation_tests/
  suites/
    BeamWeaponAbility.md
    EngineAbility.md
    ManeuveringThruster.md
    ...
```

---

## Part 1: General Protocol

### Step 1: Identify the Ability Under Test

Determine the single ability or mechanic you are testing. Examples:
- Engine provides thrust
- Thruster provides turn rate
- Weapon deals damage
- Armor absorbs damage
- ECM reduces lock-on chance

### Step 2: Reference the Suite Document

The **Suite Document** (`simulation_tests/suites/{AbilityName}.md`) contains the master list of expected and unexpected behaviors for the ability.

Before creating a new test:
1. Check the suite document to see which behaviors are already covered
2. Identify which behavior from the list this test will validate
3. Update the coverage matrix in the suite document after implementing

**Note**: Each test validates ONE specific behavior from the suite's behavior list. The suite document is the master checklist that shows complete test coverage.

### Step 3: Select One Behavior to Test

Pick a single behavior from the suite document's behavior list. Each test validates ONE specific behavior.

### Step 4: Design the Simplest Possible Scenario

#### 4a: Choose/Create the Simplest Vehicle Class
- Use the smallest hull that meets test requirements
- Prefer hulls with fewer slots if components aren't needed

#### 4b: Choose Minimum Components
- Only add components absolutely required to test the behavior
- Ships that don't move don't need engines
- Ships that aren't targets don't need armor/shields
- Ships that don't turn don't need maneuvering thrusters

#### 4c: Use Simplest Component Variants
- Prefer components with fewer abilities
- If a component has 2 abilities and you only need 1, create a test variant with just that ability
- **Rule**: Given choice between 1 component with 2 abilities vs 2 components with 1 ability each, choose 2 components
- **Exception**: When testing resource consumption, you may need both abilities on the same component (e.g., engine that provides thrust AND consumes fuel)

**Weapon Component Simplicity**:
- `firing_arc: 360` is the simplest - narrower arcs add targeting complexity
- `range` can be generous - one long-range variant is simpler than multiple range-specific variants
- Only create variant components when a property **directly affects** the test outcome

### Step 5: Review Component Necessity

For each component in your test ship, ask:
1. "Do I absolutely need this component for my test?"
2. "Could I create a simpler version of this component that works just as well?"

**Naming Convention for Test Components**: Use `test_` prefix with literal descriptions
- `test_engine_no_fuel` - Engine that provides thrust but consumes no fuel
- `test_engine_with_fuel` - Engine that provides thrust and consumes fuel
- `test_thruster_std` - Standard maneuvering thruster
- `test_armor_basic` - Armor with only damage absorption
- `test_armor_emissive` - Armor with only emissive ability

### Step 6: Document the Test Details

#### 6a: Test Identity
- **Test ID**: Ability name prefix + number (e.g., `BEAMWEAPON-001`, `ENGINE-001`, `THRUSTER-001`)
- **Category**: The ability class name (e.g., `BeamWeaponAbility`, `EngineAbility`)
- **Subcategory**: Specific aspect being tested (e.g., "Accuracy - Low", "Fuel Consumption")
- **Naming**: Test names should use **surface distance** for weapon tests
  - Example: "Low Accuracy Beam - Point Blank (20.5px surface)"

#### 6b: Summary
High-level English description of what behavior is being tested.

#### 6c: Conditions (Test Setup)
Values set by the test itself:
- Starting position(s)
- Starting direction(s)/angle(s)
- Initial velocity
- AI commands (thrust forward, turn left, fire weapon, etc.)
- Tick count and why that count is appropriate

**Tick Count Justification**: Always document why the tick count is sufficient:
```
Formula: time_to_max_speed = max_speed / acceleration_rate
         = 312.5 / 781.25 = 0.4 seconds
         = 40 ticks at 100 TPS
Buffer: 2.5x for safety margin
Selected: 100 ticks
```

**Statistical Test Tick Calculation**:

For binomial tests (hit/miss outcomes), calculate minimum ticks using:
```
n_min = (z² × p × (1-p)) / ε²

where:
  z = confidence level (1.96 for 95%, 2.58 for 99%)
  p = expected probability
  ε = acceptable margin (0.06 for ±6%, 0.01 for ±1%)
```

Example (BEAMWEAPON-001, p=0.5318, ε=0.06, 95% confidence):
```
n_min = (1.96² × 0.5318 × 0.4682) / 0.06²
n_min = (3.84 × 0.249) / 0.0036
n_min ≈ 266 ticks

With 2x safety buffer: 500 ticks
```

For p < 0.05 statistical significance: use High-Tick variant (100k ticks, ε=0.01)

#### 6d: Data File Values (From JSON)
Raw values pulled from data files. For each value, record:
- **Assumed Value**: The value used in calculations when test was designed
- **Source**: File path and field name
- **Live Value**: Current value in data file (validated at load time)

**Validation**: Values are checked at test load time. If any Assumed ≠ Live, show a warning immediately - this means the test data has changed and calculations may be invalid.

```
| Value         | Assumed | Source                                    | Live | Status |
|---------------|---------|-------------------------------------------|------|--------|
| ship.mass     | 40      | ships/Test_Engine_1x_LowMass.json → mass  | 40   | ✓      |
| engine.thrust | 500     | components/test_engine_no_fuel.json → thrust | 500 | ✓      |
| K_SPEED       | 25      | physics_constants.py → K_SPEED            | 25   | ✓      |
```

#### 6e: Calculated Values (With Formulas)
All derived values. ALWAYS show the formula and substitution:

```
max_speed:
  Formula: max_speed = (thrust * K_SPEED) / mass
  Calculation: (500 * 25) / 40 = 312.5 px/s

acceleration_rate:
  Formula: acceleration = (thrust * K_THRUST) / mass²
  Calculation: (500 * 2500) / 40² = 781.25 px/s²

time_to_max_speed:
  Formula: t = max_speed / acceleration
  Calculation: 312.5 / 781.25 = 0.4 seconds = 40 ticks
```

#### 6f: Pass Criteria
List every criterion that must be met. Use formal categories:

| Category | Description | Example |
|----------|-------------|---------|
| `EXACT_MATCH` | Must be identical (integers, strings) | `ship.mass == 40` |
| `DETERMINISTIC` | Float match with 1e-9 tolerance | `max_speed == 312.5` |
| `RANGE` | Value within bounds | `0 < final_velocity < max_speed` |
| `STATISTICAL` | P-value test for RNG outcomes | `hit_rate passes chi-square (p < 0.05)` |

**Statistical Testing Guidelines**:
- Default: Use p < 0.001 if achievable within ~1000 ticks
- Fallback: Use p < 0.05 only when p < 0.001 would require excessive tick counts
- The goal is to use the tightest tolerance that can be reliably achieved in reasonable time

**Two-Layer Validation for Statistical Tests**:

Statistical tests should validate BOTH:
1. **Formula Validation** (DeterministicMatchRule): Verify the expected value is calculated correctly
2. **Outcome Validation** (StatisticalTestRule): Verify actual results match expected statistically

This ensures both the calculation AND the game engine are correct.

Example for BEAMWEAPON-001:
```python
validation_rules=[
    # Layer 1: Verify formula calculation is correct
    DeterministicMatchRule(
        name='Expected Hit Chance',
        path='results.expected_hit_chance',
        expected=0.5318,
        description='P = 1/(1+e^-0.1273) from sigmoid formula'
    ),
    # Layer 2: Verify actual hit rate matches expected
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

### Step 7: Define Test Results Display

#### 7a: Detailed Test Results Panel
Focus ONLY on validation-relevant values. Always include:
- **Seed**: The random seed used for this test run (critical for reproducibility)
- **Ticks**: Number of simulation ticks run
- For each measured value:
  - Expected value (from calculations)
  - Actual value (from test run)
  - Status (PASS/FAIL)

```
Run Info:
  Seed: 12345678
  Ticks: 500

| Metric              | Expected | Actual   | Status      |
|---------------------|----------|----------|-------------|
| final_velocity      | 312.50   | 312.50   | ✓ EXACT     |
| distance_traveled   | 46406.25 | 46406.25 | ✓ EXACT     |
| mass                | 40       | 40       | ✓ EXACT     |
```

**Why show the seed?** The seed enables exact reproduction of any test run. If a test fails, the seed allows debugging with identical RNG sequences.

#### 7b: Test Run History (Summary)
Display the PRIMARY outcome value - the most relevant measurement for the test's purpose:

| Test Type | Primary Outcome |
|-----------|-----------------|
| Acceleration test | final_velocity or distance_traveled |
| Negative movement test | position unchanged (distance = 0) |
| Damage test | damage_dealt or target_hp_remaining |
| Hit rate test | observed_hit_rate vs expected |

---

## Checklists

### Test Design Checklist

- [ ] Identified single ability under test
- [ ] Listed expected and unexpected behaviors
- [ ] Selected ONE behavior for this test
- [ ] Chose simplest vehicle class
- [ ] Used minimum required components
- [ ] Each component has only needed abilities
- [ ] Reviewed: "Do I need each component?"
- [ ] Test uses only `simulation_tests/data/` files

### Test Documentation Checklist

- [ ] Test ID follows naming convention (CATEGORY-NNN)
- [ ] Summary describes the behavior being tested
- [ ] Conditions include all setup values
- [ ] Tick count justified with formula
- [ ] All Data File Values listed with sources
- [ ] All Calculated Values show formulas AND substitutions
- [ ] Pass Criteria use formal categories
- [ ] Primary outcome identified for Test Run History

### Test Validation Checklist

- [ ] Data File Values validated at load time (warning if Assumed ≠ Live)
- [ ] Calculated values match expected (deterministic: 1e-9 tolerance)
- [ ] Statistical tests use p < 0.001 when achievable in ~1000 ticks
- [ ] Negative tests exist for "should NOT happen" behaviors

---

## Part 2: Ability-Specific Guidance

This section grows as we implement tests for each ability.

### Propulsion

#### Things to Test
- Engine provides thrust → ship accelerates
- Thrust/mass ratio determines max_speed
- Thruster provides turn rate
- Turn rate allows rotation over time
- Ship without engine cannot accelerate (negative test)
- Ship without thruster cannot rotate (negative test)
- Fuel consumption during thrust
- No thrust when fuel depleted

#### Things to Avoid
- Don't add thrusters to pure acceleration tests
- Don't add engines to pure rotation tests
- Don't use fuel-consuming engines unless testing fuel consumption

#### Test Ships
- `test_engine_no_fuel` - For acceleration tests without fuel complexity
- `test_engine_with_fuel` - For fuel consumption tests
- `test_thruster_std` - For rotation tests

### Weapons

#### BeamWeaponAbility

See full suite document: `simulation_tests/suites/BeamWeaponAbility.md`

**Core Formula**: `P_hit = 1 / (1 + e^(-x))` (sigmoid)

**Things to Test**:
- Hit rate matches sigmoid formula at various distances
- Range penalty increases with distance
- Defense penalty from target size/maneuverability
- No hits beyond max range (negative test)
- No hits outside firing arc (negative test)

**Things to Avoid**:
- Don't use damage > 1 for hit rate tests (makes counting difficult)
- Don't use firing_arc < 360 unless testing arc limits
- Don't test multiple accuracy levels in same test

**Test Components**:
- `test_beam_low_acc_1dmg` - For low accuracy tests
- `test_beam_med_acc_1dmg` - For medium accuracy tests
- `test_beam_high_acc_1dmg` - For high accuracy tests

### Armor

*(To be added as armor tests are implemented)*

### ECM

*(To be added as ECM tests are implemented)*

---

## Validation Rule Types (Code Reference)

```python
# For exact integer/string matches
ExactMatchRule(name='Ship Mass', path='ship.mass', expected=40)

# For deterministic float values (1e-9 tolerance)
DeterministicMatchRule(
    name='Max Speed',
    path='ship.max_speed',
    expected=312.5,
    description='max_speed = (thrust * K_SPEED) / mass = (500 * 25) / 40'
)

# For range-based validation
RangeRule(name='Final Velocity', path='results.final_velocity', min=0, max=312.5)

# For RNG-based outcomes
StatisticalTestRule(
    name='Hit Rate',
    path='results.hit_rate',
    expected=0.75,
    p_threshold=0.05,  # Standard test
    # p_threshold=0.001  # HT variant
)
```
