# Simulation Testing Guide

Consolidated guide for the Starship Battles simulation test system. Covers test architecture, the TestScenario pattern, validation, troubleshooting, and writing new tests.

> **API UPDATE (PROJ-270 Phase 11, 2026-04-12):** The code examples below
> that show `def setup(self, battle_engine)` and `def update(self, battle_engine)`
> are **LEGACY** — PROJ-269 Phase 1 + PROJ-270 Phase 1 deleted those methods.
> The current `TestScenario` API is:
>
> ```python
> class MyTest(TestScenario):
>     metadata = TestMetadata(...)
>     def to_spec(self, registries=None) -> BattleSpec: ...
>     def wire_ships(self, ships_by_role, engine, initial_state): ...
>     def custom_setup(self, engine): ...   # optional
>     def validate(self, outcome, telemetry) -> list: ...
> ```
>
> See `combat_lab/scenarios/base.py` for the current canonical shape and
> any modern scenario file (e.g. `beam_accuracy_scenarios.py`) for a
> worked example. `docs/systems/combat_simulation.md` §0 is authoritative.

---

## 1. Overview & Test Architecture

### Purpose

Simulation tests validate game mechanics (weapons, propulsion, shields, etc.) by running the BattleEngine in headless mode and checking outcomes against expected values. The same tests can run in both the **CLI runner** (headless) and **Combat Lab** (visual, interactive).

**Important:** Simulation tests do NOT use pytest. They run via `python -m combat_lab.run_tests`.

### Directory Structure

```
combat_lab/
├── run_tests.py                     # CLI test runner (auto-discovery)
├── test_constants.py                # Shared constants
├── test_history.py                  # TestHistory (per-test-id shards, lazy load)
├── test_history/                    # Per-test-id shard files ({test_id}.json)
├── logging_config.py                # Logging setup
├── ABILITY_TEST_COVERAGE_PLAN.md    # Coverage tracking
├── data/                            # Test-only data (isolated from production)
│   ├── components.json              # Test-only components
│   ├── vehicleclasses.json          # Test hull classes
│   ├── modifiers.json               # Test modifiers
│   ├── ships/                       # Test ship JSON files
│   ├── ship_templates/              # Base templates for ship generation
│   ├── schemas/                     # JSON schema validation files
│   └── schema_validator.py          # Runtime schema validation
├── scenarios/                       # TestScenario implementations
│   ├── base.py                      # TestScenario + TestMetadata base classes
│   ├── templates.py                 # 5 reusable scenario templates
│   ├── validation.py                # Check-based validation system
│   ├── movement.py                  # Movement controllers
│   ├── __init__.py                  # Module exports
│   │   # Weapon scenarios
│   ├── beam_scenarios.py            # Beam weapon accuracy, resource tests
│   ├── projectile_scenarios.py      # Projectile weapon tests
│   ├── seeker_scenarios.py          # Seeker weapon tests
│   │   # Ability-specific categories
│   ├── tohit_attack_scenarios.py    # ToHitAttackModifier
│   ├── tohit_attack_fleet_scenarios.py # ToHitAttackModifier (fleet scope)
│   ├── tohit_defense_scenarios.py   # ToHitDefenseModifier
│   ├── shield_projection_scenarios.py # ShieldProjection
│   ├── shield_regen_scenarios.py    # ShieldRegeneration
│   ├── armor_layer_scenarios.py     # ArmorLayer
│   ├── emissive_armor_scenarios.py  # EmissiveArmor
│   ├── cnc_scenarios.py             # CommandAndControl
│   ├── sra_scenarios.py             # ShieldRegeneratingArmor
│   ├── damage_pipeline_scenarios.py # Integration tests (multi-component defense)
│   │   # Modifier subcategories
│   ├── mod_damage_scenarios.py      # damage_mult modifier
│   ├── mod_range_scenarios.py       # range_mult modifier
│   ├── mod_reload_scenarios.py      # reload_mult modifier
│   ├── mod_thrust_scenarios.py      # thrust_mult modifier
│   ├── mod_accuracy_scenarios.py    # accuracy_add modifier
│   ├── mod_arc_scenarios.py         # arc_set modifier
│   ├── mod_endurance_scenarios.py   # endurance_mult modifier
│   ├── mod_consumption_scenarios.py # consumption_mult modifier
│   ├── mod_stacking_scenarios.py    # Multi-modifier interactions
│   │   # System scenarios
│   ├── propulsion_scenarios.py      # Engine/thruster scenarios
│   └── resource_scenarios.py        # Fuel/energy/ammo scenarios
├── battle_states/                   # Captured battle state snapshots
├── suites/                          # Suite documentation
│   └── BeamWeaponAbility.md
├── utils/                           # Utility helpers
│   └── test_log_analyzer.py
├── validation/                      # Validation system docs
│   └── README.md
└── output/                          # Test output artifacts
```

**Key isolation rule:** Tests in `combat_lab/` use ONLY data from `combat_lab/data/`. Production data in `data/` is never modified by tests.

---

## 2. Running Simulation Tests

### CLI Runner

```bash
# Run all simulation tests
python -m combat_lab.run_tests

# Filter by ID prefix
python -m combat_lab.run_tests BEAMWEAPON

# Run a specific test
python -m combat_lab.run_tests BEAMWEAPON-001

# List all discovered tests
python -m combat_lab.run_tests --list

# Skip high-tick (-HT) tests for quick validation
python -m combat_lab.run_tests --fast

# Don't record to combat_lab/test_history/ shards
python -m combat_lab.run_tests --no-history
```

### Key Features

- **Auto-discovery**: Globs `scenarios/*_scenarios.py` — new files found automatically
- **History recording**: CLI runs write a per-test-id shard at
  `combat_lab/test_history/{test_id}.json` by default (same storage as the
  Combat Lab UI). Shards are loaded lazily and written atomically. Pass
  `--no-history` to skip.
- **`--fast` mode**: Filters out `-HT` (high-tick 100k) tests for quick validation

### Combat Lab Integration

The Combat Lab UI supports ability-specific test categories:
- TestRegistry auto-discovers scenarios and groups by category
- ComparisonScenario tests show three buttons: Visual Run, Headless Run, Visual Baseline
- Selecting a test auto-selects the most recent run and shows detailed results
- Test run history persists across sessions (shared with CLI via `combat_lab/test_history/` shards)

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
          |   run_tests.py  |  |   Combat Lab    |
          |   (Headless)    |  |    (Visual)     |
          |                 |  |                 |
          | TestScenario ---+--+--- TestScenario |
          +-----------------+  +-----------------+
```

Both environments use the exact same `BattleEngine` code. The only difference is `headless=True` (run_tests CLI) vs `headless=False` (Combat Lab).

### TestScenario Class

```python
from combat_lab.scenarios import TestScenario, TestMetadata
from combat_lab.scenarios.validation import check_exact, check_true

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
    )

    def setup(self, battle_engine):
        """Configure ships, positions, initial state."""
        pass

    def update(self, battle_engine):
        """Optional: per-tick logic (target movement controllers only).
        Firing and thrust are handled by AI strategies assigned in setup()."""
        pass

    def validate(self, engine) -> list:
        """Return list of Check objects for 3-phase validation."""
        checks = []
        checks.append(check_true(
            "Damage dealt", self.damage_dealt > 0,
            detail=f"damage={self.damage_dealt}", phase="outcome"
        ))
        return checks
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
| `ui_priority` | Display priority in Combat Lab (0=normal, higher=more important) |
| `tags` | Searchable tags |

### Validation System

The validation system uses **Check objects** with three phases:

1. **data** — Verify component/ship data loaded correctly (damage, range, mass, etc.)
2. **precondition** — Verify the test setup is correct (target moved, distance correct, etc.)
3. **outcome** — Verify the measured result matches expectations

#### Check Functions

```python
from combat_lab.scenarios.validation import (
    check_exact, check_approx, check_tost, check_true,
    Check, ValidationReport,
)
```

| Function | Purpose | Example |
|----------|---------|---------|
| `check_exact(name, expected, actual, phase)` | Exact equality | `check_exact("Mass", 400, ship.mass, phase="data")` |
| `check_approx(name, expected, actual, tolerance, phase)` | Relative tolerance | `check_approx("Distance", 100.0, dist, tolerance=0.001, phase="precondition")` |
| `check_tost(name, expected_p, successes, trials, margin, phase)` | Statistical TOST test | `check_tost("Hit Rate", 0.53, hits, shots, margin=0.10, phase="outcome")` |
| `check_true(name, condition, actual, detail, phase)` | Boolean check | `check_true("Fired", shots > 0, detail=f"shots={shots}", phase="precondition")` |

#### ValidationReport

`validate()` returns `List[Check]`. The runner wraps these in a `ValidationReport`:
- `report.passed` — True only if ALL checks pass
- `report.failed_phase` — First phase with failures (helps diagnose root cause)
- `report.summary()` — Phase-by-phase breakdown

### TestRegistry (Discovery)

```python
from combat_lab.registry import TestRegistry

registry = TestRegistry()
# Auto-discovers all scenarios in combat_lab/scenarios/*.py

weapon_tests = registry.get_by_category("Weapons")
beam_tests = registry.get_by_subcategory("Weapons", "Beam Accuracy")
accuracy_tests = registry.get_by_tag("accuracy")
test = registry.get_by_id("BEAMWEAPON-001")
```

---

## 4. Writing Simulation Tests

### Step-by-Step

**1. Identify the ability under test.** One test = one behavior.

**2. Check the coverage plan** (`combat_lab/ABILITY_TEST_COVERAGE_PLAN.md`) to see what is already covered.

**3. Design the simplest possible scenario:**
- Use the smallest hull that meets requirements (see Standard Hulls below)
- Add only components needed for the behavior under test
- Ships that do not move need no engines; ships that are not targets need no armor
- Prefer 360-degree firing arcs and generous ranges to reduce complexity
- **Rule:** Prefer two single-ability components over one multi-ability component (exception: when testing resource consumption that requires both abilities on same component)

**4. Create the scenario class** in the appropriate file under `combat_lab/scenarios/`.

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

**7. Implement `validate(engine) -> List[Check]`** with data, precondition, and outcome checks.

**8. Run the test** via `python -m combat_lab.run_tests <TEST_ID>`.

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
from combat_lab.scenarios.validation import check_exact, check_tost, check_true

class BeamRangeTest(StaticTargetScenario):
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 400

    metadata = TestMetadata(test_id="BEAM-RANGE-001", name="Beam accuracy at 400px", ...)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true(
            "Damage dealt", self.damage_dealt > 0,
            detail=f"damage={self.damage_dealt}", phase="outcome"
        ))
        return checks
```

**Note:** Test scenarios assign AI strategies (`test_stationary_fire`, `test_do_nothing`,
`test_straight_line`, `test_rotate_right`, `test_rotate_left`, `test_erratic`) instead of
manually setting `comp_trigger_pulled` or calling `thrust_forward()` in `update()`.
The AI controller handles firing and movement commands.

### Pattern 2: Resource Consumption Tests

Track energy, fuel, or ammo usage over time using `ResourceScenario`.

```python
class EnergyConsumptionTest(ResourceScenario):
    ship_file = "Test_Ship_WithEnergy.json"
    resource_type = "energy"

    metadata = TestMetadata(test_id="RESOURCE-001", ...)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_approx(
            "Energy consumed", expected_consumption, self.value_consumed,
            tolerance=0.05, phase="outcome"
        ))
        return checks
```

### Pattern 3: A/B Comparison Tests

Compare measured outcomes between a baseline and a variant using `ComparisonScenario`.
The template runs two separate battles — one internally during `setup()`, one through
the normal runner loop — then compares their results in `validate()`.

```python
from combat_lab.scenarios.templates import ComparisonScenario

class SensorIncreasesAccuracyScenario(ComparisonScenario):
    metadata = TestMetadata(test_id="TOHIT-ATK-001", name="Sensor Increases Accuracy", ...)

    # Baseline: standard beam attacker (no sensor)
    baseline_attacker_ship = "Test_Attacker_Beam_Med_NoSensor.json"
    baseline_target_ship = "Test_Target_Stationary.json"

    # Variant: beam attacker with sensor (+1.0 attack bonus)
    variant_attacker_ship = "Test_Attacker_Beam_Med_Sensor.json"
    variant_target_ship = "Test_Target_Stationary.json"

    distance = 400

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true(
            "Sensor Increases Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"baseline={self.baseline_damage_dealt}, variant={self.variant_damage_dealt}",
            phase="outcome",
        ))
        return checks
```

**Key features:**
- Both battles use the same seed for deterministic comparison
- `configure_baseline(engine)` / `configure_variant(engine)` hooks for customization
- Combat Lab shows three buttons: "Visual Run" (variant), "Headless Run" (both), "Visual Baseline" (baseline)
- Results dict stores both `baseline_*` and `variant_*` metrics

### Pattern 4: Negative Tests

Verify that something does NOT happen.

```python
class NoEngineStaysStationary(PropulsionScenario):
    ship_file = "Test_No_Engine.json"

    metadata = TestMetadata(test_id="PROP-001b", name="Ship without engine stays stationary", ...)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_exact(
            "No movement", 0.0, self.distance_traveled, phase="outcome"
        ))
        return checks
```

### Pattern 5: Resource Dependency Tests

Prove that components with `ResourceConsumption` stop functioning when resources
deplete.  Test three levels: full resource (control), 50% resource, and no resource.

```python
class BeamStopsWithoutEnergy(ComparisonScenario):
    metadata = TestMetadata(test_id="BEAMWEAPON-RES-001", ...)

    baseline_attacker_ship = "Test_Attacker_BeamGuaranteed_HighEnergy.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_BeamGuaranteed_NoEnergy.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = 100

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_exact(
            "No-Energy — Zero Damage", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))
        return checks
```

**Two resource trigger types:**

| Trigger | Example | How it stops |
|---------|---------|--------------|
| `"constant"` | Shield energy | Component becomes non-operational → loses stat contributions |
| `"activation"` | Weapon ammo | `can_afford_activation()` returns False → weapon refuses to fire |

**Generic resource support:** The resource system is fully data-driven. Any resource
type defined in `data/resources.json` works — including planetary resources like
`"metals"`, `"organics"`, etc. Tests validate this with `BEAMWEAPON-RES-METALS-*`,
`PROJECTILE-RES-METALS-*`, and `SHIELD-PROJ-METALS-*` scenarios.

---

## 6. Scenario Templates

Five templates extend `TestScenario` and provide automatic setup/collect_results:

| Template | Purpose | Key Config |
|----------|---------|------------|
| `StaticTargetScenario` | One attacker, one stationary target | `attacker_ship`, `target_ship`, `distance` |
| `DuelScenario` | Two ships engaging | `ship1_file`, `ship2_file`, `distance` |
| `PropulsionScenario` | Single ship movement/physics | `ship_file`, `thrust_forward`, `turn_left/right` |
| `ResourceScenario` | Resource consumption/regeneration | `ship_file`, `resource_type` |
| `ComparisonScenario` | A/B comparison (baseline vs variant) | 4 ship files + `distance` |

All templates auto-collect weapon stats via `_collect_weapon_stats()` and provide
`_template_preconditions()` for standard data/precondition checks.

---

## 7. Ability Test Categories

### One Category Per Ability

The test suite uses **one dedicated test category per combat ability**. Each category
is a scenario file named after the ability (e.g., `tohit_attack_scenarios.py`). Tests
use `ComparisonScenario` for measured A/B comparisons.

### Standard Test Set Per Ability

| Test | What it proves |
|------|---------------|
| Basic positive effect | The ability does what it claims |
| Same-group stacking | Intra-group MAX — redundant components don't stack |
| Different-group stacking | Inter-group SUM — diverse components combine additively |
| Negative value | The ability works bidirectionally (penalty/debuff) |

### Completed Ability Categories

| Ability | File | Test IDs |
|---------|------|----------|
| `ToHitAttackModifier` | `tohit_attack_scenarios.py` | TOHIT-ATK-001 to 005 |
| `ToHitAttackModifier` (fleet) | `tohit_attack_fleet_scenarios.py` | TOHIT-ATK-FLEET-001 to 004 |
| `ToHitDefenseModifier` | `tohit_defense_scenarios.py` | TOHIT-DEF-001 to 004 |
| `ShieldProjection` | `shield_projection_scenarios.py` | SHIELD-PROJ-001 to 007, METALS-001/002 |
| `ShieldRegeneration` | `shield_regen_scenarios.py` | SHIELD-REGEN-001 to 007 |
| `ArmorLayer` | `armor_layer_scenarios.py` | ARMOR-LAYER-001 to 003 |
| `EmissiveArmor` | `emissive_armor_scenarios.py` | EMISSIVE-001 to 007 |
| `CommandAndControl` | `cnc_scenarios.py` | CNC-001 to 006 |
| `ShieldRegeneratingArmor` | `sra_scenarios.py` | SRA-001 to 005 |
| `DamagePipeline` (integration) | `damage_pipeline_scenarios.py` | PIPELINE-001 to 005, 007 |

### Weapon & System Categories

| Category | File | Test ID Prefix |
|----------|------|---------------|
| Beam Weapons | `beam_scenarios.py` | BEAMWEAPON-* |
| Projectile Weapons | `projectile_scenarios.py` | PROJECTILE-* |
| Seeker Weapons | `seeker_scenarios.py` | SEEKER-* |
| Propulsion | `propulsion_scenarios.py` | PROP-* |
| Resources | `resource_scenarios.py` | RESOURCE-* |

### Stat Modifier Subcategories

Each modifier effect type has a dedicated test file:

| Modifier | File | Test ID Prefix |
|----------|------|---------------|
| `damage_mult` | `mod_damage_scenarios.py` | MOD-DMG-* |
| `range_mult` | `mod_range_scenarios.py` | MOD-RANGE-* |
| `reload_mult` | `mod_reload_scenarios.py` | MOD-RELOAD-* |
| `thrust_mult` | `mod_thrust_scenarios.py` | MOD-THRUST-* |
| `accuracy_add` | `mod_accuracy_scenarios.py` | MOD-ACC-* |
| `arc_set` | `mod_arc_scenarios.py` | MOD-ARC-* |
| `endurance_mult` | `mod_endurance_scenarios.py` | MOD-ENDUR-* |
| `consumption_mult` | `mod_consumption_scenarios.py` | MOD-CONSUME-* |
| Multi-modifier stacking | `mod_stacking_scenarios.py` | MOD-STACK-* |

Weapon-level resource dependency tests exist within weapon files:
- `beam_scenarios.py`: BEAMWEAPON-RES-* (energy), BEAMWEAPON-RES-METALS-*
- `projectile_scenarios.py`: PROJECTILE-RES-* (ammo), PROJECTILE-RES-METALS-*

### Pending Ability Categories

| Ability | Priority | Notes |
|---------|----------|-------|
| `PointDefense` | High | Expand SEEKER-PD-001/002 coverage |
| `VehicleLaunch` | Low | Carrier/hangar launch cycle and capacity |

See `combat_lab/ABILITY_TEST_COVERAGE_PLAN.md` for the full inventory.

---

## 8. Stacking Rules Reference

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

## 9. Engine Design Decisions (for test authors)

These engine behaviors affect how tests should be designed:

### Resource System
- Resource types are **data-driven**: any resource from `data/resources.json` works
  (fuel, energy, ammo, metals, organics, etc.). No hardcoded resource assumptions
  in the combat simulation layer.
- `"constant"` trigger consumption: checked per-tick in `component.update()`.
  Starvation sets `is_operational = False` → component loses stat contributions.
- `"activation"` trigger consumption: checked per-shot via `can_afford_activation()`.
  Component stays operational but refuses to fire.
- Resource storage components always contribute capacity regardless of operational status.

### Stats Aggregation
- `ShipStatsCalculator` skips non-operational components during Phase 3 aggregation.
- `current_shields` is capped when `max_shields` decreases (e.g., shield loses power).
- Ship defaults: `total_defense_score = 0.0`, `baseline_to_hit_offense = 0.0` (additive neutral).
- Resource tracking uses a generic `_prev_max_resources: dict` (not hardcoded per type).

### ComparisonScenario
- Runs baseline battle internally during `setup()`, variant on runner's engine.
- Both battles use the same seed (`_effective_seed`).
- `_visual_baseline = True` flag renders the baseline battle for debugging.
- Combat Lab shows an amber "Visual Baseline" button for comparison tests.
- Erratic controller seeds are derived from `_effective_seed` for reproducibility.

### Validation
- `Check.__post_init__` coerces `passed` to native `bool` (scipy returns `numpy.bool_`).
- `_safe_serialize` converts numpy scalars via `.item()` before type checks.
- `check_true` uses `detail=` for descriptive context (not `actual=` with raw numbers).
- UI `_draw_numeric_difference` skips boolean values to prevent "99900%" nonsense.

---

## 10. Best Practices

### Test Design
- **One behavior per test.** Each test validates a single specific behavior.
- **Simplest possible scenario.** Minimal ships, minimal components, minimal ticks.
- **Zero-mass components.** Only hulls and mass simulators contribute mass.
- **Fixed seeds.** Every test specifies a seed for reproducibility.
- **Deterministic first.** Prefer deterministic assertions; use statistical tests only for RNG outcomes.

### Statistical Tests
- Default: p < 0.001 if achievable within ~1000 ticks.
- Fallback: p < 0.05 only when p < 0.001 would require excessive tick counts.
- For High-Tick variants: 100k ticks, epsilon = 0.01.

### Validation Checks
- Use `check_exact` for integers, strings, and exact values.
- Use `check_approx` for deterministic floats (tolerance 1e-9 or wider).
- Use `check_tost` for RNG-based outcomes (statistical equivalence).
- Use `check_true` for boolean conditions with descriptive detail.
- **Verify ALL assumptions in preconditions** — a pass on a broken test setup is worse than a failure.

### Results & Reporting
- Store all measured values in `self.results` for detailed reporting.
- Always include seed and tick count in results.
- Identify a primary outcome value for summary display.

### Data Isolation
- Tests use ONLY `combat_lab/data/` files.
- Never modify production data in `data/`.
- Validate data at load time: Assumed vs Live values produce warnings on mismatch.

---

## 11. Troubleshooting

### Issue: Ship JSON expected_stats mismatch warnings

**Root Cause:** The `expected_stats` values in ship JSON don't match what `Ship.from_dict()` + `recalculate_stats()` computes.

**Fix:**
1. Run `python Tools/fix_designs/fix_designs.py [directory]` to recalculate `expected_stats` for all designs using `Ship.from_dict()` + `recalculate_stats()` (the single source of truth).
2. Or run `python Tools/validate_designs/validate_designs.py [directory]` to identify which designs have mismatches.
3. The `expected_stats.mass` includes hull base mass from the vehicle class — it will be higher than the sum of component masses alone.

### Issue: Ship file not found

**Fix:** Ensure ship files are in `combat_lab/data/ships/`. Use `self._load_ship('filename.json')` which resolves the path automatically.

### Issue: Test not discovered by runner

**Check:**
1. File is in `combat_lab/scenarios/`
2. File name ends with `_scenarios.py`
3. Class extends `TestScenario` (or a template)
4. Class has a `metadata` attribute (not None)

### Issue: Test fails in Combat Lab but passes in CLI

This should not happen if tests are written correctly. Check:
1. Using fixed seed?
2. Test depends on rendering or timing?
3. Calling `update()` properly each tick?

---

## 12. Future Work

### Pending Ability Categories

See the ABILITY_TEST_COVERAGE_PLAN.md for the current list. Each new ability should
follow the standard test set: basic effect, stacking (if applicable), negative value,
resource dependency (if applicable), and generic resource (metals) variant.
