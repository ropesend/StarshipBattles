# PROJ-279: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### What the monkey-patch does today

[combat_lab/spec_compiler.py:474](../../../combat_lab/spec_compiler.py#L474) ends the module with something like:

```python
def _to_spec(self, registries=None):
    return build_test_battle_spec(self, registries)

TestScenario.to_spec = _to_spec
```

This is module-import-time mutation of the `TestScenario` class. Effects:
- After `combat_lab.spec_compiler` is imported (which `runner.py` does at startup), every `TestScenario` instance has a `to_spec()` method that didn't exist before
- The method comes from a different file than the class — IDE jump-to-definition fails
- A static analyzer / new contributor reading `combat_lab/scenarios/base.py` sees no `to_spec` and is confused when callers invoke it
- A test that imports `TestScenario` BEFORE `combat_lab.spec_compiler` sees a different class shape than tests that import after

### Why the "explicit composition" answer is the cleanest

Looking at the parallel architecture in Battle Setup:
- [game/ui/screens/battle_setup_state.py](../../../game/ui/screens/battle_setup_state.py) — pure data model, no `to_spec`
- [game/ui/screens/battle_setup/spec_compiler.py](../../../game/ui/screens/battle_setup/spec_compiler.py) — `build_manual_battle_spec(state, registries, ...)` is called explicitly by [game/ui/screens/battle_setup_screen.py](../../../game/ui/screens/battle_setup_screen.py)

Combat Lab should match this. The compiler is a pure function. Scenarios describe a setup. The runner asks the compiler to produce a spec. No coupling between scenario and compiler — only between runner and compiler.

### Caller surface (audit needed in Phase 1 Task 1.1)

Likely callers based on architecture review:
- [combat_lab/runner.py](../../../combat_lab/runner.py) — `run_scenario_via_run_battle` helper
- [combat_lab/services/test_execution_service.py](../../../combat_lab/services/test_execution_service.py) — both `run_visual` and `run_headless`
- [combat_lab/services/ab_battle_runner.py](../../../combat_lab/services/ab_battle_runner.py) — A/B comparison runner
- [game/ui/screens/test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py) — `_switch_to_battle` for visual mode
- Possibly `combat_lab/services/scenario_run_helper.py`

Tests that hit `scenario.to_spec()` directly need migration too.

## Architecture

### Before
```
TestRunner
  → scenario.to_spec()                    # monkey-patched
    → build_test_battle_spec(scenario)    # actual work
      → BattleSpec
```

### After
```
TestRunner
  → build_test_battle_spec(scenario)      # explicit import + call
    → BattleSpec
```

No new types, no new files. Just deletes a layer of indirection.

### TestScenario base class
- Remove the placeholder `to_spec()` method from [combat_lab/scenarios/base.py](../../../combat_lab/scenarios/base.py) (currently exists as a stub before the patch overwrites it)
- The base class becomes purely descriptive — metadata, `before_run_battle`, `wire_ships`, `validate`, `collect_results`. No spec construction concern.

### Authoring rules (documentation update)
Add to [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md):
> Scenarios describe a battle setup. They do NOT construct `BattleSpec`s. To produce a spec from a scenario, call `build_test_battle_spec(scenario, registries)` explicitly. Adding a `to_spec` method to a scenario class is forbidden — the runner owns spec construction.

## Key Patterns to Reuse
- **Spec compiler pattern** — see [game/ui/screens/battle_setup/spec_compiler.py](../../../game/ui/screens/battle_setup/spec_compiler.py) and [game/strategy/combat/spec_compiler.py](../../../game/strategy/combat/spec_compiler.py) for the explicit-call shape

## Dependencies & Risks
1. **Test discovery order** — some tests may import `TestScenario` and expect `to_spec` to exist before any `combat_lab.spec_compiler` import has happened. Migration cleans this up but could expose order-dependency bugs. **Mitigation:** run the full sharded suite to flush these out
2. **Hidden caller via `getattr`** — some code might do `getattr(scenario, "to_spec", None)`. Grep must include this form. **Mitigation:** Phase 1 Task 1.1 audit
3. **Sequencing dependency on PROJ-278** — see plan.md Current State

## Opportunities Discovered
- The `to_spec` removal is the visible tip of a broader pattern: scenarios should be inert data objects, not behavioural mixins. Future projects could push this further (e.g. extracting `validate()` and `wire_ships()` into a separate `ScenarioBehavior` object) — out of scope here

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
