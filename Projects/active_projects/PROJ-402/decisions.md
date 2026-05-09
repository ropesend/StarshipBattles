# PROJ-402: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-03: SimulationBattleResolver catch ValidationException |
| 2026-05-09 | Widened catch to tuple `(SimulationException, ValidationException)` rather than catching a common base | `ValidationException` and `SimulationException` are sibling subclasses of `GameException`; widening to `GameException` would over-catch (e.g. configuration errors unrelated to battle context). The tuple is precise and matches what `run_battle` actually raises (battle_runner.py:640-652). |
| 2026-05-09 | Kept both regression tests (`ValidationException` and `SimulationException` paths) in `TestSimulationAdapterBattleContextPreservation` | The originally-required B-6 case is `ValidationException`; the substituted test that PROJ-381 shipped also has value (covers the existing `SimulationException` branch). Retained both to avoid losing coverage. |
| 2026-05-09 | No other adapters need the same fix | `rg "except SimulationException" game/strategy/adapters/` returned zero matches outside `simulation_adapter.py`. No follow-up work flagged. |
