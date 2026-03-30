# Simulation Testing Guide

Consolidated guide for the Starship Battles simulation test system. Covers test architecture, the TestScenario pattern, validation, troubleshooting, and migration.

---

## 1. Overview & Test Architecture

### Purpose

Simulation tests validate game mechanics (weapons, propulsion, shields, etc.) by running the BattleEngine in headless mode and checking outcomes against expected values. The same tests can run in both **pytest** (automated, headless) and **Combat Lab** (visual, interactive).

### Directory Structure (Verified)

```
simulation_tests/                    # Simulation-specific test ecosystem
├── conftest.py                      # Simulation test pytest config
├── pytest.ini                       # Simulation test settings
├── test_constants.py                # Shared constants
├── test_history.json                # Historical test run data
├── coverage_index.py                # Coverage tracking
├── logging_config.py                # Logging setup
├── data/                            # Test-only data (isolated from production)
│   ├── components.json              # Test-only components
│   ├── vehicleclasses.json          # Test hull classes
│   ├── modifiers.json               # Test modifiers
│   ├── combat_strategies.json       # Test AI strategies
│   ├── movement_policies.json       # Test movement policies
│   ├── targeting_policies.json      # Test targeting policies
│   ├── ships/                       # ~45 test ship JSON files
│   ├── ship_templates/              # Base templates for ship generation
│   ├── schemas/                     # JSON schema validation files
│   └── schema_validator.py          # Runtime schema validation
├── scenarios/                       # TestScenario implementations
│   ├── base.py                      # Base scenario class
│   ├── templates.py                 # Reusable scenario templates
│   ├── validation.py                # Validation helpers
│   ├── prerun_validation.py         # Pre-run data checks
│   ├── beam_scenarios.py            # Beam weapon scenarios
│   ├── projectile_scenarios.py      # Projectile weapon scenarios
│   ├── seeker_scenarios.py          # Seeker weapon scenarios
│   ├── propulsion_scenarios.py      # Engine/thruster scenarios
│   ├── defense_scenarios.py         # Shield/armor scenarios
│   ├── modifier_scenarios.py        # Modifier scenarios
│   ├── resource_scenarios.py        # Fuel/energy/ammo scenarios
│   └── example_beam_test.py         # Example scenario for reference
├── tests/                           # Pytest wrappers for scenarios
│   ├── test_beam_weapons.py
│   ├── test_projectile_weapons.py
│   ├── test_seeker_weapons.py
│   ├── test_propulsion.py
│   ├── test_engine_physics.py
│   ├── test_defense.py
│   ├── test_modifiers.py
│   ├── test_resource_consumption.py
│   ├── test_smoke.py
│   ├── test_coverage_index.py
│   └── test_example_scenarios.py
├── suites/                          # Suite documentation (per ability)
│   └── BeamWeaponAbility.md
├── specs/                           # Test specifications
│   └── component_test_specifications.md
├── utils/                           # Utility helpers
│   ├── README.md
│   └── test_log_analyzer.py
├── validation/                      # Validation system docs
│   └── README.md
└── output/                          # Test output artifacts

test_framework/                      # Shared test framework (used by both pytest and Combat Lab)
├── runner.py                        # TestRunner - executes scenarios
├── registry.py                      # TestRegistry - discovers and indexes scenarios
├── scenario.py                      # CombatScenario base class definition
├── test_history.py                  # Test history persistence
├── battle_state_capture.py          # State snapshot utilities
├── scenarios/                       # Combat Lab visual scenarios
│   ├── engine_performance.py
│   ├── gun_accuracy_test.py
│   ├── range_test.py
│   └── simple_duel.py
Note: TestScenario (which extends CombatScenario) lives in `simulation_tests/scenarios/base.py`.

└── services/                        # Service layer for Combat Lab
    ├── test_execution_service.py
    ├── test_results_service.py
    ├── scenario_data_service.py
    ├── metadata_management_service.py
    ├── ui_state_service.py
    └── test_lab_controller.py

tests/                               # General test suite (~7353 tests)
├── conftest.py                      # Root pytest config
├── fixtures/                        # Shared fixtures
│   ├── paths.py                     # Path utilities
│   ├── ships.py                     # Ship fixtures
│   ├── components.py                # Component fixtures
│   ├── battle.py                    # Battle engine fixtures
│   ├── ai.py                        # AI test fixtures
│   ├── common.py                    # Common utilities
│   └── test_scenarios.py            # TestScenario helpers
├── infrastructure/                  # Test infrastructure
│   └── session_cache.py             # SessionRegistryCache
├── unit/                            # Unit tests by module
│   ├── ai/                          # AI controller tests
│   ├── builder/                     # Ship builder tests
│   ├── combat/                      # Combat/weapon tests
│   ├── entities/                    # Ship/component tests
│   ├── systems/                     # Physics/system tests
│   └── ui/                          # UI component tests
├── simulation/                      # Additional simulation test output
└── ...                              # integration, regression, strategy, etc.
```

**Key isolation rule:** Tests in `simulation_tests/` use ONLY data from `simulation_tests/data/`. Production data in `data/` is never modified by tests.

---

## 2. Test Infrastructure

### Registry Hydration & SessionRegistryCache

Tests use **Fast Hydration** to avoid repeated disk I/O:

1. `SessionRegistryCache` (in `tests/infrastructure/session_cache.py`) loads all production data once per pytest session.
2. Each test gets a fresh registry populated from cache (no disk reads).
3. Registry is cleared after each test for isolation.

This is wired through `conftest.py` and the `isolated_registry` fixture.

### Core Fixtures (tests/fixtures/)

| Fixture | Source | Description |
|---------|--------|-------------|
| `project_root` | `paths.py` | Project root directory |
| `data_dir` | `paths.py` | Production data directory |
| `test_data_dir` | `paths.py` | Test-specific data directory |
| `empty_ship` | `ships.py` | Ship with only auto-equipped hull |
| `basic_ship` | `ships.py` | Ship with bridge and engine |
| `armed_ship` | `ships.py` | Ship with weapons |
| `shielded_ship` | `ships.py` | Ship with shields |
| `fully_equipped_ship` | `ships.py` | Ship with all common component types |
| `create_test_ship()` | `ships.py` | Factory function for custom ships |
| `battle_engine` | `battle.py` | Configured BattleEngine instance |
| `two_ship_battle` | `battle.py` | Engine with two opposing ships |

### Configuration Classes

```python
from game.core.config import DisplayConfig, AIConfig, PhysicsConfig

resolution = DisplayConfig.test_resolution()  # (1440, 900)
dt = PhysicsConfig.TICK_RATE                  # 0.01
spacing = AIConfig.MIN_SPACING                # 150
```

### Running Tests

```bash
# Full test suite
pytest tests/

# Incremental (fast, using testmon)
pytest tests/ --testmon

# Unit tests only
pytest tests/unit/ -v

# Simulation tests only
pytest simulation_tests/tests/ -v -m simulation

# Parallel execution (12 workers for CLI, 4 for VS Code Test Explorer)
pytest tests/ -n 12

# Specific test
pytest simulation_tests/tests/test_beam_weapons.py::TestBeamAccuracy::test_BEAM360_001 -v

# With coverage
pytest tests/ --cov=game --cov-report=html
```

---

## 3. TestScenario Pattern

### Architecture

```
+---------------------------------------------------------+
|                    BattleEngine                          |
|               (Core Simulation Logic)                   |
+------------------+-------------------+------------------+
                   |                   |
          +--------v--------+  +-------v---------+
          |     Pytest      |  |   Combat Lab    |
          |   (Headless)    |  |    (Visual)     |
          |                 |  |                 |
          | TestScenario ---+--+--- TestScenario |
          +-----------------+  +-----------------+
```

Both environments use the exact same `BattleEngine` code. The only difference is `headless=True` (pytest) vs `headless=False` (Combat Lab).

### TestScenario Class

```python
from simulation_tests.scenarios import TestScenario, TestMetadata

class MyTest(TestScenario):
    metadata = TestMetadata(
        test_id="BEAM-001",
        category="Weapons",
        subcategory="Beam Accuracy",
        name="Point-blank beam test",
        summary="Validates beam weapons hit at minimum range",
        conditions=["Distance: 50px", "Stationary target"],
        edge_cases=["Minimum range"],
        expected_outcome="Beam hits consistently",
        pass_criteria="Damage dealt > 0",
        max_ticks=500,
        seed=42,
        ui_priority=0,
        tags=["accuracy", "close_range"],
        validation_rules=[...]  # See Validation Rules section
    )

    def setup(self, battle_engine):
        """Configure ships, positions, initial state."""
        pass

    def update(self, battle_engine):
        """Optional: per-tick logic (e.g., force weapon firing)."""
        pass

    def verify(self, battle_engine):
        """Return True if test passed. Store results in self.results."""
        return True
```

### TestMetadata Fields

| Field | Purpose |
|-------|---------|
| `test_id` | Unique ID, format: `{ABILITYNAME}-NNN` (e.g., `BEAMWEAPON-001`) |
| `category` | Major category (e.g., `"Weapons"`, `"Propulsion"`) |
| `subcategory` | Specific area (e.g., `"Beam Accuracy"`, `"Fuel Consumption"`) |
| `name` | Short human-readable name |
| `summary` | What behavior is being tested |
| `conditions` | List of setup conditions |
| `edge_cases` | Edge cases covered |
| `expected_outcome` | What should happen |
| `pass_criteria` | Formal pass/fail criteria string |
| `max_ticks` | Simulation duration |
| `seed` | Fixed RNG seed for reproducibility |
| `tags` | Searchable tags |
| `validation_rules` | List of validation rule objects |

### Validation Rules

Four rule types, selected by data type:

| Data Type | Rule Class | Tolerance | Example |
|-----------|-----------|-----------|---------|
| Integers, strings | `ExactMatchRule` | `==` | `ship.mass == 40` |
| Deterministic floats | `DeterministicMatchRule` | 1e-9 | `max_speed == 312.5` |
| Bounded values | `RangeRule` | min/max | `0 < velocity < 312.5` |
| RNG outcomes | `StatisticalTestRule` | p-value | `hit_rate passes binomial (p < 0.05)` |

```python
from simulation_tests.scenarios.validation import (
    ExactMatchRule, DeterministicMatchRule, RangeRule, StatisticalTestRule
)

validation_rules = [
    ExactMatchRule(name='Ship Mass', path='ship.mass', expected=40),

    DeterministicMatchRule(
        name='Max Speed', path='ship.max_speed', expected=312.5,
        description='max_speed = (thrust * K_SPEED) / mass'
    ),

    RangeRule(name='Final Velocity', path='results.final_velocity', min=0, max=312.5),

    # Two-layer validation for statistical tests:
    # Layer 1: Verify formula calculation
    DeterministicMatchRule(
        name='Expected Hit Chance', path='results.expected_hit_chance',
        expected=0.5318, description='P = 1/(1+e^-0.1273)'
    ),
    # Layer 2: Verify actual outcome
    StatisticalTestRule(
        name='Hit Rate', test_type='binomial',
        expected_probability=0.5318, equivalence_margin=0.06,
        trials_expr='ticks_run', successes_expr='damage_dealt'
    ),
]
```

### Validation Context

Rules resolve dot-notation paths against a context dict built by `run_validation()`:

```python
context = {
    'test_scenario': self,
    'battle_engine': battle_engine,
    'results': {
        'ticks_run': 100,
        'initial_velocity_magnitude': 0.0,
        'final_velocity_magnitude': 156.25,
        'distance_traveled': 46406.25,
        # ... scenario-specific results
    },
    'metadata': <TestMetadata>,
    'ship': {  # From _extract_ship_validation_data()
        'ship': <Ship object>,
        'mass': 40.0,
        'hp': 100,
        'total_thrust': 500.0,
        'max_speed': 312.5,
        'acceleration_rate': 781.25,
        'turn_speed': 0.0,
    },
    'attacker': { ... },  # For weapon tests
}
```

### Path Naming Convention

- **Tuples** (coordinates): `results.initial_position`, `results.final_velocity`
- **Scalars** (magnitudes): `results.initial_velocity_magnitude`, `results.final_velocity_magnitude`
- **Ship attributes**: `ship.mass`, `ship.total_thrust`, `ship.max_speed`

### TestRegistry (Discovery)

```python
from test_framework.registry import TestRegistry

registry = TestRegistry()
# Auto-discovers all scenarios in simulation_tests/scenarios/*.py

weapon_tests = registry.get_by_category("Weapons")
beam_tests = registry.get_by_subcategory("Weapons", "Beam Accuracy")
accuracy_tests = registry.get_by_tag("accuracy")
test = registry.get_by_id("BEAM360-001")
categories = registry.get_categories()
```

---

## 4. Writing Simulation Tests

### Step-by-Step

**1. Identify the ability under test.** One test = one behavior.

**2. Check the suite document** (`simulation_tests/suites/{AbilityName}.md`) to see what is already covered and what behavior to validate next.

**3. Design the simplest possible scenario:**
- Use the smallest hull that meets requirements (see Standard Hulls below)
- Add only components needed for the behavior under test
- Ships that do not move need no engines; ships that are not targets need no armor
- Prefer 360-degree firing arcs and generous ranges to reduce complexity
- **Rule:** Prefer two single-ability components over one multi-ability component (exception: when testing resource consumption that requires both abilities on same component)

**4. Create the scenario class** in the appropriate file under `simulation_tests/scenarios/`.

**5. Calculate expected values with explicit formulas:**
```
max_speed:
  Formula: max_speed = (thrust * K_SPEED) / mass
  Calculation: (500 * 25) / 40 = 312.5 px/s
```

**6. Justify the tick count:**
- For deterministic tests: `time_needed = <formula> * safety_buffer`
- For statistical tests (binomial):
  ```
  n_min = (z^2 * p * (1-p)) / epsilon^2
  where z=1.96 (95%), p=expected_probability, epsilon=margin
  ```
  Use 2x safety buffer on the calculated minimum.

**7. Define validation rules** covering both formula correctness and outcome correctness.

**8. Store results BEFORE calling `super().verify()`** (see Troubleshooting, Issue 3).

**9. Create the pytest wrapper** in `simulation_tests/tests/`.

### Component Mass Convention

Test components have **0 mass**. Ship mass comes ONLY from hull components and mass simulators. This prevents unintended mass changes from altering radius, defense score, hit rates, and acceleration.

#### Standard Hull Masses

| Hull ID | Mass | Radius | Use Case |
|---------|------|--------|----------|
| `hull_test_xs` | 100 | 18.57 px | Minimum mass (matches physics safeguard) |
| `hull_test_s` | 400 | 29.47 px | Standard small target |
| `hull_test_m` | 1000 | 40.00 px | Reference mass target |
| `hull_test_l` | 4000 | 63.50 px | Large target |
| `hull_test_fighter` | 25 | 11.70 px | Fighter scale |
| `hull_test_satellite` | 100 | 18.57 px | Matches safeguard |

**Radius Formula:** `radius = 40 * (mass / 1000)^(1/3)`
**Physics Safeguard:** `max(ship.mass, 100)` prevents division-by-zero at very low mass.

#### Mass Simulators

Use only when testing mass-dependent mechanics:
- `test_mass_sim_1k` -- Adds 1,000 mass
- `test_mass_sim_10k` -- Adds 10,000 mass
- `test_mass_sim_100k` -- Adds 100,000 mass

### Test Component Naming Convention

Use `test_` prefix with literal descriptions:
- `test_engine_no_fuel` -- Thrust without fuel complexity
- `test_engine_with_fuel` -- For fuel consumption tests
- `test_thruster_std` -- Standard maneuvering thruster
- `test_beam_low_acc_1dmg` -- Low accuracy beam, 1 damage (for hit rate counting)
- `test_armor_basic` -- Damage absorption only

---

## 5. Common Test Patterns

### Pattern 1: Distance-Based Tests

Position ships at a specific distance and measure accuracy or damage.

```python
class BeamRangeTest(TestScenario):
    metadata = TestMetadata(test_id="BEAM-RANGE-001", name="Beam accuracy at 400px", ...)

    def setup(self, battle_engine):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(400, 0)
        self.initial_target_hp = target.hp
        battle_engine.start([attacker], [target], seed=self.metadata.seed)
        attacker.current_target = target
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        damage = self.initial_target_hp - self.target.hp
        self.results['damage_dealt'] = damage
        return damage > 0
```

### Pattern 2: Resource Consumption Tests

Track energy, fuel, or ammo usage over time.

```python
class EnergyConsumptionTest(TestScenario):
    metadata = TestMetadata(test_id="ENERGY-001", name="Beam weapon energy consumption", ...)

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker.json')
        self.initial_energy = self.attacker.current_energy
        # ... position ships, start engine

    def verify(self, battle_engine):
        energy_used = self.initial_energy - self.attacker.current_energy
        shots_fired = self.results['shots_fired']
        expected_energy = shots_fired * 10  # 10 energy per shot
        return abs(energy_used - expected_energy) < (expected_energy * 0.05)
```

### Pattern 3: Timing Tests

Track when events occur to validate cooldowns, charge-up times, etc.

```python
class WeaponCooldownTest(TestScenario):
    metadata = TestMetadata(test_id="COOLDOWN-001", name="Weapon cooldown timing", ...)

    def setup(self, battle_engine):
        self.attacker = self._load_ship('Test_Attacker.json')
        self.shot_ticks = []

    def update(self, battle_engine):
        weapon = self.attacker.get_component_by_id('Test_Weapon')
        if weapon.just_fired:
            self.shot_ticks.append(battle_engine.tick_counter)

    def verify(self, battle_engine):
        if len(self.shot_ticks) < 2:
            return False
        intervals = [self.shot_ticks[i+1] - self.shot_ticks[i]
                     for i in range(len(self.shot_ticks) - 1)]
        expected_cooldown = 60  # ticks
        return all(abs(iv - expected_cooldown) <= 1 for iv in intervals)
```

### Pattern 4: Multi-Ship Tests

Teams of ships with formation or combined tactics.

```python
class TeamBattleTest(TestScenario):
    metadata = TestMetadata(test_id="TEAM-001", name="2v2 team battle", ...)

    def setup(self, battle_engine):
        a1 = self._load_ship('Team0_Ship1.json')
        a2 = self._load_ship('Team0_Ship2.json')
        t1 = self._load_ship('Team1_Ship1.json')
        t2 = self._load_ship('Team1_Ship2.json')
        a1.position = pygame.math.Vector2(0, 0)
        a2.position = pygame.math.Vector2(0, 100)
        t1.position = pygame.math.Vector2(500, 0)
        t2.position = pygame.math.Vector2(500, 100)
        battle_engine.start([a1, a2], [t1, t2], seed=self.metadata.seed)

    def verify(self, battle_engine):
        return all(ship.is_alive for ship in battle_engine.teams[0])
```

### Pattern 5: A/B Comparison Tests

Compare measured outcomes between a baseline and a variant using `ComparisonScenario`.
The template runs two separate battles — one internally during `setup()`, one through
the normal runner loop — then compares their results in `validate()`.

```python
from simulation_tests.scenarios.templates import ComparisonScenario

class SensorDamageTest(ComparisonScenario):
    metadata = TestMetadata(test_id="SENSOR-002", name="Sensor damage comparison", ...)

    # Baseline: standard beam attacker (no sensor)
    baseline_attacker_ship = "Test_Attacker_Beam360_Med.json"
    baseline_target_ship = "Test_Target_Stationary.json"

    # Variant: beam attacker with sensor
    variant_attacker_ship = "Test_Attacker_Beam360_WithSensor.json"
    variant_target_ship = "Test_Target_Stationary.json"

    distance = 400

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true(
            "Sensor Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            actual=f"baseline={self.baseline_damage_dealt}, variant={self.variant_damage_dealt}",
            phase="outcome",
        ))
        return checks
```

**Key features:**
- Both battles use the same seed for deterministic comparison
- `configure_baseline(engine)` / `configure_variant(engine)` hooks for customization
- Combat Lab shows three buttons: "Visual Run" (variant), "Headless Run" (both), "Visual Baseline" (baseline)
- Results dict stores both `baseline_*` and `variant_*` metrics

### Pattern 6: Negative Tests

Verify that something does NOT happen.

```python
class NoEngineStaysStationary(TestScenario):
    metadata = TestMetadata(test_id="PROP-001b", name="Ship without engine stays stationary", ...)

    def setup(self, battle_engine):
        self.ship = self._load_ship('Test_No_Engine.json')
        self.start_pos = pygame.math.Vector2(self.ship.position)
        # ...

    def verify(self, battle_engine):
        distance = self.ship.position.distance_to(self.start_pos)
        self.results['distance_traveled'] = distance
        return distance == 0.0
```

---

## 6. Migration Guide

### What Has Been Migrated

The following scenario categories have been implemented using the TestScenario pattern:

| Category | Scenario File | Pytest File | Status |
|----------|--------------|-------------|--------|
| Beam Weapons | `beam_scenarios.py` | `test_beam_weapons.py` | Migrated |
| Projectile Weapons | `projectile_scenarios.py` | `test_projectile_weapons.py` | Migrated |
| Seeker Weapons | `seeker_scenarios.py` | `test_seeker_weapons.py` | Migrated |
| Propulsion (Engine) | `propulsion_scenarios.py` | `test_propulsion.py`, `test_engine_physics.py` | Migrated |
| Defense (Shields/Armor) | `defense_scenarios.py` | `test_defense.py` | Migrated |
| Modifiers | `modifier_scenarios.py` | `test_modifiers.py` | Migrated |
| Resource Consumption | `resource_scenarios.py` | `test_resource_consumption.py` | Migrated |

### How to Migrate an Old-Style Test

**Before** (old pytest style):

```python
@pytest.mark.simulation
class TestBeamWeapons:
    def test_low_acc_point_blank(self):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=50, ticks=500)
        assert result['damage_dealt'] > 0
```

**After** (TestScenario pattern):

1. **Create scenario** in `simulation_tests/scenarios/<category>_scenarios.py`:

```python
class BEAM360_001_LowAccPointBlank(TestScenario):
    metadata = TestMetadata(
        test_id="BEAM360-001", category="Weapons", subcategory="Beam Accuracy",
        name="Low accuracy beam at point-blank", max_ticks=500, seed=42,
        summary="Validates low accuracy beam (0.5) hits at 50px range",
        conditions=["Distance: 50px", "Stationary target"],
        pass_criteria="Damage dealt > 0",
        validation_rules=[...]
    )

    def setup(self, battle_engine):
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(50, 0)
        self.initial_target_hp = target.hp
        battle_engine.start([attacker], [target], seed=self.metadata.seed)
        attacker.current_target = target
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        damage = self.initial_target_hp - self.target.hp
        self.results['damage_dealt'] = damage
        return damage > 0
```

2. **Create pytest wrapper** in `simulation_tests/tests/test_<category>.py`:

```python
import pytest
from test_framework.runner import TestRunner
from simulation_tests.scenarios.beam_scenarios import BEAM360_001_LowAccPointBlank

@pytest.mark.simulation
class TestBeamAccuracy:
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        self.runner = TestRunner()

    def test_BEAM360_001_low_acc_point_blank(self):
        scenario = self.runner.run_scenario(BEAM360_001_LowAccPointBlank, headless=True)
        assert scenario.passed, f"Test failed: {scenario.results}"
```

3. **Delete the old test** after confirming the new one passes.

### Benefits of Migration

- **Dual execution**: Same test runs in pytest and Combat Lab
- **Rich metadata**: Self-documenting, searchable, displayable in UI
- **Auto-discovery**: TestRegistry finds all scenarios automatically
- **Reproducibility**: Fixed seeds, deterministic validation
- **Simplified data loading**: `self._load_ship()` handles paths

---

## 7. Troubleshooting

### Issue: Validation shows "Expected: None, Actual: None"

**Root Cause:** The validation rule's `path` does not resolve to the correct attribute.

**Diagnosis steps:**
1. Check if the path exists in the context dict.
2. Check if `_extract_ship_validation_data()` in `simulation_tests/scenarios/base.py` includes the needed attribute.
3. Check if the value is stored in `self.results` BEFORE `run_validation()` is called.
4. Check if you are using a tuple path instead of a magnitude path.

**Fix:** Update `_extract_ship_validation_data()` to include missing attributes:
```python
data = {
    'mass': ship.mass,
    'total_thrust': getattr(ship, 'total_thrust', 0.0),
    'max_speed': getattr(ship, 'max_speed', 0.0),
    'acceleration_rate': getattr(ship, 'acceleration_rate', 0.0),
    'turn_speed': getattr(ship, 'turn_speed', 0.0),
}
```

### Issue: "bad operand type for abs(): 'tuple'" error

**Root Cause:** Validation path points to a tuple `(x, y)` but the rule expects a float.

**Fix:** Use `_magnitude` suffix for scalar values:
```python
# WRONG - this is a tuple (x, y)
path='results.initial_velocity'

# CORRECT - this is a float
path='results.initial_velocity_magnitude'
```

### Issue: Validation runs before results are stored

**Root Cause:** The parent template's `verify()` calls `run_validation()` BEFORE the subclass stores its results.

**Fix:** Store results BEFORE calling `super().verify()`:
```python
def verify(self, battle_engine):
    # 1. Calculate values
    actual_value = self.ship.some_attribute

    # 2. Store ALL results FIRST
    self.results['my_expected'] = self.expected_value
    self.results['my_actual'] = actual_value

    # 3. THEN call parent (which runs validation)
    try:
        super().verify(battle_engine)
    except NotImplementedError:
        pass

    # 4. Return pass/fail
    return actual_value == self.expected_value
```

### Issue: Ship JSON expected_stats mismatch warnings

**Root Cause:** The `expected_stats` values in ship JSON were calculated incorrectly.

**Fix:**
1. Recalculate using physics formulas with K constants from `physics_constants.py`.
2. Update the `expected_stats` section with exact (not rounded) values.
3. Update formula descriptions in `propulsion_details.formulas`.

### Issue: ExactMatchRule fails on float values

**Root Cause:** `ExactMatchRule` uses `==`. While Python `40 == 40.0` is True, floating-point edge cases can fail.

**Fix:** Use `DeterministicMatchRule` for any floating-point values, even integers stored as floats.

### Issue: Ship file not found

**Fix:** Ensure ship files are in `simulation_tests/data/ships/`. Use `self._load_ship('filename.json')` which resolves the path automatically.

### Issue: Test not discovered by TestRegistry

**Check:**
1. File is in `simulation_tests/scenarios/`
2. Class extends `TestScenario`
3. Class has a `metadata` attribute
4. File name does not start with underscore

### Issue: Test fails in Combat Lab but passes in pytest

This should not happen if tests are written correctly. Check:
1. Using fixed seed?
2. Test depends on rendering or timing?
3. Calling `update()` properly each tick?

### Historical Fixes Log

| Test | Issue | Fix | Date |
|------|-------|-----|------|
| PROP-001 | `ship.total_thrust` path returned None | Added propulsion attrs to `_extract_ship_validation_data()` | 2026-01-17 |
| PROP-001 | `results.initial_velocity` was tuple | Changed to `results.initial_velocity_magnitude` | 2026-01-17 |
| PROP-003 | Results stored after validation ran | Moved results storage before `super().verify()` | 2026-01-17 |
| PROP-003 | Ship JSON turn_speed 826.45 vs correct 414.09 | Recalculated with correct K constants | 2026-01-17 |
| PROP-001b | `results.final_velocity` was tuple | Changed to `results.final_velocity_magnitude` | 2026-01-17 |
| PROP-003b | `results.final_velocity` was tuple | Changed to `results.final_velocity_magnitude` | 2026-01-17 |

---

## 8. Best Practices

### Test Design
- **One behavior per test.** Each test validates a single specific behavior.
- **Simplest possible scenario.** Minimal ships, minimal components, minimal ticks.
- **Zero-mass components.** Only hulls and mass simulators contribute mass.
- **Fixed seeds.** Every test specifies a seed for reproducibility.
- **Deterministic first.** Prefer deterministic assertions; use statistical tests only for RNG outcomes.

### Statistical Tests
- Default: p < 0.001 if achievable within ~1000 ticks.
- Fallback: p < 0.05 only when p < 0.001 would require excessive tick counts.
- Always use **two-layer validation**: formula correctness (DeterministicMatchRule) AND outcome correctness (StatisticalTestRule).
- For High-Tick variants: 100k ticks, epsilon = 0.01.

### Validation Rules
- Use `ExactMatchRule` for integers and strings.
- Use `DeterministicMatchRule` for deterministic floats (tolerance 1e-9).
- Use `RangeRule` for bounded values.
- Use `StatisticalTestRule` for RNG-based outcomes.
- Always show formulas and substitutions in descriptions.

### Results & Reporting
- Store all measured values in `self.results` for detailed reporting.
- Always include seed and tick count in results.
- Identify a primary outcome value for summary display (e.g., `final_velocity` for acceleration tests, `damage_dealt` for weapon tests).

### Suite Documents
- Each ability has a suite doc at `simulation_tests/suites/{AbilityName}.md`.
- Suite docs list expected behaviors, unexpected behaviors, and a coverage matrix.
- Update the coverage matrix after implementing each new test.

### Data Isolation
- Tests use ONLY `simulation_tests/data/` files.
- Never modify production data in `data/`.
- Validate data at load time: Assumed vs Live values produce warnings on mismatch.

---

## 9. One Category Per Ability (Active Direction)

The test suite is moving toward **one dedicated test category per combat ability**.
Each category is a scenario file named after the ability (e.g., `tohit_attack_scenarios.py`
for `ToHitAttackModifier`). Categories use `ComparisonScenario` to run A/B battles
and compare measured outcomes.

### Standard Test Set Per Ability

Every ability category should include at minimum:

| Test | What it proves |
|------|---------------|
| Basic positive effect | The ability does what it claims |
| Same-group stacking | Intra-group MAX — redundant components don't stack |
| Different-group stacking | Inter-group SUM — diverse components combine additively |
| Negative value | The ability works bidirectionally (penalty/debuff) |

Additional tests capture ability-specific edge cases (range interactions,
threshold behaviors, resource coupling, etc.).

### Completed Ability Categories

| Ability | File | Tests |
|---------|------|-------|
| `ToHitAttackModifier` | `tohit_attack_scenarios.py` | TOHIT-ATK-001 to 004 |
| `ToHitDefenseModifier` | `tohit_defense_scenarios.py` | TOHIT-DEF-001 to 004 |

### Pending Ability Categories

| Ability | Priority | Notes |
|---------|----------|-------|
| `ShieldProjection` | High | Migrate from `defense_scenarios.py`, add stacking tests |
| `ShieldRegeneration` | Medium | Separate from projection, test regen rate + energy coupling |
| `EmissiveArmor` | Medium | Migrate from `defense_scenarios.py`, add stacking/threshold tests |
| `CrystallineArmor` | Medium | Absorption + shield recharge interaction |
| `PointDefense` | High | Flesh out SEEKER-PD-001/002/003 placeholders |
| `VehicleLaunch` | Low | Carrier/hangar launch cycle and capacity |

See `simulation_tests/ABILITY_TEST_COVERAGE_PLAN.md` for the full inventory.

---

## 10. Stacking Rules Reference

All numeric abilities use the same two-phase aggregation:

1. **Intra-group MAX:** Components with the same `stack_group` — only the highest value counts
2. **Inter-group SUM:** Components with different `stack_group` values — values are summed

Marker abilities (`CommandAndControl`, `Armor`, etc.) use boolean OR.

There are no multiplicative exceptions. The aggregated value is then used
additively in whatever formula consumes it (e.g., added to `net_score` in the
beam hit chance sigmoid).

Test components define their `stack_group` in `components.json`:
```json
{
    "ToHitAttackModifier": {"value": 1.0, "stack_group": "sensors_a"}
}
```

Components without a `stack_group` are each treated as their own group (all stack).

---

## 11. Future Work

### Suite Documents

Only `BeamWeaponAbility.md` exists in `simulation_tests/suites/`. Suite documents
for other abilities will be created as their test categories are built out.

### Combat Lab Integration

The Combat Lab UI supports ability-specific test categories:
- TestRegistry auto-discovers scenarios and groups by category
- ComparisonScenario tests show three buttons: Visual Run, Headless Run, Visual Baseline
- Test run history persists across sessions
