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

## Current Test Suite

### Beam Weapon Tests (21 tests)

Test IDs follow the pattern: `BEAMWEAPON-XXX` for standard, `BEAMWEAPON-XXX-HT` for high-tick.

| Category | Tests | Description |
|----------|-------|-------------|
| **Standard Accuracy** | 8 tests | Low/Med/High accuracy at various ranges (500 ticks, ±6%) |
| **Moving Targets** | 2 tests | Erratic small targets with high defense (500 ticks) |
| **Boundary Tests** | 1 test | Out of range (deterministic) |
| **High-Tick Precision** | 7 tests | Same as standard but 100k ticks, ±1% margin |

### Projectile Weapon Tests (9 tests)

Test IDs follow the pattern: `PROJECTILE-XXX` and `PROJECTILE-DMG-XXX`.

| Category | Tests | Description |
|----------|-------|-------------|
| **Stationary Target** | 1 test | 100% accuracy baseline at 200px |
| **Moving Targets** | 4 tests | Slow/fast linear + small/large erratic targets |
| **Boundary Tests** | 1 test | Out of range (1200px > 1000px max) |
| **Damage Consistency** | 3 tests | No damage falloff at 10%, 50%, 90% of max range |

Projectile tests fire every tick (reload=0) with 1 damage per hit, so
`damage_dealt == hits`. Moving targets start at (100, -1200) out of weapon
range heading upward, ensuring they reach full speed before engagement.

### Defense & Modifier Tests (13 tests)

| Category | Tests | Description |
|----------|-------|-------------|
| **Shields** | 3 tests | Absorption, overflow to hull, regeneration |
| **Armor** | 2 tests | Emissive armor blocks/reduces damage |
| **ECM/Sensors** | 2 tests | Hit rate modifiers |
| **Stat Modifiers** | 6 tests | Damage/range/reload/thrust/accuracy/arc multipliers |

### Propulsion Tests (9 tests)

| Category | Tests | Description |
|----------|-------|-------------|
| **Engine Physics** | 5 tests | Acceleration, max speed, dual engines, thrust/mass |
| **Thruster Physics** | 4 tests | Turn rate, rotation, dual thrusters, mass effects |

### Seeker Weapon Tests (11 tests)

| Category | Tests | Description |
|----------|-------|-------------|
| **Endurance** | 4 tests | Close/mid/beyond/edge range lifetime |
| **Tracking** | 4 tests | Stationary/linear/orbiting/erratic targets |
| **Point Defense** | 3 tests | PDC interaction (placeholders, skipped) |

### Resource System Tests (9 tests)

Test IDs follow the pattern: `RESOURCE-XXX`.

| Category | Tests | Description |
|----------|-------|-------------|
| **Fuel** | 3 tests | Engine fuel consumption, depletion/starvation, regeneration (500 ticks) |
| **Energy** | 3 tests | Beam energy consumption, depletion, regeneration (100 ticks) |
| **Ammo** | 3 tests | Projectile/seeker ammo consumption, depletion (100 ticks) |

Resource tests validate:
- Predictable consumption rates (fuel/sec, energy/shot, ammo/shot)
- Depletion behavior (engine stops, weapon stops firing)
- Generator regeneration balances consumption

---

## Key Concepts

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
| **Standard** | 500 | ±6% | ~2.2% | Quick validation, development |
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
        ├── base.py                 # TestScenario, TestMetadata
        ├── validation.py           # Check, ValidationReport, check functions
        ├── templates.py            # Reusable scenario templates
        ├── beam_scenarios.py       # Beam weapon tests
        ├── defense_scenarios.py    # Defense/armor/shield tests
        ├── modifier_scenarios.py   # Stat modifier tests
        ├── projectile_scenarios.py # Projectile tests
        ├── seeker_scenarios.py     # Seeker/missile tests
        ├── propulsion_scenarios.py # Movement tests
        └── resource_scenarios.py   # Energy/ammo tests
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

---

## System Requirements

- Python 3.10+
- pygame-ce 2.5+
- scipy (for TOST calculations)

---

## Credits

**Created**: January 2026
**Combat Lab System**: Claude + User collaboration

---

## Next Steps

1. **Read**: [Quick Start Guide](scenarios/QUICK_START.md)
2. **Try**: Run a test in Combat Lab UI (`python main.py`)
3. **Create**: Follow Quick Start to create your first test
4. **Explore**: Read [Main Documentation](COMBAT_LAB_DOCUMENTATION.md) for deep dive
