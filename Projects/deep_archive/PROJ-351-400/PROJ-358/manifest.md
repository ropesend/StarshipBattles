# PROJ-358 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/battle_runner.py` | Production | Replace silent-ignore in `_apply_spec_components_to_ship` (lines 580-619) with `ValidationException` raise; remove the "design drift" docstring justification. |
| `game/simulation/battle_spec.py` | Production (read-only / minor) | Read `ShipSpec.components` shape; only edit if a helper for the validation lives more naturally here than in the runner. |
| `game/strategy/combat/spec_compiler.py` | Production (caller, audit) | Audit only; if validation surfaces real drift, fix the compiler — but treat that as out-of-scope follow-up unless trivial. |
| `game/ui/screens/battle_setup/spec_compiler.py` | Production (caller, audit) | Same — audit only. |
| `tests/unit/simulation/battle_runner/test_spec_component_validation.py` | Test (new) | Unmapped component raises with ship/component/design context; valid specs unchanged. |
