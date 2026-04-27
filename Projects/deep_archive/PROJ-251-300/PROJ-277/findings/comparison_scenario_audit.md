# ComparisonScenario API Audit — Phase 3 Task 3.1

**Date:** 2026-04-16
**Source:** `combat_lab/scenarios/templates.py:736-1210` + `combat_lab/spec_compiler.py:394-446`

## Class Attributes

```python
class ComparisonScenario(TestScenario):
    # Required configuration (subclasses MUST set)
    baseline_attacker_ship: Optional[str] = None
    baseline_target_ship: Optional[str] = None
    variant_attacker_ship: Optional[str] = None
    variant_target_ship: Optional[str] = None
    distance: Optional[float] = None

    # Optional configuration
    attacker_angle: float = 0.0
    target_angle: float = 0.0
    force_fire: bool = True
    expect_different_damage: bool = True

    # UI-driven rendering mode flag
    _visual_baseline: bool = False
```

**Key insight:** Baseline vs variant is expressed as **different ship
designs**, not as "strip a modifier from a common spec". So the
design.md sketch `build_baseline_spec(base_spec) -> BattleSpec` that
implies a common base is misaligned with reality.

## Method Inventory

| Method | Line | Role |
|---|---|---|
| `_validate_config` | 812 | Assert required attrs set |
| `_run_baseline_battle` | 827 | **Private baseline battle via embedded `run_battle()`** (target of deletion) |
| `_build_baseline_battle_spec` | 925 | Builds `BattleSpec` for the baseline battle (inline duplication of `_compile_comparison`) |
| `configure_baseline(engine)` | 1003 | Hook for subclasses — called after baseline ships loaded |
| `configure_variant(engine)` | 1013 | Hook for subclasses — called after variant ships loaded |
| `before_run_battle(spec)` | 1022 | **Calls `_run_baseline_battle()` if not `_visual_baseline`** (target) |
| `wire_ships(ships_by_role)` | 1036 | Routes to baseline_* / variant_* role keys based on `_visual_baseline` |
| `update(battle_engine)` | 1072 | Per-tick tracking |
| `collect_results(outcome, telemetry)` | 1078 | Branches on `_visual_baseline`: only baseline data populated in VB mode |
| `_run_validation(outcome, telemetry)` | 1132 | **Overrides base class; BYPASSES `validate()` in VB mode** (target) |
| `_template_preconditions` | 1170 | Auto-precondition checks (branches on `_visual_baseline`) |

## Instance attributes populated during runs

**Stashed by `_run_baseline_battle` (L903-909):**
- `self._baseline_attacker`
- `self._baseline_target`
- `self._baseline_initial_hp`
- `self._baseline_final_hp`
- `self._baseline_damage_dealt`
- `self._baseline_ticks`
- `self._baseline_target_alive`

**Promoted to validation-facing attrs in `collect_results` (L1098-1126):**
- `self.baseline_damage_dealt`
- `self.baseline_initial_hp`
- `self.baseline_final_hp`
- `self.baseline_ticks`
- `self.variant_damage_dealt`
- `self.variant_initial_hp`
- `self.variant_final_hp`
- `self.variant_ticks`
- Per-weapon stats via `self._collect_weapon_stats(..., 'baseline_attacker' | 'variant_attacker' | ...)`

**Role-remapping hack** at L914-917: `_run_baseline_battle` builds a
`CombatLabTelemetry` with keys `baseline_attacker` / `baseline_target`
so they don't collide with the variant run's `variant_attacker` /
`variant_target` keys.

## Subclass count

98 ComparisonScenario subclasses across 21 scenario files (via
`grep "class.*(ComparisonScenario)" combat_lab/scenarios/*.py`):

| File | Subclasses |
|---|---|
| shield_projection_scenarios.py | 10 |
| seeker_scenarios.py | 8 |
| beam_scenarios.py | 7 |
| emissive_armor_scenarios.py | 7 |
| shield_regen_scenarios.py | 7 |
| cnc_scenarios.py | 6 |
| damage_pipeline_scenarios.py | 6 |
| projectile_scenarios.py | 5 |
| sra_scenarios.py | 5 |
| mod_accuracy_scenarios.py | 4 |
| mod_damage_scenarios.py | 4 |
| mod_stacking_scenarios.py | 4 |
| tohit_attack_fleet_scenarios.py | 3+ |
| tohit_attack_scenarios.py | 3+ |
| tohit_defense_scenarios.py | 3+ |
| (others) | ~20 |

All override `validate(self, outcome, telemetry=None)` with the
LEGACY signature. Most (all?) use `self.baseline_*` and
`self.variant_*` attrs + `check_*` helpers from
`combat_lab/scenarios/validation.py`.

## Subclass hook override pattern

Typical subclass looks like:

```python
class FooScenario(ComparisonScenario):
    metadata = TestMetadata(...)
    baseline_attacker_ship = "Test_A_NoAbility.json"
    baseline_target_ship = "Test_Target.json"
    variant_attacker_ship = "Test_A_WithAbility.json"
    variant_target_ship = "Test_Target.json"
    distance = 400

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        checks.append(check_true(
            "With-Ability Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            ...
        ))
        return checks
```

A tiny minority also override `configure_baseline` / `configure_variant`
or `collect_results` (for custom telemetry). Grep for these patterns
before Phase 5 migration — they need case-by-case attention.

## External callers

External code calls `scenario.validate(outcome, telemetry)` via the
base TestScenario `_run_validation` (which ComparisonScenario overrides
at L1132). The new API `validate(ab_outcome)` is a breaking change for
every ComparisonScenario subclass — migrating all 98 is Phase 5's job.

`before_run_battle`, `wire_ships`, `collect_results`, `update` are
called by `scenario_run_helper.run_scenario_via_run_battle`. The new
A/B dispatch path (Phase 4) will call `ABBattleRunner.run()` directly
instead, so these helper methods can change shape without breaking
non-comparison scenarios.

## Implications for the planned refactor

**Design.md sketch says:**
```python
def build_baseline_spec(self, base_spec: BattleSpec) -> BattleSpec:
    return base_spec  # identity default
```

**Reality demands:**
```python
def build_baseline_spec(self) -> BattleSpec:
    # Full spec built from scenario config (ship files, distance, etc.).
    # Default uses baseline_*_ship.
    return self._default_baseline_spec()

def build_variant_spec(self) -> BattleSpec:
    # Same but with variant_*_ship.
    return self._default_variant_spec()
```

Each hook produces a COMPLETE spec from scenario config. The existing
`_build_baseline_battle_spec` (L925) becomes `_default_baseline_spec`;
the variant side can reuse `spec_compiler._compile_comparison` logic
but with the visual-baseline branch removed.

**Collect_results / baseline_* / variant_* attribute pattern:**
The 98 subclasses all read `self.baseline_*` / `self.variant_*`. The
cleanest migration path is to KEEP `collect_results` populating those
attributes, but drive them from the `ABBattleOutcome` — not from the
ad-hoc `_baseline_*` stash + the runner's `outcome`. That way
subclasses' `validate(outcome, telemetry)` bodies work unchanged,
except that `validate(ab_outcome)` signature replaces the positional
params. Since every subclass IGNORES those positional params and just
reads `self.*` attributes, this is a straightforward rename.

## Recommendation for Phase 3

Given the scope (98 subclasses) and risk of breaking all comparison
tests mid-refactor, do Phase 3 in these SAFE steps:

1. **Task 3.1 (this doc)** — ✅ done.
2. **Task 3.3 additive** — add `build_baseline_spec()` and
   `build_variant_spec()` as *new* methods; defaults delegate to the
   existing `_build_baseline_battle_spec` / spec-compiler logic. No
   existing code changes behavior.
3. **Task 3.2 / 3.4 / 3.5 / 3.6** — these are breaking. Best tackled
   TOGETHER in a dedicated session: new API goes live, all 98
   subclasses migrate in the same change (Phase 5), and the old
   methods are deleted in one atomic swap.

For this session, proceed through Tasks 3.1 and 3.3 (additive). Stop
before breaking changes; handoff the atomic-swap design to the next
session.
