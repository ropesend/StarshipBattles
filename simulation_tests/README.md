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
- **Controller**: `test_framework/services/test_lab_controller.py` - UI coordinator
- **Registry**: `test_framework/registry.py` - Auto-discovers test scenarios
- **Runner**: `test_framework/runner.py` - Executes test scenarios
- **Base Classes**: `simulation_tests/scenarios/base.py` - TestScenario, TestMetadata
- **Validation**: `simulation_tests/scenarios/validation.py` - Check, ValidationReport, check functions

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
│          (test_framework/services/test_lab_controller.py)           │
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
│             (simulation_tests/scenarios/base.py)                     │
│  - setup(engine): Initialize ships, positions                        │
│  - update(engine): Per-tick logic (optional)                        │
│  - collect_results(engine): Populate measurement attributes          │
│  - validate(engine): Return list of Check objects                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                       Validation System                              │
│           (simulation_tests/scenarios/validation.py)                 │
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
| **ToHitAttackModifier** | `tohit_attack_scenarios.py` | TOHIT-ATK-001 to 004 | Complete |
| **ToHitDefenseModifier** | `tohit_defense_scenarios.py` | TOHIT-DEF-001 to 004 | Complete |
| **ShieldProjection** | *(pending — migrate from defense_scenarios.py)* | | Planned |
| **ShieldRegeneration** | *(pending)* | | Planned |
| **EmissiveArmor** | *(pending — migrate from defense_scenarios.py)* | | Planned |

### Weapon & System Tests (Original Pattern)

These test files validate weapon systems and mechanics that span multiple abilities.
Over time, ability-specific aspects will be migrated to dedicated ability categories.

#### Beam Weapon Tests (21 tests)

Test IDs: `BEAMWEAPON-XXX` (standard), `BEAMWEAPON-XXX-HT` (high-tick).

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Standard Accuracy** | 8 tests | Low/Med/High accuracy at various ranges (500 ticks, ±10%) |
| **Moving Targets** | 2 tests | Erratic small targets with high defense (500 ticks) |
| **Boundary Tests** | 1 test | Out of range (deterministic) |
| **High-Tick Precision** | 7 tests | Same as standard but 100k ticks, ±1% margin |

#### Projectile Weapon Tests (9 tests)

Test IDs: `PROJECTILE-XXX` and `PROJECTILE-DMG-XXX`.

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Stationary Target** | 1 test | 100% accuracy baseline at 200px |
| **Moving Targets** | 4 tests | Slow/fast linear + small/large erratic targets |
| **Boundary Tests** | 1 test | Out of range (1200px > 1000px max) |
| **Damage Consistency** | 3 tests | No damage falloff at 10%, 50%, 90% of max range |

Projectile tests fire every tick (reload=0) with 1 damage per hit, so
`damage_dealt == hits`. Moving targets start at (100, -1200) out of weapon
range heading upward, ensuring they reach full speed before engagement.
Hit rates are computed from *resolved* shots only — projectiles still in
flight when the test ends are excluded from the hit/miss count.

#### Defense & Modifier Tests (14 tests)

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Shields** | 3 tests | Absorption, overflow to hull, regeneration |
| **Armor** | 2 tests | Emissive armor blocks/reduces damage |
| **ECM/Sensors** | 3 tests | Hit rate modifiers (including A/B comparison) |
| **Stat Modifiers** | 6 tests | Damage/range/reload/thrust/accuracy/arc multipliers |

#### Propulsion Tests (9 tests)

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Engine Physics** | 5 tests | Acceleration, max speed, dual engines, thrust/mass |
| **Thruster Physics** | 4 tests | Turn rate, rotation, dual thrusters, mass effects |

#### Seeker Weapon Tests (11 tests)

| Subcategory | Tests | Description |
|-------------|-------|-------------|
| **Endurance** | 4 tests | Close/mid/beyond/edge range lifetime |
| **Tracking** | 4 tests | Stationary/linear/orbiting/erratic targets |
| **Point Defense** | 3 tests | PDC interaction (placeholders, skipped) |

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
python -m simulation_tests.run_tests                # Run all
python -m simulation_tests.run_tests BEAM           # Filter by ID prefix
python -m simulation_tests.run_tests PROP-001       # Run specific test
python -m simulation_tests.run_tests --list         # List all tests
```

### Headless (Python)

```python
from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario
from test_framework.runner import TestRunner

runner = TestRunner()
scenario = runner.run_scenario(BeamLowAccuracyPointBlankScenario, headless=True)

print(f"Test: {scenario.metadata.test_id}")
print(f"Result: {'PASSED' if scenario.passed else 'FAILED'}")
print(f"Hit Rate: {scenario.results.get('hit_rate', 0):.2%}")
```

---

## File Structure

```
Starship Battles/
├── game/
│   └── ui/screens/
│       └── test_lab/screen.py      # Combat Lab UI
│
├── test_framework/
│   ├── registry.py                 # Test discovery
│   ├── runner.py                   # Test execution
│   └── services/
│       └── test_lab_controller.py  # UI controller
│
└── simulation_tests/
    ├── README.md                   # This file
    ├── COMBAT_LAB_DOCUMENTATION.md # Full documentation
    ├── scenarios/QUICK_START.md     # Tutorial
    ├── run_tests.py                # Headless test runner (python -m simulation_tests.run_tests)
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
        ├── base.py                     # TestScenario, TestMetadata
        ├── validation.py               # Check, ValidationReport, check functions
        ├── templates.py                # Templates: Static, Duel, Propulsion, Resource, Comparison
        │
        │   # Ability-specific categories (one file per ability)
        ├── tohit_attack_scenarios.py   # ToHitAttackModifier tests (TOHIT-ATK-*)
        ├── tohit_defense_scenarios.py  # ToHitDefenseModifier tests (TOHIT-DEF-*)
        │
        │   # Weapon/system-level tests
        ├── beam_scenarios.py           # Beam weapon tests (BEAMWEAPON-*)
        ├── projectile_scenarios.py     # Projectile tests (PROJECTILE-*)
        ├── seeker_scenarios.py         # Seeker/missile tests (SEEKER-*)
        ├── defense_scenarios.py        # Shield/armor/ECM tests (SHIELD-*, ARMOR-*, etc.)
        ├── modifier_scenarios.py       # Stat modifier tests (MOD-*)
        ├── propulsion_scenarios.py     # Movement tests (PROP-*)
        └── resource_scenarios.py       # Resource tests (RESOURCE-*)
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
