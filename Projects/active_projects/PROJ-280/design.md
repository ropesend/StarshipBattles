# PROJ-280: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current template shape

[combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py) defines 5 abstract templates:
1. **StaticTargetScenario** — attacker fires at stationary target; collects `damage_dealt`
2. **DuelScenario** — two ships engage; tracks damage dealt/taken; determines winner
3. **PropulsionScenario** — single ship physics; optional position tracking
4. **ResourceScenario** — resource consumption; single ship ± optional target
5. **ComparisonScenario** — A/B baseline vs variant via [combat_lab/services/ab_battle_runner.py](../../../combat_lab/services/ab_battle_runner.py)

### Observed duplication (per Combat Lab Explore agent's review)

- **`_template_preconditions()`** — nearly-identical implementations across templates: assert simulation ran, ticks > 0, ships exist. Roughly the same 10-15 lines repeated 5 times.
- **`wire_ships()`** — pre-amble (snapshot initial state, cache `initial_hp`, set up role-keyed attribute aliases) and post-amble (wire engine reference) are similar across templates.
- **Weapon stat collection** — `_collect_weapon_stats(ship, role, engine=None)` already lives on the base, but per-template glue around it duplicates.

### Why we need active enforcement, not just convention

The user's feedback memory ([feedback_no_bandaids.md]) says: never bandaid; always find architectural root cause. If we extract shared helpers but rely on convention, the next template author can quietly copy-paste-modify a sibling and re-introduce the duplication. The user explicitly chose "base-class enforcement" so the system catches drift at construction time.

## Architecture

### New base class shape

```python
# combat_lab/scenarios/base.py — additions

class TestScenario:
    # ... existing ...

    # NEW: standardized lifecycle
    def _snapshot_initial_state(self, ships_by_role: Dict[str, Ship]) -> Dict[str, Any]:
        """Captures hp, position, velocity, resources for each role'd ship.
        Templates MUST call this from wire_ships() before role-specific setup.
        """
        ...

    def _common_preconditions(self) -> List[Check]:
        """Shared preconditions — every template's _template_preconditions()
        must include these. Override _template_preconditions() to ADD checks,
        never to REPLACE these.
        """
        return [
            check_true(self._engine_started, "engine started"),
            check_true(self.ticks_run > 0, "simulation ran for at least one tick"),
            ...
        ]

    def _template_preconditions(self) -> List[Check]:
        """Subclasses extend; the base provides common checks via super()."""
        return self._common_preconditions()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Enforcement: detect templates that skip super() in _template_preconditions
        # by inspecting the AST or by runtime guard wrapper
        _validate_template_subclass(cls)
```

### Enforcement mechanisms (pick during Phase 3)

Three options to be evaluated in Phase 3:

**A. AST inspection in `__init_subclass__`** — parse subclass `_template_preconditions` and verify it calls `super()._template_preconditions()`. Static guarantee.
**B. Runtime sentinel** — base method sets `self._common_preconditions_called = True`; harness checks the flag after running checks. Detects drift on first run.
**C. Composition over inheritance** — base provides `_template_preconditions(extra_checks: List[Check]) -> List[Check]` and templates pass their extras. Enforcement free — you literally cannot skip the base checks.

Recommendation: **C** is cleanest if the API change is acceptable. Falls back to **B** if call sites resist.

### Migration plan

Phase 4 walks each template and replaces its body with the new pattern. Tests pass at every step (templates' contracts don't change externally — only internal duplication is removed).

### Authoring guide content (Phase 5)

Add to [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md) a section "Adding a new TestScenario template":
1. Subclass `TestScenario`
2. Implement `wire_ships(ships_by_role, engine, initial_state)` — DO NOT snapshot initial state yourself; the base does that
3. Implement `collect_results(outcome, telemetry)` — populate measurement attributes
4. To add preconditions, return `[*self._common_preconditions(), check_*(...) for your_specific_logic]` or use the chosen enforcement API
5. NEVER copy-paste another template's body

## Key Patterns to Reuse
- **Composition over inheritance** — see [game/simulation/combat/](../../../game/simulation/combat/) for examples of focused helper classes
- **`__init_subclass__` validation** — limited use elsewhere in the codebase; this would be a documented pattern addition

## Dependencies & Risks
1. **Concrete scenarios that override template internals** — some `*_scenarios.py` files may override `_template_preconditions()` or `wire_ships()` directly. Migration must preserve their semantics. **Mitigation:** Phase 1 audit identifies all overrides
2. **Base-class enforcement choice impacts API** — Option C changes the precondition API surface. Need user input or ratification during Phase 3
3. **Base class becoming a god class itself** — adding too many helpers to TestScenario undermines the goal. **Mitigation:** if base grows past ~300 lines, extract to a `ScenarioLifecycle` mixin

## Opportunities Discovered
- The `_collect_weapon_stats` helper is already shared but not consistently used — Phase 4 can sweep templates to use it uniformly
- Position tracking opt-in (`track_positions=True`) has duplicated wiring across PropulsionScenario implementers — could become a base-class utility

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
