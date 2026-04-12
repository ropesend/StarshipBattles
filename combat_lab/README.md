# Combat Lab - Documentation Hub

## Welcome to Combat Lab

Combat Lab is a comprehensive testing system for validating combat mechanics in Starship Battles. This document serves as your entry point to all Combat Lab documentation.

---

## Quick Links

### Getting Started
- **[Quick Start Guide](scenarios/QUICK_START.md)** - Create your first test using templates

### Core Documentation
- **[Main Documentation](COMBAT_LAB_DOCUMENTATION.md)** - Complete system overview
- **[Test Constants](test_constants.py)** - Centralized constants for tests

### Key Files
- **UI**: `game/ui/screens/test_lab/screen.py` - Combat Lab pygame interface
- **Controller**: `combat_lab/services/test_lab_controller.py` - UI coordinator
- **Registry**: `combat_lab/registry.py` - Auto-discovers test scenarios
- **Runner**: `combat_lab/runner.py` - Executes test scenarios
- **Base Classes**: `combat_lab/scenarios/base.py` - TestScenario, TestMetadata
- **Validation**: `combat_lab/scenarios/validation.py` - Check, ValidationReport, check functions

---

## What is Combat Lab?

Combat Lab provides:

- **Visual Test Runner** - In-game UI for browsing and running tests
- **Statistical Validation** - TOST (Two One-Sided Tests) equivalence testing
- **Data Verification** - Exact-match checks for component data validation
- **Headless Execution** - Run tests without UI for CI/CD integration
- **High-Precision Tests** - 100k tick tests with ±1% margins
- **Self-Documenting** - Each test includes rich metadata explaining what it validates

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Combat Lab UI                               │
│                (game/ui/screens/test_lab/screen.py)                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                     TestLabUIController                              │
│          (combat_lab/services/test_lab_controller.py)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐  ┌─────────────────────┐  ┌────────────────┐
│  TestRunner   │  │    TestRegistry     │  │   Services     │
│  (runner.py)  │  │   (registry.py)     │  │ (services/)    │
└───────┬───────┘  └──────────┬──────────┘  └────────────────┘
        │                     │
        └─────────┬───────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TestScenario                                 │
│             (combat_lab/scenarios/base.py)                     │
│  - setup(engine): Initialize ships, positions                        │
│  - update(engine): Per-tick logic (optional)                        │
│  - collect_results(engine): Populate measurement attributes          │
│  - validate(engine): Return list of Check objects                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                       Validation System                              │
│           (combat_lab/scenarios/validation.py)                 │
│  - Check: Single validation check with phase and outcome             │
│  - ValidationReport: Aggregates checks, determines pass/fail         │
│  - check_exact, check_approx, check_tost, check_true                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Test Organization: One Category Per Ability

The test suite is organized so that **each combat-relevant ability gets its own
test category**. Each category is a dedicated scenario file containing tests that
validate all expected behaviors and rule out unexpected behaviors for that one
ability. Other components are only included when necessary (e.g., a beam weapon
to measure the effect of a sensor).

Every ability category should include:

1. **Basic effect** — the ability does what it claims (positive value)
2. **Same-group stacking** — redundant components don't stack (intra-group MAX)
3. **Different-group stacking** — diverse components DO stack (inter-group SUM)
4. **Negative value** — the ability works bidirectionally (penalty/bonus)

Ability categories use the `ComparisonScenario` template to run A/B battles and
compare measured outcomes.

### Ability-Specific Categories (New Pattern)

| Category | File | Tests | Status |
|----------|------|-------|--------|
| **ToHitAttackModifier** | `tohit_attack_scenarios.py` | TOHIT-ATK-001 to 005 | Complete (5 tests) |
| **ToHitDefenseModifier** | `tohit_defense_scenarios.py` | TOHIT-DEF-001 to 004 | Complete (4 tests) |
| **ShieldProjection** | `shield_projection_scenarios.py` | SHIELD-PROJ-001 to 007, 005B, METALS-001/002 | Complete (10 tests) |
| **ShieldRegeneration** | `shield_regen_scenarios.py` | SHIELD-REGEN-001 to 007 | Complete (7 tests) |
| **ArmorLayer** | `armor_layer_scenarios.py` | ARMOR-LAYER-001 to 003 | Complete (3 tests) |
| **EmissiveArmor** | `emissive_armor_scenarios.py` | EMISSIVE-001 to 007 | Complete (7 tests) |
| **CommandAndControl** | `cnc_scenarios.py` | CNC-001 to 006 | Complete (6 tests) |
| **ShieldRegeneratingArmor** | `sra_scenarios.py` | SRA-001 to 005 | Complete (5 tests) |
| **DamagePipeline** | `damage_pipeline_scenarios.py` | PIPELINE-001 to 005, 007 | Complete (6 tests) |

#### Damage Pipeline Integration Tests (6 tests)

Test IDs: `PIPELINE-XXX`.

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Shield + Emissive** | 1 test | Emissive reduces overflow after shields deplete |
| **Shield + SRA** | 1 test | SRA absorbs overflow and recharges shields in a cycle |
| **Emissive + SRA** | 1 test | Sequential reduction: emissive first, then SRA |
| **Full Pipeline** | 1 test | Shield + Emissive + SRA vs no defenses |
| **Full + Regen** | 1 test | Regen extends full pipeline protection |
| **SRA Cap Overflow** | 1 test | SRA recharge capped at max_shields; excess wasted |

Pipeline tests validate that the damage stages (Shields → Emissive Armor →
Shield Regenerating Armor → Hull Layers) work correctly when multiple defenses
are active simultaneously. Each test uses ComparisonScenario to compare a
defended target against a baseline.

### Weapon & System Tests (Original Pattern)

These test files validate weapon systems and mechanics that span multiple abilities.
Over time, ability-specific aspects will be migrated to dedicated ability categories.

#### Beam Weapon Tests (23 tests)

Test IDs: `BEAMWEAPON-XXX` (standard), `BEAMWEAPON-XXX-HT` (high-tick), `BEAMWEAPON-RES-XXX` (resource).

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Standard Accuracy** | 8 tests | Low/Med/High accuracy at various ranges (500 ticks, ±10%) |
| **Moving Targets** | 2 tests | Erratic small targets with high defense (500 ticks) |
| **Boundary Tests** | 1 test | Out of range (deterministic) |
| **High-Tick Precision** | 7 tests | Same as standard but 100k ticks, ±1% margin |
| **Resource Dependency** | 3 tests | Energy depletion: no energy, 50% energy, control |
| **Generic Resource (Metals)** | 2 tests | Beam consuming planetary resource "metals" fires/stops correctly |

#### Projectile Weapon Tests (14 tests)

Test IDs: `PROJECTILE-XXX`, `PROJECTILE-DMG-XXX`, `PROJECTILE-RES-XXX`.

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Stationary Target** | 1 test | 100% accuracy baseline at 200px |
| **Moving Targets** | 4 tests | Slow/fast linear + small/large erratic targets |
| **Boundary Tests** | 1 test | Out of range (1200px > 1000px max) |
| **Damage Consistency** | 3 tests | No damage falloff at 10%, 50%, 90% of max range |
| **Resource Dependency** | 3 tests | Ammo depletion: no ammo, 50% ammo, control (ComparisonScenario) |
| **Generic Resource (Metals)** | 2 tests | Projectile consuming planetary resource "metals" fires/stops correctly |

Projectile tests fire every tick (reload=0) with 1 damage per hit, so
`damage_dealt == hits`. Moving targets start at (100, -1200) out of weapon
range heading upward, ensuring they reach full speed before engagement.
Hit rates are computed from *resolved* shots only — projectiles still in
flight when the test ends are excluded from the hit/miss count.

#### Stat Modifier Tests

Each modifier has its own category under the "Modifiers" group. See the File Structure
section for the full list of `mod_*_scenarios.py` files (DamageMultiplier, RangeMultiplier,
ReloadMultiplier, ThrustMultiplier, AccuracyAdditive, ArcSet, EnduranceMultiplier,
ConsumptionMultiplier, ModifierStacking).

#### Propulsion Tests (9 tests)

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Engine Physics** | 5 tests | Acceleration, max speed, dual engines, thrust/mass |
| **Thruster Physics** | 4 tests | Turn rate, rotation, dual thrusters, mass effects |

#### Seeker Weapon Tests (11 tests)

Test IDs: `SEEKER-SPEED-XXX`, `SEEKER-ENDUR-XXX`, `SEEKER-TURN-XXX`, `SEEKER-DMG-XXX`, `SEEKER-HP-XXX`, `SEEKER-RES-XXX`, `SEEKER-PD-XXX`.

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Speed** | 1 test | Fast vs slow projectile speed — travel time comparison |
| **Endurance** | 1 test | Long vs short endurance — range reach comparison |
| **Turn Rate** | 1 test | Fast vs slow turn — off-axis launch, redirect to target |
| **Damage** | 1 test | 4x warhead damage produces 4x hull damage |
| **HP** | 1 test | Higher missile HP survives PDC better |
| **Resource** | 3 tests | Ammo dependency: no ammo, limited ammo, control |
| **Point Defense** | 2 tests | PDC intercepts seekers; to_hit_defense reduces PDC accuracy |

#### Resource System Tests (9 tests)

Test IDs: `RESOURCE-XXX`.

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Fuel** | 3 tests | Engine fuel consumption, depletion/starvation, regeneration (500 ticks) |
| **Energy** | 3 tests | Beam energy consumption, depletion, regeneration (100 ticks) |
| **Ammo** | 3 tests | Projectile/seeker ammo consumption, depletion (100 ticks) |

Resource tests validate:
- Predictable consumption rates (fuel/sec, energy/shot, ammo/shot)
- Depletion behavior (engine stops, weapon stops firing)
- Generator regeneration balances consumption

---

## Key Concepts

### Verify Every Assumption (CRITICAL)

A test that checks only the outcome can pass for the wrong reason. Each
phase must verify the assumptions that subsequent phases depend on:

- **Data phase**: every loaded weapon/ship stat (damage, range, speed, reload)
- **Precondition phase**: geometry (distances), movement (target speed,
  displacement, ticks in range), and weapon activity (shots fired)
- **Outcome phase**: hard-to-game bounds (100% for stationary, both upper
  AND lower bounds for erratic targets, minimum shot counts)

If a test depends on a moving target, the precondition phase MUST verify
the target actually moved at the expected speed and covered the expected
distance. A "pass" on a broken test is worse than a failure.

### TOST (Two One-Sided Tests)

Traditional hypothesis testing proves things are **different**.
TOST proves things are **equivalent** within a margin.

- **p < 0.05** = PASS (proven equivalent)
- **p >= 0.05** = FAIL (not proven equivalent)

### Surface Distance (CRITICAL)

Beam weapons measure distance to target **surface**, not center:

```python
# Target radius from mass
target_radius = 40 * (mass / 1000) ** (1/3)

# Surface distance (what weapons use)
surface_distance = center_distance - target_radius

# Example: mass=400, center_distance=100
# radius = 29.47px, surface_distance = 70.53px
```

### Speed Units (CRITICAL)

Ship speed and projectile speed use **different scales**:

```python
# Ship speed: directly in px/tick
max_speed = (total_thrust * K_SPEED) / mass  # K_SPEED=25
# Example: thrust=600, mass=932 → 16.1 px/tick

# Projectile speed: divided by PROJECTILE_SPEED_SCALE (100)
effective_speed = projectile_speed / 100
# Example: projectile_speed=20000 → 200 px/tick
```

A projectile with speed 20000 moves at 200 px/tick.
A ship with Top Spd 37.5 moves at 37.5 px/tick.
The projectile is 5.3x faster than the ship.

### Turn Speed Units

`turn_speed` in ship stats is in **degrees per 100 ticks**, not per tick.
`rotate()` divides by 100, so effective rotation = `turn_speed / 100` deg/tick.

```python
# Example: turn_speed=1562.5
# Actual: 1562.5 / 100 = 15.625 deg/tick
# 180-degree turn: 180 / 15.625 = 11.5 ticks
```

This matters for erratic target leash calculations — overshoot = max_speed * (180 / effective_turn_rate).

### In-Flight Projectile Tracking

Projectile hit rates are computed from **resolved shots only**. Projectiles
still in flight when the test ends are excluded from the hit/miss count:

```python
resolved_shots = total_shots_fired - in_flight
resolved_hit_rate = hits / resolved_shots
```

This prevents travel-time artifacts: without this correction, long-range
tests appear to have lower accuracy simply because more projectiles are
mid-flight at test end. The DMG consistency tests (010/050/090) all show
100% resolved hit rate at every range.

### Position Tracking

Scenarios can enable per-tick position recording for path analysis:

```python
class MyScenario(StaticTargetScenario):
    track_positions = True

    def custom_setup(self, engine):
        self._tracking_weapon_range = 1000  # for in_range flags
```

This records tick, x, y, speed, heading, distance, and in_range for every
ship every tick. Results include `tracking_summary` with ticks_in_range,
min/max distance. Zero overhead when disabled (single bool check).

### Defense Score (Logarithmic Formula)

```python
def calculate_defense_score(mass, acceleration=0.0, turn_speed=0.0, ecm_score=0.0):
    # Radius calculation
    radius = 40 * ((max(mass, 100) / 1000) ** (1/3))

    # Size score (logarithmic)
    diameter = radius * 2
    d_ratio = max(0.1, diameter / 80.0)
    size_score = -2.5 * math.log10(d_ratio)

    # Maneuver score
    maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))

    return size_score + maneuver_score + ecm_score
```

### Standard vs High-Tick Tests

| Type | Ticks | Margin | Standard Error | Use Case |
|------|-------|--------|----------------|----------|
| **Standard** | 500 | ±10% | ~2.2–4.4% | Quick validation, development |
| **High-Tick** | 100,000 | ±1% | ~0.16% | Precise validation, releases |

---

## Running Tests

### In Combat Lab UI

```bash
python main.py
# Navigate to "Combat Lab"
# Browse tests by category
# Select test and click "Run Visual" or "Run Headless"
```

### Headless (Command Line)

```bash
python -m combat_lab.run_tests                # Run all
python -m combat_lab.run_tests BEAM           # Filter by ID prefix
python -m combat_lab.run_tests PROP-001       # Run specific test
python -m combat_lab.run_tests --list         # List all tests
python -m combat_lab.run_tests --fast         # Skip high-tick (-HT) tests (~2min → ~30s)
python -m combat_lab.run_tests --no-history   # Don't record results to test_history.json
```

By default, CLI runs record results to `combat_lab/test_history.json`
(same file the Combat Lab UI uses). Use `--no-history` to skip recording.

### Headless (Python)

```python
from combat_lab.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from combat_lab.runner import TestRunner

runner = TestRunner()
scenario = runner.run_scenario(BeamLowAccuracyPointBlankScenario, headless=True)

print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if scenario.passed else 'FAILED'}")
print(f"Hit Rate: {scenario.results.get('hit_rate', 0):.2%}")
```

---

## Creating New Ability Tests

### Step-by-Step: Add a New Ability Category

Each combat ability should have a dedicated test category. Follow this process:

**1. Identify the standard test set.** Every ability needs at minimum:

| Test | Purpose | Template |
|------|---------|----------|
| Basic positive effect | Ability does what it claims | ComparisonScenario |
| Same-group stacking | Intra-group MAX (redundancy) | ComparisonScenario |
| Different-group stacking | Inter-group SUM (diversity) | ComparisonScenario |
| Negative value | Bidirectional behavior | ComparisonScenario |
| Resource dependency (if applicable) | Stops working without power/ammo | ComparisonScenario |

**2. Create test components** in `combat_lab/data/components.json`:
- Zero mass (isolate the ability from physics side effects)
- Minimal abilities (only what's needed for the test)
- Explicit `stack_group` for stacking tests
- Grouped variants: `test_sensor_1_group_a`, `test_sensor_1_group_b`

**3. Create test ships** in `combat_lab/data/ships/`:
- One ship per configuration (no runtime ship building)
- Ship names describe their config, not their role in a comparison
- Use existing hulls (`TestS_2L`) and armor (`test_armor_extreme_hp`)

**4. Create the scenario file** `combat_lab/scenarios/<ability>_scenarios.py`:

```python
from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_true

class MyAbilityBasicEffectScenario(ComparisonScenario):
    metadata = TestMetadata(
        test_id="MYABILITY-001",
        category="MyAbility",        # Named after the ability class
        subcategory="Basic Effect",
        name="My Ability Increases X",
        summary="Compares X: without ability vs with ability",
        conditions=[...],
        edge_cases=[...],
        expected_outcome="Variant has higher X than baseline",
        pass_criteria="variant_X > baseline_X",
        max_ticks=1000,
        seed=42,
        tags=["myability", "comparison"],
    )

    baseline_attacker_ship = "Test_Ship_NoAbility.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Ship_WithAbility.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = 100

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data: verify the ability is present and has expected value
        # Precondition: both battles ran and produced results
        # Outcome: the ability caused the expected difference
        return checks
```

**5. Export the scenarios** in `combat_lab/scenarios/__init__.py`:
```python
from combat_lab.scenarios.myability_scenarios import (
    MyAbilityBasicEffectScenario,
    ...
)
```

**6. Run and verify:**
```bash
python -m combat_lab.run_tests MYABILITY    # New tests only
python -m combat_lab.run_tests              # Full suite
```

### ComparisonScenario: Which Ship Varies?

The key design decision for each test: **which ship carries the ability under test?**

| Ability type | What varies | Example |
|-------------|-------------|---------|
| Attack modifier (sensor) | **Attacker** — different attackers, same target | TOHIT-ATK-001 |
| Defense modifier (ECM) | **Target** — same attacker, different targets | TOHIT-DEF-001 |
| Shield | **Target** — shielded vs unshielded target | SHIELD-PROJ-001 |
| Weapon resource | **Attacker** — different resource levels | BEAMWEAPON-RES-001 |

### Stacking Test Design

For abilities with `stack_group` support:

```json
// Component A: explicit group
"ToHitAttackModifier": {"value": 1.0, "stack_group": "sensors_a"}

// Component B: different group (stacks with A)
"ToHitAttackModifier": {"value": 1.0, "stack_group": "sensors_b"}
```

**Same-group test:** Two components with identical `stack_group`. Intra-group MAX
means the second adds no benefit. Both battles should produce identical results.

**Different-group test:** Components from `group_a` + `group_b`. Inter-group SUM
means values combine additively (1.0 + 1.0 = 2.0). The variant should show
a measurably stronger effect than the single-group baseline.

For abilities WITHOUT stack_group (like ShieldProjection): all components always
SUM. The stacking test uses 1 component vs 2 components — no groups needed.

### Resource Dependency Test Design

If a component has `ResourceConsumption`, test three resource levels:

| Test | Storage | Expected behavior |
|------|---------|-------------------|
| No resource | None | Component never functions (0 shots / 0 protection) |
| 50% resource | Enough for ~500 ticks | Functions for half the test, then stops |
| Full resource (control) | Abundant | Functions identically to baseline |

Two resource trigger types behave differently:

| Trigger | Example | Deactivation mechanism |
|---------|---------|----------------------|
| `"constant"` (per-tick) | Shield energy, engine fuel | `is_operational = False` → component loses stat contributions |
| `"activation"` (per-shot) | Weapon energy/ammo | `can_afford_activation() = False` → weapon refuses to fire |

### Validation Best Practices for Comparison Tests

- Use `check_exact` for deterministic outcomes (same seed, guaranteed-hit weapons)
- Use `check_true` with `detail=` (not `actual=`) for boolean assertions
- Use `check_tost` for stochastic outcomes (hit rates with non-guaranteed beams)
- Always verify preconditions: weapon fired, target took damage, ticks ran
- For resource tests: verify exact shot count matches expected resource capacity
- For stacking tests: verify the aggregated stat value in the data phase

---

## File Structure

```
Starship Battles/
├── game/
│   └── ui/screens/
│       └── test_lab/screen.py      # Combat Lab UI
│
├── combat_lab/
│   ├── registry.py                 # Test discovery
│   ├── runner.py                   # Test execution
│   └── services/
│       └── test_lab_controller.py  # UI controller
│
└── combat_lab/
    ├── README.md                   # This file
    ├── COMBAT_LAB_DOCUMENTATION.md # Full documentation
    ├── scenarios/QUICK_START.md     # Tutorial
    ├── run_tests.py                # Headless test runner (python -m combat_lab.run_tests)
    ├── test_constants.py           # Centralized constants
    ├── logging_config.py           # Combat Lab logging
    │
    ├── data/
    │   ├── components.json         # Test components
    │   ├── modifiers.json          # Stat modifiers
    │   ├── vehicleclasses.json     # Ship hulls
    │   └── ships/                  # Ship configurations
    │
    ├── validation/                 # Validation system docs
    │
    └── scenarios/
        ├── base.py                          # TestScenario, TestMetadata
        ├── validation.py                    # Check, ValidationReport, check functions
        ├── templates.py                     # Templates: Static, Duel, Propulsion, Resource, Comparison
        ├── movement.py                      # StraightLine, CircularOrbit, Erratic controllers
        │
        │   # Ability-specific categories (one file per ability)
        ├── tohit_attack_scenarios.py        # ToHitAttackModifier (TOHIT-ATK-001 to 005)
        ├── tohit_attack_fleet_scenarios.py  # ToHitAttackModifier fleet-level (TOHIT-ATK-FLEET-*)
        ├── tohit_defense_scenarios.py       # ToHitDefenseModifier (TOHIT-DEF-001 to 004)
        ├── shield_projection_scenarios.py   # ShieldProjection (SHIELD-PROJ-001 to 007, 005B, METALS)
        ├── shield_regen_scenarios.py        # ShieldRegeneration (SHIELD-REGEN-001 to 007)
        ├── armor_layer_scenarios.py         # ArmorLayer (ARMOR-LAYER-001 to 003)
        ├── emissive_armor_scenarios.py     # EmissiveArmor (EMISSIVE-001 to 007)
        ├── cnc_scenarios.py                # CommandAndControl (CNC-001 to 006)
        ├── sra_scenarios.py                # ShieldRegeneratingArmor (SRA-001 to 005)
        ├── damage_pipeline_scenarios.py    # DamagePipeline Integration (PIPELINE-001 to 005, 007)
        │
        │   # Weapon/system-level tests (include resource dependency tests)
        ├── beam_scenarios.py                # BeamWeapon (BEAMWEAPON-*, BEAMWEAPON-RES-*)
        ├── projectile_scenarios.py          # Projectile (PROJECTILE-*, PROJECTILE-RES-*)
        ├── seeker_scenarios.py              # Seeker (SEEKER-*)
        │
        │   # Stat Modifier Categories (one file per modifier type)
        ├── mod_damage_scenarios.py          # DamageMultiplier (MOD-DMG-*)
        ├── mod_range_scenarios.py           # RangeMultiplier (MOD-RANGE-*)
        ├── mod_reload_scenarios.py          # ReloadMultiplier (MOD-RELOAD-*)
        ├── mod_thrust_scenarios.py          # ThrustMultiplier (MOD-THRUST-*)
        ├── mod_accuracy_scenarios.py        # AccuracyAdditive (MOD-ACC-*)
        ├── mod_arc_scenarios.py             # ArcSet (MOD-ARC-*)
        ├── mod_endurance_scenarios.py       # EnduranceMultiplier (MOD-ENDUR-*)
        ├── mod_consumption_scenarios.py     # ConsumptionMultiplier (MOD-CONSUME-*)
        ├── mod_stacking_scenarios.py        # ModifierStacking (MOD-STACK-*)
        ├── propulsion_scenarios.py          # Movement (PROP-*)
        └── resource_scenarios.py            # Resources (RESOURCE-*)
```

---

## Common Tasks

| I want to... | See... |
|--------------|--------|
| Create a new test | [Quick Start Guide](scenarios/QUICK_START.md) |
| Understand TOST | [Main Docs - Validation System](COMBAT_LAB_DOCUMENTATION.md#validation-system) |
| Calculate hit rates | [Main Docs - Beam Weapon Mechanics](COMBAT_LAB_DOCUMENTATION.md#beam-weapon-mechanics) |
| Debug failing tests | [Main Docs - Troubleshooting](COMBAT_LAB_DOCUMENTATION.md#troubleshooting) |
| Run tests headlessly | [Main Docs - Running Tests](COMBAT_LAB_DOCUMENTATION.md#running-tests) |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **TOST validation** | Proves equivalence, not just "no difference detected" |
| **Surface distance** | Beam raycasting hits target surface, not center |
| **Logarithmic defense** | Better scaling across ship size range |
| **Zero-mass components** | Isolates hull mass for predictable defense scores |
| **1 billion HP targets** | Survives 100k ticks at 99% hit rate |
| **Two test tiers** | Fast feedback (500) + precise validation (100k) |
| **Damage=1, reload=0** | Projectile: damage_dealt == hits; fires every tick for high sample counts |
| **Resolved hit rate** | Excludes in-flight projectiles from denominator — eliminates travel-time artifacts |
| **Position tracking** | Optional per-tick recording for path analysis — zero overhead when off |
| **Point-blank ≥ 100px** | Ships with mass=400 have ~29.5px radius; avoids visual overlap |
| **Game-realistic speeds** | Projectile speed=20000 matches actual railgun; 5.3x faster than fastest ship |
| **Same start position** | PROJ-002/003 both start (100,-1200) — only speed differs for clean comparison |
| **High agility thruster** | test_thruster_high (raw=500) for erratic targets to stay within leash |
| **Generic arc_set detection** | Modifier arc defaults based on effect type, not hardcoded modifier IDs |
| **History on startup** | Combat Lab loads test_history.json into registry so status dots show immediately |
| **Atomic JSON writes** | `save_json()` writes to .tmp then renames — original file survives interrupted writes |
| **Corrupt file recovery** | Corrupt test_history.json is backed up to .corrupt and system starts fresh |
| **Always-visible ships** | Colored dot always drawn in battle view — prevents transparent-image invisibility |
| **Verify assumptions** | Preconditions check movement, speed, distance — not just outcomes |
| **ComparisonScenario** | A/B template runs baseline + variant battles, compares measured outcomes |
| **Visual Baseline button** | Amber button renders the baseline battle for debugging (ComparisonScenario only) |
| **Additive ability stacking** | All numeric abilities use intra-group MAX, inter-group SUM — no multiplicative exceptions |
| **One category per ability** | Each combat ability gets a dedicated scenario file with basic effect + stacking + negative tests |
| **Auto-discovery** | `run_tests.py` globs `*_scenarios.py` — new scenario files are found automatically |
| **CLI records history** | `run_tests.py` writes results to `test_history.json` by default — Combat Lab UI sees CLI results |
| **`--fast` flag** | Skips `-HT` (high-tick) tests for quick validation during development |
| **`_`-prefixed JSON keys skipped** | Component loader skips keys like `_comment` during formula parsing to avoid spam |

---

## System Requirements

- Python 3.10+
- pygame-ce 2.5+
- scipy (for TOST calculations)

---

## Credits

**Created**: January 2026
**Last Updated**: March 2026
**Combat Lab System**: Claude + User collaboration

---

## Next Steps

1. **Read**: [Quick Start Guide](scenarios/QUICK_START.md)
2. **Try**: Run a test in Combat Lab UI (`python main.py`)
3. **Create**: Follow Quick Start to create your first test
4. **Explore**: Read [Main Documentation](COMBAT_LAB_DOCUMENTATION.md) for deep dive
