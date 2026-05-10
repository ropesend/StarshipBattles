# Simulation Testing Compact Reference

> **Last verified:** 2026-05-08 - Compared `docs/guides/simulation_testing.md`,
> `AgentCoordination/Scratchpad/reports/guides_simulation_testing_ALT_compact.md`,
> and current Combat Lab source. Corrects stale `scenario.to_spec()` and
> `test_history.json` wording.

Use this when writing or maintaining Combat Lab simulation scenarios. It keeps
the compact reference style, but preserves current contracts, paths, invariants,
extension recipes, warnings, and test commands.

## Purpose

Combat Lab scenarios validate combat mechanics by running the real simulation
engine headlessly or visually and checking `BattleOutcome` plus optional
`CombatLabTelemetry`. The scenario suite itself does not use pytest; run it with
`python -m combat_lab.run_tests`. Framework/unit guards still live under
`tests/unit/combat_lab/` and should be used when changing the framework.

Tests are isolated from production game data. Scenario data lives under
`combat_lab/data/`; do not modify root `data/` for Combat Lab tests.

## Core Paths

```text
combat_lab/run_tests.py                         CLI runner
combat_lab/registry.py                          scenario auto-discovery
combat_lab/runner.py                            TestRunner, DesignOnlyMaterializer setup
combat_lab/services/scenario_run_helper.py      run_scenario_via_run_battle
combat_lab/spec_compiler.py                     build_test_battle_spec(scenario, registries)
combat_lab/telemetry.py                         CombatLabTelemetry
combat_lab/test_history.py                      sharded TestHistory
combat_lab/scenarios/base.py                    TestScenario, TestMetadata
combat_lab/scenarios/templates.py               canonical scenario templates
combat_lab/scenarios/validation.py              Check, ValidationReport, check_* helpers
combat_lab/scenarios/movement.py                test movement controllers
combat_lab/scenarios/ab_outcome.py              ABBattleOutcome
combat_lab/services/ab_battle_runner.py         ABBattleRunner
combat_lab/scenario_role_registry.py            Combat Lab role registry accessor
combat_lab/data/components.json                 test-only components
combat_lab/data/vehicleclasses.json             test hull classes
combat_lab/data/modifiers.json                  test modifiers
combat_lab/data/scenario_roles.json             valid scenario_role labels
combat_lab/data/ships/                          test ship JSON files
combat_lab/test_history/{test_id}.json          per-test result shards
game/simulation/battle_runner.py                run_battle, materialize_spec_ships
game/simulation/battle_spec.py                  BattleSpec and related DTOs
game/simulation/battle_outcome.py               BattleOutcome and related DTOs
game/simulation/combat/telemetry.py             TelemetryLevel
tests/unit/combat_lab/                          framework guard tests
```

Scenario files are auto-discovered from `combat_lab/scenarios/*_scenarios.py`.
A concrete test class must subclass `TestScenario` or a template and define
non-`None` `metadata`.

## Commands

```bash
python -m combat_lab.run_tests                  # all simulation scenarios
python -m combat_lab.run_tests BEAMWEAPON       # filter by ID prefix
python -m combat_lab.run_tests BEAMWEAPON-001   # one scenario
python -m combat_lab.run_tests --list           # list discovered scenarios
python -m combat_lab.run_tests --fast           # skip high-tick (-HT) scenarios
python -m combat_lab.run_tests --no-history     # do not write history shards
python main.py                                  # open app, then Combat Lab UI
pytest tests/unit/combat_lab/test_spec_compiler.py
pytest tests/unit/combat_lab/test_scenario_roles_consistency.py
```

CLI runs write `combat_lab/test_history/{test_id}.json` by default. The Combat
Lab UI reads the same shards. `--fast` filters out `-HT` high-tick scenarios.

## Current Battle Flow

Combat Lab is spec-driven:

```text
TestScenario instance
  -> combat_lab.spec_compiler.build_test_battle_spec(scenario, registries)
  -> scenario.before_run_battle(spec)
  -> game.simulation.battle_runner.run_battle(spec, ai_factory=..., ship_builder=...)
  -> role-keyed materialization and scenario.wire_ships(...)
  -> scenario.custom_setup(engine)
  -> per-tick scenario.update(engine) and telemetry capture
  -> BattleOutcome + CombatLabTelemetry
  -> scenario.collect_results(outcome, telemetry)
  -> scenario.validate(...)
```

Normal template scenarios describe setup through class attributes. The runner
owns spec construction. Do not add `to_spec()` for normal template scenarios.
A subclass may define `to_spec(self, registries=None)` only for custom layouts
that do not fit the five canonical templates; `build_test_battle_spec` detects
subclass overrides before template dispatch.

`run_battle(...)` requires `ai_factory`. If `ship_builder` is omitted, callers
must pass `registry_provider`; simulation-layer code must not call
`get_default_registry_provider()` directly. Combat Lab is outside the simulation
layer, so `scenario_run_helper.py` builds a context ship builder with
`get_default_registry_provider()`.

`TestRunner.__init__` installs `DesignOnlyMaterializer` backed by
`combat_lab.design_loader.load_combat_lab_design`; UI callers must call
`TestRunner.cleanup()` after execution so the materializer does not leak into
Battle Setup or strategy flows. CLI runs are process-local and do not need
cleanup.

Visual Combat Lab runs use the same spec contract through the visual driver,
not a raw `BattleEngine` setup path. The legacy `setup(engine)` / `verify(engine)`
style is deleted. Validators consume DTOs, not a live engine.

## TestScenario Shape

```python
from typing import Any

from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.scenarios.validation import Check, check_true


class MyScenario(StaticTargetScenario):
    metadata = TestMetadata(
        test_id="MY-001",
        category="MyAbility",
        subcategory="Basic Effect",
        name="My ability changes the measured result",
        summary="Compares setup against expected behavior.",
        conditions=["Fixed seed", "Stationary target"],
        edge_cases=[],
        expected_outcome="Measured result changes as expected",
        pass_criteria="outcome check passes",
        max_ticks=500,
        seed=42,
        ui_priority=0,
        tags=["myability"],
        telemetry_level="DETAILED",
    )

    attacker_ship = "Test_Attacker.json"
    target_ship = "Test_Target.json"
    distance = 100

    def wire_ships(
        self,
        ships_by_role: dict[str, Any],
        *,
        engine: Any = None,
        initial_state: dict[str, Any] | None = None,
    ) -> None:
        super().wire_ships(
            ships_by_role,
            engine=engine,
            initial_state=initial_state,
        )

    def custom_setup(self, engine: Any) -> None:
        self.attacker.current_target = self.target

    def validate(self, outcome: Any, telemetry: Any = None) -> list[Check]:
        checks = self._template_preconditions()
        damage = self.initial_hp - self.target.hp
        checks.append(check_true(
            "Damage dealt",
            damage > 0,
            detail=f"damage={damage}",
            phase="outcome",
        ))
        return checks
```

Use template-provided collection attributes where available. Store important
measured values in `self.results`, including seed and tick count. Use
`_collect_extra_results(outcome, telemetry)` for scenario-specific metrics that
the template does not collect.

## Metadata

`TestMetadata` fields:

| Field | Purpose |
|---|---|
| `test_id` | unique ID, usually `{ABILITYNAME}-NNN` |
| `category` | major grouping shown in Combat Lab |
| `subcategory` | narrower grouping |
| `name` | short human-readable name |
| `summary` | behavior under test |
| `conditions` | setup facts |
| `edge_cases` | edge cases covered |
| `expected_outcome` | expected behavior |
| `pass_criteria` | formal pass/fail text |
| `max_ticks` | intended simulation duration |
| `seed` | fixed RNG seed |
| `ui_priority` | display priority, `0` normal |
| `tags` | searchable tags |
| `telemetry_level` | `"MINIMAL"`, `"NORMAL"`, or `"DETAILED"`; default `"DETAILED"` |

`build_test_battle_spec` also sets a safety ceiling:
`absolute_max_ticks = max(max_ticks * 10, 1000)`.

## Scenario Templates

| Template | Use | Required config |
|---|---|---|
| `StaticTargetScenario` | one attacker vs stationary target | `attacker_ship`, `target_ship`, `distance` |
| `DuelScenario` | two active ships | `ship1_file`, `ship2_file`, `distance` |
| `PropulsionScenario` | single-ship movement/physics | `ship_file`, movement flags |
| `ResourceScenario` | consumption/regeneration | `ship_file`, `resource_type` |
| `ComparisonScenario` | baseline vs variant A/B test | baseline/variant ship files, `distance` |

Template rules:

- `_template_preconditions()` must include `self._common_preconditions()` if
  overridden. The framework enforces this with a runtime sentinel.
- `wire_ships()` should call `_snapshot_initial_state(ships_by_role,
  initial_state)` when the template supports it, then apply template-specific
  policies.
- `initial_state` is a pre-engine-start snapshot of HP/resources. Use it when
  initial values matter, because `engine.start()` can run component updates that
  drain always-on resources.
- Prefer existing templates over custom setup.
- Do not duplicate the universal "Simulation Ran" check;
  `_common_preconditions()` owns it.

## Scenario Roles

Combat Lab wires materialized ships through `ships_by_role`. The producer is
`ShipSpec.scenario_role`, not parsed text from `instance_id`.

- Valid labels live in `combat_lab/data/scenario_roles.json`.
- Current labels: `attacker`, `target`, `ship1`, `ship2`, `ship`, `low`, `med`,
  `high`, `provider_a`, `provider_b`, `baseline_attacker`, `baseline_target`,
  `variant_attacker`, `variant_target`.
- Loader/accessor: `combat_lab/scenario_role_registry.py::get_default_combat_lab_role_registry`.
- Compiler: `combat_lab/spec_compiler.py::_ship_spec` validates
  `scenario_role` and raises `ValueError` for unknown labels.
- Consumer: `game/simulation/battle_runner.py::materialize_spec_ships` reads
  `ShipSpec.scenario_role`.
- If a new template reads `ships_by_role["new_role"]`, add `new_role` to
  `combat_lab/data/scenario_roles.json`.
- `tests/unit/combat_lab/test_scenario_roles_consistency.py` scans literal role
  keys in `combat_lab/scenarios/`. Dynamic keys are not fully detectable; keep
  them rare and documented.

`scenario_role` is distinct from gameplay `design_role`; both use
`game.core.roles.RoleRegistry` but separate registry instances.

## Validation Helpers

Import from `combat_lab.scenarios.validation`:

| Helper | Use |
|---|---|
| `check_exact` | integers, strings, exact deterministic values |
| `check_approx` | deterministic floats with relative tolerance |
| `check_tost` | statistical equivalence for RNG outcomes |
| `check_true` | boolean assertions with descriptive `detail=` |

Validation phases should prove assumptions before outcomes:

- Data: loaded stats and ability values are the expected ones.
- Preconditions: ticks ran, geometry is valid, targets moved/fired, shots occurred.
- Outcome: the mechanic produced the measured effect.

TOST proves equivalence within a margin. In this helper, `p < 0.05` means pass
and `p >= 0.05` means not proven equivalent. Use `detail=` for explanatory
context in boolean checks. `Check.__post_init__` coerces numpy booleans to
native `bool`; serialization converts numpy scalars before type checks.

## Authoring Workflow

1. Write or identify the failing scenario/framework test first.
2. Pick exactly one behavior under test.
3. Choose the simplest fitting template.
4. Add or reuse zero-mass test components in `combat_lab/data/components.json`.
5. Add or reuse ships in `combat_lab/data/ships/`; prefer one ship file per configuration.
6. Add the scenario class to the relevant `combat_lab/scenarios/*_scenarios.py` file.
7. Set fixed `seed`, justified `max_ticks`, `telemetry_level`, and precise metadata.
8. Validate data, preconditions, and outcome.
9. Run the focused test ID, then a broader prefix or full Combat Lab run.

For a new combat ability, create one dedicated category/file when practical.
Standard coverage:

- Basic positive effect.
- Same-group stacking: intra-group MAX.
- Different-group stacking: inter-group SUM.
- Negative value or penalty/debuff.
- Resource dependency when applicable.
- Generic resource variant when resource behavior matters.

## Test Data Conventions

Test components use the `test_` prefix and literal names, for example:

- `test_engine_no_fuel`
- `test_engine_with_fuel`
- `test_thruster_std`
- `test_beam_low_acc_1dmg`
- `test_armor_basic`

Component mass convention: test components have `0` mass. Ship mass should come
only from hull components and explicit mass simulators.

Standard hulls:

| Hull ID | Mass | Radius | Use |
|---|---:|---:|---|
| `hull_test_xs` | 100 | 18.57 px | minimum mass |
| `hull_test_s` | 400 | 29.47 px | standard small target |
| `hull_test_m` | 1000 | 40.00 px | reference mass |
| `hull_test_l` | 4000 | 63.50 px | large target |
| `hull_test_fighter` | 25 | 11.70 px | fighter scale |
| `hull_test_satellite` | 100 | 18.57 px | safeguard match |

Radius formula:

```text
radius = 40 * (mass / 1000)^(1/3)
```

Physics safeguard:

```text
max(ship.mass, 100)
```

Mass simulators:

- `test_mass_sim_1k`
- `test_mass_sim_10k`
- `test_mass_sim_100k`

Prefer two single-ability components over one multi-ability component, except
when testing resource consumption that requires abilities to live on the same
component.

## Common Patterns

Distance-based tests:

- Position ships at a controlled distance.
- Use surface distance for weapon ranges and hit probability.
- Let AI strategies fire/move ships instead of manually pulling triggers in
  `update()`.
- Common test movement policies include `test_stationary_fire`,
  `test_do_nothing`, `test_straight_line`, `test_rotate_right`,
  `test_rotate_left`, and `test_erratic`.

Resource tests:

- Use `ResourceScenario` or `ComparisonScenario`.
- Test full resource, partial resource, and no resource.
- Verify exact shot count or uptime when capacity is expected to limit behavior.

A/B tests:

- Use `ComparisonScenario`.
- Same effective seed for baseline and variant.
- Vary only the ship that should carry the ability under test.
- Read `self.baseline_*` and `self.variant_*` populated by collection, or inspect
  `ab.baseline_outcome`, `ab.variant_outcome`, `ab.baseline_telemetry`, and
  `ab.variant_telemetry`.

Negative tests:

- Prove a thing does not happen.
- Include preconditions that the test could have detected the behavior if it
  happened.

Position tracking:

```python
class MyScenario(StaticTargetScenario):
    track_positions = True

    def custom_setup(self, engine) -> None:
        self._tracking_weapon_range = 1000
```

This records per-tick position, speed, heading, distance, and in-range flags.

## Coverage Layout

Ability-specific files:

| Ability/category | File | Test IDs |
|---|---|---|
| `ToHitAttackModifier` | `tohit_attack_scenarios.py` | `TOHIT-ATK-001` to `005` |
| `ToHitAttackModifier` fleet scope | `tohit_attack_fleet_scenarios.py` | `TOHIT-ATK-FLEET-*` |
| `ToHitDefenseModifier` | `tohit_defense_scenarios.py` | `TOHIT-DEF-001` to `004` |
| `ShieldProjection` | `shield_projection_scenarios.py` | `SHIELD-PROJ-*`, `SHIELD-PROJ-METALS-*` |
| `ShieldRegeneration` | `shield_regen_scenarios.py` | `SHIELD-REGEN-*` |
| `ArmorLayer` | `armor_layer_scenarios.py` | `ARMOR-LAYER-*` |
| `EmissiveArmor` | `emissive_armor_scenarios.py` | `EMISSIVE-*` |
| `CommandAndControl` | `cnc_scenarios.py` | `CNC-*` |
| `ShieldRegeneratingArmor` | `sra_scenarios.py` | `SRA-*` |
| `DamagePipeline` | `damage_pipeline_scenarios.py` | `PIPELINE-*` |

Weapon/system files:

| Category | File | Test IDs |
|---|---|---|
| Beam weapons | `beam_scenarios.py` | `BEAMWEAPON-*`, `BEAMWEAPON-RES-*` |
| Projectile weapons | `projectile_scenarios.py` | `PROJECTILE-*`, `PROJECTILE-RES-*` |
| Seeker weapons | `seeker_scenarios.py` | `SEEKER-*` |
| Propulsion | `propulsion_scenarios.py` | `PROP-*` |
| Resources | `resource_scenarios.py` | `RESOURCE-*` |

Modifier files:

- `mod_damage_scenarios.py` - `MOD-DMG-*`
- `mod_range_scenarios.py` - `MOD-RANGE-*`
- `mod_reload_scenarios.py` - `MOD-RELOAD-*`
- `mod_thrust_scenarios.py` - `MOD-THRUST-*`
- `mod_accuracy_scenarios.py` - `MOD-ACC-*`
- `mod_arc_scenarios.py` - `MOD-ARC-*`
- `mod_endurance_scenarios.py` - `MOD-ENDUR-*`
- `mod_consumption_scenarios.py` - `MOD-CONSUME-*`
- `mod_stacking_scenarios.py` - `MOD-STACK-*`

Use `combat_lab/ABILITY_TEST_COVERAGE_PLAN.md` for the current inventory and
remaining coverage, rather than encoding pending-work lists here.

## Invariants and Formulas

Data isolation:

- Combat Lab tests use only `combat_lab/data/`.
- Do not modify production `data/`.
- Validate assumed values against live loaded values.

Stacking:

```text
numeric abilities: intra-group MAX, then inter-group SUM
marker abilities: boolean OR
no stack_group: each component is its own group and stacks
```

There are no multiplicative exceptions for numeric combat ability stacking in
this test guide. Aggregated numeric values are then consumed additively by the
formula that uses them, such as beam hit chance.

Resources:

| Trigger | Example | Failure mode |
|---|---|---|
| `constant` | shields, engines | component becomes non-operational and loses stat contributions |
| `activation` | weapons | `can_afford_activation()` returns false, so the weapon refuses to fire |

Resource types are data-driven. Tests cover generic resources such as `metals`;
do not hardcode fuel/energy/ammo assumptions. Resource storage components always
contribute capacity regardless of operational status.

Stats:

- `ShipStatsCalculator` skips non-operational components during Phase 3 aggregation.
- `current_shields` is capped when `max_shields` decreases.
- Ship defaults are additive-neutral: `total_defense_score = 0.0`,
  `baseline_to_hit_offense = 0.0`.
- Resource max tracking uses a generic `_prev_max_resources: dict`.

Distance:

```text
target_radius = 40 * (mass / 1000) ** (1/3)
surface_distance = center_distance - target_radius
```

Beam weapons use target surface distance, not center distance.

Speeds:

```text
ship max_speed = (total_thrust * 25) / mass        # px/tick
projectile effective_speed = projectile_speed / 100
turn per tick = turn_speed / 100                   # degrees/tick
```

Projectile hit rates:

```text
resolved_shots = total_shots_fired - in_flight
resolved_hit_rate = hits / resolved_shots
```

Do not count in-flight projectiles as misses.

Defense score:

```python
radius = 40 * ((max(mass, 100) / 1000) ** (1 / 3))
diameter = radius * 2
d_ratio = max(0.1, diameter / 80.0)
size_score = -2.5 * math.log10(d_ratio)
maneuver_score = math.sqrt((acceleration / 20.0) + (turn_speed / 360.0))
defense_score = size_score + maneuver_score + ecm_score
```

Statistical tiers:

| Tier | Ticks | Margin | Use |
|---|---:|---:|---|
| Standard | 500 | +/-10% | fast development validation |
| High-tick | 100000 | +/-1% | precision validation |

For probabilistic tests, prefer deterministic assertions when possible. Use TOST
for RNG equivalence. Default to `p < 0.001` if feasible within about 1000 ticks;
use `p < 0.05` only when stricter precision would require excessive ticks.

## Telemetry

`TestMetadata.telemetry_level` is parsed into
`game/simulation/combat/telemetry.py::TelemetryLevel`:

| Level | BattleOutcome detail |
|---|---|
| `MINIMAL` | end reason, duration, seed, per-ship status/components/pose |
| `NORMAL` | MINIMAL plus weapon summaries and ship stats |
| `DETAILED` | NORMAL plus hit records and modifier applications |

Combat Lab defaults to `DETAILED` because scenarios often need weapon and
in-flight projectile data. Use lower levels only when a scenario does not need
forensics and batch speed matters.

`CombatLabTelemetry` currently carries role-keyed in-flight projectile counts
captured just before the engine is torn down. Use it for resolved projectile hit
rates and avoid post-run engine references.

## ComparisonScenario Details

`ComparisonScenario` runs baseline and variant as paired battles with the same
effective seed.

Useful APIs:

- `validate(self, ab: ABBattleOutcome) -> list[Check]`
- `configure_baseline(engine) -> None`
- `configure_variant(engine) -> None`
- `build_baseline_spec(self) -> BattleSpec`
- `build_variant_spec(self) -> BattleSpec`
- `combat_lab/services/ab_battle_runner.py::ABBattleRunner.run(baseline_spec, variant_spec) -> ABBattleOutcome`

Current implementation detail: the normal path still runs the private baseline
via `_run_baseline_battle()` and stashes `_baseline_outcome` /
`_baseline_telemetry`; `_run_validation()` packages those with the variant
outcome into `ABBattleOutcome`. The `ABBattleRunner` API exists, but do not
assume all comparison scenarios have been fully flipped to it.

Combat Lab UI shows Visual Run, Headless Run, and Visual Baseline for comparison
tests. Visual Baseline renders the baseline; validation is preconditions-only in
visual-baseline mode because there is no variant outcome in that mode.

Choose which side varies:

| Ability type | Vary |
|---|---|
| attack modifier/sensor | attacker |
| defense modifier/ECM | target |
| shield/armor defense | target |
| weapon resource | attacker |

## History and Reporting

Current history storage is sharded:

- One JSON file per test ID under `combat_lab/test_history/{test_id}.json`.
- Shards are lazy-loaded by `TestHistory`.
- Writes use `save_json()` temp-and-rename behavior.
- A corrupt shard is backed up to `{test_id}.json.corrupt` and that one test
  starts fresh; other shards are unaffected.
- A legacy monolithic `combat_lab/test_history.json`, if present, is split once
  into shards and renamed to `test_history.json.migrated`.

If comments or older docs mention `test_history.json` as the active storage
file, treat that as stale.

## Troubleshooting

Ship `expected_stats` mismatch:

```bash
python Tools/fix_designs/fix_designs.py combat_lab/data/ships
python Tools/validate_designs/validate_designs.py combat_lab/data/ships
```

`expected_stats.mass` includes hull base mass from the vehicle class.

Ship file not found:

- Put files under `combat_lab/data/ships/`.
- Use `self._load_ship("filename.json")` where applicable.

Test not discovered:

- File is under `combat_lab/scenarios/`.
- Filename ends with `_scenarios.py`.
- Class extends `TestScenario` or a template.
- Class has non-`None` `metadata`.

CLI pass but Combat Lab fail:

- Confirm fixed seed.
- Remove rendering/timing dependencies.
- Confirm the visual path is still using the spec-driven runner/controller, not
  raw engine setup.
- Confirm scenario `update()` does not assume a live engine after `run_battle`
  returns.

## System Requirements

- Python 3.13+ project baseline.
- `pygame-ce` for UI execution.
- `scipy` for TOST calculations.

## Extension Checklist

- Use strict TDD for framework or scenario behavior changes.
- Keep one behavior per test.
- Minimize ship/component complexity.
- Use fixed seeds and justified tick counts.
- Set telemetry level deliberately.
- Verify data and preconditions before outcomes.
- Use surface distance for range/hit checks.
- Use resolved projectile shots for projectile hit rates.
- Keep test components zero-mass unless mass is the behavior under test.
- Register new literal `ships_by_role[...]` labels in `combat_lab/data/scenario_roles.json`.
- Prefer existing templates; custom `to_spec()` is an escape hatch only.
- Run focused tests first, then `python -m combat_lab.run_tests --fast` or full
  Combat Lab suite when scope warrants.
