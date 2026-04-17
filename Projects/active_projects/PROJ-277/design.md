# PROJ-277: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation.

## Initial Analysis

`ComparisonScenario` at [combat_lab/scenarios/templates.py:827-920, 1120-1166](../../../combat_lab/scenarios/templates.py) embeds `run_battle()` inside scenario methods:

- `_run_baseline_battle()` (L827) is called from `before_run_battle()` — orchestration inverted
- Baseline outcome + telemetry stashed on `self._baseline_*` attributes (L915-920)
- Telemetry keys get role-remapped: `"attacker"` becomes `"baseline_attacker"` at L915-920 to disambiguate
- `_run_validation()` override at L1120-1166 branches on `_visual_baseline` mode and BYPASSES `validate()` entirely

The `_run_validation()` bypass is a silent contract violation. `validate()` is defined on the scenario base class; subclasses expect it to run. Visual-baseline mode exists to render the baseline battle visually — it has no reason to SKIP validation.

## Swarm Findings Summary

### Architecture
- Single entry `run_battle(spec) -> BattleOutcome` already produces a complete outcome + captures telemetry via `per_tick_callback`
- `CombatLabTelemetry` at `combat_lab/telemetry.py:30-38` is the per-test telemetry DTO
- `scenario_run_helper.py::run_scenario` at L67-100 currently calls `run_battle()` once and passes the single (outcome, telemetry) pair to scenario validation
- For A/B: call `run_battle()` TWICE, pack both outcomes + telemetry into `ABBattleOutcome`, pass to validate

### Key Patterns to Reuse
- **Frozen DTO** (pattern 3) — `ABBattleOutcome` as `@dataclass(frozen=True)`
- **Single-source orchestration** — `ABBattleRunner.run(baseline_spec, variant_spec)` owns the two battles, scenarios are passive inputs
- **Unified validation contract** — `validate(ab_outcome)` always runs; visual-baseline is a rendering mode, not a validation gate

### Dependencies & Risks
1. **Risk: ComparisonScenario subclass count.** ~10-20 test files inherit. Phase 5 must migrate all. Mitigation: grep for `class.*\(ComparisonScenario\)` to enumerate.
2. **Risk: role-keyed ship registry.** Current `ship_builder` at L844 tracks roles via `self._role_to_ship_instance_id`. A/B runner must preserve role tracking across both runs — roles map to ShipSpecs in each spec. Mitigation: roles live in the spec; runner just invokes `run_battle` twice with the same role schema.
3. **Risk: telemetry composition.** When the scenario validates `ABBattleOutcome`, both `baseline_telemetry` and `variant_telemetry` are available — no role remapping needed. Scenarios can compare `ab.baseline_telemetry.ship_stats["attacker"]` to `ab.variant_telemetry.ship_stats["attacker"]`.
4. **Dependency: PROJ-274 (ship_materializer).** NOT a hard dependency — ComparisonScenario continues to pass its role-tracking ship_builder as an override. However, if PROJ-274 lands first, Phase 3 can simplify further by using context materializer.

### Opportunities Discovered
- Visual-baseline mode can be reinstated cleanly as a rendering option that runs BOTH baseline and variant, showing baseline first. Currently it's a "skip variant" mode — but a user wanting to see the baseline usually also wants to see the variant for comparison.
- Scenarios can now express "compare telemetry X between baseline and variant" as a first-class pattern; today it's ad-hoc per-scenario.

## Design Decisions

See [decisions.md](decisions.md).

## Interface Sketch

```python
# combat_lab/scenarios/ab_outcome.py

from dataclasses import dataclass
from game.simulation.battle_outcome import BattleOutcome
from combat_lab.telemetry import CombatLabTelemetry

@dataclass(frozen=True)
class ABBattleOutcome:
    baseline_outcome: BattleOutcome
    baseline_telemetry: CombatLabTelemetry
    variant_outcome: BattleOutcome
    variant_telemetry: CombatLabTelemetry
```

```python
# combat_lab/services/ab_battle_runner.py

class ABBattleRunner:
    def __init__(self, *, ai_factory, ship_builder=None):
        self._ai_factory = ai_factory
        self._ship_builder = ship_builder

    def run(self, baseline_spec: BattleSpec, variant_spec: BattleSpec) -> ABBattleOutcome:
        baseline_outcome, baseline_telemetry = self._run_one(baseline_spec)
        variant_outcome, variant_telemetry = self._run_one(variant_spec)
        return ABBattleOutcome(
            baseline_outcome=baseline_outcome,
            baseline_telemetry=baseline_telemetry,
            variant_outcome=variant_outcome,
            variant_telemetry=variant_telemetry,
        )

    def _run_one(self, spec) -> Tuple[BattleOutcome, CombatLabTelemetry]:
        telemetry = CombatLabTelemetry()
        outcome = run_battle(
            spec,
            ai_factory=self._ai_factory,
            ship_builder=self._ship_builder,
            per_tick_callback=telemetry.on_tick,
        )
        return outcome, telemetry
```

## ComparisonScenario Refactor

Before:
```python
class ComparisonScenario(TestScenario):
    def before_run_battle(self, spec):
        self._run_baseline_battle(spec)  # ← embeds run_battle()
        return spec  # variant spec

    def _run_baseline_battle(self, spec):
        baseline_spec = self._build_baseline_spec()
        self._baseline_outcome = run_battle(baseline_spec, ...)
        self._baseline_telemetry = ...  # role-remapped

    def _run_validation(self, outcome, telemetry):
        if self._visual_baseline:
            return  # silent bypass
        return self.validate(outcome, telemetry, self._baseline_outcome, self._baseline_telemetry)
```

After:
```python
class ComparisonScenario(TestScenario):
    def build_baseline_spec(self, base_spec: BattleSpec) -> BattleSpec:
        """Override to modify base spec into baseline spec (e.g. strip a modifier)."""
        return base_spec

    def build_variant_spec(self, base_spec: BattleSpec) -> BattleSpec:
        """Override to modify base spec into variant spec (e.g. apply a new ability)."""
        return base_spec

    def validate(self, ab: ABBattleOutcome) -> List[Check]:
        """Receives both outcomes + telemetries. No _baseline_* attrs needed."""
        ...
```

## Dispatch Update

`scenario_run_helper.py::run_scenario` at L67-100:

```python
# Before (simplified):
def run_scenario(scenario):
    spec = scenario.to_spec(...)
    scenario.before_run_battle(spec)  # ← may embed an entire run_battle call
    telemetry = CombatLabTelemetry()
    outcome = run_battle(spec, ..., per_tick_callback=telemetry.on_tick)
    return scenario._run_validation(outcome, telemetry)

# After:
def run_scenario(scenario):
    base_spec = scenario.to_spec(...)
    if isinstance(scenario, ComparisonScenario):
        runner = ABBattleRunner(ai_factory=..., ship_builder=scenario.ship_builder)
        baseline_spec = scenario.build_baseline_spec(base_spec)
        variant_spec = scenario.build_variant_spec(base_spec)
        ab_outcome = runner.run(baseline_spec, variant_spec)
        return scenario.validate(ab_outcome)
    # non-comparison scenarios: single run as before
    telemetry = CombatLabTelemetry()
    outcome = run_battle(base_spec, ..., per_tick_callback=telemetry.on_tick)
    return scenario.validate(outcome, telemetry)
```

## Visual-Baseline Mode

Today: `_visual_baseline` flag causes `_run_validation()` to skip `validate()`.

Replacement: visual-baseline mode renders the BASELINE battle only (a rendering choice). `validate()` STILL RUNS on the full `ABBattleOutcome` after both battles complete. This aligns with the principle that validation is ALWAYS part of a scenario's contract.

Implementation: in the UI path, pass a `render_variant: bool` flag to `ABBattleRunner.run()` — it still runs both battles, but only one is rendered visually. Validation output is displayed regardless.
